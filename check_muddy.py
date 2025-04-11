import requests
from datetime import datetime, timedelta
import os
import time
import sys

# Telegram credentials (replace with environment variables or use GitHub/GitLab secrets)
TELEGRAM_BOT_TOKEN = "7556981326:AAFdyn2sZdBJVo1qFeN72AmIMiUbDBtpA3E"
TELEGRAM_CHAT_ID = "5643667423"
SEEN_FILE = "seen.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MuddyMonitorBot/1.0; +https://github.com/mtullaga)"
}

def send_telegram(msg):
    """Send notification via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"Telegram sent: {msg}")
        else:
            print(f"Telegram failed: {response.text}")
    except Exception as e:
        print(f"Telegram error: {e}")

def head_with_retry(url, retries=3, delay=1):
    for _ in range(retries):
        try:
            return requests.head(url, headers=HEADERS, timeout=5)
        except requests.RequestException:
            time.sleep(delay)
    print(f"Failed to reach {url} after {retries} attempts.")
    return None

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_seen(url):
    with open(SEEN_FILE, "a") as f:
        f.write(url + "\n")

def check_reports():
    base_url = "https://muddywatersresearch.com/wp-content/uploads"
    seen = load_seen()
    today = datetime.utcnow()
    found_any = False

    for offset in range(0, 4):
        d = today + timedelta(days=offset)
        y, m, d_str = d.strftime("%Y"), d.strftime("%m"), d.strftime("%Y%m%d")
        url = f"{base_url}/{y}/{m}/MW_{d_str}.pdf"

        if url in seen:
            print(f"Skipping already seen: {url}")
            continue

        response = head_with_retry(url)
        if response and response.status_code == 200:
            send_telegram(f"🧨 *New Muddy Waters Report!*\n{url}")
            save_seen(url)
            found_any = True

    if not found_any:
        send_telegram(f"No new reports found this run.")

if __name__ == "__main__":
    check_reports()
    sys.exit(0)
