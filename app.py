import requests
from bs4 import BeautifulSoup
import time
import json
import os

USERS_FILE = "users.json"
CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"telegram_token": "", "interval": 1800}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def search_naver_news(query):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://search.naver.com/search.naver?where=news&query={query}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    links = []
    for item in soup.select("a.news_tit")[:3]:
        title = item.get("title")
        link = item.get("href")
        links.append((title, link))
    return links

def send_to_telegram(chat_id, token, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

def main():
    sent_links = set()
    while True:
        config = load_config()
        users = load_users()
        for user in users:
            for keyword in user["keywords"]:
                articles = search_naver_news(keyword.strip())
                for title, link in articles:
                    if link not in sent_links:
                        send_to_telegram(user["chat_id"], config["telegram_token"], f"[{keyword.strip()}] {title}\n{link}")
                        sent_links.add(link)
        time.sleep(config["interval"])

if __name__ == "__main__":
    main()
