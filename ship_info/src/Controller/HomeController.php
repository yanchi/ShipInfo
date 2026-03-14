<?php

namespace App\Controller;

use App\Repository\CompanyRepository;
use App\Repository\OperationRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class HomeController extends AbstractController
{
    #[Route('/', name: 'app_home')]
    public function index(
        CompanyRepository $companyRepository,
        OperationRepository $operationRepository
    ): Response {
        // 会社と航路を1クエリで取得
        $companies = $companyRepository->createQueryBuilder('c')
            ->leftJoin('c.routes', 'r')
            ->addSelect('r')
            ->orderBy('c.id', 'ASC')
            ->getQuery()
            ->getResult();

        // 全航路IDを収集して、最新運航情報を1クエリで取得
        $routeIds = [];
        foreach ($companies as $company) {
            foreach ($company->getRoutes() as $route) {
                $routeIds[] = $route->getId();
            }
        }

        $latestByRoute = [];
        if ($routeIds) {
            // 各航路の最新operationDateのみをDB側で取得（サブクエリでバインド不要）
            $subQb = $operationRepository->createQueryBuilder('o2')
                ->select('MAX(o2.operationDate)')
                ->where('o2.route = o.route');

            $ops = $operationRepository->createQueryBuilder('o')
                ->join('o.route', 'r')
                ->addSelect('r')
                ->where('o.route IN (:ids)')
                ->setParameter('ids', $routeIds)
                ->andWhere('o.operationDate = (' . $subQb->getDQL() . ')')
                ->orderBy('o.id', 'DESC') // 同一route+dateの重複はIDが新しい方を優先
                ->getQuery()
                ->getResult();

            foreach ($ops as $op) {
                $rid = $op->getRoute()->getId();
                if (!isset($latestByRoute[$rid])) {
                    $latestByRoute[$rid] = $op;
                }
            }
        }

        // テンプレート用データ構造を組み立て
        $shipData = [];
        foreach ($companies as $company) {
            $routeData = [];
            foreach ($company->getRoutes() as $route) {
                $operation = $latestByRoute[$route->getId()] ?? null;
                $routeData[] = [
                    'name' => $route->getName(),
                    'status' => ($operation?->getStatus()) ?: 'normal',
                    'status_text' => ($operation?->getStatusText()) ?: '通常運航',
                ];
            }
            $shipData[] = [
                'name' => $company->getName(),
                'routes' => $routeData,
            ];
        }

        return $this->render('home/index.html.twig', [
            'ship_data' => $shipData,
        ]);
    }
}
