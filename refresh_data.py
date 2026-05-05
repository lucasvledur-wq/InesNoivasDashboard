"""
Refresh data script — run this manually or via scheduled task.
Pulls data from Google Ads and GA4 via Zapier MCP and saves to local cache.

When run from Claude Code, it uses the Zapier MCP tools.
Can also be triggered via: python refresh_data.py
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

GA4_PROPERTY_ID = "453035485"


def _date_range(days: int) -> tuple[str, str]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def save_cache(name: str, days: int, rows: list[dict]):
    path = DATA_DIR / f"{name}_{days}d.json"
    data = {"date": str(date.today()), "rows": rows}
    path.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  Saved {len(rows)} rows -> {path.name}")


def ga4_report_body(days: int, dimensions: list[str], metrics: list[str],
                    limit: int = 100, order_by_dim: str | None = None) -> str:
    start, end = _date_range(days)
    body: dict = {
        "dateRanges": [{"startDate": start, "endDate": end}],
        "dimensions": [{"name": d} for d in dimensions],
        "metrics": [{"name": m} for m in metrics],
        "limit": limit,
    }
    if order_by_dim:
        body["orderBys"] = [{"dimension": {"dimensionName": order_by_dim}}]
    return json.dumps(body)


def print_instructions():
    print("""
=== Instruções de Refresh via Claude Code ===

Cole os comandos abaixo no Claude Code para atualizar os dados.
Cada período (7, 14, 30, 90 dias) precisa de chamadas separadas.

--- GOOGLE ADS: Campaign Report ---
Use: execute_zapier_write_action
App: Google Ads | Action: create_report
Params: resource=campaign, datePreset=LAST_30_DAYS, limit=50
Instructions: Include search_impression_share, search_budget_lost_impression_share,
  search_rank_lost_impression_share, top_impression_percentage,
  absolute_top_impression_percentage plus standard metrics.

--- GOOGLE ADS: Ad Group Report ---
Use: execute_zapier_write_action
App: Google Ads | Action: create_report
Params: resource=ad_group, datePreset=LAST_30_DAYS, limit=50

--- GA4: Page Performance ---
POST to: https://analyticsdata.googleapis.com/v1beta/properties/453035485:runReport
""")

    for days in [7, 14, 30, 90]:
        start, end = _date_range(days)
        print(f"\n  [{days}d] startDate={start}, endDate={end}")

    print(f"""
Body dimensions: pagePath
Body metrics: screenPageViews, sessions, averageSessionDuration, conversions

--- GA4: Daily Metrics ---
Body dimensions: date
Body metrics: screenPageViews, sessions, averageSessionDuration, conversions,
  totalUsers, newUsers, engagementRate, bounceRate

--- GA4: Channel Groups ---
Body dimensions: sessionDefaultChannelGroup
Body metrics: sessions, totalUsers, conversions, engagementRate, averageSessionDuration
""")


if __name__ == "__main__":
    print_instructions()
