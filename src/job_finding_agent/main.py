import logging 
import yaml
from job_finding_agent.sources.arbetsformedlingen import fetch
from job_finding_agent.store import Store

log = logging.getLogger("jobagent")

def cli() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = yaml.safe_load(open("config.yaml"))
    store = Store()

    all_jobs = []
    muni_ids = [m["id"] for m in cfg.get("municipalities", [])]
    log.info("municipalities=%s", [m["name"] for m in cfg.get("municipalities", [])] or "all")

    for role in cfg["roles"]:
        try:
            all_jobs += fetch(role, cfg["max_jobs_per_run"], cfg["lookback_days"], muni_ids)
        except Exception:
            log.exception("fetch failed for role=%r, continuing...", role)

    new = store.filter_new(all_jobs)[: cfg["max_jobs_per_run"]]
    store.save(new)
    log.info("fetched=%d new=%d", len(all_jobs), len(new))

    for j in new:
        print(f"- {j.title} @ {j.employer} ({j.municipality})\n {j.url}")

if __name__ == "__main__":
    cli()