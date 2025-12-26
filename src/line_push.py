import os
import requests

def push_line(text: str) -> None:
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {os.environ['LINE_CHANNEL_ACCESS_TOKEN']}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": os.environ["LINE_USER_ID"],
        "messages": [{"type": "text", "text": text[:5000]}],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
