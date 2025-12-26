from prompts import GEMINI_ECON_PROMPT, GEMINI_SOCIAL_PROMPT, CHATGPT_DAILY_EDIT_PROMPT
from gemini_client import gemini_generate
from openai_client import chatgpt_edit
from line_push import push_line

def main():
    econ = gemini_generate(GEMINI_ECON_PROMPT)
    social = gemini_generate(GEMINI_SOCIAL_PROMPT)

    combined = (
        CHATGPT_DAILY_EDIT_PROMPT
        + "\n\n---\n【Gemini: 経済ニュース】\n" + econ
        + "\n\n---\n【Gemini: 世の中ニュース】\n" + social
    )
    msg = chatgpt_edit(combined)
    push_line(msg)

if __name__ == "__main__":
    main()
