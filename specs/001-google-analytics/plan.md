# Implementation Plan: Google アナリティクス追加

**Branch**: `001-google-analytics` | **Date**: 2026-03-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-google-analytics/spec.md`

## Summary

全ページ共通の Twig ベーステンプレート（`base.html.twig`）に GA4 の gtag.js スクリプトを条件付きで埋め込む。測定 ID は `.env` 環境変数で管理し、`APP_ENV=prod` のときのみ有効化する。DB・コントローラー変更なし。

## Technical Context

**Language/Version**: PHP 8.x / Symfony (latest stable)
**Primary Dependencies**: Twig テンプレートエンジン（既存）
**Storage**: N/A（DB 変更なし）
**Testing**: PHPUnit（既存）
**Target Platform**: Web アプリケーション（Docker Compose / VPS）
**Project Type**: Web application
**Performance Goals**: スクリプト追加による表示速度への影響なし（`async` 属性付き）
**Constraints**: 既存ページへの機能・デザイン影響ゼロ
**Scale/Scope**: 3ファイル変更のみ（`.env`、`twig.yaml`、`base.html.twig`）

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Data Integrity | ✅ N/A | データ取り込みなし |
| II. Layered Architecture | ✅ Pass | Twig テンプレート変更のみ。Python / Symfony / DB レイヤー跨ぎなし |
| III. Security | ✅ Pass | 測定 ID を `.env` 管理。injection 経路なし（外部入力を HTML に渡さない） |
| IV. Simplicity | ✅ Pass | 3ファイル変更。新規抽象化レイヤーなし |
| V. Observability | ✅ N/A | スクレイピング・API エラーログへの影響なし |

**Complexity Tracking**: 違反なし。記載不要。

## Project Structure

### Documentation (this feature)

```text
specs/001-google-analytics/
├── plan.md              ← このファイル
├── research.md          ✅ Phase 0 完了
├── data-model.md        ✅ Phase 1 完了
├── quickstart.md        ✅ Phase 1 完了
└── tasks.md             ← /speckit.tasks で生成
```

### Source Code (変更対象)

```text
ship_info/
├── .env                          # GOOGLE_ANALYTICS_ID= を追記
├── config/packages/twig.yaml     # globals に ga_measurement_id を追加
└── templates/base.html.twig      # <head> 内に GA4 スクリプトを条件付き追加
```

## Implementation Design

### 1. `.env` への追記

```dotenv
GOOGLE_ANALYTICS_ID=
```

空値がデフォルト。本番では `.env.local` または環境変数で上書き。

### 2. `config/packages/twig.yaml` の変更

```yaml
twig:
    file_name_pattern: '*.twig'
    globals:
        ga_measurement_id: '%env(default::GOOGLE_ANALYTICS_ID)%'
```

`default::GOOGLE_ANALYTICS_ID` は未設定時に空文字列を返す Symfony の env var processor。

### 3. `templates/base.html.twig` の変更

`</head>` 直前に以下を追加:

```twig
{% if app.environment == 'prod' and ga_measurement_id %}
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={{ ga_measurement_id }}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', '{{ ga_measurement_id }}');
    </script>
{% endif %}
```

**セキュリティ**: `ga_measurement_id` は `.env` 由来の内部設定値であり、ユーザー入力ではない。Twig の自動エスケープは維持。

## Testing Plan

| テスト | 方法 | 合格条件 |
|--------|------|----------|
| dev 環境で GA スクリプト非出力 | PHPUnit でページ HTML を検証 | `gtag` 文字列が含まれない |
| prod 環境 + ID 設定済みで GA スクリプト出力 | PHPUnit でページ HTML を検証 | `G-TESTID` が含まれる |
| prod 環境 + ID 未設定でスクリプト非出力 | PHPUnit でページ HTML を検証 | `gtag` 文字列が含まれない |
| 既存ページの表示崩れなし | 手動確認 | ページレイアウト・機能に変化なし |
