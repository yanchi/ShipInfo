# Implementation Plan: SEO 対策

**Branch**: `002-seo` | **Date**: 2026-03-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-seo/spec.md`

## Summary

全ページ共通の `base.html.twig` に meta description・canonical URL・OGP・Twitter Card タグを追加し、各ページテンプレートで per-page 説明文をオーバーライドする。sitemap.xml と robots.txt は `public/` に静的ファイルとして設置する。

## Technical Context

**Language/Version**: PHP 8.x / Symfony (latest stable)
**Primary Dependencies**: Twig テンプレートエンジン（既存）
**Storage**: N/A（DB 変更なし）
**Testing**: PHPUnit（既存）
**Target Platform**: Web アプリケーション（Docker Compose / VPS）
**Project Type**: Web application
**Performance Goals**: N/A（静的 HTML 出力のみ）
**Constraints**: 既存ページへの機能・デザイン影響ゼロ
**Scale/Scope**: 5ファイル変更 + 静的ファイル 2 件追加

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Data Integrity | ✅ N/A | データ取り込みなし |
| II. Layered Architecture | ✅ Pass | Twig テンプレート + 静的ファイル変更のみ。レイヤー跨ぎなし |
| III. Security | ✅ Pass | canonical は `app.request` 由来、Twig 自動エスケープ有効。ユーザー入力を HTML に渡さない |
| IV. Simplicity | ✅ Pass | sitemap は静的ファイル。新規抽象化レイヤーなし |
| V. Observability | ✅ N/A | スクレイピング・API ログへの影響なし |

**Complexity Tracking**: 違反なし。記載不要。

## Project Structure

### Documentation (this feature)

```text
specs/002-seo/
├── plan.md              ← このファイル
├── research.md          ✅ Phase 0 完了
├── data-model.md        ✅ Phase 1 完了
├── quickstart.md        ✅ Phase 1 完了
└── tasks.md             ← /speckit.tasks で生成
```

### Source Code（変更対象）

```text
ship_info/
├── public/
│   ├── sitemap.xml                          # 新規：公開ページ URL 一覧
│   └── robots.txt                           # 新規：クローラー設定
└── templates/
    ├── base.html.twig                       # meta/canonical/OGP/Twitter Card 追加
    ├── home/index.html.twig                 # meta_description ブロック追加
    └── details/index.html.twig             # meta_description ブロック追加
```

## Implementation Design

### 1. `base.html.twig` の変更

`<head>` 内に以下を追加（`<title>` の直後）：

```twig
{# --- SEO --- #}
{% block meta_description %}
    <meta name="description" content="フェリーの運航情報を提供するサービスです。">
{% endblock %}

{% set canonical_url = app.request.schemeAndHttpHost ~ app.request.pathInfo %}
<link rel="canonical" href="{{ canonical_url }}">

{# --- OGP --- #}
<meta property="og:title" content="{% block og_title %}{{ block('title') }}{% endblock %}">
<meta property="og:description" content="{{ block('meta_description') | striptags | trim }}">
<meta property="og:url" content="{{ canonical_url }}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="フェリー運航情報サービス">

{# --- Twitter Card --- #}
<meta name="twitter:card" content="summary">
```

### 2. `home/index.html.twig` の変更

```twig
{% block meta_description %}
    <meta name="description" content="フェリーの現在の運航状況を確認できます。欠航情報をいち早くお知らせします。">
{% endblock %}
```

### 3. `details/index.html.twig` の変更

```twig
{% block meta_description %}
    <meta name="description" content="今日のフェリー運航情報です。航路ごとの出発・到着時刻や運航ステータスを確認できます。">
{% endblock %}
```

### 4. `public/sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://ship.isl-mentor.com/</loc>
        <changefreq>hourly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://ship.isl-mentor.com/details/today</loc>
        <changefreq>hourly</changefreq>
        <priority>0.9</priority>
    </url>
</urlset>
```

### 5. `public/robots.txt`

```
User-agent: *
Allow: /
Disallow: /contact

Sitemap: https://ship.isl-mentor.com/sitemap.xml
```

## Testing Plan

| テスト | 方法 | 合格条件 |
|--------|------|----------|
| meta description 出力確認 | ページソース確認 | 各ページ固有の description が含まれる |
| canonical URL 確認 | ページソース確認 | `https://ship.isl-mentor.com/...` 形式の URL が含まれる |
| OGP タグ確認 | OGP チェッカー | og:title・og:description・og:url が正しく取得される |
| sitemap.xml 確認 | `/sitemap.xml` にアクセス | 2 件の URL を含む XML が返される |
| robots.txt 確認 | `/robots.txt` にアクセス | Sitemap 行が含まれる |
