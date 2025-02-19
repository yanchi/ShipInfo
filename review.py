import openai
import os
import subprocess

# OpenAI APIキーを取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# 変更があったファイルを取得
with open("changed_files.txt", "r") as file:
    changed_files = [line.strip() for line in file.readlines()]

# 変更ファイルがなければ終了
if not changed_files:
    print("No changed files to review.")
    exit(0)

# すべての変更ファイルのコードを読み込む
code_snippets = []
for file_path in changed_files:
    # PHPなどのコードファイルのみ対象にする（不要なら削除）
    if file_path.endswith((".php", ".js", ".py", ".ts")):
        try:
            with open(file_path, "r", encoding="utf-8") as code_file:
                code_snippets.append(f"### {file_path} ###\n{code_file.read()}\n")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

# すべてのコードをまとめてAIに送信
if code_snippets:
    client = openai.OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "あなたは優秀なコードレビュワーです。"},
            {"role": "user", "content": "以下のコードをレビューしてください。\n\n" + "\n".join(code_snippets)}
        ]
    )

    # レビュー結果を取得
    review_text = response.choices[0].message.content

    # GitHub Pull Request にコメントを投稿
    subprocess.run([
        "gh", "pr", "comment", os.getenv("PR_NUMBER"),
        "--body", review_text
    ], check=True)
