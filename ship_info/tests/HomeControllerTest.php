<?php

namespace App\Tests;

use App\Entity\Company;
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
        $client->request('GET', '/');
        $this->assertSelectorTextContains('p', '現在、運航情報はありません。');
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
