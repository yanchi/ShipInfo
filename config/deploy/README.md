# VPS デプロイ手順

## 前提

- VPS に Docker / Docker Compose がインストール済み
- ドメイン `ship.isl-mentor.com` が VPS の IP に向いている
- OS: Rocky Linux（`dnf` を使用）

---

## 1. リポジトリを取得

```bash
git clone <repo_url> /home/rocky/ShipInfo
```

---

## 2. 環境変数を設定

```bash
cp /home/rocky/ShipInfo/.env.example /home/rocky/ShipInfo/.env
vi /home/rocky/ShipInfo/.env  # 各値を本番用に書き換える
```

---

## 3. Nginx + Certbot をインストール

```bash
sudo dnf install -y epel-release
sudo dnf install -y nginx certbot python3-certbot-nginx
```

---

## 4. Nginx の sites-enabled を有効化

Rocky Linux はデフォルトで `sites-available/sites-enabled` が存在しないため作成する。

```bash
sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
```

`/etc/nginx/nginx.conf` の `http {}` ブロック末尾に include を追加：

```bash
sudo sed -i '/^}/i\    include /etc/nginx/sites-enabled/*.conf;' /etc/nginx/nginx.conf
# 2箇所入った場合は http {} の外の行を削除する
grep -n "sites-enabled" /etc/nginx/nginx.conf
```

---

## 5. HTTP のみの Nginx 設定で起動（certbot 用）

```bash
sudo tee /etc/nginx/sites-available/shipinfo << 'EOF'
server {
    listen 80;
    server_name ship.isl-mentor.com;

    location / {
        proxy_pass         http://127.0.0.1:8080;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/shipinfo /etc/nginx/sites-enabled/shipinfo.conf
sudo nginx -t && sudo systemctl start nginx
```

---

## 6. コンテナを起動

```bash
docker compose -f /home/rocky/ShipInfo/docker-compose.prod.yml up -d
```

---

## 7. SSL 証明書を取得（初回のみ）

```bash
sudo certbot --nginx -d ship.isl-mentor.com
sudo systemctl reload nginx
```

certbot が `/etc/nginx/sites-available/shipinfo` を自動で HTTPS 対応に書き換える。

---

## 8. マイグレーションを適用

```bash
docker compose -f /home/rocky/ShipInfo/docker-compose.prod.yml exec -T symfony php bin/console doctrine:migrations:migrate --no-interaction
```

---

## 9. 初回セットアップを実行（初回のみ）

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
