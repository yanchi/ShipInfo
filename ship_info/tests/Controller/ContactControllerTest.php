<?php

namespace App\Tests\Controller;

use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;

class ContactControllerTest extends WebTestCase
{
    public function testContactPageReturns200(): void
    {
        $client = static::createClient();
        $client->request('GET', '/contact');
        $this->assertResponseIsSuccessful();
    }

    public function testContactPageShowsContactInfo(): void
    {
        $client = static::createClient();
        $client->request('GET', '/contact');

        $content = $client->getResponse()->getContent();
        $this->assertStringContainsString('info@ferry-info.com', $content);
        $this->assertStringContainsString('123-456-7890', $content);
        $this->assertSelectorTextContains('h2', 'お問い合わせ');
    }
}
