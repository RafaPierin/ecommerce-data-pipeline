"""Run the full pipeline: extract -> transform -> quality checks -> load -> dashboard.

Usage:
    python pipeline.py                                  # mock API, local SQLite
    python pipeline.py --api-url https://.../orders     # real API
    python pipeline.py --target bigquery --dataset my_project.analytics
"""
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dashboard import render  # noqa: E402
from extract import extract  # noqa: E402
from load import load_bigquery, load_sqlite  # noqa: E402
from quality_checks import run_checks  # noqa: E402
from transform import transform  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("pipeline")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default=None, help="Orders API endpoint (default: mock API)")
    parser.add_argument("--target", choices=["sqlite", "bigquery"], default="sqlite")
    parser.add_argument("--dataset", default=None, help="BigQuery dataset, e.g. project.analytics")
    args = parser.parse_args()

    raw = extract(args.api_url)
    clean = transform(raw)
    checks = run_checks(clean)
    log.info("All %s data quality checks passed", len(checks))

    if args.target == "bigquery":
        load_bigquery(clean, args.dataset)
        log.info("Loaded to BigQuery. Connect Looker Studio to %s.fct_daily_sales", args.dataset)
    else:
        models = load_sqlite(clean)
        path = render(models)
        log.info("Dashboard saved to %s", path)


if __name__ == "__main__":
    main()
