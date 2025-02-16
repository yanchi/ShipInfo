<?php

namespace App\Controller;

use Psr\Clock\ClockInterface;
use App\Repository\CompanyRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class DetailsController extends AbstractController
{
    private ClockInterface $clock;

    public function __construct(ClockInterface $clock)
    {
        $this->clock = $clock;
    }

    #[Route('/details/today', name: 'app_details_today')]
    public function index(
        CompanyRepository $companyRepository
    ): Response {
        // 今日の日付を取得
        $today = $this->clock->now()->format('Y-m-d'); // 日付だけにフォーマット

        // フェリー会社と紐づく航路と運航情報を取得
        $companies = $companyRepository->createQueryBuilder('c')
            ->leftJoin('c.routes', 'r')
            ->leftJoin('r.operations', 'o', 'WITH', 'o.operationDate >= :today') // 条件を「本日以降」に変更
            ->setParameter('today', $today)
            ->addSelect('r')
            ->addSelect('o')
            ->getQuery()
            ->getResult();
            
        return $this->render('details/index.html.twig', [
            'companies' => $companies,
        ]);
    }
}
