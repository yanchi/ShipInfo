# Data Model: Google アナリティクス追加

データベース変更なし。

## 設定値

| 設定名 | 管理場所 | 形式 | 説明 |
|--------|----------|------|------|
| `GOOGLE_ANALYTICS_ID` | `.env` / 環境変数 | `G-XXXXXXXXXX` | GA4 測定 ID。未設定（空）の場合はスクリプト非出力 |

## 変更ファイル

| ファイル | 変更内容 |
|----------|----------|
| `ship_info/.env` | `GOOGLE_ANALYTICS_ID=` を追記（空値） |
| `ship_info/config/packages/twig.yaml` | `globals.ga_measurement_id` を追加 |
| `ship_info/templates/base.html.twig` | `<head>` 内に GA4 スクリプトを条件付き追加 |
