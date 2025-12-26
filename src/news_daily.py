# src/news_daily.py
# 最新ニュース用（検索 → 編集 → LINE通知）

from datetime import datetime
import json

from search_news import search
from gemini_client import gemini_generate
from prompts import GEMINI_DAILY_EDIT_PROMPT
from line_push import push_line


def main():
    # 日本時間の「今日」を文字列に
    today_str = datetime.now().strftime("%m月%d日")

    # 「今日」を強く意識させた検索クエリ
    queries = {
        "economy": f"日本 経済 ニュース 今日 {today_str}",
        "society": f"日本 社会 制度 ニュース 今日 {today_str}",
        "talk": f"日本 話題 ニュース 今日 {today_str}",
    }

    collected = {}

    # 各カテゴリごとに検索
    for category, query in queries.items():
        collected[category] = search(query, num=5)

    # Geminiに渡す素材（検索結果）
    material = json.dumps(collected, ensure_ascii=False, indent=2)

    # 編集フェーズ用プロンプト
    prompt = (
        GEMINI_DAILY_EDIT_PROMPT
        + "\n\n【以下は本日検索で取得したニュース素材です】\n"
        + material
        + "\n\n条件：この素材以外の情報は使わないこと。"
        + " 発表日が今日または昨日でない記事は原則除外すること。"
    )

    # 編集（要約・線引き）
    edited_text = gemini_generate(prompt)

    # LINEに送信
    push_line(edited_text)


if __name__ == "__main__":
    main()
