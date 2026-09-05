# Job Alert Pipeline

An automated pipeline that scrapes Kenyan job boards, deduplicates listings against a local history, and pushes new, relevant job postings straight to Telegram, no manual checking required.

Built as a personal project to combine backend engineering practice (API integration, web scraping, data modeling, persistence) with a real, ongoing use case: an efficient, low-noise job search.

## How it works

1. **Fetch** - pulls job listings from [BrighterMonday](https://www.brightermonday.co.ke), filtered to configured categories (e.g. Software & Data, Engineering & Technology).
2. **Dedup-gate** - before doing any expensive per-job scraping, each listing's URL is hashed and checked against a local SQLite store of previously-seen jobs. Only genuinely new listings proceed.
3. **Parse** - for new listings, the job's detail page is fetched and its embedded [JSON-LD](https://schema.org/JobPosting) structured data is parsed (rather than fragile HTML scraping) to extract clean, structured fields.
4. **Standardize** - every source's raw data is normalized into one consistent `Job` shape, so filtering, storage, and alerting logic never need to know which site a listing came from.
5. **Persist** - new jobs are saved to `jobs.db` (SQLite), which is committed back to the repository after each run. This is how state survives between runs on GitHub Actions' stateless runners.
6. **Alert** - new jobs are formatted and sent as Telegram messages via a bot.

The entire pipeline runs on a schedule via **GitHub Actions**, with no server to host or maintain.

## Architecture

```
job-alert-pipeline/
├── .github/workflows/run.yml    # scheduled + manually-triggerable pipeline run
├── src/
│   ├── main.py                  # orchestrates fetch -> dedup -> alert -> persist
│   ├── models.py                # Job dataclass, Remote enum, hash-based id, from_dict factory
│   ├── helpers.py               # shared conversions: timestamps, JSON-LD graph resolution
│   ├── store.py                 # SQLite persistence and dedup lookups
│   ├── notifier.py              # Telegram message formatting and sending
│   └── sources/
│       └── brightermonday.py    # BrighterMonday-specific fetch + parse logic
├── config.yaml                  # job categories to search
├── requirements.txt
└── jobs.db                      # committed to the repo - acts as persistent history across runs
```

### Design notes

- **Sources are self-contained.** Each source module (`sources/brightermonday.py`) is responsible for fetching and translating a specific site's quirks into one standardized dict shape. `Job.from_dict()` never needs to know which source it came from. This makes adding a new source (e.g. a different job board) a matter of writing one new file, not touching existing code.
- **JSON-LD over raw HTML scraping.** BrighterMonday (and other sites on the same Ringier/ROAM platform) embed structured [schema.org `JobPosting`](https://schema.org/JobPosting) data in each listing's page, originally intended for search engines. Reading this directly is far more reliable than parsing arbitrary HTML/CSS, which breaks on redesigns.
- **Dedup-before-fetch, not fetch-then-dedup.** Because BrighterMonday's rich data requires an extra request per job (unlike a single bulk API call), listing summaries are checked against known IDs *before* their detail pages are fetched, avoiding unnecessary requests to jobs already seen.
- **SQLite committed to git, not gitignored.** GitHub Actions runners are stateless between runs. Committing `jobs.db` back to the repository after each run is what allows dedup history to persist. This is a deliberate architectural choice, not an oversight.

## Setup

1. Clone the repo and create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```
2. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and get your bot token and chat ID.
3. For local testing, create a `.env` file (not committed):
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```
4. Edit `config.yaml` to set which BrighterMonday categories to track.
5. Run locally:
   ```
   python -m src.main
   ```

## Running in production

The pipeline runs automatically via GitHub Actions (`.github/workflows/run.yml`) on a schedule. For this to work in your own fork:
- Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as **repository secrets** (Settings -> Secrets and variables -> Actions)
- The workflow has `contents: write` permission so it can commit the updated `jobs.db` back to the repo after each run

## Sources

| Source | Method | Status |
|---|---|---|
| BrighterMonday | JSON-LD parsing (per-listing detail pages) | Active |
| Arbeitnow | Public JSON API | Removed - listings skewed EU/Germany with little relevance to Kenya-based job seekers; may revisit with proper remote-eligibility filtering later |
| CareerJet Kenya | - | Not pursued - protected by Cloudflare Turnstile; scraping around active bot-detection was judged not worth pursuing for a personal project |

## Roadmap

- [ ] Keyword/relevance filtering before alerting (currently all new jobs in configured categories are alerted)
- [ ] Fuzu as a second local source
- [ ] Automated tests (pytest) for normalization, dedup, and filtering logic
- [ ] LLM-assisted extraction with a verifier layer for sources without structured data

## Tech stack

Python, `requests`, `BeautifulSoup4`, SQLite, PyYAML, python-dotenv, GitHub Actions, Telegram Bot API