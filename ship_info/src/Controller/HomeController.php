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
            $ops = $operationRepository->findLatestByRouteIds($routeIds);
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
                $statusClasses = $operation?->getStatus() ?? [];
                $statusTexts = $operation?->getStatusText() ?: ['通常運航'];
                $statuses = [];
                foreach ($statusTexts as $i => $text) {
                    $statuses[] = ['class' => $statusClasses[$i] ?? '', 'text' => $text];
                }
                $routeData[] = [
                    'name' => $route->getName(),
                    'statuses' => $statuses,
                ];
            }
            $urls = [
                'マリックスライン' => 'https://marixline.com/',
                "A'LINE" => 'https://www.aline-ferry.com/',
            ];
            $shipData[] = [
                'name' => $company->getName(),
                'url' => $urls[$company->getName()] ?? null,
                'routes' => $routeData,
            ];
        }

        return $this->render('home/index.html.twig', [
            'ship_data' => $shipData,
        ]);
    }
}
