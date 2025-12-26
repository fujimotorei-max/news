from search_news import search
from gemini_client import gemini_generate
from prompts import GEMINI_DAILY_EDIT_PROMPT
from line_push import push_line
import json

def main():
    queries = {
        "economy": "日本 経済 ニュース 今日",
        "society": "日本 社会 制度 ニュース 今日",
        "talk": "日本 話題 ニュース 今日"
    }

    collected = {}
    for k, q in queries.items():
        collected[k] = search(q, num=5)

    material = json.dumps(collected, ensure_ascii=False, indent=2)

    prompt = (
        GEMINI_DAILY_EDIT_PROMPT
        + "\n\n【以下は本日検索で取得したニュース素材です】\n"
        + material
    )

    edited = gemini_generate(prompt)
    push_line(edited)

if __name__ == "__main__":
    main()
