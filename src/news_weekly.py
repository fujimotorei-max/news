from prompts import GEMINI_WEEKLY_MED_PROMPT
from gemini_client import gemini_generate
from line_push import push_line

def main():
    text = gemini_generate(GEMINI_WEEKLY_MED_PROMPT)
    push_line(text)

if __name__ == "__main__":
    main()
