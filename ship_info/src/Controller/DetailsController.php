<?php

namespace App\Controller;

use Doctrine\DBAL\Types\Types;
use Psr\Clock\ClockInterface;
use App\Repository\CompanyRepository;
use App\Repository\OperationRepository;
use App\Service\OperationDeduplicator;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\DependencyInjection\Attribute\Autowire;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class DetailsController extends AbstractController
{
    public function __construct(
        private readonly ClockInterface $clock,
        private readonly OperationDeduplicator $deduplicator,
        #[Autowire(param: 'app.company_urls')] private readonly array $companyUrls,
    ) {}

    #[Route('/details/today', name: 'app_details_today')]
    public function index(
        CompanyRepository $companyRepository,
        OperationRepository $operationRepository
    ): Response {
        $today = \DateTimeImmutable::createFromInterface($this->clock->now())->setTime(0, 0, 0);

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
            ->setParameter('today', $today, Types::DATE_MUTABLE)
            ->orderBy('o.departureTime', 'ASC')
            ->getQuery()
            ->getResult();

        return $this->render('details/index.html.twig', [
            'companies' => $companies,
            'operationsByRoute' => $this->deduplicator->groupByRoute($operations),
            'companyUrls' => $this->companyUrls,
        ]);
    }
}
