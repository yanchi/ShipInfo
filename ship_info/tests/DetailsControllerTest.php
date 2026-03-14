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
            $em->clear();
            $company = $em->find(Company::class, $companyId);
            if ($company) {
                $em->remove($company);
                $em->flush();
            }
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

        $route = (new Route())
            ->setName('A港 ⇔ B港')
            ->setCompany($company)
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($route);

        // 遅い便を先にInsertして、ソートが挿入順に依存しないことを確認
        $laterOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTime('2025-02-12'))
            ->setStatus(['normal'])
            ->setStatusText(['通常運航'])
            ->setDepartureTime(new \DateTime('2025-02-12 14:00:00'))
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($laterOp);

        $earlierOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTime('2025-02-12'))
            ->setStatus(['normal'])
            ->setStatusText(['通常運航'])
            ->setDepartureTime(new \DateTime('2025-02-12 08:00:00'))
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($earlierOp);

        $em->flush();
        $companyId = $company->getId();
        $em->clear();

        try {
            $this->mockClock('2025-02-12');
            $client->request('GET', '/details/today');

            $content = $client->getResponse()->getContent();
            $this->assertResponseIsSuccessful();
            // 08:00 が 14:00 より前に出現する
            $this->assertLessThan(
                strpos($content, '14:00'),
                strpos($content, '08:00'),
                '出発時刻が昇順で表示されていない'
            );
        } finally {
            $em->clear();
            $company = $em->find(Company::class, $companyId);
            if ($company) {
                $em->remove($company);
                $em->flush();
            }
        }
    }

    public function testDetailsPageDeduplicatesSameHourMinuteWithDifferentYear(): void
    {
        $client = static::createClient();
        $em = static::getContainer()->get('doctrine.orm.entity_manager');

        $now = new \DateTimeImmutable();
        $company = (new Company())
            ->setName('重複テスト運輸')
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($company);

        $route = (new Route())
            ->setName('X港 ⇔ Y港')
            ->setCompany($company)
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($route);

        // 正しい年のレコード
        $correctOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTime('2025-02-12'))
            ->setStatus(['normal'])
            ->setStatusText(['通常運航'])
            ->setDepartureTime(new \DateTime('2025-02-12 10:00:00'))
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($correctOp);

        // スクレイパーバグで年が1900になったレコード（同H:i重複）
        $buggedOp = (new Operation())
            ->setRoute($route)
            ->setOperationDate(new \DateTime('2025-02-12'))
            ->setStatus(['normal'])
            ->setStatusText(['通常運航'])
            ->setDepartureTime(new \DateTime('1900-02-12 10:00:00'))
            ->setCreatedAt($now)
            ->setUpdatedAt($now);
        $em->persist($buggedOp);

        $em->flush();
        $companyId = $company->getId();
        $em->clear();

        try {
            $this->mockClock('2025-02-12');
            $client->request('GET', '/details/today');

            $content = $client->getResponse()->getContent();
            $this->assertResponseIsSuccessful();
            // 同一H:iの重複が1件に集約されているため、"10:00" の出現は1回のみ
            $this->assertSame(1, substr_count($content, '10:00'), '同一H:iの重複が除去されていない');
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
