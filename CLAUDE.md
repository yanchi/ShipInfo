# ShipInfo - CLAUDE.md

## プロジェクト概要

フェリー運航情報を収集・管理・提供するサービス。

- **スクレイピング**: Python でフェリー会社のウェブサイトから運航情報を収集
- **バックエンド**: Symfony (PHP) による REST API・ウェブアプリケーション
- **データベース**: MySQL 8.0
- **インフラ**: Docker Compose

## プロジェクト構成

```
ShipInfo/
├── python/src/              # Pythonスクレイピングコード
│   ├── scraper.py           # スクレイピング共通処理
│   ├── aline_search.py      # A'LINEフェリー情報取得
│   ├── get_latest_status_urls.py  # 運航情報URL収集
│   ├── scrape_operation_details.py  # 運航詳細スクレイピング
│   └── save_kametoku_info.py  # スクレイピングデータをDBへ保存
├── ship_info/               # Symfonyアプリケーション
│   └── src/
│       ├── Controller/      # HomeController, DetailsController, ContactController
│       ├── Entity/          # Company, Operation, Route, RawScrapedData
│       └── Repository/
├── docker-compose.yml       # python / symfony / db (MySQL) の3サービス
├── Dockerfile.python
└── Dockerfile.symfony
```

## 開発環境

### Docker 起動

```bash
docker-compose up -d
```

- Python HTTP サーバー: http://localhost:8000
- Symfony アプリ: http://localhost:8080
- MySQL: localhost:3306

### 環境変数 (.env)

```
APP_ENV=dev
APP_SECRET=...
MYSQL_HOST=db
MYSQL_DATABASE=ship_info
MYSQL_USER=user
MYSQL_PASSWORD=password
DATABASE_URL=mysql://user:password@db:3306/ship_info
MARIXLINE_SERVICE_URL=https://marixline.com/service/
```

### Pythonスクリプト実行

```bash
cd python/src
python save_kametoku_info.py
```

## 技術スタック

- **Python 3.9+**: スクレイピング (BeautifulSoup / requests)
- **PHP / Symfony**: ウェブアプリケーション
- **MySQL 8.0**: データ永続化
- **Docker / Docker Compose**: ローカル開発環境
