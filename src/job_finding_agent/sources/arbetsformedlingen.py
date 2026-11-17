import logging
import httpx
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
from job_finding_agent.models import JobPosting

log  = logging.getLogger(__name__)
BASE = "https://jobsearch.api.jobtechdev.se/search"

FIELD_MAP = {
    "id": "source_id",
    "webpage_url": "url",
    "headline": "title",
    "publication_date": "published",
    "last_publication_date": "last_published",
    "application_deadline": "deadline",
    "removed": "removed",
    "description.text": "description",
    "employment_type.label": "employment_type",
    "duration.label": "duration",
    "working_hours_type.label": "working_hours",
    "salary_type.label": "salary_type",
    "occupation.label": "occupation",
    "employer.name": "employer",
    "employer.url": "employer_url",
    "application_details.url": "apply_url",
    "workplace_address.municipality": "municipality",
}

@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=1, max=20), reraise=True)
def _get(client: httpx.Client, params: dict) -> dict:
    r = client.get(BASE, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def _dig(obj: dict, path: str):
    """Follow 'a.b.c' through nested dicts; return None if any step is missing/None."""
    for key in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _parse(hit: dict) -> JobPosting:
    data = {field: _dig(hit, path) for path, field in FIELD_MAP.items()}
    data["source_id"] = str(data["source_id"])
    data = {k: v for k, v in data.items() if v is not None} # Drop Nones so model defaults apply (e.g. removed=False, description="")
    return JobPosting(**data)

def fetch(query: str, limit: int, lookback_days: int, municipality_ids=None) -> list[JobPosting]:
    since = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%S")
    jobs: list[JobPosting] = []
    offset = 0
    with httpx.Client() as client:
        while len(jobs) < limit:
            page = min(100, limit - len(jobs))
            params = {"q": query, "limit": page, "offset": offset, "published-after": since}
            if municipality_ids:
                params["municipality"] = municipality_ids   # repeated key per ID

            data = _get(client, params)
            total = (data.get("total") or {}).get("value", 0)
            log.info("query=%r offset=%d total=%d api_ms=%s result_ms=%s",
                     query, offset, total,
                     data.get("query_time_in_millis"), data.get("result_time_in_millis"))
            hits = data.get("hits", [])

            for h in hits:
                try:
                    jobs.append(_parse(h))
                except Exception:
                    log.exception("failed to parse hit id=%s", h.get("id"))

            offset += page
            if not hits or offset >= total:
                break
    return jobs
