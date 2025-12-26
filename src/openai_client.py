import os
from openai import OpenAI

def chatgpt_edit(user_prompt: str, model: str = "gpt-4.1-mini") -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    res = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "あなたは冷静で簡潔なニュース編集者です。"},
            {"role": "user", "content": user_prompt},
        ],
    )
    return res.choices[0].message.content
