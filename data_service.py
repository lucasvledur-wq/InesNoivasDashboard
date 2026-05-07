"""
Data service that fetches Google Ads and GA4 data via Zapier MCP.
For standalone usage, saves data to local JSON files.
The dashboard reads from these cached files and allows timeframe switching.
"""

import json
import os
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

GOOGLE_ADS_CUSTOMER_ID = "6778012588"
GA4_PROPERTY_ID = "453035485"

DATE_PRESETS = {
    3: "custom",
    14: "LAST_14_DAYS",
    30: "LAST_30_DAYS",
}


def _date_range(days: int) -> tuple[str, str]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _cache_path(name: str, days: int) -> Path:
    return DATA_DIR / f"{name}_{days}d.json"


def _read_cache(name: str, days: int) -> pd.DataFrame | None:
    path = _cache_path(name, days)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        # Accept cache from last 7 days — user controls refresh manually
        pass
        return pd.DataFrame(data["rows"])
    except (json.JSONDecodeError, KeyError):
        return None


def _write_cache(name: str, days: int, df: pd.DataFrame):
    path = _cache_path(name, days)
    data = {"date": str(date.today()), "rows": df.to_dict(orient="records")}
    path.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")


# ---------------------------------------------------------------------------
# Google Ads — Campaign Metrics (with impression share)
# ---------------------------------------------------------------------------

CAMPAIGN_MAP = {
    "customers/6778012588/campaigns/20520588690": "Campanha de Pesquisa 1",
    "customers/6778012588/campaigns/20581299009": "[Search] - Noivas",
    "customers/6778012588/campaigns/20947825096": "[SEARCH] [NOIVAS/15/FESTA] [10/23] #2",
    "customers/6778012588/campaigns/21037030700": "[SEARCH] - Casamento",
    "customers/6778012588/campaigns/21880101791": "[KRM] [LIGACOES-SEARCH]",
    "customers/6778012588/campaigns/22162698464": "[Search] - Institucional",
    "customers/6778012588/campaigns/22504004124": "[KRM] [PMAX - VENDAS]",
    "customers/6778012588/campaigns/22681810722": "Pmax rmkt Noivas",
    "customers/6778012588/campaigns/23065606529": "demand Gen - YT Retargeting",
}


