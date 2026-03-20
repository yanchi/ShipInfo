# Research: Google アナリティクス追加

## GA4 gtag.js スクリプト形式

**Decision**: Google 公式の gtag.js スニペットをそのまま使用する

**Rationale**: GA4 の標準トラッキングはページビューを自動送信する。カスタムイベントは不要。

**Snippet** (測定 ID = `G-XXXXXXXXXX` の場合):
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**Alternatives considered**: Google Tag Manager 経由での導入 → 今回は不要な複雑さを持ち込むため不採用（Constitution Principle IV）

---

## Symfony での環境変数 → Twig グローバル変数

**Decision**: `config/packages/twig.yaml` の `globals` に `%env(default::GOOGLE_ANALYTICS_ID)%` を登録する

**Rationale**:
- Symfony の `%env(default:fallback:VAR)%` 構文で、未設定時は空文字列にフォールバックできる
- Twig テンプレートからコントローラーを経由せず参照できる（全ページ共通）
- `.env` に `GOOGLE_ANALYTICS_ID=` と記載しておけば、本番では `.env.local` や環境変数で上書き可能

**Twig 設定例**:
```yaml
twig:
  globals:
    ga_measurement_id: '%env(default::GOOGLE_ANALYTICS_ID)%'
```

**Alternatives considered**:
- コントローラーで `$this->render()` に毎回渡す → 全コントローラーへの変更が必要で冗長
- Symfony Parameter として `services.yaml` に書く → env var のフォールバック処理が複雑になる

---

## Twig での環境判定

**Decision**: `app.environment` を使用して本番環境のみ有効化する

**Rationale**: Symfony の Twig グローバル変数 `app` には `environment` プロパティが含まれており、`APP_ENV` の値を反映する。追加の設定不要。

**実装例**:
```twig
{% if app.environment == 'prod' and ga_measurement_id %}
  <!-- GA4 script here -->
{% endif %}
```

**Alternatives considered**: PHP 側でフラグを渡す → Twig 側で完結できるため不要
