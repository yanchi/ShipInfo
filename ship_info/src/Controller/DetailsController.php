<?php

namespace App\Controller;

use Psr\Clock\ClockInterface;
use App\Repository\CompanyRepository;
use App\Repository\OperationRepository;
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
        CompanyRepository $companyRepository,
        OperationRepository $operationRepository
    ): Response {
        $today = $this->clock->now()->format('Y-m-d');

        // 会社・航路を取得（operationsは別クエリで取得してlazy load問題を回避）
        $companies = $companyRepository->createQueryBuilder('c')
            ->leftJoin('c.routes', 'r')
            ->addSelect('r')
            ->getQuery()
            ->getResult();

        // 今日の運航情報を出発時刻昇順で取得（routeをJOINしてlazy load回避）
        $operations = $operationRepository->createQueryBuilder('o')
            ->join('o.route', 'r')
            ->addSelect('r')
            ->where('o.operationDate = :today')
            ->setParameter('today', $today)
            ->orderBy('o.departureTime', 'ASC')
            ->getQuery()
            ->getResult();

        // 航路IDをキーにグループ化（同一route+出発時刻(H:i)の重複を除去）
        // ※スクレイパーバグで同一時刻が異なる年(1900等)で登録されることへの対応
        $operationsByRoute = [];
        foreach ($operations as $operation) {
            $routeId = $operation->getRoute()->getId();
            $departureHi = $operation->getDepartureTime()?->format('H:i') ?? 'null';
            $dedupeKey = $routeId . '_' . $departureHi;
            $existing = $operationsByRoute[$routeId][$dedupeKey] ?? null;
            // 同H:i重複時は年が新しい（正しい）レコードを優先 ※年1900スクレイパーバグ対応
            $opTime = $operation->getDepartureTime();
            $exTime = $existing?->getDepartureTime();
            if ($existing === null || ($opTime !== null && ($exTime === null || $opTime > $exTime))) {
                $operationsByRoute[$routeId][$dedupeKey] = $operation;
            }
        }
        // テンプレート向けに値のみの配列に変換
        $operationsByRoute = array_map('array_values', $operationsByRoute);

        return $this->render('details/index.html.twig', [
            'companies' => $companies,
            'operationsByRoute' => $operationsByRoute,
        ]);
    }
}
