<?php

namespace App\Tests;

use App\Entity\Company;
use App\Entity\Operation;
use App\Entity\Route;
use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;

class HomeControllerTest extends WebTestCase
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

        // 古い日付の運航（欠航）→ 表示されないはず
        $olderOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTime('2025-02-10'))
            ->setStatus(['cancelled'])
            ->setStatusText(['欠航'])
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($olderOp);

        // 新しい日付の運航（通常）→ こちらが表示される
        $newerOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTime('2025-02-12'))
            ->setStatus(['normal'])
            ->setStatusText(['通常運航'])
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($newerOp);

        $em->flush();
        $companyId = $company->getId();
        $em->clear();

        try {
            $client->request('GET', '/');
            $content = $client->getResponse()->getContent();

            $this->assertResponseIsSuccessful();
            // 最新日付（2025-02-12）の通常運航が表示される
            $this->assertStringContainsString('通常運航', $content);
            // 古い日付（2025-02-10）の欠航は表示されない
            $this->assertStringNotContainsString('欠航', $content);
        } finally {
            $em->clear();
            $company = $em->find(Company::class, $companyId);
            if ($company) {
                $em->remove($company);
                $em->flush();
            }
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
            // operationがない場合、フォールバック値が表示される
            $this->assertStringContainsString('通常運航', $content);
        } finally {
            $em->clear();
            $company = $em->find(Company::class, $companyId);
            if ($company) {
                $em->remove($company);
                $em->flush();
            }
        }
    }
}
