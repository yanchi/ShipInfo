<?php

namespace App\Service;

use App\Entity\Operation;

class OperationDeduplicator
{
    /**
     * 同一route + 出発時刻(H:i) の重複を除去し、航路IDをキーにしたOperation配列を返す。
     * 同一H:iが重複する場合、年が新しい（正しい）レコードを優先する。
     * ※スクレイパーバグで同一時刻が異なる年(1900等)で登録されることへの対応。
     *
     * @param Operation[] $operations
     * @return array<int, Operation[]>
     */
    public function groupByRoute(array $operations): array
    {
        $operationsByRoute = [];
        foreach ($operations as $operation) {
            $routeId = $operation->getRoute()->getId();
            // 出発時刻なしは航路あたり1件のみ想定（欠航・通常運航）。複数ある場合は後勝ち。
            $departureHi = $operation->getDepartureTime()?->format('H:i') ?? 'null';
            $dedupeKey = $routeId . '_' . $departureHi;
            $existing = $operationsByRoute[$routeId][$dedupeKey] ?? null;
            $opTime = $operation->getDepartureTime();
            $exTime = $existing?->getDepartureTime();
            if ($existing === null || ($opTime !== null && ($exTime === null || $opTime > $exTime))) {
                $operationsByRoute[$routeId][$dedupeKey] = $operation;
            }
        }
        return array_map('array_values', $operationsByRoute);
    }
}
