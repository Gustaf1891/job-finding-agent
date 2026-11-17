import sqlite3

db = sqlite3.connect("data/jobs.db")

total, distinct = db.execute("SELECT count(*), count(DISTINCT source_id) FROM jobs").fetchone()
print(f"rows={total} distinct_ids={distinct}")

for row in db.execute("SELECT title, employer, municipality, deadline FROM jobs LIMIT 5"):
    print(row)

# How many NULLs per column
cols = [r[1] for r in db.execute("PRAGMA table_info(jobs)")]
for c in cols:
    n = db.execute(f"SELECT count(*) FROM jobs WHERE {c} IS NULL").fetchone()[0]
    print(f"{c:20} NULL: {n}/{total}")
