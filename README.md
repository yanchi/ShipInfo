# ShipInfo

[![CI](https://github.com/yanchi/ShipInfo/actions/workflows/ci.yml/badge.svg)](https://github.com/yanchi/ShipInfo/actions/workflows/ci.yml)

フェリー会社のウェブサイトをスクレイピングし、運航情報（欠航・遅延・通常）を収集・保存・通知するサービス。

**Python（スクレイパー）+ Symfony/PHP（Webアプリ）+ MySQL** の3層構成を Docker Compose で統合している。

---

## アーキテクチャ

```
[フェリー会社サイト]
       ↓ HTTP スクレイピング (BeautifulSoup)
[Python スクレイパー]
       ↓ INSERT … ON DUPLICATE KEY UPDATE
[MySQL 8.0]
       ↑ Doctrine ORM
[Symfony 7.2 Web アプリ]
       ↓ Twig テンプレート
[ブラウザ]

異常ステータス検出時 → SMTP メール通知
```

---

## Problem / Solution

### 課題

- フェリー会社ごとに公式サイトの構成が異なり、複数社の運航状況を横断して確認しづらい
- 欠航・遅延などの異常ステータスを見落としやすく、利用者が気づくまでに時間がかかる
- 公式サイトは「今この便はどうか」の確認には適しておらず、一覧性が低い

### 解決アプローチ

- 各社サイトをスクレイピングして運航情報を収集し、共通スキーマで MySQL に保存
- Symfony 側で統一された UI として提供し、複数社の情報を一画面で比較できる
- 異常ステータス検出時はメール通知を送れる構成にし、見落としを防ぐ

### このプロジェクトで意識したこと

単なる画面表示アプリではなく、**収集 → 保存 → 表示 → 通知** までを一貫して実装したバックエンド寄りのサービス。
実務を想定し、冪等性・設定管理・テスタビリティ・実 DB 統合テストといった設計上の品質を重視している。

---

## 技術スタック

| レイヤー | 技術 |
|---|---|
| スクレイピング | Python 3.12 / requests / BeautifulSoup4 |
| バックエンド | PHP 8.2 / Symfony 7.2 / Doctrine ORM |
| DB | MySQL 8.0 |
| インフラ | Docker / Docker Compose |
| テスト | PHPUnit 9 (統合テスト) / pytest 44件 |
| CI | GitHub Actions |

---

## 設計上のこだわり

### 1. upsert で冪等なデータ収集

スクレイパーが同一データを再実行しても重複しないよう、`INSERT … ON DUPLICATE KEY UPDATE` を使用。
DBレベルのユニーク制約 `(route_id, operation_date)` と組み合わせて一貫性を保証している。

```python
# python/src/db.py
cursor.execute("""
    INSERT INTO operations (route_id, operation_date, status, ...)
    VALUES (%s, %s, %s, ...)
    ON DUPLICATE KEY UPDATE status = VALUES(status), updated_at = VALUES(updated_at)
""", ...)
```

### 2. 異常ステータス検出時のメール通知

欠航・遅延などの非通常ステータスをスクレイプ時に検出し、SMTP でアラートメールを送信。
`SMTP_HOST` 未設定時は警告ログのみでクラッシュしない設計。

```python
# python/src/notifier.py
def send_alert(abnormal_entries: list[dict]) -> None:
    if not abnormal_entries:
        return
    # 環境変数未設定はスキップ（ログ出力）
    if not smtp_host or not notify_to:
        logging.warning("...")
        return
    ...
```

### 3. `ClockInterface` 注入によるテスタビリティ

「今日の運航情報」を返すコントローラーで、`new \DateTime('now')` を直接呼ばず PSR の `ClockInterface` を注入。
テストから任意の日付に差し替えられる。

```php
// ship_info/src/Controller/DetailsController.php
public function __construct(
    private readonly ClockInterface $clock,
    #[Autowire(param: 'app.company_urls')] private readonly array $companyUrls,
) {}

// テストでは MockClock を差し込む
$mockClock->method('now')->willReturn(new \DateTimeImmutable('2025-02-12'));
```

### 4. Symfony パラメータによる設定の一元管理

フェリー会社の公式サイト URL をコントローラーにハードコードせず、`services.yaml` の `parameters` に集約。
`#[Autowire(param: '...')]` で型安全に注入。

```yaml
# ship_info/config/services.yaml
parameters:
    app.company_urls:
        マリックスライン: 'https://marixline.com/'
        "A'LINE": 'https://www.aline-ferry.com/'
```

### 5. 実DBを使った統合テスト

モックDBを避け、テスト専用DB（`ship_info_test`）に対して実際にデータを投入・検証。
`WebTestCase` ベースの統合テストで、HTTPリクエストからレンダリング結果まで一気通貫でテストしている。

```php
// ship_info/tests/IntegrationTestCase.php
abstract class IntegrationTestCase extends WebTestCase
{
    protected function cleanupEntity(EntityManagerInterface $em, string $class, int $id): void
    protected function mockClock(string $date): void
}
```

---

## テスト

```bash
# PHP (統合テスト: 11件)
cd ship_info && php bin/phpunit

# Python (ユニットテスト: 44件)
cd python && python -m pytest tests/ -v
```

GitHub Actions で `push` / `pull_request` 時に自動実行される。MySQL サービスコンテナを CI 上で起動し、実DBに対してマイグレーションとテストを実行。

---

## ローカル起動

```bash
# 1. コンテナ起動
docker-compose up -d

# 2. マイグレーション
docker-compose exec symfony php bin/console doctrine:migrations:migrate --no-interaction

# 3. スクレイピング実行
docker-compose exec python python save_kametoku_info.py
```

| URL | 内容 |
|---|---|
| http://localhost:8080 | 各航路の最新運航ステータス |
| http://localhost:8080/details/today | 当日の便一覧（出発時刻順） |
| http://localhost:8080/contact | お問い合わせ |

### 環境変数 (`.env`)

```env
APP_ENV=dev
DATABASE_URL=mysql://user:password@db:3306/ship_info
MARIXLINE_SERVICE_URL=https://marixline.com/service/
# メール通知（省略可）
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your@example.com
SMTP_PASSWORD=secret
NOTIFY_FROM=your@example.com
NOTIFY_TO=alert@example.com
```

---

## 今後の予定

- `Operation.status` の PHP enum 化（[#14](https://github.com/yanchi/ShipInfo/issues/14)）
- 対応フェリー会社の拡充
