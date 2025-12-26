from prompts import GEMINI_MED_WEEKLY_PROMPT, CHATGPT_WEEKLY_MED_EDIT_PROMPT
from gemini_client import gemini_generate
from openai_client import chatgpt_edit
from line_push import push_line

def main():
    med = gemini_generate(GEMINI_MED_WEEKLY_PROMPT)
    combined = CHATGPT_WEEKLY_MED_EDIT_PROMPT + "\n\n---\n" + med
    msg = chatgpt_edit(combined)
    push_line(msg)

if __name__ == "__main__":
    main()