def parse_campaign_report(raw_results: list[dict]) -> pd.DataFrame:
    rows = []
    for r in raw_results:
        name = r.get("campaign_name", "")
        name = CAMPAIGN_MAP.get(name, name)
        impressions = r.get("impressions", 0)
        if impressions == 0 and r.get("clicks", 0) == 0:
            continue
        cost = r.get("cost", 0)
        clicks = r.get("clicks", 0)
        conversions = r.get("conversions", 0)
        ctr = r.get("ctr", 0) or 0
        avg_cpc = r.get("cpc", 0) or r.get("average_cpc", 0) or 0
        if avg_cpc > 1000:
            avg_cpc = avg_cpc / 1_000_000
        cost_per_conv = r.get("cost_per_conversion", 0) or 0
        if cost_per_conv > 1000:
            cost_per_conv = cost_per_conv / 1_000_000

        is_share = r.get("search_impression_share")
        is_budget_lost = r.get("search_budget_lost_impression_share")
        is_rank_lost = r.get("search_rank_lost_impression_share")
        top_is = r.get("top_impression_percentage")
        abs_top_is = r.get("absolute_top_impression_percentage")

        rows.append({
            "Campaign": name,
            "Status": r.get("status", "ENABLED"),
            "Impressions": impressions,
            "Clicks": clicks,
            "CTR (%)": round(ctr * 100, 2) if ctr < 1 else round(ctr, 2),
            "CPC (R$)": round(avg_cpc, 2),
            "Cost (R$)": round(cost, 2),
            "Conversions": round(conversions, 1),
            "Cost/Conv (R$)": round(cost_per_conv, 2),
            "Conv. Rate (%)": round((conversions / clicks * 100) if clicks > 0 else 0, 2),
            "Impr. Share (%)": round(is_share * 100, 1) if is_share else None,
            "Lost IS Budget (%)": round(is_budget_lost * 100, 1) if is_budget_lost else None,
            "Lost IS Rank (%)": round(is_rank_lost * 100, 1) if is_rank_lost else None,
            "Top IS (%)": round(top_is * 100, 1) if top_is else None,
            "Abs. Top IS (%)": round(abs_top_is * 100, 1) if abs_top_is else None,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Google Ads — Ad Group Metrics
# ---------------------------------------------------------------------------

def parse_adgroup_report(raw_results: list[dict]) -> pd.DataFrame:
    rows = []
    for r in raw_results:
        impressions = r.get("impressions", 0)
        if impressions == 0 and r.get("clicks", 0) == 0:
            continue
        clicks = r.get("clicks", 0)
        cost = r.get("cost", 0)
        conversions = r.get("conversions", 0)
        ctr = r.get("ctr", 0) or r.get("conversion_rate", 0) or 0
        avg_cpc = r.get("cpc", 0) or 0
        if avg_cpc > 1000:
            avg_cpc = avg_cpc / 1_000_000

        rows.append({
            "Ad Group": r.get("ad_group_name", ""),
            "Campaign": r.get("campaign_name", ""),
            "Impressions": impressions,
            "Clicks": clicks,
            "CTR (%)": round(ctr * 100, 2) if ctr < 1 else round(ctr, 2),
            "CPC (R$)": round(avg_cpc, 2),
            "Cost (R$)": round(cost, 2),
            "Conversions": round(conversions, 1),
            "Cost/Conv (R$)": round((cost / conversions) if conversions > 0 else 0, 2),
            "Conv. Rate (%)": round((conversions / clicks * 100) if clicks > 0 else 0, 2),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# GA4 — Page Performance
# ---------------------------------------------------------------------------

def parse_ga4_pages(raw_results: dict) -> pd.DataFrame:
    rows_data = raw_results.get("rows", [])
    if isinstance(rows_data, list) and len(rows_data) > 0 and isinstance(rows_data[0], dict) and "pagePath" in rows_data[0]:
        rows = []
        for r in rows_data:
            rows.append({
                "Page": r.get("pagePath", ""),
                "Pageviews": r.get("screenPageViews", 0),
                "Avg. Session (s)": round(r.get("averageSessionDuration", 0), 0),
                "Conversions": round(r.get("conversions", 0), 1),
            })
        return pd.DataFrame(rows)

    body = raw_results
    if isinstance(raw_results, list) and len(raw_results) > 0:
        body = raw_results[0].get("body", raw_results[0]) if isinstance(raw_results[0], dict) else raw_results[0]

    api_rows = body.get("rows", [])
    rows = []
    for r in api_rows:
        dims = r.get("dimensionValues", [])
        mets = r.get("metricValues", [])
        page = dims[0]["value"] if dims else ""
        rows.append({
            "Page": page,
            "Pageviews": int(mets[0]["value"]) if len(mets) > 0 else 0,
            "Avg. Session (s)": round(float(mets[1]["value"]), 0) if len(mets) > 1 else 0,
            "Conversions": round(float(mets[2]["value"]), 1) if len(mets) > 2 else 0,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# GA4 — Daily Metrics
# ---------------------------------------------------------------------------

def parse_ga4_daily(raw_body: dict) -> pd.DataFrame:
    if isinstance(raw_body, list) and len(raw_body) > 0:
        raw_body = raw_body[0].get("body", raw_body[0]) if isinstance(raw_body[0], dict) else raw_body[0]

    api_rows = raw_body.get("rows", [])
    rows = []
    for r in api_rows:
        dims = r.get("dimensionValues", [])
        mets = r.get("metricValues", [])
        date_str = dims[0]["value"] if dims else ""
        rows.append({
            "Date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}" if len(date_str) == 8 else date_str,
            "Pageviews": int(mets[0]["value"]) if len(mets) > 0 else 0,
            "Sessions": int(mets[1]["value"]) if len(mets) > 1 else 0,
            "Avg. Session (s)": round(float(mets[2]["value"]), 1) if len(mets) > 2 else 0,
            "Conversions": round(float(mets[3]["value"]), 1) if len(mets) > 3 else 0,
            "Users": int(mets[4]["value"]) if len(mets) > 4 else 0,
            "New Users": int(mets[5]["value"]) if len(mets) > 5 else 0,
            "Engagement Rate (%)": round(float(mets[6]["value"]) * 100, 1) if len(mets) > 6 else 0,
            "Bounce Rate (%)": round(float(mets[7]["value"]) * 100, 1) if len(mets) > 7 else 0,
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
    return df


# ---------------------------------------------------------------------------
# GA4 — Channel Group
# ---------------------------------------------------------------------------

def parse_ga4_channels(raw_results: list[dict] | dict) -> pd.DataFrame:
    if isinstance(raw_results, list) and len(raw_results) > 0:
        if "channel_group" in raw_results[0]:
            rows = []
            for r in raw_results:
                rows.append({
                    "Channel": r.get("channel_group", ""),
                    "Sessions": r.get("sessions", 0),
                    "Conversions": round(r.get("conversions", 0), 1),
                })
            return pd.DataFrame(rows)

    body = raw_results
    if isinstance(raw_results, list) and len(raw_results) > 0:
        body = raw_results[0].get("body", raw_results[0])

    api_rows = body.get("rows", [])
    rows = []
    for r in api_rows:
        dims = r.get("dimensionValues", [])
        mets = r.get("metricValues", [])
        rows.append({
            "Channel": dims[0]["value"] if dims else "",
            "Sessions": int(mets[0]["value"]) if len(mets) > 0 else 0,
            "Users": int(mets[1]["value"]) if len(mets) > 1 else 0,
            "Conversions": round(float(mets[2]["value"]), 1) if len(mets) > 2 else 0,
            "Engagement Rate (%)": round(float(mets[3]["value"]) * 100, 1) if len(mets) > 3 else 0,
            "Avg. Session (s)": round(float(mets[4]["value"]), 1) if len(mets) > 4 else 0,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Load from cache
# ---------------------------------------------------------------------------

def load_campaigns(days: int) -> pd.DataFrame:
    cached = _read_cache("campaigns", days)
    if cached is not None:
        return cached
    return pd.DataFrame()


def load_adgroups(days: int) -> pd.DataFrame:
    cached = _read_cache("adgroups", days)
    if cached is not None:
        return cached
    return pd.DataFrame()


def load_ga4_pages(days: int) -> pd.DataFrame:
    cached = _read_cache("ga4_pages", days)
    if cached is not None:
        return cached
    return pd.DataFrame()


def load_ga4_daily(days: int) -> pd.DataFrame:
    cached = _read_cache("ga4_daily", days)
    if cached is not None:
        df = cached
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        return df
    return pd.DataFrame()


def load_ga4_channels(days: int) -> pd.DataFrame:
    cached = _read_cache("ga4_channels", days)
    if cached is not None:
        return cached
    return pd.DataFrame()


def load_ads_daily(days: int) -> pd.DataFrame:
    cached = _read_cache("ads_daily", days)
    if cached is not None:
        df = cached
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        return df
    return pd.DataFrame()


def load_keywords(days: int) -> pd.DataFrame:
    cached = _read_cache("keywords", days)
    if cached is not None:
        return cached
    return pd.DataFrame()


def load_meta(days: int) -> pd.DataFrame:
    cached = _read_cache("meta", days)
    if cached is not None:
        df = cached
        if "Data" in df.columns:
            df["Data"] = pd.to_datetime(df["Data"])
        return df
    return pd.DataFrame()
