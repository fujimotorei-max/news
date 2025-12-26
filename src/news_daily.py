# src/news_daily.py
from datetime import datetime
import json

from search_news import search, TRUSTED_DOMAINS, BLOCKED_DOMAINS
from gemini_client import gemini_generate
from prompts import GEMINI_DAILY_EDIT_PROMPT
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
    # 「今日/昨日」寄せ：d2（過去2日）
    date_restrict = "d2"
    today_str = datetime.now().strftime("%m月%d日")

    # ★重要ニュース向けの検索クエリ（地方小ネタを拾いにくい言葉に寄せる）
    economy_queries = [
        f"日銀 発表 {today_str}",
        f"日銀 金利 {today_str}",
        f"為替 円 ドル {today_str}",
        f"物価 CPI 日本 {today_str}",
        f"株式市場 日本 {today_str}",
        f"財務省 発表 {today_str}",
    ]

    society_system_queries = [
        f"政府 方針 決定 {today_str}",
        f"官邸 発表 {today_str}",
        f"法改正 施行 日本 {today_str}",
        f"厚生労働省 発表 {today_str}",
        f"経済産業省 発表 {today_str}",
        f"総務省 発表 {today_str}",
    ]

    # 会話用は「全国ニュース」寄せ（ローカル番組・PRを避ける）
    talk_queries = [
        f"NHK 事件 {today_str}",
        f"NHK 事故 {today_str}",
        f"全国 ニュース 炎上 {today_str}",
        f"大手新聞 速報 {today_str}",
    ]

    collected = {
        "economy": [],
        "society_system": [],
        "talking_points": [],
    }

    # 信頼ソースだけで拾う（ここが“センス”を作る）
    allow_domains = TRUSTED_DOMAINS
    block_domains = BLOCKED_DOMAINS

    # 候補数は多めに確保（後段の編集で絞る）
    for q in economy_queries:
        collected["economy"].extend(search(q, num=5, date_restrict=date_restrict,
                                          allow_domains=allow_domains, block_domains=block_domains))
    for q in society_system_queries:
        collected["society_system"].extend(search(q, num=5, date_restrict=date_restrict,
                                                 allow_domains=allow_domains, block_domains=block_domains))
    for q in talk_queries:
        collected["talking_points"].extend(search(q, num=5, date_restrict=date_restrict,
                                                 allow_domains=allow_domains, block_domains=block_domains))

    # 重複除去
    collected["economy"] = dedupe_by_link(collected["economy"])
    collected["society_system"] = dedupe_by_link(collected["society_system"])
    collected["talking_points"] = dedupe_by_link(collected["talking_points"])

    material = json.dumps(collected, ensure_ascii=False, indent=2)

    prompt = (
        GEMINI_DAILY_EDIT_PROMPT
        + "\n\n【以下は直近2日（今日/昨日）に限定して、信頼ソースから取得したニュース素材です】\n"
        + material
        + "\n\n条件：この素材以外の情報は使わないこと。推測・一般論は禁止。"
        + " 社会・制度と経済は“全国レベルの重要ニュース”を優先し、地方の小ネタは原則除外。"
        + " 発表日が古そうなものは除外（タイトル/本文に今日/昨日の要素が薄い場合は落とす）。"
    )

    edited = gemini_generate(prompt)
    push_line(edited)


if __name__ == "__main__":
    main()
