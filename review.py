import openai
import os
import json
import subprocess

# OpenAI APIキーを取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# PR番号を取得
pr_number = os.getenv("PR_NUMBER")

# 過去のレビュー履歴を取得
past_reviews = ""
if os.path.exists("past_reviews.txt"):
    with open("past_reviews.txt", "r", encoding="utf-8") as file:
        past_reviews = file.read()

# GitHub APIを使って「修正しないファイル一覧」を取得
def get_skip_files(pr_number):
    """ PRのコメントを取得し、「修正しないファイル一覧」を抽出する """
    result = subprocess.run(
        ["gh", "api", f"repos/{os.getenv('GITHUB_REPOSITORY')}/issues/{pr_number}/comments"],
        capture_output=True,
        text=True
    )
    
    comments = json.loads(result.stdout)
    skip_files = []
    
    for comment in comments:
        if "### 修正しないファイル一覧" in comment["body"]:
            lines = comment["body"].split("\n")
            for line in lines:
                if line.startswith("- "):  # ファイルリスト部分
                    skip_files.append(line[2:].strip())  # "- " を削除
    
    return skip_files

# 修正しないファイルを取得
skip_files = get_skip_files(pr_number)

# 変更があったファイルを取得
with open("changed_files.txt", "r") as file:
    changed_files = [line.strip() for line in file.readlines()]

# 変更ファイルがなければ終了
if not changed_files:
    print("No changed files to review.")
    exit(0)

# 各ファイルを個別にレビューし、コメントを投稿
for file_path in changed_files:
    # スキップ対象のファイルかチェック
    if file_path in skip_files:
        print(f"Skipping {file_path}, marked as '修正しない'.")
        continue

    # PHP, JS, TS, Pythonなどのコードファイルのみを対象にする
    if file_path.endswith((".php", ".js", ".py", ".ts")):
        try:
            with open(file_path, "r", encoding="utf-8") as code_file:
                code_content = code_file.read()

            # レビュー用のプロンプトを作成（日本語で指示を追加）
            review_prompt = f"""
あなたは経験豊富なコードレビュワーです。
以下のルールに従ってコードをレビューし、統一された評価基準を適用してください。
**必ず日本語で回答してください！**

【レビューガイドライン】
- 変数名・関数名が適切か（キャメルケース・スネークケースなどの命名規則を考慮）
- エラーハンドリングが適切に行われているか
- パフォーマンスや保守性に問題がないか
- セキュリティリスクがないか
- コードの可読性が確保されているか

【過去のレビュー履歴】（参考にして、同じ基準でレビューしてください）
{past_reviews}

【レビュー対象のファイル】 {file_path}

【コード】
{code_content}
"""

            # AIにコードレビューを依頼
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": review_prompt}],
                temperature=0
            )

            # レビュー結果を取得
            review_text = response.choices[0].message.content

            # GitHub Pull Request にコメントを投稿
            subprocess.run([
                "gh", "pr", "comment", pr_number,
                "--body", f"### レビュー結果（{file_path}）\n{review_text}"
            ], check=True)

            # 過去のレビュー履歴を追加
            past_reviews += f"\n\n【{file_path} のレビュー】\n{review_text}"

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

# 過去のレビュー履歴を保存
with open("past_reviews.txt", "w", encoding="utf-8") as file:
    file.write(past_reviews)

print("All reviews completed.")
