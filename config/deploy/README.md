# VPS デプロイ手順

## 前提

- VPS に Docker / Docker Compose がインストール済み
- Nginx がインストール済み
- Certbot がインストール済み
- ドメイン `ship.isl-mentor.com` が VPS の IP に向いている

---

## 1. リポジトリを取得

```bash
git clone <repo_url> /opt/shipinfo
cd /opt/shipinfo
```

---

## 2. 環境変数を設定

```bash
cp .env.example .env
vi .env  # 各値を本番用に書き換える
```

---

## 3. Nginx 設定を配置

```bash
sudo cp config/deploy/nginx.conf /etc/nginx/sites-available/shipinfo
sudo ln -sf /etc/nginx/sites-available/shipinfo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 4. SSL 証明書を取得（初回のみ）

```bash
sudo certbot --nginx -d ship.isl-mentor.com
```

---

## 5. コンテナを起動

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## 6. マイグレーションを適用

```bash
docker compose -f docker-compose.prod.yml exec symfony php bin/console doctrine:migrations:migrate --no-interaction
```

---

## 7. 初回セットアップを実行（初回のみ）

```bash
bash /home/rocky/ShipInfo/setup.sh
```

`setup.sh` がマスターデータ（companies / routes）の投入と cron の登録を一括実行する。

---

## 更新デプロイ手順

リポジトリルートの `deploy.sh` を実行する。

```bash
bash /home/rocky/ShipInfo/deploy.sh
```

`deploy.sh` が git pull → ビルド＆再起動 → マイグレーションを一括実行する。

---

## ポート構成

| サービス | ホスト側バインド | 備考 |
|---|---|---|
| symfony | 127.0.0.1:8080 | Nginx 経由でのみ外部公開 |
| python  | 0.0.0.0:8000   | 必要に応じてファイアウォールで制限 |
| db      | なし（内部のみ）| |
