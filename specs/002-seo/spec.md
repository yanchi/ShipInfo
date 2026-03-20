# Feature Specification: SEO 対策

**Feature Branch**: `002-seo`
**Created**: 2026-03-20
**Status**: Draft
**Input**: User description: "SEO対策入れれる？"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 検索結果での適切な表示（Priority: P1）

ユーザーが Google 等でフェリー運航情報を検索したとき、ShipInfo のページが適切なタイトルと説明文付きで検索結果に表示される。

**Why this priority**: 検索結果の見た目はクリック率に直結する最重要項目。meta description がないと Google が本文から勝手に切り取るため、意図しない説明文が表示される。

**Independent Test**: 各ページのソースを確認し、ページ固有の `<meta name="description">` と `<link rel="canonical">` が含まれることで独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** トップページを開く、**When** ページソースを確認する、**Then** サイト概要を説明する `<meta name="description">` が含まれている
2. **Given** 運航詳細ページを開く、**When** ページソースを確認する、**Then** そのページ固有の説明文が `<meta name="description">` に設定されている
3. **Given** 任意のページを開く、**When** ページソースを確認する、**Then** そのページの正規 URL を示す `<link rel="canonical">` が含まれている

---

### User Story 2 - SNS シェア時の適切な表示（Priority: P2）

ユーザーが LINE や X（Twitter）で ShipInfo のページを共有したとき、リンクプレビューにタイトル・説明・画像が表示される。

**Why this priority**: 日本では LINE での情報共有が多く、OGP 対応でリンクの信頼感・クリック率が上がる。

**Independent Test**: OGP チェッカー（ogp.me 等）でページ URL を確認し、タイトル・description・画像が正しく取得されることで独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** 任意のページを開く、**When** ページソースを確認する、**Then** OGP タグ（`og:title`、`og:description`、`og:url`、`og:type`）が含まれている
2. **Given** トップページを LINE でシェアする、**When** トーク画面でリンクを表示する、**Then** サービス名と説明文のプレビューが表示される

---

### User Story 3 - 検索エンジンへのページ登録促進（Priority: P3）

Google Search Console にサイトマップを登録することで、全ページが検索エンジンにインデックスされやすくなる。

**Why this priority**: sitemap.xml と robots.txt はインデックス促進の基本施策。小規模サイトでは影響は限定的だが、設置コストが低い。

**Independent Test**: `/sitemap.xml` にアクセスして全ページ URL が含まれる XML が返ること、`/robots.txt` にアクセスして適切な内容が返ることで独立してテスト可能。

**Acceptance Scenarios**:

1. **Given** サイトが公開されている、**When** `/sitemap.xml` にアクセスする、**Then** サイト内の全公開ページ URL を含む XML が返される
2. **Given** サイトが公開されている、**When** `/robots.txt` にアクセスする、**Then** クローラーへの許可設定と sitemap の URL が記載されたテキストが返される

---

### Edge Cases

- ページタイトルや説明文が未設定の場合、サイト共通のデフォルト値が使用されること
- canonical URL はプロトコル・ドメインを含む完全な URL（`https://ship.isl-mentor.com/...`）であること
- 開発環境の URL（`localhost`）が本番の OGP・canonical に混入しないこと

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 全ページに `<meta name="description">` を設定しなければならない。ページごとに固有の説明文を持ち、共通デフォルトにフォールバックできること
- **FR-002**: 全ページに `<link rel="canonical">` を設定しなければならない。値はそのページの正規 URL（https スキーム + 本番ドメイン）であること
- **FR-003**: 全ページに OGP タグ（`og:title`、`og:description`、`og:url`、`og:type`、`og:site_name`）を設定しなければならない
- **FR-004**: サイトは `/sitemap.xml` エンドポイントで全公開ページの URL 一覧を XML 形式で返さなければならない
- **FR-005**: サイトは `/robots.txt` エンドポイントでクローラー向け設定ファイルを返さなければならない。sitemap.xml の URL を含むこと
- **FR-006**: サイトのドメイン（`https://ship.isl-mentor.com`）は環境変数で管理し、コードにハードコードしてはならない

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 全ページの `<meta name="description">` が 50〜160 文字の範囲で設定されている（Google 推奨範囲）
- **SC-002**: Google Search Console でサイトマップを登録後、全ページがインデックス対象として認識される
- **SC-003**: OGP チェッカーで全ページの `og:title`・`og:description`・`og:url` が正しく取得できる（取得エラー 0 件）
- **SC-004**: `/sitemap.xml` が全公開ページ（ホーム・運航詳細・お問い合わせ）の URL を含む

## Assumptions

- 対象ページはホーム・運航詳細・お問い合わせの 3 ページ
- OGP 画像（`og:image`）はこの機能のスコープ外とする（別途デザインが必要なため）
- 本番ドメインは `https://ship.isl-mentor.com`
- 構造化データ（JSON-LD）はこの機能のスコープ外とする（効果測定後に検討）
