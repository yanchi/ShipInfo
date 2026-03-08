# Data Model: 今日の運航情報ページ UX改善

**Branch**: `001-details-ux` | **Date**: 2026-03-08

## 変更概要

スキーマ変更なし。既存エンティティをそのまま使用する。

## 既存エンティティ（参照用）

### Operation（運航情報）

| フィールド | 型 | nullable | 説明 |
|-----------|-----|----------|------|
| id | int | no | 主キー |
| route | Route | no | 紐づく航路（FK） |
| operationDate | DATE | no | 運航日（今日フィルタ対象） |
| status | string(50) | yes | ステータスコード（CSS クラス名に使用） |
| status_text | string(50) | yes | ステータス表示テキスト（日本語、DB格納済み） |
| departureTime | DATETIME | yes | 出発時刻（null なら非表示。ソートキー） |
| arrivalTime | DATETIME | yes | 到着時刻（null なら非表示） |
| memo | TEXT | yes | 備考（空/null なら非表示） |
| createdAt | DATETIME | no | 作成日時 |
| updatedAt | DATETIME | no | 更新日時 |

**ユニーク制約**: `(route_id, operation_date)` — 1航路1日1レコード

### Route（航路）

| フィールド | 型 | nullable | 説明 |
|-----------|-----|----------|------|
| id | int | no | 主キー |
| name | string | no | 航路名（カード見出しに使用） |
| direction | string | yes | 方向（航路名サブタイトルに使用） |
| company | Company | no | 紐づく会社（FK） |

### Company（フェリー会社）

| フィールド | 型 | nullable | 説明 |
|-----------|-----|----------|------|
| id | int | no | 主キー |
| name | string | no | 会社名（セクション見出しに使用） |

## クエリ設計（DetailsController）

### 変更前

```
operationDate >= :today  (本日以降)
ソートなし
```

### 変更後

```
operationDate = :today   (本日のみ)
ORDER BY o.departureTime ASC  (出発時刻昇順)
```

### DQL イメージ

```
SELECT c, r, o
FROM Company c
LEFT JOIN c.routes r
LEFT JOIN r.operations o WITH o.operationDate = :today
ORDER BY o.departureTime ASC
```

**パラメータ**: `:today` = `$clock->now()->format('Y-m-d')` (既存の ClockInterface を使用)

## ステータス CSS クラス対応表（暫定）

| status 値 | CSS クラス | 表示色 | 備考 |
|-----------|-----------|--------|------|
| normal | .status.normal | 緑 | 既存 |
| delay または delayed | .status.delay / .delayed | 黄 | DB 実値確認後に調整 |
| cancel または cancelled | .status.cancel / .cancelled | 赤 | DB 実値確認後に調整 |
| suspend | .status.suspend | グレー | 新規追加 |
| null / 不明 | .status（クラスなし） | デフォルト | フォールバック |
