<?php
// src/DataFixtures/Test/TestFixtures.php
namespace App\DataFixtures\Test;

use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;
use App\Entity\Route;
use App\Entity\Operation;

class TestFixtures extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        /*
        // Routeのname=徳之島 ⇔ 鹿児島でデータ検索し、CompanyとJOIN
        $routeRepository = $manager->getRepository(Route::class);
        $route = $routeRepository->createQueryBuilder('r')
            ->innerJoin('r.company', 'c')
            ->where('r.name = :routeName')
            ->andWhere('c.name = :companyName')
            ->setParameter('routeName', '徳之島 ⇔ 鹿児島')
            ->setParameter('companyName', 'マリックスライン')
            ->getQuery()
            ->getOneOrNullResult();
            
        // 運航情報データ
        $operation1 = new Operation();
        $operation1->setRoute($route);
        $operation1->setOperationDate(new \DateTime("2025-02-11"));
        $operation1->setStatus("normal");
        $operation1->setStatusText("通常運航");
        $operation1->setArrivalTime(new \DateTime("2025-02-10 14:00:00"));
        $operation1->setDepartureTime(new \DateTime("2025-02-10 10:00:00"));
        $operation1->setMemo("天候良好");
        $operation1->setCreatedAt(new \DateTimeImmutable());
        $operation1->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($operation1);

        // Routeのname=徳之島 ⇔ 那覇でデータ検索し、CompanyとJOIN
        $routeRepository = $manager->getRepository(Route::class);
        $route = $routeRepository->createQueryBuilder('r')
            ->innerJoin('r.company', 'c')
            ->where('r.name = :routeName')
            ->andWhere('c.name = :companyName')
            ->setParameter('routeName', '徳之島 ⇔ 那覇')
            ->setParameter('companyName', 'マリックスライン')
            ->getQuery()
            ->getOneOrNullResult();
            
        // 運航情報データ
        $operation2 = new Operation();
        $operation2->setRoute($route);
        $operation2->setOperationDate(new \DateTime("2025-02-11"));
        $operation2->setStatus("normal");
        $operation2->setStatusText("通常運航");
        $operation2->setArrivalTime(new \DateTime("2025-02-10 14:00:00"));
        $operation2->setDepartureTime(new \DateTime("2025-02-10 10:00:00"));
        $operation2->setMemo("天候良好");
        $operation2->setCreatedAt(new \DateTimeImmutable());
        $operation2->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($operation2);

        // データを保存
        $manager->flush();
        */
    }
}
