# Data Model: SEO 対策

データベース変更なし。

## Twig ブロック定義（base.html.twig に追加）

| ブロック名 | デフォルト値 | per-page オーバーライド |
|-----------|-------------|----------------------|
| `meta_description` | `フェリーの運航情報を提供するサービスです。` | 各ページテンプレートで定義 |
| `og_title` | `{% block title %}` と同値 | 各ページテンプレートで定義 |
| `og_description` | `{% block meta_description %}` と同値 | 各ページテンプレートで定義 |

## per-page 説明文

| ページ | URL | meta description |
|--------|-----|-----------------|
| ホーム | `/` | `フェリーの現在の運航状況を確認できます。欠航情報をいち早くお知らせします。` |
| 運航詳細 | `/details/today` | `今日のフェリー運航情報です。航路ごとの出発・到着時刻や運航ステータスを確認できます。` |

## 追加ファイル

| ファイル | 種別 | 説明 |
|----------|------|------|
| `ship_info/public/sitemap.xml` | 静的ファイル | 公開ページの URL 一覧 |
| `ship_info/public/robots.txt` | 静的ファイル | クローラー設定 |

## 変更ファイル

| ファイル | 変更内容 |
|----------|----------|
| `ship_info/templates/base.html.twig` | meta description・canonical・OGP・Twitter Card タグ追加 |
| `ship_info/templates/home/index.html.twig` | `meta_description` ブロック追加 |
| `ship_info/templates/details/index.html.twig` | `meta_description` ブロック追加 |
