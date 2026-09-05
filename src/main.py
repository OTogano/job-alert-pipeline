import yaml
from models import Job
from sources.arbeitnow import fetch_arbeitnow_jobs
from sources.brightermonday import(
    fetch_brightermonday_full_listings,
    fetch_brightermonday_listings_summaries,
)

def load_config(path="../config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    all_jobs = []

    # Arbeitnow
    arbeitnow_raw = fetch_arbeitnow_jobs()
    for raw in arbeitnow_raw:
        job =Job.from_dict(raw, source="arbeitnow")
        all_jobs.append(job)

    # Brighter Monday
    for category in config["job-categories"]:
        summaries = fetch_brightermonday_listings_summaries(category)
        raw_listings = fetch_brightermonday_full_listings(summaries)
        for raw in raw_listings:
            job = Job.from_dict(raw, source="brightermonday")
            all_jobs.append(job)

    return all_jobs


if __name__ == "__main__":
    jobs = main()
    print(f"Total jobs collected: {len(jobs)}")
    for job in jobs:
        print(job)
