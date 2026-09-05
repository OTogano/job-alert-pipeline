import yaml
from .notifier import notify_new_jobs
from .models import Job
from .sources.brightermonday import(
    fetch_brightermonday_full_listings,
    fetch_brightermonday_listings_summaries,
)
from .helpers import compute_job_id
from .store import init_db, get_known_ids, save_job

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    init_db()
    known_ids = get_known_ids()
    config = load_config()
    all_jobs = []

    # Brighter Monday
    """
    Brighter Monday's website is structured such that the full job listing information is
    accessed from the jobs title card. Rather than scrapping all the Job listings by navigating
    each card, which is an expensive fetch, only scrape the ones that are new/not saved to store.db. 
    """
    for category in config["job-categories"]:
        summaries = fetch_brightermonday_listings_summaries(category)

        new_summaries = [
            s for s in summaries
            if compute_job_id(s["url"], "brightermonday") not in known_ids
        ]

        raw_listings = fetch_brightermonday_full_listings(new_summaries)
        for raw in raw_listings:
            job = Job.from_dict(raw, source="brightermonday")
            all_jobs.append(job)
            save_job(job)

    notify_new_jobs(all_jobs)
    return all_jobs


if __name__ == "__main__":
    jobs = main()
    print(f"Total jobs collected: {len(jobs)}")
    for job in jobs:
        print(job)
