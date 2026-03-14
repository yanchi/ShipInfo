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
     * 指定した航路IDごとに最新 operationDate かつ最大 ID を持つ Operation を 1 件ずつ返す。
     * 同一 route+date の重複がある場合は ID が最大のレコードを採用する。
     *
     * @param int[] $routeIds
     * @return Operation[]
     */
    public function findLatestByRouteIds(array $routeIds): array
    {
        if (empty($routeIds)) {
            return [];
        }

        // 最新 operationDate を取得する相関サブクエリ（o3 用）
        $maxDateSubQb = $this->createQueryBuilder('o2')
            ->select('MAX(o2.operationDate)')
            ->where('o2.route = o3.route');

        // route ごとの最新日付の中で最大 ID を取得する相関サブクエリ
        $maxIdSubQb = $this->createQueryBuilder('o3')
            ->select('MAX(o3.id)')
            ->where('o3.route = o.route')
            ->andWhere('o3.operationDate = (' . $maxDateSubQb->getDQL() . ')');

        return $this->createQueryBuilder('o')
            ->join('o.route', 'r')
            ->addSelect('r')
            ->where('o.route IN (:ids)')
            ->setParameter('ids', $routeIds)
            ->andWhere('o.id = (' . $maxIdSubQb->getDQL() . ')')
            ->getQuery()
            ->getResult();
    }
}
