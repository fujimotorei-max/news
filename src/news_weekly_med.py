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
        # 制度
        "厚生労働省 医療 方針",
        "診療報酬 改定",
        "医療制度 改正 日本",
        "医師 働き方改革",
        # ガイドライン
        "学会 ガイドライン 改訂 医療",
        "診断基準 改訂 日本 医療",
        "感染症 指針 改訂 日本",
        "予防接種 制度 変更",
        # 医療ニュース
        "医療事故 日本",
        "医療訴訟 日本",
        "救急搬送 日本 問題",
        "医師不足 日本",
        "産科 不足 日本",
        "医療 AI 日本",
        "病院 経営 日本",
        "薬 不足 日本",
        "感染症 日本 ニュース",
        "災害医療 日本",
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
        + "\n\n"
        + "あなたは医学生向け週刊医療ニュースの編集者です。"
        + " 以下のニュース素材を、重要度・学習価値・社会的影響の観点から評価し、"
        + " 今週の重要ニュースを2〜3本に厳選してください。\n\n"
        
        + "ニュースは以下の3種類に分類して考えてください：\n"
        + "① 医療制度・政策（診療報酬、制度改正、厚労省方針など）\n"
        + "② ガイドライン・診断基準（学会ガイドライン、指針改訂など）\n"
        + "③ 医療ニュース（医療事故、医師不足、感染症、医療AI、病院経営、社会問題など）\n\n"
        + "可能であれば、特定の分野に偏らないように選んでください。\n\n"
        + "研究段階・新薬・単一施設の症例報告・宣伝・煽り記事は除外してください。\n"
        + "必ず提供されたニュース素材の情報のみを使用し、推測や一般論は書かないでください。"
        + "\n\n出力形式：\n"
        + "【今週の医療ニュース】\n"
        + "■タイトル\n"
        + "・何が起きたか\n"
        + "・なぜ重要か\n"
        + "・医学生としてどこを理解すべきか\n"
        + "・元記事URL\n"
    )

    edited = gemini_generate(prompt)
    push_line(edited)


if __name__ == "__main__":
    main()
