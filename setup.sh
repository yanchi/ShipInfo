#!/bin/bash
# 初回セットアップ用スクリプト（一度だけ実行）
set -e

COMPOSE="docker compose -f /home/rocky/ShipInfo/docker-compose.prod.yml"

echo "=== マスターデータ投入 ==="
$COMPOSE exec -T db mysql -u user -p"${MYSQL_PASSWORD}" --default-character-set=utf8mb4 ship_info <<'SQL'
SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE routes;
TRUNCATE TABLE companies;
SET FOREIGN_KEY_CHECKS=1;
INSERT INTO companies (name, created_at, updated_at) VALUES ('マリックスライン', NOW(), NOW()), ('A\'LINE', NOW(), NOW());
INSERT INTO routes (name, company_id, direction, created_at, updated_at) VALUES
  ('徳之島 ⇔ 鹿児島', 1, '上り', NOW(), NOW()),
  ('徳之島 ⇔ 鹿児島', 2, '上り', NOW(), NOW()),
  ('徳之島 ⇔ 那覇', 1, '下り', NOW(), NOW()),
  ('徳之島 ⇔ 那覇', 2, '下り', NOW(), NOW());
SQL

echo "=== cron設定 ==="
(crontab -l 2>/dev/null | grep -v "save_kametoku_info\|aline_search"; cat /home/rocky/ShipInfo/crontab.txt) | crontab -

echo "=== 完了 ==="
