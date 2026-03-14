# Tasks: 今日の運航情報ページ UX改善

**Input**: Design documents from `/specs/001-details-ux/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅

**Tests**: 本フィーチャーで新規の自動テストは追加しないが、既存の PHPUnit テスト（DetailsControllerTest / HomeControllerTest）の更新は含む（spec.md に明示なし）。各フェーズの Checkpoint で手動検証を行う。

**Organization**: タスクはユーザーストーリー単位でグループ化し、独立した実装・検証を可能にする。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 他のタスクと並行実行可能（別ファイル・依存なし）
- **[Story]**: 対応ユーザーストーリー（US1〜US4）
- 各タスクに実際のファイルパスを明記

---

## Phase 1: Setup（スキップ）

新規ファイル・ディレクトリの作成は不要。既存の3ファイルを変更するだけなので、特別なセットアップは不要。Phase 2 から開始する。

---

## Phase 2: Foundational（CSS 基盤整備）

**Purpose**: US1・US4 で必要なCSSクラスを整備し、既存の重複定義を解消する。全ユーザーストーリーの前提となる。

**⚠️ CRITICAL**: この Phase が完了するまでユーザーストーリーの実装を始めない。

- [x] T001 `ship_info/public/css/styles.css` の重複 `.status` ブロック（73-92行目と127-141行目）を統合し、`.status.normal`（緑: `#d4edda`/`#155724`）・`.status.delayed`（黄: `#fff3cd`/`#856404`）・`.status.cancelled`（赤: `#f8d7da`/`#721c24`）・`.status.suspend`（グレー: `#e2e3e5`/`#383d41`）の4クラスをバッジ形式（`font-weight: bold; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.85em;`）で1箇所にまとめる。また `.route-direction` クラス（`font-size: 0.85em; color: #666; margin: 0 0 0.5rem 0;`）を `.route-title` の直後に追加する

**Checkpoint**: ブラウザの DevTools で `.status.normal`・`.status.suspend` クラスをテスト要素に付与し、緑・グレーのバッジが表示されることを確認

---

## Phase 3: User Story 1 - ステータスを一目で確認する（Priority: P1）🎯 MVP

**Goal**: 各便のステータスが色付きバッジで表示され、欠航・遅延を即座に視認できる

**Independent Test**: `operation.status = 'cancelled'` のデータが存在する状態でページを表示し、赤いバッジで欠航が表示されることを確認する

### Implementation for User Story 1

- [x] T002 [US1] `ship_info/templates/details/index.html.twig` の `<p>状況: {{ operation.getStatusText() }}</p>` を `<span class="status {{ operation.status }}">{{ operation.getStatusText() }}</span>` に置き換え、p タグではなく span でバッジ表示にする（operation.status が CSS クラス名に対応）
- [x] T003 [US1] `ship_info/templates/details/index.html.twig` の `<h4 class="route-title">航路: {{ route.name }}</h4>` から「航路:」プレフィックスを削除し `{{ route.name }}` のみにする。直後に `{% if route.direction %}<p class="route-direction">{{ route.direction }}</p>{% endif %}` を追加して方向をサブタイトル表示にする
- [x] T004 [US1] `ship_info/templates/details/index.html.twig` の `<p>運航日: {{ operation.operationDate|date('Y-m-d') }}</p>` 行を削除する（常に今日の情報のため不要）。`<h3 class="company-title">フェリー会社: {{ company.name }}</h3>` から「フェリー会社:」プレフィックスを削除して `{{ company.name }}` のみにする
- [x] T005 [US1] `ship_info/templates/details/index.html.twig` の `<p>備考: {{ operation.memo }}</p>` を `{% if operation.memo %}<p class="operation-memo">備考: {{ operation.memo }}</p>{% endif %}` に変更して、memo が null または空文字の場合に非表示にする

**Checkpoint**: ページを表示して (1) ステータスが色付きバッジになっている (2) 方向が航路名サブタイトルで表示されている (3) 運航日ラベルが消えている (4) memo が空の便に備考欄が出ないことを確認

---

## Phase 4: User Story 2 - 出発時刻順に便を確認する（Priority: P2）

**Goal**: 同一航路の運航情報が出発時刻の早い順に並ぶ。出発・到着時刻が null の場合は該当行を非表示にする

**Independent Test**: 同一航路に複数便がある状態でページを表示し、上から出発時刻が昇順に並んでいることを確認する

### Implementation for User Story 2

- [x] T006 [US2] `ship_info/src/Controller/DetailsController.php` の QueryBuilder（28〜35行目）に `->addOrderBy('o.departureTime', 'ASC')` を追加して、運航情報を出発時刻昇順で取得する
- [x] T007 [US2] `ship_info/templates/details/index.html.twig` の `<p>出発時刻: {{ operation.departureTime|date('H:i') }}</p>` を `{% if operation.departureTime %}<p>出発 {{ operation.departureTime|date('H:i') }}</p>{% endif %}` に変更する。同様に `<p>到着時刻: {{ operation.arrivalTime|date('H:i') }}</p>` を `{% if operation.arrivalTime %}<p>到着 {{ operation.arrivalTime|date('H:i') }}</p>{% endif %}` に変更する（ラベルも「出発時刻:」→「出発」とシンプルに）

**Checkpoint**: 同一航路に複数便があるデータでページを表示し、出発時刻昇順に並んでいることを確認。departureTime が null の便に時刻行が表示されないことを確認

---

## Phase 5: User Story 3 - 今日の情報だけを確認する（Priority: P2）

