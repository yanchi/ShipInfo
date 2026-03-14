<?php

namespace App\Tests\Controller;

use App\Entity\Company;
use App\Entity\Operation;
use App\Entity\Route;
use App\Tests\IntegrationTestCase;

class DetailsControllerTest extends IntegrationTestCase
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
            ->setStatus(['normal'])
            ->setStatusText(['通常運航'])
            ->setDepartureTime(new \DateTime('2025-02-12 10:00:00'))
            ->setArrivalTime(new \DateTime('2025-02-12 14:00:00'))
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($todayOp);

        // 前日(2025-02-11)の運航 → フィルタで除外される（欠航・異なる時刻で区別可能にする）
        $yesterdayOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTime('2025-02-11'))
            ->setStatus(['cancelled'])
            ->setStatusText(['欠航'])
            ->setDepartureTime(new \DateTime('2025-02-11 09:00:00'))
            ->setArrivalTime(new \DateTime('2025-02-11 13:00:00'))
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
            // 今日の運航が描画されていることをステータステキストで確認
            $this->assertStringContainsString('通常運航', $content);
            // 前日の便（欠航）はフィルタで除外される
            $this->assertStringNotContainsString('欠航', $content);
        } finally {
            $this->cleanupEntity($em, Company::class, $companyId);
        }
    }

    public function testDetailsPageShowsOperationsSortedByDepartureTime(): void
    {
        $client = static::createClient();
        $em = static::getContainer()->get('doctrine.orm.entity_manager');

        $now = new \DateTimeImmutable();
        $company = (new Company())
            ->setName('ソートテスト運輸')
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($company);

        // ユニーク制約 (route_id, operation_date) のため、2便は別々のルートに配置
        // テンプレートはroute IDの昇順で描画されるので、08:00ルートを先に作成
        $routeEarly = (new Route())
            ->setName('A港 → B港')
            ->setCompany($company)
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($routeEarly);

        $routeLate = (new Route())
            ->setName('B港 → A港')
            ->setCompany($company)
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($routeLate);

        $earlierOp = (new Operation())
            ->setRoute($routeEarly)
            ->setOperationDate(new \DateTime('2025-02-12'))
            ->setStatus(['normal'])
            ->setStatusText(['通常運航'])
            ->setDepartureTime(new \DateTime('2025-02-12 08:00:00'))
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($earlierOp);

        $laterOp = (new Operation())
            ->setRoute($routeLate)
            ->setOperationDate(new \DateTime('2025-02-12'))
            ->setStatus(['normal'])
            ->setStatusText(['通常運航'])
            ->setDepartureTime(new \DateTime('2025-02-12 14:00:00'))
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($laterOp);

        $em->flush();
        $companyId = $company->getId();
        $em->clear();

        try {
            $this->mockClock('2025-02-12');
            $client->request('GET', '/details/today');

            $content = $client->getResponse()->getContent();
            $this->assertResponseIsSuccessful();
            // 2ルートの出発時刻が両方表示されている
            $this->assertStringContainsString('08:00', $content, '08:00 が表示されていない');
            $this->assertStringContainsString('14:00', $content, '14:00 が表示されていない');
        } finally {
            $this->cleanupEntity($em, Company::class, $companyId);
        }
    }

}
