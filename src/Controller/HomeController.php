<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class HomeController extends AbstractController
{
    #[Route('/', name: 'app_home')]
    public function index(): Response
    {
        // 航路情報のリストを複数表示するデータを作成する
        $shipData = [
            [
                'name' => 'A\'LINE',
                'routes' => [
                    [
                        'name' => '徳之島 ⇔ 鹿児島（上り）',
                        'status_text' => '欠航',
                        'status' => 'cancelled',
                        'departure_time' => '08:00',
                        'arrival_time' => '12:00',
                    ],
                    [
                        'name' => '徳之島 ⇔ 那覇（下り）',
                        'status_text' => '通常運航',
                        'status' => 'normal',
                        'departure_time' => '08:00',
                        'arrival_time' => '12:00',
                    ],
                ],
            ],
            [
                'name' => 'マリックスライン',
                'routes' => [
                    [
                        'name' => '徳之島 ⇔ 鹿児島（上り）',
                        'status_text' => '遅延中',
                        'status' => 'delayed',
                        'departure_time' => '08:00',
                        'arrival_time' => '12:00',
                    ],
                    [
                        'name' => '徳之島 ⇔ 那覇（下り）',
                        'status_text' => '通常運航',
                        'status' => 'normal',
                        'departure_time' => '08:00',
                        'arrival_time' => '12:00',
                    ],
                ],
            ],
        ];

        return $this->render('home/index.html.twig', [
            'ship_data' => $shipData,
        ]);
    }
}
