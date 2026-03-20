# Quickstart: SEO 対策

## 動作確認手順

### 1. meta description・OGP の確認

ブラウザでページを開きソースを表示し、以下が含まれることを確認：

```html
<meta name="description" content="...">
<link rel="canonical" href="https://...">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:url" content="https://...">
```

### 2. sitemap.xml の確認

```
https://ship.isl-mentor.com/sitemap.xml
```

XML が返され、全公開ページ URL が含まれることを確認。

### 3. robots.txt の確認

```
https://ship.isl-mentor.com/robots.txt
```

`Sitemap:` の行が含まれることを確認。

### 4. OGP チェッカーでの確認

- [ogp.me](https://ogp.me) または Facebook Sharing Debugger でページ URL を入力
- `og:title`・`og:description`・`og:url` が正しく取得されることを確認

### 5. Google Search Console へのサイトマップ登録

1. Google Search Console で `https://ship.isl-mentor.com` プロパティを開く
2. サイドメニュー「サイトマップ」→ `sitemap.xml` を入力して送信
