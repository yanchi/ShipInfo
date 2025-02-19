import openai
import os
import subprocess

# OpenAI APIキーを取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# コードの読み込み
with open("ship_info/src/Entity/Operation.php", "r") as file:
    code = file.read()

# AIにコードレビューを依頼
client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "あなたは優秀なコードレビュワーです。"},
        {"role": "user", "content": f"以下のコードをレビューしてください。\n\n{code}"}
    ]
)

# レビュー結果
review_text = response.choices[0].message.content

# GitHub Pull Request にコメントを投稿
subprocess.run([
    "gh", "pr", "comment", os.getenv("PR_NUMBER"),
    "--body", review_text
], check=True)
