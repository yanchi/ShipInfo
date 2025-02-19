import openai
import os

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# コードの読み込み
with open("ship_info/src/Entity/Operation.php", "r") as file:
    code = file.read()

# AIにコードレビューを依頼（新しいAPI形式）
client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "あなたは優秀なコードレビュワーです。"},
        {"role": "user", "content": f"以下のコードをレビューしてください。\n\n{code}"}
    ]
)

# レビュー結果を出力
review_text = response.choices[0].message.content
print("=== AI Code Review Result ===", flush=True)
print(review_text, flush=True)
print("=== End of Review ===", flush=True)
