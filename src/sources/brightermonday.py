import json
import time
import requests
from bs4 import BeautifulSoup
from .helpers import find_node_by_type, resolve_jsonld_graph


def fetch_brightermonday_listings_summaries(category:str):
    response = requests.get(f"https://www.brightermonday.co.ke/jobs/{category}")

    soup = BeautifulSoup(response.text, "html.parser")
    titles = soup.find_all("a",attrs={"data-cy": "listing-title-link"})
    output = []
    for title in titles:
        output.append({
            "title": title.get("title"),
            "url": title.get("href")
        })
    return output

def build_standard_job_dict(job_posting: dict, resolved_graph:dict, url:str) -> dict:
    org_ref = job_posting.get("hiringOrganization",{})
    org_node =  resolved_graph.get(org_ref.get("@id"),{})
    company = org_node.get("name")

    location_data = job_posting.get("jobLocation")
    if location_data:
        location = location_data.get("address", {}).get("addressRegion")
    else:
        location = None

    remote_raw = job_posting.get("jobLocationType")
    if remote_raw == "TELECOMMUTE":
        remote = True
    elif remote_raw is not None:
        remote = False
    else:
        remote = None

    tags = [t for t in [job_posting.get("industry"), job_posting.get("occupationalCategory")] if t]

    return {
        "title": job_posting.get("title"),
        "company": company,
        "url": url,
        "location": location,
        "remote": remote,
        "tags": tags,
        "date": job_posting.get("datePosted"),
    }

def fetch_brightermonday_full_listings(summaries: list):
    listings = []
    for summary in summaries:
        response = requests.get(summary["url"])
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.find("script", type="application/ld+json").get_text()
        text_to_dict = json.loads(text)
        text_to_resolve = text_to_dict["@graph"]
        resolved_text = resolve_jsonld_graph(text_to_resolve)
        job_posting = find_node_by_type(resolved_text, "JobPosting")

        standardized = build_standard_job_dict(job_posting, resolved_text, summary["url"])
        listings.append(standardized)

        time.sleep(1)
    return listings

test_summaries = [
    {'title': 'Senior QA Automation Engineer', 'url': 'https://www.brightermonday.co.ke/listings/qa-developer-5p64x6'},
    {'title': 'FreshDesk Specialist', 'url': 'https://www.brightermonday.co.ke/listings/freshdesk-specialist-x8d448'}
]

# output = fetch_brightermonday_full_listings(test_summaries)
# import json
# print(json.dumps(output, indent=2))