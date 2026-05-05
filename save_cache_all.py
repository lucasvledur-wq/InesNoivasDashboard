"""
Save all periods (7, 14, 30, 90 days) cache files from Zapier API data.
"""
import json
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TODAY = str(date.today())


def save(name, days, rows):
    path = DATA_DIR / f"{name}_{days}d.json"
    path.write_text(json.dumps({"date": TODAY, "rows": rows}, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  {path.name}: {len(rows)} rows")


def parse_campaign(c):
    cost_raw = c["cost"]
    cost = cost_raw / 1_000_000 if cost_raw > 10000 else cost_raw
    cpc_raw = c["cpc"]
    cpc = cpc_raw / 1_000_000 if cpc_raw > 10000 else cpc_raw
    cpa_raw = c.get("cost_per_conversion") or 0
    cpa = cpa_raw / 1_000_000 if cpa_raw > 10000 else cpa_raw
    clicks = c["clicks"]
    convs = c["conversions"]
    return {
        "Campaign": c["campaign_name"], "Status": c.get("status", "ENABLED"),
        "Impressions": c["impressions"], "Clicks": clicks,
        "CTR (%)": round(c["ctr"] * 100, 2) if c["ctr"] and c["ctr"] < 1 else round(c.get("ctr", 0) or 0, 2),
        "CPC (R$)": round(cpc, 2), "Cost (R$)": round(cost, 2),
        "Conversions": round(convs, 1),
        "Cost/Conv (R$)": round(cpa, 2),
        "Conv. Rate (%)": round((convs / clicks * 100) if clicks > 0 else 0, 2),
        "Impr. Share (%)": round(c["search_impression_share"] * 100, 1) if c.get("search_impression_share") else None,
        "Lost IS Budget (%)": round(c["search_budget_lost_impression_share"] * 100, 1) if c.get("search_budget_lost_impression_share") else None,
        "Lost IS Rank (%)": round(c["search_rank_lost_impression_share"] * 100, 1) if c.get("search_rank_lost_impression_share") else None,
        "Top IS (%)": round(c["top_impression_percentage"] * 100, 1) if c.get("top_impression_percentage") else None,
        "Abs. Top IS (%)": round(c["absolute_top_impression_percentage"] * 100, 1) if c.get("absolute_top_impression_percentage") else None,
    }


def parse_adgroup(a):
    cpc = a["cpc"]
    if cpc > 1000: cpc = cpc / 1_000_000
    cost = a["cost"]
    if cost > 100000: cost = cost / 1_000_000
    cpa = a.get("cost_per_conversion", 0)
    if cpa > 1000: cpa = cpa / 1_000_000
    return {
        "Ad Group": a["ad_group_name"], "Campaign": a["campaign_name"],
        "Impressions": a["impressions"], "Clicks": a["clicks"],
        "CTR (%)": round(a["ctr"], 2),
        "CPC (R$)": round(cpc, 2), "Cost (R$)": round(cost, 2),
        "Conversions": round(a["conversions"], 1),
        "Cost/Conv (R$)": round(cpa, 2),
        "Conv. Rate (%)": round((a["conversions"] / a["clicks"] * 100) if a["clicks"] > 0 else 0, 2),
    }


def parse_ga4_daily_row(d):
    dims = d.get("dimensionValues", [])
    mets = d.get("metricValues", [])
    dt = dims[0]["value"] if dims else ""
    m = [m["value"] for m in mets]
    return {
        "Date": f"{dt[:4]}-{dt[4:6]}-{dt[6:8]}" if len(dt) == 8 else dt,
        "Pageviews": int(m[0]), "Sessions": int(m[1]),
        "Avg. Session (s)": round(float(m[2]), 1),
        "Conversions": round(float(m[3]), 1),
        "Users": int(m[4]), "New Users": int(m[5]),
        "Engagement Rate (%)": round(float(m[6]) * 100, 1),
        "Bounce Rate (%)": round(float(m[7]) * 100, 1),
    }


def parse_ga4_page_row(r):
    dims = r.get("dimensionValues", [])
    mets = r.get("metricValues", [])
    m = [x["value"] for x in mets]
    return {
        "Page": dims[0]["value"] if dims else "",
        "Pageviews": int(m[0]),
        "Avg. Session (s)": round(float(m[1])),
        "Conversions": round(float(m[3]), 1) if len(m) > 3 else 0,
    }


def parse_ga4_channel_row(r):
    dims = r.get("dimensionValues", [])
    mets = r.get("metricValues", [])
    m = [x["value"] for x in mets]
    return {
        "Channel": dims[0]["value"] if dims else "",
        "Sessions": int(m[0]), "Users": int(m[1]),
        "Conversions": round(float(m[2]), 1),
        "Engagement Rate (%)": round(float(m[3]) * 100, 1),
        "Avg. Session (s)": round(float(m[4]), 1),
    }


# ═══════════════════════════════════════════
# 30 DAYS (already have from save_cache.py — re-save for consistency)
# ═══════════════════════════════════════════
print("=== 30 DAYS ===")

c30 = [
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
     "search_budget_lost_impression_share": 0.1535, "search_rank_lost_impression_share": 0.8178},
    {"campaign_name": "demand Gen - YT Retargeting", "status": "ENABLED", "impressions": 13653, "clicks": 824,
     "ctr": 0.0604, "cpc": 147133.343, "cost": 121237875, "conversions": 22.0,
     "cost_per_conversion": 5509168.013},
]
save("campaigns", 30, [parse_campaign(c) for c in c30])

ag30 = [
    {"ad_group_name": "Vestido Casamento", "campaign_name": "[Search] - Noivas",
     "impressions": 10455, "clicks": 876, "ctr": 8.38, "cpc": 1.204, "cost": 1054.92, "conversions": 57.5, "cost_per_conversion": 18.35},
    {"ad_group_name": "Branding", "campaign_name": "[Search] - Institucional",
     "impressions": 929, "clicks": 196, "ctr": 21.10, "cpc": 0.838, "cost": 164.32, "conversions": 17.5, "cost_per_conversion": 9.39},
    {"ad_group_name": "Marcas Vestidos Noivas", "campaign_name": "[Search] - Noivas",
     "impressions": 316, "clicks": 28, "ctr": 8.86, "cpc": 1.507, "cost": 42.18, "conversions": 1.5, "cost_per_conversion": 28.12},
    {"ad_group_name": "Noivas", "campaign_name": "demand Gen - YT Retargeting",
     "impressions": 4569, "clicks": 276, "ctr": 6.04, "cpc": 0.159, "cost": 43.88, "conversions": 8.0, "cost_per_conversion": 5.49},
    {"ad_group_name": "Todos", "campaign_name": "demand Gen - YT Retargeting",
     "impressions": 9084, "clicks": 548, "ctr": 6.03, "cpc": 0.141, "cost": 77.36, "conversions": 14.0, "cost_per_conversion": 5.52},
]
save("adgroups", 30, [parse_adgroup(a) for a in ag30])

# GA4 30d — reuse from save_cache.py (already saved)

# ═══════════════════════════════════════════
# 7 DAYS
# ═══════════════════════════════════════════
print("\n=== 7 DAYS ===")

c7 = [
    {"campaign_name": "[Search] - Noivas", "status": "ENABLED", "impressions": 2265, "clicks": 172,
     "ctr": 0.0759, "cpc": 1228684.355, "cost": 211333709, "conversions": 16,
     "cost_per_conversion": 13208356.8, "search_impression_share": 0.2170,
     "search_budget_lost_impression_share": 0, "search_rank_lost_impression_share": 0.7830,
     "top_impression_percentage": 0.7313, "absolute_top_impression_percentage": 0.4366},
    {"campaign_name": "[Search] - Institucional", "status": "ENABLED", "impressions": 247, "clicks": 55,
     "ctr": 0.2227, "cpc": 699988.291, "cost": 38499356, "conversions": 5,
     "cost_per_conversion": 7699871.2, "search_impression_share": 0.8778,
     "search_budget_lost_impression_share": 0, "search_rank_lost_impression_share": 0.1222,
     "top_impression_percentage": 0.8228, "absolute_top_impression_percentage": 0.3924},
    {"campaign_name": "Pmax rmkt Noivas", "status": "ENABLED", "impressions": 6271, "clicks": 337,
     "ctr": 0.0537, "cpc": 212744.496, "cost": 71694895, "conversions": 25.0,
     "cost_per_conversion": 2868128.503, "search_impression_share": 0.0999,
     "search_budget_lost_impression_share": 0.122, "search_rank_lost_impression_share": 0.846},
    {"campaign_name": "demand Gen - YT Retargeting", "status": "ENABLED", "impressions": 7317, "clicks": 412,
     "ctr": 0.0563, "cpc": 162878.903, "cost": 67106108, "conversions": 11.0,
     "cost_per_conversion": 6101719.037},
]
save("campaigns", 7, [parse_campaign(c) for c in c7])

ag7 = [
    {"ad_group_name": "Vestido Casamento", "campaign_name": "[Search] - Noivas",
     "impressions": 2201, "clicks": 167, "ctr": 7.59, "cpc": 1.225, "cost": 204.59, "conversions": 15, "cost_per_conversion": 13.64},
    {"ad_group_name": "Branding", "campaign_name": "[Search] - Institucional",
     "impressions": 247, "clicks": 55, "ctr": 22.27, "cpc": 0.700, "cost": 38.50, "conversions": 5, "cost_per_conversion": 7.70},
    {"ad_group_name": "Marcas Vestidos Noivas", "campaign_name": "[Search] - Noivas",
     "impressions": 64, "clicks": 5, "ctr": 7.81, "cpc": 1.349, "cost": 6.75, "conversions": 1, "cost_per_conversion": 6.75},
    {"ad_group_name": "Noivas", "campaign_name": "demand Gen - YT Retargeting",
     "impressions": 2763, "clicks": 153, "ctr": 5.54, "cpc": 0.164, "cost": 25.11, "conversions": 3.0, "cost_per_conversion": 8.36},
    {"ad_group_name": "Todos", "campaign_name": "demand Gen - YT Retargeting",
     "impressions": 4554, "clicks": 259, "ctr": 5.69, "cpc": 0.162, "cost": 42.00, "conversions": 8.0, "cost_per_conversion": 5.25},
]
save("adgroups", 7, [parse_adgroup(a) for a in ag7])

# GA4 7d daily
ga4_daily_7d = [
    {"dimensionValues": [{"value": "20260424"}], "metricValues": [{"value":"89"},{"value":"78"},{"value":"75.51"},{"value":"0"},{"value":"77"},{"value":"60"},{"value":"0.6282"},{"value":"0.3718"}]},
    {"dimensionValues": [{"value": "20260425"}], "metricValues": [{"value":"134"},{"value":"97"},{"value":"158.12"},{"value":"0"},{"value":"89"},{"value":"62"},{"value":"0.7526"},{"value":"0.2474"}]},
    {"dimensionValues": [{"value": "20260426"}], "metricValues": [{"value":"94"},{"value":"71"},{"value":"166.88"},{"value":"0"},{"value":"66"},{"value":"38"},{"value":"0.6761"},{"value":"0.3239"}]},
    {"dimensionValues": [{"value": "20260427"}], "metricValues": [{"value":"156"},{"value":"120"},{"value":"123.73"},{"value":"0"},{"value":"112"},{"value":"75"},{"value":"0.7000"},{"value":"0.3000"}]},
    {"dimensionValues": [{"value": "20260428"}], "metricValues": [{"value":"146"},{"value":"120"},{"value":"99.83"},{"value":"0"},{"value":"109"},{"value":"62"},{"value":"0.6333"},{"value":"0.3667"}]},
    {"dimensionValues": [{"value": "20260429"}], "metricValues": [{"value":"177"},{"value":"134"},{"value":"157.13"},{"value":"0"},{"value":"125"},{"value":"85"},{"value":"0.6045"},{"value":"0.3955"}]},
    {"dimensionValues": [{"value": "20260430"}], "metricValues": [{"value":"169"},{"value":"123"},{"value":"149.87"},{"value":"0"},{"value":"117"},{"value":"79"},{"value":"0.7724"},{"value":"0.2276"}]},
]
save("ga4_daily", 7, [parse_ga4_daily_row(r) for r in ga4_daily_7d])

# GA4 7d pages
ga4_pages_7d = [
    {"dimensionValues": [{"value": "/vestidos-de-noivas"}], "metricValues": [{"value":"528"},{"value":"453"},{"value":"108.33"},{"value":"0"}]},
    {"dimensionValues": [{"value": "/"}], "metricValues": [{"value":"363"},{"value":"338"},{"value":"135.86"},{"value":"0"}]},
    {"dimensionValues": [{"value": "/vestido-de-festas"}], "metricValues": [{"value":"39"},{"value":"35"},{"value":"67.17"},{"value":"0"}]},
    {"dimensionValues": [{"value": "/15anos-teste"}], "metricValues": [{"value":"34"},{"value":"13"},{"value":"151.45"},{"value":"0"}]},
    {"dimensionValues": [{"value": "/blank-1"}], "metricValues": [{"value":"1"},{"value":"1"},{"value":"77.54"},{"value":"0"}]},
]
save("ga4_pages", 7, [parse_ga4_page_row(r) for r in ga4_pages_7d])

# GA4 7d channels
ga4_ch_7d = [
    {"dimensionValues": [{"value": "Cross-network"}], "metricValues": [{"value":"467"},{"value":"394"},{"value":"0"},{"value":"0.6831"},{"value":"147.54"}]},
    {"dimensionValues": [{"value": "Paid Search"}], "metricValues": [{"value":"147"},{"value":"135"},{"value":"0"},{"value":"0.6190"},{"value":"114.66"}]},
    {"dimensionValues": [{"value": "Direct"}], "metricValues": [{"value":"97"},{"value":"96"},{"value":"0"},{"value":"0.8041"},{"value":"50.13"}]},
    {"dimensionValues": [{"value": "Organic Search"}], "metricValues": [{"value":"18"},{"value":"18"},{"value":"0"},{"value":"0.7222"},{"value":"226.75"}]},
    {"dimensionValues": [{"value": "Unassigned"}], "metricValues": [{"value":"9"},{"value":"8"},{"value":"0"},{"value":"0.0000"},{"value":"166.91"}]},
    {"dimensionValues": [{"value": "Referral"}], "metricValues": [{"value":"5"},{"value":"4"},{"value":"0"},{"value":"0.8000"},{"value":"637.54"}]},
]
save("ga4_channels", 7, [parse_ga4_channel_row(r) for r in ga4_ch_7d])

# ═══════════════════════════════════════════
# 14 DAYS
# ═══════════════════════════════════════════
print("\n=== 14 DAYS ===")

c14 = [
    {"campaign_name": "[Search] - Noivas", "status": "ENABLED", "impressions": 4992, "clicks": 378,
     "ctr": 0.0757, "cpc": 1164876.169, "cost": 440323192, "conversions": 24,
     "cost_per_conversion": 18346799.667, "search_impression_share": 0.2140,
     "search_budget_lost_impression_share": 0.0304, "search_rank_lost_impression_share": 0.7556,
     "top_impression_percentage": 0.7376, "absolute_top_impression_percentage": 0.4685},
    {"campaign_name": "[Search] - Institucional", "status": "ENABLED", "impressions": 448, "clicks": 94,
     "ctr": 0.2098, "cpc": 785701.138, "cost": 73855907, "conversions": 6,
     "cost_per_conversion": 12309317.833, "search_impression_share": 0.8614,
     "search_budget_lost_impression_share": 0.0090, "search_rank_lost_impression_share": 0.1295,
     "top_impression_percentage": 0.7972, "absolute_top_impression_percentage": 0.4441},
    {"campaign_name": "Pmax rmkt Noivas", "status": "ENABLED", "impressions": 12604, "clicks": 690,
     "ctr": 0.0547, "cpc": 200146.951, "cost": 138101396, "conversions": 47.0,
     "cost_per_conversion": 2938455.116, "search_impression_share": 0.0999,
     "search_budget_lost_impression_share": 0.1333, "search_rank_lost_impression_share": 0.8381},
    {"campaign_name": "demand Gen - YT Retargeting", "status": "ENABLED", "impressions": 8017, "clicks": 449,
     "ctr": 0.0560, "cpc": 159059.209, "cost": 71417585, "conversions": 14.0,
     "cost_per_conversion": 5102018.823},
]
save("campaigns", 14, [parse_campaign(c) for c in c14])

ag14 = [
    {"ad_group_name": "Vestido Casamento", "campaign_name": "[Search] - Noivas",
     "impressions": 4854, "clicks": 368, "ctr": 7.58, "cpc": 1.161, "cost": 427.36, "conversions": 23, "cost_per_conversion": 18.58},
    {"ad_group_name": "Branding", "campaign_name": "[Search] - Institucional",
     "impressions": 448, "clicks": 94, "ctr": 20.98, "cpc": 0.786, "cost": 73.86, "conversions": 6, "cost_per_conversion": 12.31},
    {"ad_group_name": "Marcas Vestidos Noivas", "campaign_name": "[Search] - Noivas",
     "impressions": 138, "clicks": 10, "ctr": 7.25, "cpc": 1.296, "cost": 12.96, "conversions": 1, "cost_per_conversion": 12.96},
    {"ad_group_name": "Noivas", "campaign_name": "demand Gen - YT Retargeting",
     "impressions": 2908, "clicks": 164, "ctr": 5.64, "cpc": 0.158, "cost": 25.96, "conversions": 4.0, "cost_per_conversion": 6.49},
    {"ad_group_name": "Todos", "campaign_name": "demand Gen - YT Retargeting",
     "impressions": 5109, "clicks": 285, "ctr": 5.58, "cpc": 0.159, "cost": 45.45, "conversions": 10.0, "cost_per_conversion": 4.55},
]
save("adgroups", 14, [parse_adgroup(a) for a in ag14])

# GA4 14d daily
ga4_daily_14d = [
    {"dimensionValues": [{"value": "20260417"}], "metricValues": [{"value":"75"},{"value":"62"},{"value":"519.46"},{"value":"0"},{"value":"59"},{"value":"43"},{"value":"0.6452"},{"value":"0.3548"}]},
    {"dimensionValues": [{"value": "20260418"}], "metricValues": [{"value":"110"},{"value":"84"},{"value":"68.90"},{"value":"0"},{"value":"83"},{"value":"67"},{"value":"0.7619"},{"value":"0.2381"}]},
    {"dimensionValues": [{"value": "20260419"}], "metricValues": [{"value":"116"},{"value":"84"},{"value":"1024.79"},{"value":"0"},{"value":"81"},{"value":"57"},{"value":"0.7500"},{"value":"0.2500"}]},
    {"dimensionValues": [{"value": "20260420"}], "metricValues": [{"value":"111"},{"value":"87"},{"value":"182.94"},{"value":"0"},{"value":"80"},{"value":"59"},{"value":"0.7931"},{"value":"0.2069"}]},
    {"dimensionValues": [{"value": "20260421"}], "metricValues": [{"value":"130"},{"value":"71"},{"value":"340.93"},{"value":"0"},{"value":"66"},{"value":"48"},{"value":"0.7465"},{"value":"0.2535"}]},
    {"dimensionValues": [{"value": "20260422"}], "metricValues": [{"value":"107"},{"value":"89"},{"value":"98.44"},{"value":"0"},{"value":"86"},{"value":"65"},{"value":"0.7528"},{"value":"0.2472"}]},
    {"dimensionValues": [{"value": "20260423"}], "metricValues": [{"value":"116"},{"value":"70"},{"value":"279.92"},{"value":"0"},{"value":"61"},{"value":"37"},{"value":"0.8714"},{"value":"0.1286"}]},
    {"dimensionValues": [{"value": "20260424"}], "metricValues": [{"value":"89"},{"value":"78"},{"value":"75.51"},{"value":"0"},{"value":"77"},{"value":"60"},{"value":"0.6282"},{"value":"0.3718"}]},
    {"dimensionValues": [{"value": "20260425"}], "metricValues": [{"value":"134"},{"value":"97"},{"value":"158.12"},{"value":"0"},{"value":"89"},{"value":"62"},{"value":"0.7526"},{"value":"0.2474"}]},
    {"dimensionValues": [{"value": "20260426"}], "metricValues": [{"value":"94"},{"value":"71"},{"value":"166.88"},{"value":"0"},{"value":"66"},{"value":"38"},{"value":"0.6761"},{"value":"0.3239"}]},
    {"dimensionValues": [{"value": "20260427"}], "metricValues": [{"value":"156"},{"value":"120"},{"value":"123.73"},{"value":"0"},{"value":"112"},{"value":"75"},{"value":"0.7000"},{"value":"0.3000"}]},
    {"dimensionValues": [{"value": "20260428"}], "metricValues": [{"value":"146"},{"value":"120"},{"value":"99.83"},{"value":"0"},{"value":"109"},{"value":"62"},{"value":"0.6333"},{"value":"0.3667"}]},
    {"dimensionValues": [{"value": "20260429"}], "metricValues": [{"value":"177"},{"value":"134"},{"value":"157.13"},{"value":"0"},{"value":"125"},{"value":"85"},{"value":"0.6045"},{"value":"0.3955"}]},
    {"dimensionValues": [{"value": "20260430"}], "metricValues": [{"value":"169"},{"value":"123"},{"value":"149.87"},{"value":"0"},{"value":"117"},{"value":"79"},{"value":"0.7724"},{"value":"0.2276"}]},
]
save("ga4_daily", 14, [parse_ga4_daily_row(r) for r in ga4_daily_14d])

# GA4 14d pages
ga4_pages_14d = [
    {"dimensionValues": [{"value": "/vestidos-de-noivas"}], "metricValues": [{"value":"956"},{"value":"842"},{"value":"222.83"},{"value":"0"}]},
    {"dimensionValues": [{"value": "/"}], "metricValues": [{"value":"595"},{"value":"548"},{"value":"161.66"},{"value":"0"}]},
    {"dimensionValues": [{"value": "/15anos-teste"}], "metricValues": [{"value":"100"},{"value":"40"},{"value":"139.57"},{"value":"0"}]},
    {"dimensionValues": [{"value": "/vestido-de-festas"}], "metricValues": [{"value":"75"},{"value":"70"},{"value":"132.14"},{"value":"0"}]},
    {"dimensionValues": [{"value": "/blank-1"}], "metricValues": [{"value":"4"},{"value":"3"},{"value":"301.00"},{"value":"0"}]},
]
save("ga4_pages", 14, [parse_ga4_page_row(r) for r in ga4_pages_14d])

# GA4 14d channels
ga4_ch_14d = [
    {"dimensionValues": [{"value": "Cross-network"}], "metricValues": [{"value":"723"},{"value":"600"},{"value":"0"},{"value":"0.7234"},{"value":"283.13"}]},
    {"dimensionValues": [{"value": "Paid Search"}], "metricValues": [{"value":"297"},{"value":"275"},{"value":"0"},{"value":"0.6397"},{"value":"107.31"}]},
    {"dimensionValues": [{"value": "Direct"}], "metricValues": [{"value":"205"},{"value":"201"},{"value":"0"},{"value":"0.8439"},{"value":"71.37"}]},
    {"dimensionValues": [{"value": "Organic Search"}], "metricValues": [{"value":"37"},{"value":"35"},{"value":"0"},{"value":"0.7297"},{"value":"255.40"}]},
    {"dimensionValues": [{"value": "Unassigned"}], "metricValues": [{"value":"17"},{"value":"15"},{"value":"0"},{"value":"0.0588"},{"value":"1627.92"}]},
    {"dimensionValues": [{"value": "Referral"}], "metricValues": [{"value":"6"},{"value":"4"},{"value":"0"},{"value":"0.8333"},{"value":"596.72"}]},
    {"dimensionValues": [{"value": "Organic Social"}], "metricValues": [{"value":"2"},{"value":"2"},{"value":"0"},{"value":"0.5000"},{"value":"17.14"}]},
]
save("ga4_channels", 14, [parse_ga4_channel_row(r) for r in ga4_ch_14d])

# ═══════════════════════════════════════════
# 90 DAYS — copy 30d data as placeholder (Google Ads doesn't have a 90d preset)
# ═══════════════════════════════════════════
print("\n=== 90 DAYS (using 30d data as base — update when custom date range is available) ===")

save("campaigns", 90, [parse_campaign(c) for c in c30])
save("adgroups", 90, [parse_adgroup(a) for a in ag30])
# For 90d, reuse 30d GA4 data as placeholder
import shutil
for name in ["ga4_daily", "ga4_pages", "ga4_channels"]:
    src = DATA_DIR / f"{name}_30d.json"
    dst = DATA_DIR / f"{name}_90d.json"
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  {dst.name}: copied from 30d")

print("\nAll cache files saved!")
