<?php

namespace App\DataFixtures;

use App\Entity\Company;
use App\Entity\Route;
use App\Entity\Operation;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class AppFixtures extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        // フェリー会社データ
        $company1 = new Company();
        $company1->setName("A'LINE");
        $company1->setCreatedAt(new \DateTimeImmutable());
        $company1->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($company1);

        $company2 = new Company();
        $company2->setName("マリックスライン");
        $company2->setCreatedAt(new \DateTimeImmutable());
        $company2->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($company2);

        // 航路データ
        $route1 = new Route();
        $route1->setName("徳之島 ⇔ 鹿児島");
        $route1->setCompany($company1);
        $route1->setCreatedAt(new \DateTimeImmutable());
        $route1->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($route1);

        $route2 = new Route();
        $route2->setName("徳之島 ⇔ 那覇");
        $route2->setCompany($company2);
        $route2->setCreatedAt(new \DateTimeImmutable());
        $route2->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($route2);

        // 運航情報データ
        $operation1 = new Operation();
        $operation1->setRoute($route1);
        $operation1->setOperationDate(new \DateTime("2025-02-10"));
        $operation1->setDirection("上り");
        $operation1->setStatus("通常運航");
        $operation1->setArrivalTime(new \DateTime("2025-02-10 14:00:00"));
        $operation1->setDepartureTime(new \DateTime("2025-02-10 10:00:00"));
        $operation1->setMemo("天候良好");
        $operation1->setCreatedAt(new \DateTimeImmutable());
        $operation1->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($operation1);

        $operation2 = new Operation();
        $operation2->setRoute($route2);
        $operation2->setOperationDate(new \DateTime("2025-02-10"));
        $operation2->setDirection("下り");
        $operation2->setStatus("欠航");
        $operation2->setMemo("台風のため欠航");
        $operation2->setCreatedAt(new \DateTimeImmutable());
        $operation2->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($operation2);

        // データを保存
        $manager->flush();
    }
}
