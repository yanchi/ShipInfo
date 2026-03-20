# Tasks: Google アナリティクス追加

**Input**: Design documents from `/specs/001-google-analytics/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅

**Tests**: spec.md でテスト追加の指定なし → テストタスクは含まない

**Organization**: 2つのユーザーストーリーを独立したフェーズで実装

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 対象ユーザーストーリー（US1, US2）
- ファイルパスはリポジトリルートからの相対パス

---

## Phase 1: Setup

**Purpose**: 環境変数の設定

- [x] T001 `GOOGLE_ANALYTICS_ID=` を `ship_info/.env` の末尾に追記する

---

## Phase 2: Foundational（ブロッキング前提条件）

**Purpose**: 全ページに GA 測定 ID を渡す Twig グローバル変数の設定

**⚠️ CRITICAL**: このフェーズ完了後にユーザーストーリーの実装を開始できる

- [x] T002 `ship_info/config/packages/twig.yaml` に `globals.ga_measurement_id: '%env(default::GOOGLE_ANALYTICS_ID)%'` を追加する

**Checkpoint**: Twig グローバル変数 `ga_measurement_id` が全テンプレートで参照可能になった

---

## Phase 3: User Story 1 - サイト訪問データの計測（Priority: P1）🎯 MVP

**Goal**: 本番環境の全ページで GA4 ページビューが計測される

**Independent Test**: 本番環境（APP_ENV=prod）でサイトを開き、ページソースに `gtag` スクリプトが含まれ、GA4 管理画面のリアルタイムレポートにアクセスが記録されることを確認する

### Implementation for User Story 1

- [x] T003 [US1] `ship_info/templates/base.html.twig` の `</head>` 直前に GA4 gtag.js の条件付きスクリプトブロックを追加する（条件: `app.environment == 'prod'` かつ `ga_measurement_id` が非空）

**Checkpoint**: APP_ENV=prod + 測定 ID 設定済みの環境で全ページに GA スクリプトが出力される

---

## Phase 4: User Story 2 - 開発環境での計測除外（Priority: P2）

**Goal**: dev 環境では GA スクリプトが出力されない

**Independent Test**: APP_ENV=dev の環境でページソースに `gtag` 文字列が含まれないことを確認する

### Implementation for User Story 2

- [x] T004 [US2] `ship_info/templates/base.html.twig` のスクリプトブロックの条件式 `app.environment == 'prod'` が正しく記述されていることをレビューし、dev 環境での非出力を手動確認する

> **Note**: T003 の実装に条件式が含まれるため、追加コード変更は不要。このタスクは動作確認と検証。

**Checkpoint**: US1・US2 ともに独立して動作確認できる

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 運用・保守性の確認

- [x] T005 [P] `ship_info/.env` のコメントに `GOOGLE_ANALYTICS_ID` の説明（形式: `G-XXXXXXXXXX`）を追記する
- [x] T006 [P] `specs/001-google-analytics/quickstart.md` の手順に沿って本番環境での動作を最終確認する

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし — 即開始可能
- **Foundational (Phase 2)**: Phase 1 完了後 — 全ユーザーストーリーをブロック
- **US1 (Phase 3)**: Phase 2 完了後に開始可能
- **US2 (Phase 4)**: Phase 3 完了後（T003 の実装に依存）
- **Polish (Phase 5)**: Phase 4 完了後

### Task Dependencies

```
T001 → T002 → T003 → T004 → T005 [P]
                           → T006 [P]
```

### Parallel Opportunities

- T005・T006 は並列実行可能（異なるファイル）
- それ以外は順次実行（ファイル依存あり）

---

## Implementation Strategy

### MVP First（User Story 1 のみ）

1. Phase 1: T001 — `.env` に環境変数追加
2. Phase 2: T002 — `twig.yaml` に Twig グローバル追加
3. Phase 3: T003 — `base.html.twig` に GA スクリプト追加
4. **STOP and VALIDATE**: 本番環境で GA 計測を確認
5. デプロイ可能 → 以後 US2 確認・Polish へ

### Incremental Delivery

1. T001 + T002 → 基盤完成
2. T003 → GA 計測 MVP リリース
3. T004 → dev 環境除外を確認
4. T005 + T006 → 運用ドキュメント整備

---

## Notes

- [P] タスク = 異なるファイル、依存関係なし
- [Story] ラベルはユーザーストーリーとのトレーサビリティのため
- 変更ファイルは 3 件のみ（`.env`、`twig.yaml`、`base.html.twig`）
- コントローラー・DB・Python 側の変更は不要
