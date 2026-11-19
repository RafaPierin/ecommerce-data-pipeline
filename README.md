# E-commerce Data Pipeline: API → Clean Data → SQL Models → Dashboard

An end-to-end analytics pipeline that turns messy e-commerce order data into a trusted sales dashboard. It extracts orders from a paginated REST API, cleans and validates them, builds SQL models, and feeds a dashboard that refreshes without anyone exporting a CSV.

![Dashboard](docs/dashboard.png)

> Runs out of the box with a mock API and synthetic data. Point it at a real API or BigQuery with one flag.

## The problem

Raw API data is rarely ready for reporting. In this project the source returns:

- **60 duplicate orders** repeated across pages
- **3 different date formats** in the same field
- Prices as text (`"$59.90"`) mixed with numbers
- The same country written 3 ways (`USA`, `us`, `United States`)
- Missing sales channels and discounts

Any of these silently breaks a revenue number. This pipeline fixes all of them before the data reaches the dashboard.

## How it works

```
Orders API ──► extract.py ──► transform.py ──► quality_checks.py ──► load.py ──► SQL models ──► Dashboard
 (paginated)    raw JSON       clean table      7 checks, stops       SQLite or     daily sales,    Looker Studio
                + retries                       the run on failure    BigQuery      products        or PNG preview
```

| Step | What it does |
| --- | --- |
| **Extract** | Pages through the API, retries with backoff on rate limits (HTTP 429) and network errors, saves raw JSON |
| **Transform** | Deduplicates, parses mixed dates to UTC, converts prices, standardizes countries and emails, calculates gross and net revenue |
| **Quality checks** | Uniqueness, nulls, positive prices, non-negative revenue, accepted values. The run stops if any check fails |
| **Load** | Writes the clean table and builds the SQL models in SQLite (local) or BigQuery |
| **Models** | `fct_daily_sales` (revenue, orders, AOV by day and channel) and `fct_product_performance` (revenue and refund rate by product) |
| **Dashboard** | KPI cards, weekly revenue trend, revenue by channel and product, refund rate |

## Results on the demo dataset

- 2,460 raw records → 2,400 clean rows (60 duplicates removed)
- 7 of 7 data quality checks passing
- 2 analytics models ready for BI tools

## Run it

```bash
pip install -r requirements.txt
python pipeline.py
```

The dashboard is saved to `docs/dashboard.png` and the warehouse to `data/warehouse.db`.

**With a real API:**

```bash
export ORDERS_API_KEY=your_key
python pipeline.py --api-url https://api.yourstore.com/orders
```

**With BigQuery** (uncomment the optional packages in `requirements.txt`):

```bash
export GOOGLE_APPLICATION_CREDENTIALS=service-account.json
python pipeline.py --target bigquery --dataset my_project.analytics
```

Then connect Looker Studio to `my_project.analytics.fct_daily_sales`.

## Project structure

```
├── pipeline.py              # Orchestrates the full run
├── src/
│   ├── mock_api.py          # Synthetic, intentionally messy Orders API
│   ├── extract.py           # Pagination, retries, raw storage
│   ├── transform.py         # Cleaning and standardization rules
│   ├── quality_checks.py    # Data tests
│   ├── load.py              # SQLite / BigQuery loaders and model builds
│   └── dashboard.py         # Dashboard preview
├── sql/
│   ├── fct_daily_sales.sql
│   └── fct_product_performance.sql
└── docs/dashboard.png
```

## Stack

Python · pandas · SQL · BigQuery · SQLite · REST APIs · Looker Studio · matplotlib

## About me

I'm Rafael, an Analytics Engineer from Brazil working in US time zones. I build data pipelines, automations and dashboards for businesses. At C6 Bank I built 50+ production pipelines in BigQuery.

[LinkedIn](https://linkedin.com/in/rafaelpierin) · [Fiverr](#) · pierinrafa@gmail.com
