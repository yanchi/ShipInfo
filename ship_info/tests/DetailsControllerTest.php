<?php
namespace App\Tests\Controller;

use Psr\Clock\ClockInterface;
use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;

class DetailsControllerTest extends WebTestCase
{
    public function testOperationsTodayPage(): void
    {
        $client = static::createClient();

        // Clockのモックを作成
        $mockClock = $this->createMock(ClockInterface::class);
        $mockClock->method('now')->willReturn(new \DateTimeImmutable('2025-02-12'));

        // コンテナにモックをセット
        self::getContainer()->set(ClockInterface::class, $mockClock);

        // "/details/today" にリクエストを送信
        $crawler = $client->request('GET', '/details/today');

        // レスポンスが200 (OK) であることを確認
        $this->assertResponseIsSuccessful();

        // ページタイトルが「今日の運航情報」であることを確認
        $this->assertSelectorTextContains('h2', '今日の運航情報');

        // フェリー会社が表示されているか確認 (例: A'LINE)
        $this->assertSelectorExists('h3', 'フェリー会社: A\'LINE');

        // 航路が表示されているか確認 (例: 徳之島 ⇔ 鹿児島)
        $this->assertSelectorExists('h4', '航路: 徳之島 ⇔ 鹿児島');

        // 運航情報がテーブルに表示されているか確認
        $this->assertSelectorExists('.operations-table');
    }

    public function testNoOperationsMessage(): void
    {
        $client = static::createClient();

        // "/details/today" にリクエストを送信
        $crawler = $client->request('GET', '/details/today');

        // 運航情報がない場合のメッセージが表示されているか確認
        $this->assertSelectorTextContains('p.no-data', 'この航路には本日の運航情報がありません。');
    }
}
