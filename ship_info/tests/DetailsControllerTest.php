<?php

namespace App\Tests\Controller;

use App\Entity\Company;
use App\Entity\Operation;
use App\Entity\Route;
use Psr\Clock\ClockInterface;
use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;

class DetailsControllerTest extends WebTestCase
{
    public function testDetailsPageReturns200(): void
    {
        $client = static::createClient();
        $this->mockClock('2025-02-12');
        $client->request('GET', '/details/today');
        $this->assertResponseIsSuccessful();
    }

    public function testDetailsPageShowsTodayHeading(): void
    {
        $client = static::createClient();
        $this->mockClock('2025-02-12');
        $client->request('GET', '/details/today');
        $this->assertSelectorTextContains('h2', '今日の運航情報');
    }

    public function testDetailsPageShowsNoDataMessageWhenEmpty(): void
    {
        $client = static::createClient();
        $this->mockClock('2025-02-12');
        $client->request('GET', '/details/today');
        $this->assertSelectorTextContains('p', '本日の運航情報はありません。');
    }

    public function testDetailsPageFiltersOperationsByDate(): void
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

        // 本日(2025-02-12)の運航 → 表示される
        $todayOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTime('2025-02-12'))
            ->setStatus('normal')
            ->setStatusText('通常運航')
            ->setDepartureTime(new \DateTime('2025-02-12 10:00:00'))
            ->setArrivalTime(new \DateTime('2025-02-12 14:00:00'))
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($todayOp);

        // 前日(2025-02-11)の運航 → フィルタで除外される
        $yesterdayOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTime('2025-02-11'))
            ->setStatus('normal')
            ->setStatusText('通常運航')
            ->setDepartureTime(new \DateTime('2025-02-11 10:00:00'))
            ->setArrivalTime(new \DateTime('2025-02-11 14:00:00'))
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($yesterdayOp);
        $em->flush();
        $companyId = $company->getId();
        // identity mapをクリアしてDQLが正しくフィルタされた結果を返すようにする
        $em->clear();

        try {
            $this->mockClock('2025-02-12');
            $client->request('GET', '/details/today');

            $content = $client->getResponse()->getContent();
            $this->assertResponseIsSuccessful();
            $this->assertStringContainsString('2025-02-12', $content);
            $this->assertStringNotContainsString('2025-02-11', $content);
        } finally {
            $em->clear();
            $company = $em->find(Company::class, $companyId);
            if ($company) {
                $em->remove($company);
                $em->flush();
            }
        }
    }

    private function mockClock(string $date): void
    {
        $mockClock = $this->createMock(ClockInterface::class);
        $mockClock->method('now')->willReturn(new \DateTimeImmutable($date));
        self::getContainer()->set(ClockInterface::class, $mockClock);
    }
}
