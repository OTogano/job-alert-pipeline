import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def format_job_message(job) -> str:
    remote_label = job.remote.name if job.remote else "Unknown"
    tags = ", ".join(job.tags) if job.tags else "—"
    return (
        f"*{job.title}*\n"
        f"{job.company} — {job.location or 'Unknown location'}\n"
        f"Remote: {remote_label}\n"
        f"Tags: {tags}\n"
        f"{job.url}"
    )


def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Failed to send Telegram message: {response.text}")


def notify_new_jobs(jobs: list):
    for job in jobs:
        message = format_job_message(job)
        send_telegram_message(message)