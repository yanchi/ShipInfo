<?php

namespace App\Repository;

use App\Entity\Operation;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Operation>
 */
class OperationRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Operation::class);
    }

    /**
     * 指定した航路IDの最新 operationDate を持つ Operation を返す。
     * (route_id, operation_date) に UNIQUE 制約があるため、1 航路あたり最大 1 件を返す。
     *
     * @param int[] $routeIds
     * @return Operation[]
     */
    public function findLatestByRouteIds(array $routeIds): array
    {
        if (empty($routeIds)) {
            return [];
        }

        $subQb = $this->createQueryBuilder('o2')
            ->select('MAX(o2.operationDate)')
            ->where('o2.route = o.route');

        return $this->createQueryBuilder('o')
            ->join('o.route', 'r')
            ->addSelect('r')
            ->where('o.route IN (:ids)')
            ->setParameter('ids', $routeIds)
            ->andWhere('o.operationDate = (' . $subQb->getDQL() . ')')
            ->orderBy('o.id', 'DESC')
            ->getQuery()
            ->getResult();
    }
}
