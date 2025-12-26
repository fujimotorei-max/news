from prompts import GEMINI_DAILY_PROMPT
from gemini_client import gemini_generate
from line_push import push_line

def main():
    text = gemini_generate(GEMINI_DAILY_PROMPT)
    push_line(text)

if __name__ == "__main__":
    main()
