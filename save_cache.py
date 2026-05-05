"""
Process raw Zapier API responses and save to local cache.
Run this after pulling data from Zapier.
"""
import json
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TODAY = str(date.today())


def save(name: str, days: int, rows: list[dict]):
    path = DATA_DIR / f"{name}_{days}d.json"
    path.write_text(json.dumps({"date": TODAY, "rows": rows}, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  {path.name}: {len(rows)} rows")


# ─── Google Ads Campaigns (30d) ───
campaigns_raw = [
    {"campaign_name": "[Search] - Noivas", "status": "ENABLED", "impressions": 10771, "clicks": 904,
     "ctr": 0.0839, "cpc": 1213608.697, "cost": 1097102262, "conversions": 59.0,
     "cost_per_conversion": 18595972.9, "search_impression_share": 0.2101,
     "search_budget_lost_impression_share": 0.0308, "search_rank_lost_impression_share": 0.7591,
     "top_impression_percentage": 0.7473, "absolute_top_impression_percentage": 0.4637},
    {"campaign_name": "[Search] - Institucional", "status": "ENABLED", "impressions": 929, "clicks": 196,
     "ctr": 0.2110, "cpc": 838382.929, "cost": 164323054, "conversions": 17.5,
     "cost_per_conversion": 9389888.8, "search_impression_share": 0.8514,
     "search_budget_lost_impression_share": 0.0163, "search_rank_lost_impression_share": 0.1322,
     "top_impression_percentage": 0.8063, "absolute_top_impression_percentage": 0.4660},
    {"campaign_name": "Pmax rmkt Noivas", "status": "ENABLED", "impressions": 29663, "clicks": 1580,
     "ctr": 0.0533, "cpc": 231276.623, "cost": 365417064, "conversions": 124.5,
     "cost_per_conversion": 2934763.589, "search_impression_share": 0.0999,
     "search_budget_lost_impression_share": 0.1535, "search_rank_lost_impression_share": 0.8178,
     "top_impression_percentage": None, "absolute_top_impression_percentage": None},
    {"campaign_name": "demand Gen - YT Retargeting", "status": "ENABLED", "impressions": 13653, "clicks": 824,
     "ctr": 0.0604, "cpc": 147133.343, "cost": 121237875, "conversions": 22.0,
     "cost_per_conversion": 5509168.013, "search_impression_share": None,
     "search_budget_lost_impression_share": None, "search_rank_lost_impression_share": None,
     "top_impression_percentage": None, "absolute_top_impression_percentage": None},
]

campaigns_parsed = []
for c in campaigns_raw:
    cost = c["cost"] / 1_000_000
    cpc = c["cpc"] / 1_000_000
    cpa = c["cost_per_conversion"] / 1_000_000 if c["cost_per_conversion"] else 0
    clicks = c["clicks"]
    convs = c["conversions"]
    campaigns_parsed.append({
        "Campaign": c["campaign_name"],
        "Status": c["status"],
        "Impressions": c["impressions"],
        "Clicks": clicks,
        "CTR (%)": round(c["ctr"] * 100, 2),
        "CPC (R$)": round(cpc, 2),
        "Cost (R$)": round(cost, 2),
        "Conversions": round(convs, 1),
        "Cost/Conv (R$)": round(cpa, 2),
        "Conv. Rate (%)": round((convs / clicks * 100) if clicks > 0 else 0, 2),
        "Impr. Share (%)": round(c["search_impression_share"] * 100, 1) if c["search_impression_share"] else None,
        "Lost IS Budget (%)": round(c["search_budget_lost_impression_share"] * 100, 1) if c["search_budget_lost_impression_share"] else None,
        "Lost IS Rank (%)": round(c["search_rank_lost_impression_share"] * 100, 1) if c["search_rank_lost_impression_share"] else None,
        "Top IS (%)": round(c["top_impression_percentage"] * 100, 1) if c["top_impression_percentage"] else None,
        "Abs. Top IS (%)": round(c["absolute_top_impression_percentage"] * 100, 1) if c["absolute_top_impression_percentage"] else None,
    })

save("campaigns", 30, campaigns_parsed)

# ─── Google Ads Ad Groups (30d) ───
adgroups_raw = [
    {"ad_group_name": "Vestido Casamento", "campaign_name": "[Search] - Noivas",
     "impressions": 10455, "clicks": 876, "ctr": 8.38, "cpc": 1.204, "cost": 1054.92,
     "conversions": 57.5, "cost_per_conversion": 18.35, "conversion_rate": 6.56},
    {"ad_group_name": "Branding", "campaign_name": "[Search] - Institucional",
     "impressions": 929, "clicks": 196, "ctr": 21.10, "cpc": 0.838, "cost": 164.32,
     "conversions": 17.5, "cost_per_conversion": 9.39, "conversion_rate": 8.93},
    {"ad_group_name": "Marcas Vestidos Noivas", "campaign_name": "[Search] - Noivas",
     "impressions": 316, "clicks": 28, "ctr": 8.86, "cpc": 1.507, "cost": 42.18,
     "conversions": 1.5, "cost_per_conversion": 28.12, "conversion_rate": 5.36},
    {"ad_group_name": "Noivas", "campaign_name": "demand Gen - YT Retargeting",
     "impressions": 4569, "clicks": 276, "ctr": 6.04, "cpc": 0.159, "cost": 43.88,
     "conversions": 8.0, "cost_per_conversion": 5.49, "conversion_rate": 2.90},
    {"ad_group_name": "Todos", "campaign_name": "demand Gen - YT Retargeting",
     "impressions": 9084, "clicks": 548, "ctr": 6.03, "cpc": 0.141, "cost": 77.36,
     "conversions": 14.0, "cost_per_conversion": 5.52, "conversion_rate": 2.56},
]

adgroups_parsed = []
for a in adgroups_raw:
    adgroups_parsed.append({
        "Ad Group": a["ad_group_name"],
        "Campaign": a["campaign_name"],
        "Impressions": a["impressions"],
        "Clicks": a["clicks"],
        "CTR (%)": round(a["ctr"], 2),
        "CPC (R$)": round(a["cpc"], 2),
        "Cost (R$)": round(a["cost"], 2),
        "Conversions": round(a["conversions"], 1),
        "Cost/Conv (R$)": round(a["cost_per_conversion"], 2),
        "Conv. Rate (%)": round(a["conversion_rate"], 2),
    })

save("adgroups", 30, adgroups_parsed)

# ─── GA4 Pages (30d) ───
ga4_pages_raw = [
    ["/vestidos-de-noivas", "2077", "1868", "173.63", "0"],
    ["/", "1234", "1130", "123.92", "0"],
    ["/15anos-teste", "197", "96", "125.20", "0"],
    ["/vestido-de-festas", "163", "160", "76.11", "0"],
    ["/blank-1", "10", "8", "179.22", "0"],
]

ga4_pages_parsed = []
for p in ga4_pages_raw:
    ga4_pages_parsed.append({
        "Page": p[0],
        "Pageviews": int(p[1]),
        "Avg. Session (s)": round(float(p[2])),
        "Conversions": round(float(p[4]), 1),
    })

save("ga4_pages", 30, ga4_pages_parsed)

# ─── GA4 Daily (30d) ───
ga4_daily_raw = [
    ["20260401", "204", "171", "133.48", "0", "164", "120", "0.7953", "0.2047"],
    ["20260402", "140", "108", "139.56", "0", "104", "60", "0.7130", "0.2870"],
    ["20260403", "129", "94", "100.83", "0", "90", "56", "0.6277", "0.3723"],
    ["20260404", "123", "98", "117.25", "0", "95", "62", "0.6735", "0.3265"],
    ["20260405", "130", "104", "170.28", "0", "101", "74", "0.7692", "0.2308"],
    ["20260406", "80", "61", "136.54", "0", "58", "32", "0.6721", "0.3279"],
    ["20260407", "115", "95", "195.50", "0", "88", "60", "0.7053", "0.2947"],
    ["20260408", "102", "84", "75.30", "0", "78", "56", "0.6786", "0.3214"],
    ["20260409", "136", "95", "135.42", "0", "89", "63", "0.6737", "0.3263"],
    ["20260410", "144", "109", "103.14", "0", "107", "75", "0.7339", "0.2661"],
    ["20260411", "110", "83", "148.30", "0", "77", "57", "0.7349", "0.2651"],
    ["20260412", "105", "70", "293.39", "0", "69", "47", "0.8000", "0.2000"],
    ["20260413", "132", "101", "86.28", "0", "97", "66", "0.7228", "0.2772"],
    ["20260414", "108", "78", "124.20", "0", "77", "53", "0.6923", "0.3077"],
    ["20260415", "102", "79", "86.15", "0", "69", "46", "0.7342", "0.2658"],
    ["20260416", "91", "70", "86.90", "0", "69", "51", "0.7429", "0.2571"],
    ["20260417", "75", "62", "519.46", "0", "59", "43", "0.6452", "0.3548"],
    ["20260418", "110", "84", "68.90", "0", "83", "67", "0.7619", "0.2381"],
    ["20260419", "116", "84", "1024.79", "0", "81", "57", "0.7500", "0.2500"],
    ["20260420", "111", "87", "182.94", "0", "80", "59", "0.7931", "0.2069"],
    ["20260421", "130", "71", "340.93", "0", "66", "48", "0.7465", "0.2535"],
    ["20260422", "107", "89", "98.44", "0", "86", "65", "0.7528", "0.2472"],
    ["20260423", "116", "70", "279.92", "0", "61", "37", "0.8714", "0.1286"],
    ["20260424", "89", "78", "75.51", "0", "77", "60", "0.6282", "0.3718"],
    ["20260425", "134", "97", "158.12", "0", "89", "62", "0.7526", "0.2474"],
    ["20260426", "94", "71", "166.88", "0", "66", "38", "0.6761", "0.3239"],
    ["20260427", "156", "120", "123.73", "0", "112", "75", "0.7000", "0.3000"],
    ["20260428", "146", "120", "99.83", "0", "109", "62", "0.6333", "0.3667"],
    ["20260429", "177", "134", "157.13", "0", "125", "85", "0.6045", "0.3955"],
    ["20260430", "169", "123", "149.87", "0", "117", "79", "0.7724", "0.2276"],
]

ga4_daily_parsed = []
for d in ga4_daily_raw:
    dt = d[0]
    ga4_daily_parsed.append({
        "Date": f"{dt[:4]}-{dt[4:6]}-{dt[6:8]}",
        "Pageviews": int(d[1]),
        "Sessions": int(d[2]),
        "Avg. Session (s)": round(float(d[3]), 1),
        "Conversions": round(float(d[4]), 1),
        "Users": int(d[5]),
        "New Users": int(d[6]),
        "Engagement Rate (%)": round(float(d[7]) * 100, 1),
        "Bounce Rate (%)": round(float(d[8]) * 100, 1),
    })

save("ga4_daily", 30, ga4_daily_parsed)

# ─── GA4 Channels (30d) ───
ga4_channels_raw = [
    ["Paid Search", "1456", "1269", "0", "0.6916", "133.33"],
    ["Cross-network", "745", "617", "0", "0.7235", "278.80"],
    ["Direct", "444", "428", "0", "0.8446", "86.58"],
    ["Organic Search", "103", "86", "0", "0.6796", "144.83"],
    ["Unassigned", "29", "27", "0", "0.0690", "1001.73"],
    ["Referral", "8", "4", "0", "0.7500", "672.23"],
    ["Organic Social", "4", "3", "0", "0.7500", "91.13"],
]

ga4_channels_parsed = []
for ch in ga4_channels_raw:
    ga4_channels_parsed.append({
        "Channel": ch[0],
        "Sessions": int(ch[1]),
        "Users": int(ch[2]),
        "Conversions": round(float(ch[3]), 1),
        "Engagement Rate (%)": round(float(ch[4]) * 100, 1),
        "Avg. Session (s)": round(float(ch[5]), 1),
    })

save("ga4_channels", 30, ga4_channels_parsed)

print("\nDone! All 30-day data cached.")
