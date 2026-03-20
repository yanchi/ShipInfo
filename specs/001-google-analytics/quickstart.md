# Quickstart: Google アナリティクス導入

## 前提

- GA4 プロパティが作成済みで、測定 ID（`G-XXXXXXXXXX` 形式）を取得済みであること

## 本番環境への設定手順

1. VPS の `.env.local`（または環境変数）に測定 ID を設定:
   ```
   GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
   ```

2. Symfony のキャッシュをクリア:
   ```bash
   docker-compose exec symfony php bin/console cache:clear --env=prod
   ```

3. ブラウザで本番サイトを開き、ページソースに gtag.js スクリプトが含まれていることを確認

4. GA4 管理画面の「リアルタイム」レポートでアクセスが記録されることを確認

## 開発環境での動作確認

- `APP_ENV=dev` の場合、GA スクリプトは出力されない（意図的な動作）
- `GOOGLE_ANALYTICS_ID` を未設定のままにしておけばスクリプトは出力されない

## テスト方法

```bash
docker-compose exec symfony php bin/phpunit
```
