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
    # PHP, JS, TS, Pythonなどのコードファイルのみを対象にする
    if file_path.endswith((".php", ".js", ".py", ".ts")):
        try:
            with open(file_path, "r", encoding="utf-8") as code_file:
                code_snippets.append(f"### {file_path} ###\n{code_file.read()}\n")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

# コードが空なら終了
if not code_snippets:
    print("No valid code files to review.")
    exit(0)

# 過去のレビュー履歴を取得（履歴があれば一貫したレビューが可能）
past_reviews = ""
if os.path.exists("past_reviews.txt"):
    with open("past_reviews.txt", "r", encoding="utf-8") as file:
        past_reviews = file.read()

# レビュー用のプロンプトを作成
code_snippets_text = "\n".join(code_snippets)
review_prompt = f"""
あなたは経験豊富なコードレビュワーです。
以下のルールに従ってコードをレビューし、統一された評価基準を適用してください。

【過去のレビュー履歴】（参考にして、同じ基準でレビューしてください）
{past_reviews}

【レビューガイドライン】
- 変数名・関数名が適切か（キャメルケース・スネークケースなどの命名規則を考慮）
- エラーハンドリングが適切に行われているか
- パフォーマンスや保守性に問題がないか
- セキュリティリスクがないか
- コードの可読性が確保されているか

【出力フォーマット】
### 🚨 問題点
- 問題点を明確にリストアップ

### ✅ 修正案
[ここに具体的な修正コード例を記述]

### 📌 コメント
- 修正の理由を説明

【レビュー対象のコード】
{code_snippets_text}
"""

# AIにコードレビューを依頼
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "system", "content": review_prompt}],
    temperature=0  # ← これで毎回同じような回答になる
)

# レビュー結果を取得
review_text = response.choices[0].message.content

# レビュー結果を保存（次回のレビューと一貫性を持たせるため）
with open("past_reviews.txt", "w", encoding="utf-8") as file:
    file.write(review_text)

# GitHub Pull Request にコメントを投稿
subprocess.run([
    "gh", "pr", "comment", os.getenv("PR_NUMBER"),
    "--body", review_text
], check=True)
