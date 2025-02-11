<?php

namespace App\Tests;

use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;

class HomeControllerTest extends WebTestCase
{
    public function testSomething(): void
    {
        $client = static::createClient();

        // '/' へのリクエストを送信
        $client->request('GET', '/');

        // レスポンスが200 OKか確認
        $this->assertResponseIsSuccessful();

        // ページタイトルが正しいか確認
        $this->assertSelectorTextContains('h1', 'フェリー運航情報サービス');

        // フェリー会社名が表示されているか確認
        $this->assertSelectorTextContains('h3', "A'LINE");
        //$this->assertSelectorTextContains('h3', "マリックスライン");
    }
}
