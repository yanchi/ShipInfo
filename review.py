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

# 過去のレビュー履歴を取得（履歴があれば一貫したレビューが可能）
past_reviews = ""
if os.path.exists("past_reviews.txt"):
    with open("past_reviews.txt", "r", encoding="utf-8") as file:
        past_reviews = file.read()

# 既にレビューしたファイルを記録するリスト
reviewed_files = set()
if os.path.exists("reviewed_files.txt"):
    with open("reviewed_files.txt", "r", encoding="utf-8") as file:
        reviewed_files = set(file.read().splitlines())

# 各ファイルを個別にレビューし、コメントを投稿
for file_path in changed_files:
    # PHP, JS, TS, Pythonなどのコードファイルのみを対象にする
    if file_path.endswith((".php", ".js", ".py", ".ts")) and file_path not in reviewed_files:
        try:
            with open(file_path, "r", encoding="utf-8") as code_file:
                code_content = code_file.read()

            # レビュー用のプロンプトを作成（日本語で指示を追加）
            review_prompt = f"""
あなたは経験豊富なコードレビュワーです。
以下のルールに従ってコードをレビューし、統一された評価基準を適用してください。
**必ず日本語で回答してください！**

【過去のレビュー履歴】（参考にして、同じ基準でレビューしてください）
{past_reviews}

【レビューガイドライン】
- 変数名・関数名が適切か（キャメルケース・スネークケースなどの命名規則を考慮）
- エラーハンドリングが適切に行われているか
- パフォーマンスや保守性に問題がないか
- セキュリティリスクがないか
- コードの可読性が確保されているか

【レビュー対象のファイル】 {file_path}

【コード】
{code_content}
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

            # GitHub Pull Request にコメントを投稿
            subprocess.run([
                "gh", "pr", "comment", os.getenv("PR_NUMBER"),
                "--body", f"### レビュー結果（{file_path}）\n{review_text}"
            ], check=True)

            # レビュー済みファイルに追加
            reviewed_files.add(file_path)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

# レビュー済みファイルのリストを保存（次回の実行でスキップするため）
with open("reviewed_files.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(reviewed_files))

print("All reviews completed.")
