import requests
from helpers import unix_timestamp_to_iso

def fetch_arbeitnow_jobs():
    response = requests.get("https://arbeitnow.com/api/job-board-api")

    results = response.json()

    output = []

    for job in results["data"]:
        output.append({
            "title":job["title"],
            "company":job["company_name"],
            "url":job["url"],
            "location":job["location"],
            "remote":job["remote"],
            "tags":job["tags"],
            "date":unix_timestamp_to_iso(job["created_at"])
        })

    return output