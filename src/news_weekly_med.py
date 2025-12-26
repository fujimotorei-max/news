# src/news_weekly_med.py
from datetime import datetime
import json

from search_news import search, TRUSTED_DOMAINS, BLOCKED_DOMAINS
from gemini_client import gemini_generate
from prompts import GEMINI_WEEKLY_MED_EDIT_PROMPT
from line_push import push_line


def dedupe_by_link(items: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for it in items:
        link = it.get("link")
        if not link or link in seen:
            continue
        seen.add(link)
        out.append(it)
    return out


def main():
    # 週1なら「直近7日」でOK（今週感を担保）
    date_restrict = "d7"

    # 今日の日付（検索のノイズを減らすために足す）
    today_str = datetime.now().strftime("%m月%d日")

    # ★医療Weekly：国試・実習に刺さる“制度/標準診療/定義”寄せクエリ
    queries = [
        f"厚生労働省 通知 医療 {today_str}",
        "厚生労働省 ガイドライン 改訂",
        "診療報酬 改定 医療 厚生労働省",
        "医師 働き方改革 医療 制度 改正",
        "感染症 対策 指針 改訂 日本",
        "予防接種 定期接種 変更 厚生労働省",
        "学会 ガイドライン 改訂 日本",
        "診断基準 改訂 日本 学会",
        "救急 医療体制 指針 改訂",
        "周産期 医療体制 指針 改訂",
    ]

    allow_domains = TRUSTED_DOMAINS
    block_domains = BLOCKED_DOMAINS

    results = []
    for q in queries:
        results.extend(
            search(
                q,
                num=5,
                date_restrict=date_restrict,
                allow_domains=allow_domains,
                block_domains=block_domains,
            )
        )

    results = dedupe_by_link(results)

    material = json.dumps({"items": results}, ensure_ascii=False, indent=2)

    prompt = (
        GEMINI_WEEKLY_MED_EDIT_PROMPT
        + "\n\n【以下は直近7日（今週）に限定して取得したニュース素材です】\n"
        + material
        + "\n\n条件：この素材以外の情報は使わないこと。推測・一般論は禁止。"
        + " 研究段階・新薬・単一施設の症例報告・煽り見出しは原則除外。"
        + " 国試・実習で使う“標準知識につながる線”が太いものを2〜3本に厳選。"
    )

    edited = gemini_generate(prompt)
    push_line(edited)


if __name__ == "__main__":
    main()
