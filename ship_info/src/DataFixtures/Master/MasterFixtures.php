<?php
// src/DataFixtures/Master/MasterFixtures.php
namespace App\DataFixtures\Master;

use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;
use App\Entity\Company;
use App\Entity\Route;

class MasterFixtures extends Fixture
{
    public function load(ObjectManager $manager): void
    {

        $company1 = new Company();
        $company1->setName("マリックスライン");
        $company1->setCreatedAt(new \DateTimeImmutable());
        $company1->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($company1);

        $company2 = new Company();
        $company2->setName("A'LINE");
        $company2->setCreatedAt(new \DateTimeImmutable());
        $company2->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($company2);


        $route1 = new Route();
        $route1->setName("徳之島 ⇔ 鹿児島");
        $route1->setCompany($company1);
        $route1->setDirection("上り");
        $route1->setCreatedAt(new \DateTimeImmutable());
        $route1->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($route1);

        $route2 = new Route();
        $route2->setName("徳之島 ⇔ 鹿児島");
        $route2->setCompany($company2);
        $route2->setDirection("下り");
        $route2->setCreatedAt(new \DateTimeImmutable());
        $route2->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($route2);

        $route3 = new Route();
        $route3->setName("徳之島 ⇔ 那覇");
        $route3->setCompany($company1);
        $route3->setDirection("下り");
        $route3->setCreatedAt(new \DateTimeImmutable());
        $route3->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($route3);

        $route4 = new Route();
        $route4->setName("徳之島 ⇔ 那覇");
        $route4->setCompany($company2);
        $route4->setDirection("下り");
        $route4->setCreatedAt(new \DateTimeImmutable());
        $route4->setUpdatedAt(new \DateTimeImmutable());
        $manager->persist($route4);

        $manager->flush();
    }
}
