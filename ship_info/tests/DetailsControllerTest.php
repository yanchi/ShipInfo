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
    }
}
