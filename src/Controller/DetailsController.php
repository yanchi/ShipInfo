<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

final class DetailsController extends AbstractController
{
    #[Route('/details', name: 'app_details')]
    public function index(): Response
    {
        // 航路詳細データ
        $routeDetails = [
            [
                'company' => 'A\'LINE',
                'route_name' => '徳之島 ⇔ 鹿児島',
                'up_status_text' => '通常運航',
                'down_status_text' => '欠航',
                'up_status' => 'normal',
                'down_status' => 'cancelled',
                'departure_time' => '08:00',
                'arrival_time' => '12:00',
            ],
            [
                'company' => 'マリックスライン',
                'route_name' => '徳之島 ⇔ 那覇',
                'up_status_text' => '遅延中',
                'down_status_text' => '通常運航',
                'up_status' => 'delayed',
                'down_status' => 'normal',
                'departure_time' => '09:00',
                'arrival_time' => '13:00',
            ],
        ];


        return $this->render('details/index.html.twig', [
            'route_details' => $routeDetails,
        ]);
    }
}
