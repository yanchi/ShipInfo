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
    }
}
