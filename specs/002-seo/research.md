# Research: SEO 対策

## meta description の実装方式

**Decision**: Twig の `{% block meta_description %}` で per-page オーバーライド方式を採用

**Rationale**: `base.html.twig` にデフォルト値付きブロックを定義し、各ページテンプレートでオーバーライドする。Symfony/Twig 標準パターンで追加ライブラリ不要。

**Alternatives considered**: コントローラーから変数を渡す → 全コントローラー変更が必要で冗長

---

## canonical URL の生成方法

**Decision**: Twig の `app.request.schemeAndHttpHost ~ app.request.pathInfo` で動的生成

**Rationale**:
- 環境変数のハードコード不要（開発・本番で自動的に正しい値になる）
- Symfony の `app` Twig グローバル経由でリクエスト情報を取得できる
- Twig の自動エスケープが有効なためインジェクションリスクなし

**Alternatives considered**:
- 環境変数 `APP_BASE_URL` で固定 → デプロイ設定が増える
- `absolute_url()` Twig 関数 → `app.request` と同等だが可読性が低い

---

## OGP タグの実装方式

**Decision**: `{% block og_* %}` ブロック群を base.html.twig に定義し、per-page でオーバーライド

**Rationale**: meta description と同じパターンで統一。`og:url` は canonical と同じ動的生成値を使用。

**実装する OGP タグ**:
- `og:title` - ページタイトルと同値をデフォルトに
- `og:description` - meta description と同値をデフォルトに
- `og:url` - canonical URL と同値
- `og:type` - `website` 固定
- `og:site_name` - `フェリー運航情報サービス` 固定
- `og:image` - スコープ外（spec の Assumptions に明記済み）

---

## sitemap.xml の実装方式

**Decision**: `public/sitemap.xml` に静的ファイルとして設置

**Rationale**: 公開ページが 3 件固定（ホーム・運航詳細・お問い合わせは除外）のため、動的生成は不要。静的ファイルが最もシンプル（Constitution Principle IV）。

**Alternatives considered**: 専用コントローラーで動的生成 → ページ数が増えない限り過剰エンジニアリング

---

## robots.txt の実装方式

**Decision**: `public/robots.txt` に静的ファイルとして設置

**Rationale**: Symfony は `public/` 以下の静的ファイルを自動的に配信する。コントローラー不要。

**内容**:
```
User-agent: *
Allow: /
Disallow: /contact

Sitemap: https://ship.isl-mentor.com/sitemap.xml
```

お問い合わせページはダミーのため `Disallow` 設定。

---

## Twitter Card 対応

**Decision**: `twitter:card` タグを追加（`summary` 固定）

**Rationale**: X（旧 Twitter）は OGP を一部読むが `twitter:card` の明示が推奨。`summary` 型は画像なしでも機能する。
