<?php

namespace App\Tests;

use Doctrine\ORM\EntityManagerInterface;
use Psr\Clock\ClockInterface;
use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;

abstract class IntegrationTestCase extends WebTestCase
{
    protected function cleanupEntity(EntityManagerInterface $em, string $class, int $id): void
    {
        $em->clear();
        $entity = $em->find($class, $id);
        if ($entity) {
            $em->remove($entity);
            $em->flush();
        }
    }

    protected function mockClock(string $date): void
    {
        $mockClock = $this->createMock(ClockInterface::class);
        $mockClock->method('now')->willReturn(new \DateTimeImmutable($date));
        self::getContainer()->set(ClockInterface::class, $mockClock);
    }
}
