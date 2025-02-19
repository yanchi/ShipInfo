import openai
import os

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# コードレビューを実行
try:
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "あなたは優秀なコードレビュワーです。"},
            {"role": "user", "content": "以下のコードをレビューしてください。\n\n" + open("ship_info/src/Entity/Operation.php").read()}
        ]
    )
    review_text = response["choices"][0]["message"]["content"]
    print("=== AI Code Review Result ===", flush=True)
    print(review_text, flush=True)
    print("=== End of Review ===", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
