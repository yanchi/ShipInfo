<?php

namespace App\Tests;

use App\Entity\Company;
use App\Entity\Operation;
use App\Entity\Route;

class HomeControllerTest extends IntegrationTestCase
{
    public function testHomePageReturns200(): void
    {
        $client = static::createClient();
        $client->request('GET', '/');
        $this->assertResponseIsSuccessful();
    }

    public function testHomePageShowsNoDataMessageWhenEmpty(): void
    {
        $client = static::createClient();
        $em = static::getContainer()->get('doctrine.orm.entity_manager');

        $companies = $em->getRepository(\App\Entity\Company::class)->findAll();
        foreach ($companies as $company) {
            $em->remove($company);
        }
        $em->flush();

        try {
            $client->request('GET', '/');
            $this->assertSelectorTextContains('p', '現在、運航情報はありません。');
        } finally {
            $em->clear();
        }
    }

    public function testHomePageShowsLatestOperationForRoute(): void
    {
        $client = static::createClient();
        $em = static::getContainer()->get('doctrine.orm.entity_manager');

        $now = new \DateTimeImmutable();
        $today = '2025-02-12';
        $this->mockClock($today);

        $company = (new Company())
            ->setName('最新便テスト運輸')
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($company);

        $route = (new Route())
            ->setName('P港 ⇔ Q港')
            ->setCompany($company)
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($route);

        // 古い日付の運航（欠航）→ 今日ではないので表示されないはず
        $olderOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTimeImmutable('2025-02-10'))
            ->setStatus(['cancelled'])
            ->setStatusText(['欠航'])
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($olderOp);

        // 今日の運航（通常）→ こちらが表示される
        $newerOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTimeImmutable($today))
            ->setStatus(['normal'])
            ->setStatusText(['通常運航'])
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($newerOp);

        $em->flush();
        $companyId = $company->getId();
        $em->clear();

        try {
            $crawler = $client->request('GET', '/');

            $this->assertResponseIsSuccessful();
            // 今日（2025-02-12）の通常運航が表示される
            $this->assertSelectorTextContains('span.status', '通常運航');
            // 古い日付（2025-02-10）の欠航はステータス欄に表示されない
            $statusTexts = implode('', $crawler->filter('span.status')->each(fn($n, $i) => $n->text()));
            $this->assertStringNotContainsString('欠航', $statusTexts);
        } finally {
            $this->cleanupEntity($em, Company::class, $companyId);
        }
    }

    public function testHomePageDisplaysCompanyAndFallbackStatus(): void
    {
        $client = static::createClient();
        $em = static::getContainer()->get('doctrine.orm.entity_manager');

        $now = new \DateTimeImmutable();
        $company = (new Company())
            ->setName('テスト運輸')
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($company);

        $route = (new Route())
            ->setName('那覇 ⇔ 鹿児島')
            ->setCompany($company)
            ->setDirection('上り')
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($route);
        $em->flush();

        $companyId = $company->getId();
        $em->clear();

        try {
            $client->request('GET', '/');
            $content = $client->getResponse()->getContent();

            $this->assertResponseIsSuccessful();
            $this->assertStringContainsString('テスト運輸', $content);
            $this->assertStringContainsString('那覇 ⇔ 鹿児島', $content);
            // operationがない場合、「運航予定なし」が表示される
            $this->assertStringContainsString('運航予定なし', $content);
        } finally {
            $this->cleanupEntity($em, Company::class, $companyId);
        }
    }
}
