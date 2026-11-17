import sqlite3
from pathlib import Path
from job_finding_agent.models import JobPosting

COLUMNS = list(JobPosting.model_fields)

class Store:
    def __init__(self, path: str = 'data/jobs.db'):
        Path(path).parent.mkdir(parents=True, exist_ok=True) # Make sure Path exists and connect to (open/create) jobs.db file
        self.db = sqlite3.connect(path)
        cols = ", ".join(c for c in COLUMNS) # Build a table using Jobposting fields, set primary key to source, source_id where source is Arbetsförmedlingen and source_id is listing id
        self.db.execute(
            f"CREATE TABLE IF NOT EXISTS jobs ({cols}, PRIMARY KEY (source, source_id))"
        )

    def filter_new(self, jobs: list[JobPosting]) -> list[JobPosting]:
        """
        Takes a fresh batch of scraped JobPosting objects and removes previous seen ones. Checks in memory duplicates using seen set and catches duplicates in database using
        SQL check. 
        """
        seen, new = set(), []
        for j in jobs:
            key = (j.source, j.source_id)

            if key in seen:
                continue
            seen.add(key)
            row = self.db.execute(
                "SELECT 1 FROM jobs WHERE source=? AND source_id=?", key, # using ? and key checks current (source, source_id) pair
            ).fetchone()
            if not row:
                new.append(j)
        return new

    def save(self, jobs: list[JobPosting]) -> None:
        """
        Saves new jobs to database. Convert each posting into JSON format, ignore rows violating primary key, and insert remaining rows to database. 
        """
        placeholders = ", ".join("?" for _ in COLUMNS)
        rows = []
        for j in jobs:
            d = j.model_dump(mode="json") # Convert each jobposting into JSON, datetime -> ISO strings
            rows.append([d[c] for c in COLUMNS])
        self.db.executemany(
            f"INSERT OR IGNORE INTO jobs ({', '.join(COLUMNS)}) VALUES ({placeholders})", rows, # Insert all rows at once, ignore rows that violate the (source, source_id) primary key 
            )
        self.db.commit() 