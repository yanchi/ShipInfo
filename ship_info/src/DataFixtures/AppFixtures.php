<?php
// src/DataFixtures/AppFixtures.php
namespace App\DataFixtures;

use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;
use Doctrine\Common\DataFixtures\DependentFixtureInterface;

class AppFixtures extends Fixture implements DependentFixtureInterface
{
    public function load(ObjectManager $manager): void
    {
        // このクラス自体でデータを作成しない場合、空のloadメソッドでOK
    }

    public function getDependencies(): array
    {
        $dependencies = [
            \App\DataFixtures\Master\MasterFixtures::class, // マスターデータ
        ];

        // if ($_ENV['APP_ENV'] === 'test' || $_ENV['APP_ENV'] === 'dev') {
        //     $dependencies[] = \App\DataFixtures\Test\TestFixtures::class; // テストデータ
        // }

        return $dependencies;
    }
}
