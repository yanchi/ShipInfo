# Research: 今日の運航情報ページ UX改善

**Branch**: `001-details-ux` | **Date**: 2026-03-08

## Decision 1: 日付フィルタの実装方法

**Decision**: Doctrine QueryBuilder で `o.operationDate = :today` を使い、文字列 `'Y-m-d'` フォーマットで比較する。

**Rationale**: `operationDate` は `DATE_MUTABLE`（DATE型）カラム。Doctrine は DATE 型カラムへの文字列パラメータを自動変換するため、`'Y-m-d'` 文字列での等値比較が最もシンプルかつ正確。`BETWEEN` は不要。

**Alternatives considered**:
- `operationDate >= today AND operationDate < tomorrow`: 冗長。DATE 型に DATETIME を混在させるリスクがある。
- PHP の `\DateTimeInterface` オブジェクトを直接渡す: Doctrine が型変換するが、文字列の方が明示的。

**Affected file**: `DetailsController.php` 行 30

---

## Decision 2: 出発時刻昇順ソートの実装場所

**Decision**: QueryBuilder に `->orderBy('o.departureTime', 'ASC')` を追加して DB 側でソートする。

**Rationale**: PHP/Twig 側で配列ソートするより、DB ソートの方が確実で将来のページネーション追加にも対応しやすい。`departureTime` が null の場合、MySQL は ASC で NULL を先頭に出す（`IS NULL` を先に処理）。spec は null の場合に行を非表示にするため、NULL 先頭表示は許容範囲内。

**Alternatives considered**:
- Twig の `sort` フィルタ: Twig 標準には datetime ソートがなく、カスタム Extension が必要で過剰。
- PHP 配列 `usort`: Controller に表示ロジックが混入して Principle IV 違反。

**Affected file**: `DetailsController.php` 行 28-34

---

## Decision 3: ステータスバッジの CSS アプローチ

**Decision**: 既存の `.status` クラスを踏襲しつつ、`operation.status` の値を CSS クラスとして使用する。表示テキストは `operation.statusText`（DB に保存済みの日本語テキスト）を使う。`suspend` 用クラスを新規追加する。

**Rationale**: Entity の `status` フィールド（例: `normal`, `delay`, `cancel`, `suspend`）が CSS クラス名と1:1 対応する設計が最もシンプル。`statusText` は DB に格納された日本語テキストをそのまま表示するため、ハードコードなし。

**CSS 追加**: `.status.suspend { background-color: #e2e3e5; color: #383d41; }` (グレー)

**Alternatives considered**:
- Twig でステータス値→日本語のマッピングを行う: DB の `status_text` フィールドが既にある以上、二重管理になる。
- 専用の Twig Extension でバッジ HTML 生成: Principle IV 違反（単一用途の抽象化）。

**Note (Deferred)**: 実際の `status` フィールドの値（`delay` vs `delayed` など）はリリース後に DB データを確認して CSS クラス名を調整する。現状の CSS には `.status.delayed`・`.status.cancelled` があるが、DB の実際の値次第では追記が必要。

**Affected file**: `styles.css` 行 79-92、`details/index.html.twig`

---

## Decision 4: テンプレートの表示構造

**Decision**: 方向（direction）は `<p class="route-direction">` で航路名直下に表示。運航日は常に今日のため表示不要。時刻・memo は Twig の `{% if %}` で条件付き表示。

**Rationale**: 既存の `.route-card`・`.operation-details` クラスを活用。新規クラスは最小限（`.route-direction`・`.status-badge` のみ）。

**Template structure**:
```
会社セクション（.company-section）
  会社名 <h3>
  航路カード（.route-card）
    航路名 <h4>
    方向 <p class="route-direction">  ← サブタイトル
    運航情報（.operation-card）×n（出発時刻昇順）
      ステータスバッジ <span class="status {status}">
      出発時刻（null なら非表示）
      到着時刻（null なら非表示）
      備考（空/null なら非表示）
```

**Affected file**: `details/index.html.twig`
