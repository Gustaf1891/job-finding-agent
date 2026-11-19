# Job Finding Agent

A pipeline that finds relevant job listings from Sweden's public job board (Platsbanken) and, in
upcoming versions, ranks them against my CV using an LLM and highlights skills I'm missing.

> **Status:** work in progress. Data fetching, deduplication and storage work. LLM-based matching is
> under development.

## What it does today

- Fetches job ads from the [Arbetsförmedlingen JobSearch API](https://jobsearch.api.jobtechdev.se)
- Filters by search terms (roles), municipality and publication date
- Deduplicates against previously seen ads (SQLite)
- Validates and cleans each ad into a typed `JobPosting` model (Pydantic)
- Retries failed API calls with exponential backoff and logs each run

## Roadmap

- [ ] LLM analysis per ad: required experience, dealbreakers, requirement-by-requirement CV match
- [ ] Ranking and a daily summary report with links
- [ ] Skill-gap analysis across listings with study suggestions
- [ ] LangGraph workflow wrapping the pipeline
- [ ] Containerization and deployment on Azure (scheduled job, managed database, monitoring)
- [ ] Optional second source (Indeed via Apify)

## Tech stack

Python 3.12, uv, httpx, Pydantic, SQLite, tenacity.
Planned: LangChain/LangGraph, Azure.

## Getting started

```bash
git clone <repo-url>
cd job-finding-agent
uv sync
cp config.example.yaml config.yaml   # then edit
uv run jobagent
```

## Configuration

`config.yaml`:

```yaml
roles: ["data engineer", "AI engineer"]
max_jobs_per_run: 50
lookback_days: 3
municipalities:            # JobTech municipality concept IDs; empty = all of Sweden
  - id: "AvNB_uwa_6n6"
    name: "Stockholm"
```

## Project structure

```
src/jobagent/
  sources/arbetsformedlingen.py   # API client and parsing
  models.py                       # JobPosting model
  store.py                        # SQLite storage and dedupe
  main.py                         # CLI entry point
```

## Data source

Job ads come from Arbetsförmedlingen's open JobTech API, published under CC0. No API key is needed.