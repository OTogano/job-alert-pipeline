import requests
from bs4 import BeautifulSoup


def fetch_brighter_moday_listings_summaries():
    response = requests.get("https://www.brightermonday.co.ke/jobs/software-data")

    soup = BeautifulSoup(response.text, "html.parser")
    titles = soup.find_all("a",attrs={"data-cy": "listing-title-link"})
    output = []
    print(titles[0])
    # for title in titles:
    #     output.append({


    #     })

fetch_brighter_moday_listings_summaries()