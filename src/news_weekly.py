from search_news import search
from gemini_client import gemini_generate
from prompts import GEMINI_WEEKLY_MED_EDIT_PROMPT
from line_push import push_line
import json

def main():
    queries = [
        "日本 医療 ガイドライン 改訂 今週",
        "厚生労働省 医療 制度 発表",
        "医学会 ガイドライン 改訂",
        "医療制度 改正 日本"
    ]

    results = []
    for q in queries:
        results.extend(search(q, num=3))

    material = json.dumps(results, ensure_ascii=False, indent=2)

    prompt = (
        GEMINI_WEEKLY_MED_EDIT_PROMPT
        + "\n\n【以下は今週の検索結果（事実素材）です】\n"
        + material
        + "\n\n条件：この素材以外の情報は使わないこと。"
    )

    edited = gemini_generate(prompt)
    push_line(edited)

if __name__ == "__main__":
    main()
