import os

# scrape_operation_details が import 時に参照する環境変数を設定
os.environ.setdefault("MARIXLINE_SERVICE_URL", "http://dummy-for-tests")
