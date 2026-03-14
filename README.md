# ShipInfo

ShipInfoは、フェリー運航情報を収集し、効率的に管理・提供するサービスです。このプロジェクトは、スクレイピングを用いて運航情報を取得し、それをデータベースに保存し、ウェブアプリケーションを通じてユーザーに提供します。

---

## 🚀 主な機能

- **運航情報の収集**: フェリー会社のウェブサイトから運航状況をスクレイピング。
- **データ管理**: MySQLデータベースを用いて運航データを管理。
- **データ提供**: REST APIやウェブアプリケーションを通じて運航情報を提供。

---

## 📦 プロジェクト構成

ShipInfo/
├── python/src/              # Pythonで実装されたスクレイピングおよびデータ保存コード
│   ├── scraper.py                     # スクレイピング共通処理
│   ├── db.py                          # DB接続・upsert_operation など共通クエリ
│   ├── notifier.py                    # 異常ステータス検出時のメール通知
│   ├── aline_search.py                # A'LINEフェリー情報取得
│   ├── get_latest_status_urls.py      # 運航情報取得用のURLを収集
│   ├── scrape_operation_details.py    # 運航情報のスクレイピング処理
│   └── save_kametoku_info.py          # スクレイピングしたデータをDBにupsert
├── ship_info/               # Symfonyによるウェブアプリケーション
│   ├── src/                 # アプリケーションコード
│   │   ├── Controller/      # HomeController, DetailsController, ContactController
│   │   ├── Entity/          # Company, Operation, Route, RawScrapedData
│   │   └── Repository/
│   ├── migrations/          # Doctrine migrations
│   ├── tests/               # PHPUnit テスト
│   ├── config/              # Symfonyの設定ファイル
│   └── public/              # 公開ディレクトリ
├── docker-compose.yml       # Docker構成ファイル
└── README.md                # このファイル

---

## 🛠️ 環境構築

### **1. 必要なツール**

- DockerおよびDocker Compose
- Python 3.12以上
- Composer（Symfonyの依存ライブラリ管理ツール）

### **2. クローンリポジトリ**

git clone https://github.com/yourusername/ShipInfo.git
cd ShipInfo

### **3. 環境変数の設定**

- `.env` ファイルをプロジェクトルートに配置します。開発環境用の例：

APP_ENV=dev
APP_SECRET=your_random_secret
MYSQL_HOST=db
MYSQL_DATABASE=ship_info
MYSQL_USER=user
MYSQL_PASSWORD=password
DATABASE_URL=mysql://user:password@db:3306/ship_info
MARIXLINE_SERVICE_URL=https://marixline.com/service/
# メール通知（任意）
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
ALERT_FROM=your_email@example.com
ALERT_TO=your_email@example.com

---

### **4. Dockerコンテナの起動**

docker-compose up -d

---

### **5. マイグレーション適用**

docker-compose exec symfony php bin/console doctrine:migrations:migrate --no-interaction

---

## 📖 使い方

### **データ収集（スクレイピング）**

Pythonスクリプトでデータを収集します。

docker-compose exec python python save_kametoku_info.py

定期実行には `cron` または `task scheduler` を利用してください。

---

### **ウェブアプリケーションの利用**

開発環境では以下のURLからアクセスできます：

- ホーム（最新運航情報）: http://localhost:8080
- 当日の運航詳細: http://localhost:8080/details/today
- お問い合わせ: http://localhost:8080/contact

---

### **テスト実行**

docker-compose exec symfony php bin/phpunit

---

## 📋 今後の改良予定

- `Operation.status` の PHP enum 化（#14）
- 複数フェリー会社に対応した柔軟なスクレイピング機能の拡充

---

## 👥 貢献方法

1. このリポジトリをForkしてください。
2. 新しいブランチを作成します（例: `git checkout -b feature/your-feature`）。
3. コードをコミットします（例: `git commit -m 'Add some feature'`）。
4. プルリクエストを作成します。

---

## ⚖️ ライセンス

このプロジェクトはMITライセンスのもとで公開されています。詳細は `LICENSE` ファイルをご確認ください。

---

## 📞 問い合わせ

何か質問がある場合や問題が発生した場合は、以下の連絡先にお問い合わせください：

- 開発者: Yamamichi Takashi
- Email: your_email@example.com
