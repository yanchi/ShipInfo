import openai
import os

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# コードレビューを実行
response = openai.ChatCompletion.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "あなたは優秀なコードレビュワーです。"},
        {"role": "user", "content": "以下のコードをレビューしてください。\n\n" + open("Operation.php").read()}
    ]
)

# レビュー結果を出力
review_text = response["choices"][0]["message"]["content"]
print("=== AI Code Review Result ===")
print(review_text)
print("=== End of Review ===")