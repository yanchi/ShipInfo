import os
import sys

# scrape_operation_details が import 時に参照する環境変数を設定
os.environ.setdefault("MARIXLINE_SERVICE_URL", "http://dummy-for-tests")

# src ディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