**Goal**: `/details/today` が文字通り今日の日付の運航情報のみ表示し、明日以降が混入しない

**Independent Test**: 今日と明日の operationDate を持つ Operation がそれぞれ存在する状態でページを表示し、今日分のみ表示されることを確認する

### Implementation for User Story 3

- [x] T008 [US3] `ship_info/src/Controller/DetailsController.php` の QueryBuilder 内 `->leftJoin('r.operations', 'o', 'WITH', 'o.operationDate >= :today')` を `->leftJoin('r.operations', 'o', 'WITH', 'o.operationDate = :today')` に変更して、今日の日付のみにフィルタする（`>=` を `=` に変更）

**Checkpoint**: 翌日の運航情報データが DB に存在する場合に、`/details/today` に翌日データが表示されないことを確認（today パラメータは `ClockInterface` から取得しており既存の実装を踏襲）

---

## Phase 6: User Story 4 - スマートフォンで快適に確認する（Priority: P3）

**Goal**: 画面幅 375px のスマートフォンで全情報が横スクロールなしに表示される

**Independent Test**: Chrome DevTools でデバイスを iPhone SE（375px）に設定し、ページを表示して横スクロールバーが出ないことを確認する

### Implementation for User Story 4

- [x] T009 [US4] `ship_info/public/css/styles.css` の `@media (max-width: 768px)` ブロックに `.route-cards-container { flex-direction: column; }` と `.operation-details { padding: 0; }` を追加する。既存の `@media (max-width: 480px)` ブロックの `.route-cards-container { padding: 10px; }` が 375px でも正しく機能することを確認し、必要なら `@media (max-width: 375px)` ブロックを追加して `.route-cards-container { padding: 8px; }` を設定する

**Checkpoint**: Chrome DevTools で iPhone SE（375px）を選択してページを表示し、横スクロールなしに全カードが表示されることを確認

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 全ユーザーストーリーを横断する最終調整

- [x] T010 [P] `ship_info/public/css/styles.css` の `<p>方向: {{ route.direction }}</p>` の記述がテンプレートに残っていないか確認し、残っていれば削除する（T003 で対応済みのはずだが確認）
- [x] T011 全受け入れシナリオの手動検証: spec.md の Acceptance Scenarios（US1〜US4）を順番に実施し、すべて PASS することを確認する

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: 依存なし。即開始可能
- **US1 (Phase 3)**: Phase 2 完了後に開始（CSS クラスが必要）
- **US2 (Phase 4)**: Phase 2 完了後に開始（Phase 3 と並行可能）
- **US3 (Phase 5)**: Phase 2 完了後に開始。T008 は T006 の後が望ましい（同一ファイル）
- **US4 (Phase 6)**: Phase 2 完了後に開始（Phase 3〜5 と並行可能）
- **Polish (Phase 7)**: 全フェーズ完了後

### User Story Dependencies

- **US1 (P1)**: Phase 2 完了後すぐ開始可能
- **US2 (P2)**: Phase 2 完了後すぐ開始可能（US1 と並行可能、別ファイル: Controller vs Template）
- **US3 (P2)**: T006 完了後に T008 を実施（同一 Controller ファイル）
- **US4 (P3)**: Phase 2 完了後すぐ開始可能（CSS のみ）

### Within Each User Story

- US1: T002 → T003 → T004 → T005（同一テンプレートファイルなので順次）
- US2: T006（Controller）→ T007（Template）の順
- US3: T006 完了後に T008（同一 Controller ファイル）
- US4: T009 単独

### Parallel Opportunities

- Phase 2 完了後、US1（Template）・US2/US3（Controller）・US4（CSS）はすべて別ファイルなので並行実行可能
- T010 と T011 は独立して実行可能

---

## Parallel Example: After Phase 2

```bash
# Phase 2 完了後、以下を並行実行可能（別ファイル）

# Developer A: Template (US1)
Task T002: status badge 表示（templates/details/index.html.twig）
Task T003: direction subtitle（templates/details/index.html.twig）
Task T004: ラベル削除（templates/details/index.html.twig）
Task T005: memo 条件表示（templates/details/index.html.twig）

# Developer B: Controller (US2 + US3)
Task T006: ORDER BY departureTime（DetailsController.php）
Task T008: operationDate = today フィルタ（DetailsController.php）

# Developer C: CSS (US4)
Task T009: モバイル 375px 対応（styles.css）
```

---

## Implementation Strategy

### MVP First（US1 のみ）

1. Phase 2: CSS 基盤整備（T001）
2. Phase 3: US1 実装（T002〜T005）
3. **STOP & VALIDATE**: ステータスバッジが正しく表示されることを確認
4. Phase 4〜7 は後続スプリントで追加

### Incremental Delivery

1. Phase 2 → Phase 3（US1: バッジ表示）→ 確認 → デプロイ
2. Phase 4（US2: ソート + 時刻 null 対応）→ 確認
3. Phase 5（US3: 今日フィルタ修正）→ 確認
4. Phase 6（US4: モバイル対応）→ 確認
5. Phase 7（ポリッシュ）→ 最終確認

---

## Notes

- `status` フィールドの実際の DB 値（`delay` vs `delayed` など）はリリース後に確認し CSS クラス名を調整する（Deferred: research.md Decision 3 参照）
- Twig の auto-escape は維持する（Constitution Principle III 遵守）
- ClockInterface を使った日付取得は既存実装を変更しない
- [P] タスクは別ファイルを操作するため並行実行可能
