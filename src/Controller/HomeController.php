<?php

namespace App\Controller;

use App\Repository\CompanyRepository;
use App\Repository\RouteRepository;
use App\Repository\OperationRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class HomeController extends AbstractController
{
    #[Route('/', name: 'app_home')]
    public function index(
        CompanyRepository $companyRepository,
        RouteRepository $routeRepository,
        OperationRepository $operationRepository
    ): Response {
        // フェリー会社ごとのデータ構造を構築
        $shipData = [];
        $companies = $companyRepository->findAll();

        foreach ($companies as $company) {
            
            $routes = $routeRepository->findBy(['company' => $company]);
            $routeData = [];

            foreach ($routes as $route) {
                $operation = $operationRepository->findOneBy(['route' => $route], ['operationDate' => 'ASC']);
                $routeData[] = [
                    'name' => $route->getName(),
                    'status' => $operation ? $operation->getStatus() : 'normal',
                    'status_text' => $operation ? $operation->getStatusText() : '通常運航',
                ];
            }

            $shipData[] = [
                'name' => $company->getName(),
                'routes' => $routeData,
            ];
        }

        // テンプレートにデータを渡す
        return $this->render('home/index.html.twig', [
            'ship_data' => $shipData,
        ]);
    }
}
