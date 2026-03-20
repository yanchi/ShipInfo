# Tasks: SEO 対策

**Input**: Design documents from `/specs/002-seo/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅

**Tests**: spec.md でテスト追加の指定なし → テストタスクは含まない

**Organization**: 3つのユーザーストーリーを独立したフェーズで実装

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 対象ユーザーストーリー（US1, US2, US3）
- ファイルパスはリポジトリルートからの相対パス

---

## Phase 1: Setup

**Purpose**: 静的ファイルの設置（他フェーズに依存しない）

- [x] T001 [P] `ship_info/public/sitemap.xml` を新規作成する（ホーム・運航詳細の 2 URL を含む XML）
- [x] T002 [P] `ship_info/public/robots.txt` を新規作成する（`/contact` を Disallow、Sitemap URL を記載）

---

## Phase 2: Foundational（ブロッキング前提条件）

**Purpose**: 全ページ共通の SEO タグを base テンプレートに追加

**⚠️ CRITICAL**: このフェーズ完了後に各ページ固有のオーバーライドを追加できる

- [x] T003 `ship_info/templates/base.html.twig` の `<title>` 直後に以下を追加する：`{% block meta_description %}` デフォルト description・`<link rel="canonical">`・OGP タグ群（og:title, og:description, og:url, og:type, og:site_name）・Twitter Card タグ（`twitter:card`）

**Checkpoint**: 全ページのソースに meta description・canonical・OGP が出力される

---

## Phase 3: User Story 1 - 検索結果での適切な表示（Priority: P1）🎯 MVP

**Goal**: 各ページが固有の meta description と canonical URL を持つ

**Independent Test**: ホームと運航詳細ページのソースを確認し、それぞれ固有の `<meta name="description">` と `<link rel="canonical">` が含まれること

### Implementation for User Story 1

- [x] T004 [P] [US1] `ship_info/templates/home/index.html.twig` に `{% block meta_description %}` を追加し、ホームページ固有の説明文を設定する
- [x] T005 [P] [US1] `ship_info/templates/details/index.html.twig` に `{% block meta_description %}` を追加し、運航詳細ページ固有の説明文を設定する

**Checkpoint**: ホームと運航詳細でそれぞれ異なる meta description が出力される

---

## Phase 4: User Story 2 - SNS シェア時の適切な表示（Priority: P2）

**Goal**: OGP チェッカーで全ページの og:title・og:description・og:url が正しく取得される

**Independent Test**: OGP チェッカー（ogp.me）で各ページ URL を確認し、og:title・og:description・og:url が取得されること

### Implementation for User Story 2

- [x] T006 [US2] `ship_info/templates/base.html.twig` の OGP ブロックを確認し、`og:description` が `meta_description` ブロックの内容（striptags・trim フィルタ適用）を正しく参照していることをレビューする

> **Note**: T003 の実装に OGP タグが含まれるため、追加コード変更は不要。このタスクは動作確認と検証。

**Checkpoint**: US1・US2 ともに独立して動作確認できる

---

## Phase 5: User Story 3 - 検索エンジンへのページ登録促進（Priority: P3）

**Goal**: `/sitemap.xml` と `/robots.txt` が正しく配信される

**Independent Test**: `/sitemap.xml` にアクセスして 2 件の URL を含む XML が返ること、`/robots.txt` に Sitemap 行が含まれること

### Implementation for User Story 3

- [x] T007 [US3] `/sitemap.xml` と `/robots.txt` にアクセスし、それぞれ期待する内容が返ることを手動確認する（T001・T002 で作成済みのファイルの検証）

**Checkpoint**: 全ユーザーストーリーが独立して動作確認できる

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 最終確認

- [x] T008 [P] `specs/002-seo/quickstart.md` の手順に沿って本番環境での動作を最終確認する（OGP チェッカー・Google Search Console へのサイトマップ登録）

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし — T001・T002 は即並列開始可能
- **Foundational (Phase 2)**: Phase 1 と並列実行可能（異なるファイル）
- **US1 (Phase 3)**: Phase 2 完了後（T003 の base テンプレートに依存）
- **US2 (Phase 4)**: Phase 3 完了後（T003 実装の確認）
- **US3 (Phase 5)**: Phase 1 完了後（T001・T002 の検証）
- **Polish (Phase 6)**: 全フェーズ完了後

### Task Dependencies

```
T001 [P] ─────────────────────────────────── T007
T002 [P] ─────────────────────────────────── T007
T003 → T004 [P]
     → T005 [P]
     → T006
```

### Parallel Opportunities

- T001・T002・T003 は並列実行可能（異なるファイル）
- T004・T005 は T003 完了後に並列実行可能

---

## Implementation Strategy

### MVP First（User Story 1 のみ）

1. Phase 1: T001・T002（静的ファイル設置）と Phase 2: T003（base テンプレート）を並列実行
2. Phase 3: T004・T005（per-page description）
3. **STOP and VALIDATE**: 各ページの meta description・canonical を確認
4. デプロイ可能 → 以後 US2・US3 確認へ

### Incremental Delivery

1. T001 + T002 + T003 → 基盤完成（全ページに共通 SEO タグ）
2. T004 + T005 → per-page description 追加（US1 MVP）
3. T006 → OGP 動作確認（US2）
4. T007 → sitemap・robots 確認（US3）
5. T008 → 本番最終確認

---

## Notes

- [P] タスク = 異なるファイル、依存関係なし
- [Story] ラベルはユーザーストーリーとのトレーサビリティのため
- 変更ファイル: 3件（base.html.twig・home/index.html.twig・details/index.html.twig）
- 新規ファイル: 2件（sitemap.xml・robots.txt）
- コントローラー・DB・Python 側の変更は不要
