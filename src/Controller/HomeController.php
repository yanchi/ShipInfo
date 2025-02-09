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
                        'up_status' => '通常運航',
                        'up_status_text' => 'On schedule',
                        'down_status' => '欠航',
                        'down_status_text' => 'Cancelled',
                        'up_departure_time' => '08:00',
                        'up_arrival_time' => '12:00',
                        'down_departure_time' => '14:00',
                        'down_arrival_time' => '18:00',
                    ],
                    [
                        'name' => '徳之島 ⇔ 那覇（下り）',
                        'up_status' => '通常運航',
                        'up_status_text' => 'On schedule',
                        'down_status' => '欠航',
                        'down_status_text' => 'Cancelled',
                        'up_departure_time' => '08:00',
                        'up_arrival_time' => '12:00',
                        'down_departure_time' => '14:00',
                        'down_arrival_time' => '18:00',
                    ],
                ],
            ],
            [
                'name' => 'マリックスライン',
                'routes' => [
                    [
                        'name' => '徳之島 ⇔ 鹿児島（上り）',
                        'up_status' => '遅延中',
                        'up_status_text' => 'Delayed',
                        'down_status' => '通常運航',
                        'down_status_text' => 'On schedule',
                        'up_departure_time' => '08:00',
                        'up_arrival_time' => '12:00',
                        'down_departure_time' => '14:00',
                        'down_arrival_time' => '18:00',
                    ],
                    [
                        'name' => '徳之島 ⇔ 那覇（下り）',
                        'up_status' => '通常運航',
                        'up_status_text' => 'On schedule',
                        'down_status' => '通常運航',
                        'down_status_text' => 'On schedule',
                        'up_departure_time' => '08:00',
                        'up_arrival_time' => '12:00',
                        'down_departure_time' => '14:00',
                        'down_arrival_time' => '18:00',
                    ],
                ],
            ],
        ];

        return $this->render('home/index.html.twig', [
            'ship_data' => $shipData,
        ]);
    }
}
