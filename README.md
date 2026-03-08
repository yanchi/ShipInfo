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
│   ├── get_latest_status_urls.py      # 運航情報取得用のURLを収集
│   ├── scrape_operation_details.py    # 運航情報のスクレイピング処理
│   └── save_kametoku_info.py          # スクレイピングしたデータをDBに保存
├── ship_info/               # Symfonyによるウェブアプリケーション
│   ├── .env                 # 環境変数（本番環境用はVPSで生成）
│   ├── config/              # Symfonyの設定ファイル
│   ├── src/                 # アプリケーションコード
│   ├── public/              # 公開ディレクトリ
│   └── ...
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
MARIXLINE_SERVICE_URL=https://marixline.com/service/

---

### **4. Dockerコンテナの起動**

docker-compose up -d

---

## 📖 使い方

### **データ収集（スクレイピング）**

1. Pythonスクリプトでデータを収集します。

cd python/src
python save_kametoku_info.py

2. スクリプトを定期実行するには、`cron` または `task scheduler` を利用してください。

---

### **ウェブアプリケーションの利用**

1. アプリケーションにアクセスします。

- 開発環境では以下のURLからアクセスできます：
  http://localhost:8080

2. フェリー運航情報を閲覧または検索。

---

## 📋 今後の改良予定

- フェリー運航データのリアルタイム更新機能。
- REST APIの拡張。
- 複数フェリー会社に対応した柔軟なスクレイピング機能。

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
