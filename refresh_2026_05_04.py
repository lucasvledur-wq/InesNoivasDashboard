"""Refresh all 30d caches with fresh data pulled 2026-05-04."""
import json
from datetime import date
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent / "data"
TODAY = str(date.today())

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


def save(name, days, rows):
    path = DATA_DIR / f"{name}_{days}d.json"
    path.write_text(json.dumps({"date": TODAY, "rows": rows}, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  {path.name}: {len(rows)} rows")


def micros(v):
    v = float(v) if v else 0
    return v / 1_000_000 if v > 10_000 else v


# ══════════════════════════════════════════════════════════════════════════
# 1. CAMPAIGNS 30d
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Campaigns ===")

camp_raw = [
    {"campaign_name":"[Search] - Noivas","campaign_status":"ENABLED","clicks":"915","impressions":"10818","cost_micros":"1097790528","conversions":61.995149,"ctr":0.08458125346644481,"average_cpc":1199771.068852459,"cost_per_conversion":17707684.322203986,"search_impression_share":0.20998257406024395,"search_budget_lost_impression_share":0.03240394987967803,"search_rank_lost_impression_share":0.757613476060078,"top_impression_percentage":0.7471668620554904,"absolute_top_impression_percentage":0.46150840171942165},
    {"campaign_name":"[Search] - Institucional","campaign_status":"ENABLED","clicks":"191","impressions":"939","cost_micros":"152183826","conversions":14.5,"ctr":0.20340788072417465,"average_cpc":796773.9581151833,"cost_per_conversion":10495436.27586207,"search_impression_share":0.8586309523809523,"search_budget_lost_impression_share":0.013392857142857142,"search_rank_lost_impression_share":0.12797619047619047,"top_impression_percentage":0.7989690721649485,"absolute_top_impression_percentage":0.46219931271477666},
    {"campaign_name":"Pmax rmkt Noivas","campaign_status":"ENABLED","clicks":"1408","impressions":"28062","cost_micros":"297813334","conversions":101.457677,"ctr":0.05017461335613998,"average_cpc":211515.15198863635,"cost_per_conversion":2935345.484009061,"search_impression_share":0.0999,"search_budget_lost_impression_share":0.1326936681995048,"search_rank_lost_impression_share":0.8402016271666077,"top_impression_percentage":None,"absolute_top_impression_percentage":None},
    {"campaign_name":"demand Gen - YT Retargeting","campaign_status":"ENABLED","clicks":"1165","impressions":"18785","cost_micros":"169127246","conversions":23.007441,"ctr":0.06201756720787863,"average_cpc":145173.6017167382,"cost_per_conversion":7350980.319801754,"search_impression_share":None,"search_budget_lost_impression_share":None,"search_rank_lost_impression_share":None,"top_impression_percentage":None,"absolute_top_impression_percentage":None},
]

camp_rows = []
for r in camp_raw:
    cost = micros(r["cost_micros"])
    cpc = micros(r["average_cpc"])
    cpconv = micros(r["cost_per_conversion"])
    clicks = int(r["clicks"])
    impr = int(r["impressions"])
    conv = float(r["conversions"])
    ctr = r.get("ctr") or 0
    is_share = r.get("search_impression_share")
    is_budget = r.get("search_budget_lost_impression_share")
    is_rank = r.get("search_rank_lost_impression_share")
    top_is = r.get("top_impression_percentage")
    abs_top = r.get("absolute_top_impression_percentage")
    camp_rows.append({
        "Campaign": r["campaign_name"],
        "Status": r["campaign_status"],
        "Impressions": impr,
        "Clicks": clicks,
        "CTR (%)": round(ctr * 100, 2),
        "CPC (R$)": round(cpc, 2),
        "Cost (R$)": round(cost, 2),
        "Conversions": round(conv, 1),
        "Cost/Conv (R$)": round(cpconv, 2),
        "Conv. Rate (%)": round((conv / clicks * 100) if clicks else 0, 2),
        "Impr. Share (%)": round(is_share * 100, 1) if is_share else None,
        "Lost IS Budget (%)": round(is_budget * 100, 1) if is_budget else None,
        "Lost IS Rank (%)": round(is_rank * 100, 1) if is_rank else None,
        "Top IS (%)": round(top_is * 100, 1) if top_is else None,
        "Abs. Top IS (%)": round(abs_top * 100, 1) if abs_top else None,
    })
save("campaigns", 30, camp_rows)

# ══════════════════════════════════════════════════════════════════════════
# 2. AD GROUPS 30d (only those with clicks > 0)
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Ad Groups ===")

# From Zapier — map adGroup IDs to names. Active adgroups with clicks > 0:
# 157462860669: 883 clicks ([Search] - Noivas / Vestido Casamento)
# 184501338201: 32 clicks (Pmax rmkt - small group)
# 179656431771: 191 clicks (Institucional / Branding)
# 186207837556: 597 clicks (demand Gen / Noivas)
# 186207837596: 568 clicks (demand Gen / Todos)

# We don't have ad_group_name in raw — use known mapping from prior pulls
ag_raw = [
    {"ad_group_name":"Vestido Casamento","campaign_name":"[Search] - Noivas","clicks":883,"impressions":10498,"cost_micros":1046379850,"conversions":60.495149,"ctr":0.08411125928748334,"average_cpc":1185028.1426953566,"cost_per_conversion":17296921.60936739},
    {"ad_group_name":"Marcas Vestidos Noivas","campaign_name":"[Search] - Noivas","clicks":32,"impressions":317,"cost_micros":51410678,"conversions":1.5,"ctr":0.10094637223974763,"average_cpc":1606583.6875,"cost_per_conversion":34273785.333333336},
    {"ad_group_name":"Branding","campaign_name":"[Search] - Institucional","clicks":191,"impressions":939,"cost_micros":152183826,"conversions":14.5,"ctr":0.20340788072417465,"average_cpc":796773.9581151833,"cost_per_conversion":10495436.27586207},
    {"ad_group_name":"Noivas","campaign_name":"demand Gen - YT Retargeting","clicks":597,"impressions":9316,"cost_micros":87870966,"conversions":8.996166,"ctr":0.06408329755259769,"average_cpc":147187.54773869348,"cost_per_conversion":9767601.664975945},
    {"ad_group_name":"Todos","campaign_name":"demand Gen - YT Retargeting","clicks":568,"impressions":9461,"cost_micros":81162711,"conversions":14.011275,"ctr":0.06003593700454497,"average_cpc":142892.09683098592,"cost_per_conversion":5792671.330767543},
]

ag_rows = []
for r in ag_raw:
    cost = micros(r["cost_micros"])
    cpc = micros(r["average_cpc"])
    clicks = int(r["clicks"])
    impr = int(r["impressions"])
    conv = float(r["conversions"])
    ctr = r["ctr"]
    ag_rows.append({
        "Ad Group": r["ad_group_name"],
        "Campaign": r["campaign_name"],
        "Impressions": impr,
        "Clicks": clicks,
        "CTR (%)": round(ctr * 100, 2),
        "CPC (R$)": round(cpc, 2),
        "Cost (R$)": round(cost, 2),
        "Conversions": round(conv, 1),
        "Cost/Conv (R$)": round((cost / conv) if conv else 0, 2),
        "Conv. Rate (%)": round((conv / clicks * 100) if clicks else 0, 2),
    })
save("adgroups", 30, ag_rows)

# ══════════════════════════════════════════════════════════════════════════
# 3. ADS DAILY 30d (cost already in BRL, not micros)
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Ads Daily ===")

ads_raw = [
    {"date":"2026-04-04","clicks":127,"impressions":2419,"cost":65.409366,"conversions":7.998266},
    {"date":"2026-04-05","clicks":141,"impressions":2553,"cost":63.927919,"conversions":6},
    {"date":"2026-04-06","clicks":93,"impressions":1265,"cost":55.190722,"conversions":7.999578},
    {"date":"2026-04-07","clicks":108,"impressions":2031,"cost":58.442617,"conversions":7},
    {"date":"2026-04-08","clicks":89,"impressions":1191,"cost":48.522868,"conversions":2.994852},
    {"date":"2026-04-09","clicks":105,"impressions":1642,"cost":55.606127,"conversions":8.000277},
    {"date":"2026-04-10","clicks":134,"impressions":2042,"cost":68.884349,"conversions":8},
    {"date":"2026-04-11","clicks":112,"impressions":1638,"cost":57.479584,"conversions":8.002421},
    {"date":"2026-04-12","clicks":92,"impressions":1430,"cost":56.699747,"conversions":6.009066},
    {"date":"2026-04-13","clicks":120,"impressions":2008,"cost":82.788972,"conversions":10.988432},
    {"date":"2026-04-14","clicks":114,"impressions":1691,"cost":64.427381,"conversions":7},
    {"date":"2026-04-15","clicks":71,"impressions":950,"cost":53.54733,"conversions":6.00014},
    {"date":"2026-04-16","clicks":102,"impressions":1547,"cost":61.730018,"conversions":5},
    {"date":"2026-04-17","clicks":86,"impressions":1251,"cost":48.694793,"conversions":2.000257},
    {"date":"2026-04-18","clicks":111,"impressions":1620,"cost":56.76757,"conversions":5.999766},
    {"date":"2026-04-19","clicks":110,"impressions":1706,"cost":57.449187,"conversions":5},
    {"date":"2026-04-20","clicks":80,"impressions":1350,"cost":53.116642,"conversions":4.999331},
    {"date":"2026-04-21","clicks":64,"impressions":1246,"cost":36.010678,"conversions":5.000141},
    {"date":"2026-04-22","clicks":106,"impressions":1790,"cost":48.986573,"conversions":4},
    {"date":"2026-04-23","clicks":78,"impressions":998,"cost":34.038569,"conversions":7.00137},
    {"date":"2026-04-24","clicks":109,"impressions":1495,"cost":47.530418,"conversions":13.008034},
    {"date":"2026-04-25","clicks":102,"impressions":1596,"cost":35.567189,"conversions":7.998218},
    {"date":"2026-04-26","clicks":122,"impressions":2149,"cost":43.519479,"conversions":3},
    {"date":"2026-04-27","clicks":136,"impressions":2390,"cost":84.969785,"conversions":8.002437},
    {"date":"2026-04-28","clicks":162,"impressions":2626,"cost":64.53572,"conversions":8.994347},
    {"date":"2026-04-29","clicks":196,"impressions":2940,"cost":58.529621,"conversions":8.994041},
    {"date":"2026-04-30","clicks":149,"impressions":2904,"cost":53.981856,"conversions":7.005123},
    {"date":"2026-05-01","clicks":213,"impressions":3346,"cost":62.141528,"conversions":6.971924},
    {"date":"2026-05-02","clicks":201,"impressions":2840,"cost":68.210079,"conversions":5.992246},
    {"date":"2026-05-03","clicks":246,"impressions":3950,"cost":70.208247,"conversions":6},
]

ads_daily_rows = []
for r in ads_raw:
    cost = float(r["cost"])
    if cost > 10_000:
        cost = cost / 1_000_000
    clicks = int(r["clicks"])
    impr = int(r["impressions"])
    conv = float(r["conversions"])
    ads_daily_rows.append({
        "Date": r["date"],
        "Clicks": clicks,
        "Impressions": impr,
        "Cost (R$)": round(cost, 2),
        "Conversions": round(conv, 1),
        "CTR (%)": round(clicks / impr * 100, 2) if impr else 0,
        "CPC (R$)": round(cost / clicks, 2) if clicks else 0,
        "Cost/Lead (R$)": round(cost / conv, 2) if conv else 0,
    })

save("ads_daily", 30, ads_daily_rows)
save("ads_daily", 14, ads_daily_rows[-14:])
save("ads_daily", 7, ads_daily_rows[-7:])

# ══════════════════════════════════════════════════════════════════════════
# 4. GA4 DAILY 30d
# ══════════════════════════════════════════════════════════════════════════
print("\n=== GA4 Daily ===")

ga4_daily_raw = [
    ("20260404",123,98,117.25,0,95,62,0.6735,0.3265),
    ("20260405",130,104,170.28,0,101,74,0.7692,0.2308),
    ("20260406",80,61,136.54,0,58,32,0.6721,0.3279),
    ("20260407",115,95,195.50,0,88,60,0.7053,0.2947),
    ("20260408",102,84,75.30,0,78,56,0.6786,0.3214),
    ("20260409",136,95,135.42,0,89,63,0.6737,0.3263),
    ("20260410",144,109,103.14,0,107,75,0.7339,0.2661),
    ("20260411",110,83,148.30,0,77,57,0.7349,0.2651),
    ("20260412",105,70,293.39,0,69,47,0.8,0.2),
    ("20260413",132,101,86.28,0,97,66,0.7228,0.2772),
    ("20260414",108,78,124.20,0,77,53,0.6923,0.3077),
    ("20260415",102,79,86.15,0,69,46,0.7342,0.2658),
    ("20260416",91,70,86.90,0,69,51,0.7429,0.2571),
    ("20260417",75,62,519.46,0,59,43,0.6452,0.3548),
    ("20260418",110,84,68.90,0,83,67,0.7619,0.2381),
    ("20260419",116,84,1024.79,0,81,57,0.75,0.25),
    ("20260420",111,87,182.94,0,80,59,0.7931,0.2069),
    ("20260421",130,71,340.93,0,66,48,0.7465,0.2535),
    ("20260422",107,89,98.44,0,86,65,0.7528,0.2472),
    ("20260423",116,70,279.92,0,61,37,0.8714,0.1286),
    ("20260424",89,78,75.51,0,77,60,0.6282,0.3718),
    ("20260425",134,97,158.12,0,89,62,0.7526,0.2474),
    ("20260426",94,71,166.88,0,66,38,0.6761,0.3239),
    ("20260427",156,120,123.73,0,112,75,0.7,0.3),
    ("20260428",146,120,99.83,0,109,62,0.6333,0.3667),
    ("20260429",177,134,157.13,0,125,85,0.6045,0.3955),
    ("20260430",169,123,149.87,0,117,79,0.7724,0.2276),
    ("20260501",185,151,131.76,0,141,85,0.6755,0.3245),
    ("20260502",171,130,85.39,0,125,83,0.6154,0.3846),
    ("20260503",172,184,51.80,0,178,47,0,1),
]
ga4_daily_rows = []
for d in ga4_daily_raw:
    date_str = d[0]
    formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    ga4_daily_rows.append({
        "Date": formatted,
        "Pageviews": int(d[1]),
        "Sessions": int(d[2]),
        "Avg. Session (s)": round(float(d[3]), 1),
        "Conversions": round(float(d[4]), 1),
        "Users": int(d[5]),
        "New Users": int(d[6]),
        "Engagement Rate (%)": round(float(d[7]) * 100, 1),
        "Bounce Rate (%)": round(float(d[8]) * 100, 1),
    })
save("ga4_daily", 30, ga4_daily_rows)
save("ga4_daily", 14, ga4_daily_rows[-14:])
save("ga4_daily", 7, ga4_daily_rows[-7:])

# ══════════════════════════════════════════════════════════════════════════
# 5. GA4 PAGES 30d (with events from page+event report)
# ══════════════════════════════════════════════════════════════════════════
print("\n=== GA4 Pages ===")

pages_raw = [
    ("/vestidos-de-noivas", 2148, 161.74),
    ("/", 1223, 125.02),
    ("/15anos-teste", 186, 129.53),
    ("/vestido-de-festas", 167, 73.37),
    ("/blank-1", 12, 182.13),
]
# Page event lookup (whatsapp total, generate_lead)
page_events = defaultdict(lambda: [0, 0])
page_event_rows = [
    ("/vestidos-de-noivas","Whatsapp LPs",224),
    ("/","Whatsapp LPs",71),
    ("/vestido-de-festas","Whatsapp LPs",45),
    ("/15anos-teste","Whatsapp LPs",11),
    ("/vestidos-de-noivas","Whatsapp",8),
    ("/vestidos-de-noivas","generate_lead",5),
]
for page, event, count in page_event_rows:
    if event in ("Whatsapp LPs", "Whatsapp"):
        page_events[page][0] += count
    elif event == "generate_lead":
        page_events[page][1] += count

pages_rows = []
for page, pv, dur in pages_raw:
    wlp, gl = page_events.get(page, [0, 0])
    pages_rows.append({
        "Page": page,
        "Pageviews": int(pv),
        "Avg. Session (s)": round(float(dur), 0),
        "Conversions": 0,
        "Whatsapp LP": wlp,
        "Generate Lead": gl,
    })
save("ga4_pages", 30, pages_rows)

# ══════════════════════════════════════════════════════════════════════════
# 6. GA4 CHANNELS 30d (with conversion events)
# ══════════════════════════════════════════════════════════════════════════
print("\n=== GA4 Channels ===")

ch_raw = [
    ("Paid Search", 1193, 1054, 0, 0.6756, 134.69),
    ("Cross-network", 1044, 866, 0, 0.6245, 220.29),
    ("Direct", 430, 417, 0, 0.8256, 89.39),
    ("Unassigned", 112, 109, 0, 0.0089, 291.31),
    ("Organic Search", 101, 87, 0, 0.6931, 149.36),
    ("Referral", 33, 28, 0, 0.7273, 180.50),
    ("Organic Social", 4, 3, 0, 0.75, 91.13),
]
ch_event_rows = [
    ("Paid Search","Whatsapp LPs",125),
    ("Cross-network","Whatsapp LPs",111),
    ("Direct","Whatsapp LPs",72),
    ("Unassigned","Whatsapp LPs",23),
    ("Organic Search","Whatsapp LPs",13),
    ("Paid Search","Whatsapp",6),
    ("Referral","Whatsapp LPs",6),
    ("Paid Search","generate_lead",4),
    ("Cross-network","Whatsapp",1),
    ("Direct","Whatsapp",1),
    ("Direct","generate_lead",1),
    ("Organic Social","Whatsapp LPs",1),
]
ch_events = defaultdict(lambda: [0, 0])
for ch, ev, c in ch_event_rows:
    if ev in ("Whatsapp LPs", "Whatsapp"):
        ch_events[ch][0] += c
    elif ev == "generate_lead":
        ch_events[ch][1] += c

ch_rows = []
for ch, sess, users, conv, eng, dur in ch_raw:
    wlp, gl = ch_events.get(ch, [0, 0])
    ch_rows.append({
        "Channel": ch,
        "Sessions": int(sess),
        "Users": int(users),
        "Conversions": round(float(conv), 1),
        "Engagement Rate (%)": round(float(eng) * 100, 1),
        "Avg. Session (s)": round(float(dur), 1),
        "Whatsapp LP": wlp,
        "Generate Lead": gl,
    })
save("ga4_channels", 30, ch_rows)

print("\n✅ Refresh complete!")
