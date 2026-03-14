#!/bin/bash
# デプロイスクリプト
set -e

COMPOSE="docker compose -f /home/rocky/ShipInfo/docker-compose.prod.yml"

echo "=== git pull ==="
git -C /home/rocky/ShipInfo pull

echo "=== ビルド＆再起動 ==="
$COMPOSE up -d --build

echo "=== マイグレーション ==="
$COMPOSE exec -T symfony php bin/console doctrine:migrations:migrate --no-interaction

echo "=== デプロイ完了 ==="
