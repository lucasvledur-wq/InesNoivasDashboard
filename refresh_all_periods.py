"""
Refresh all caches for periods 3d, 14d, 30d, 90d — 2026-05-04
Processes raw Zapier data pulled during this session.
"""
import json
import os
from datetime import date
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TODAY = str(date.today())


def save(name: str, days: int, rows: list[dict]):
    path = DATA_DIR / f"{name}_{days}d.json"
    data = {"date": TODAY, "rows": rows}
    path.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  Saved {path.name}: {len(rows)} rows")


# ============================================================================
# CAMPAIGNS — parse raw Zapier results
# ============================================================================

def parse_campaigns(raw, period_label=""):
    rows = []
    for r in raw:
        # Handle nested format (campaign.name) vs flat format (campaign_name)
        if "campaign" in r and isinstance(r["campaign"], dict):
            name = r["campaign"].get("name", "")
            status = r["campaign"].get("status", "ENABLED")
            metrics = r.get("metrics", {})
            impressions = int(metrics.get("impressions", 0))
            clicks = int(metrics.get("clicks", 0))
            cost = float(metrics.get("costMicros", 0))
            if cost > 10_000:
                cost = cost / 1_000_000
            conversions = float(metrics.get("conversions", 0))
            ctr = float(metrics.get("ctr", 0) or 0)
            avg_cpc = float(metrics.get("averageCpc", 0) or metrics.get("average_cpc", 0) or 0)
            if avg_cpc > 1000:
                avg_cpc = avg_cpc / 1_000_000
            cost_per_conv = float(metrics.get("costPerConversion", 0) or 0)
            if cost_per_conv > 1000:
                cost_per_conv = cost_per_conv / 1_000_000
            is_share = metrics.get("searchImpressionShare") or metrics.get("search_impression_share")
            is_budget_lost = metrics.get("searchBudgetLostImpressionShare") or metrics.get("search_budget_lost_impression_share")
            is_rank_lost = metrics.get("searchRankLostImpressionShare") or metrics.get("search_rank_lost_impression_share")
            top_is = metrics.get("topImpressionPercentage") or metrics.get("top_impression_percentage")
            abs_top_is = metrics.get("absoluteTopImpressionPercentage") or metrics.get("absolute_top_impression_percentage")
        else:
            name = r.get("campaign_name", "")
            status = r.get("status", "ENABLED")
            impressions = int(r.get("impressions", 0))
            clicks = int(r.get("clicks", 0))
            cost = float(r.get("cost", 0))
            if cost > 10_000:
                cost = cost / 1_000_000
            conversions = float(r.get("conversions", 0))
            ctr = float(r.get("ctr", 0) or 0)
            avg_cpc = float(r.get("average_cpc", 0) or r.get("cpc", 0) or 0)
            if avg_cpc > 1000:
                avg_cpc = avg_cpc / 1_000_000
            cost_per_conv = float(r.get("cost_per_conversion", 0) or 0)
            if cost_per_conv > 1000:
                cost_per_conv = cost_per_conv / 1_000_000
            is_share = r.get("impression_share") or r.get("search_impression_share")
            is_budget_lost = r.get("budget_lost_impression_share") or r.get("search_budget_lost_impression_share")
            is_rank_lost = r.get("rank_lost_impression_share") or r.get("search_rank_lost_impression_share")
            top_is = r.get("top_impression_percentage")
            abs_top_is = r.get("absolute_top_impression_percentage")

        if impressions == 0 and clicks == 0:
            continue
        if status == "REMOVED":
            continue

        rows.append({
            "Campaign": name,
            "Status": status,
            "Impressions": impressions,
            "Clicks": clicks,
            "CTR (%)": round(ctr * 100, 2) if ctr and ctr < 1 else round(ctr, 2) if ctr else 0,
            "CPC (R$)": round(avg_cpc, 2),
            "Cost (R$)": round(cost, 2),
            "Conversions": round(conversions, 1),
            "Cost/Conv (R$)": round(cost_per_conv, 2),
            "Conv. Rate (%)": round((conversions / clicks * 100) if clicks > 0 else 0, 2),
            "Impr. Share (%)": round(float(is_share) * 100, 1) if is_share else None,
            "Lost IS Budget (%)": round(float(is_budget_lost) * 100, 1) if is_budget_lost else None,
            "Lost IS Rank (%)": round(float(is_rank_lost) * 100, 1) if is_rank_lost else None,
            "Top IS (%)": round(float(top_is) * 100, 1) if top_is else None,
            "Abs. Top IS (%)": round(float(abs_top_is) * 100, 1) if abs_top_is else None,
        })
    return rows


# ============================================================================
# AD GROUPS — parse raw Zapier results
# ============================================================================

def parse_adgroups(raw):
    rows = []
    for r in raw:
        if "adGroup" in r and isinstance(r["adGroup"], dict):
            ad_group_name = r["adGroup"].get("name", "")
            campaign_name = r.get("campaign", {}).get("name", "")
            status = r["adGroup"].get("status", "ENABLED")
            metrics = r.get("metrics", {})
            impressions = int(metrics.get("impressions", 0))
            clicks = int(metrics.get("clicks", 0))
            cost = float(metrics.get("costMicros", 0))
            if cost > 10_000:
                cost = cost / 1_000_000
            conversions = float(metrics.get("conversions", 0))
            ctr = float(metrics.get("ctr", 0) or 0)
            avg_cpc = float(metrics.get("averageCpc", 0) or metrics.get("average_cpc", 0) or 0)
            if avg_cpc > 1000:
                avg_cpc = avg_cpc / 1_000_000
        else:
            ad_group_name = r.get("ad_group_name", "")
            campaign_name = r.get("campaign_name", "")
            status = r.get("status", "ENABLED")
            impressions = int(r.get("impressions", 0))
            clicks = int(r.get("clicks", 0))
            cost = float(r.get("cost", 0))
            if cost > 10_000:
                cost = cost / 1_000_000
            conversions = float(r.get("conversions", 0))
            ctr = float(r.get("ctr", 0) or 0)
            avg_cpc = float(r.get("average_cpc", 0) or r.get("cpc", 0) or 0)
            if avg_cpc > 1000:
                avg_cpc = avg_cpc / 1_000_000

        if impressions == 0 and clicks == 0:
            continue
        if status == "REMOVED":
            continue

        rows.append({
            "Ad Group": ad_group_name,
            "Campaign": campaign_name,
            "Impressions": impressions,
            "Clicks": clicks,
            "CTR (%)": round(ctr * 100, 2) if ctr and ctr < 1 else round(ctr, 2) if ctr else 0,
            "CPC (R$)": round(avg_cpc, 2),
            "Cost (R$)": round(cost, 2),
            "Conversions": round(conversions, 1),
            "Cost/Conv (R$)": round((cost / conversions) if conversions > 0 else 0, 2),
            "Conv. Rate (%)": round((conversions / clicks * 100) if clicks > 0 else 0, 2),
        })
    return rows


# ============================================================================
# ADS DAILY — parse raw Zapier results
# ============================================================================

def parse_ads_daily(raw):
    rows = []
    for r in raw:
        d = r.get("date", "")
        cost = float(r.get("cost", 0))
        if cost > 10_000:
            cost = cost / 1_000_000
        clicks = int(r.get("clicks", 0))
        impressions = int(r.get("impressions", 0))
        conversions = float(r.get("conversions", 0))
        ctr = float(r.get("ctr", 0) or 0)
        avg_cpc = float(r.get("average_cpc", 0) or 0)
        if avg_cpc > 1000:
            avg_cpc = avg_cpc / 1_000_000
        cost_per_conv = float(r.get("cost_per_conversion", 0) or 0)
        if cost_per_conv > 1000:
            cost_per_conv = cost_per_conv / 1_000_000

        rows.append({
            "Date": d,
            "Impressions": impressions,
            "Clicks": clicks,
            "Cost (R$)": round(cost, 2),
            "Conversions": round(conversions, 1),
            "CTR (%)": round(ctr * 100, 2) if ctr < 1 else round(ctr, 2),
            "CPC (R$)": round(avg_cpc, 2),
            "Cost/Lead (R$)": round(cost_per_conv, 2),
        })
    return rows


# ============================================================================
# GA4 DAILY — parse raw GA4 API response
# ============================================================================

def parse_ga4_daily(raw_body):
    api_rows = raw_body.get("rows", [])
    rows = []
    for r in api_rows:
        dims = r.get("dimensions", [])
        mets = r.get("metrics", [])
        date_str = dims[0] if isinstance(dims[0], str) else dims[0].get("value", "")
        if len(date_str) == 8 and date_str.isdigit():
            formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        else:
            formatted = date_str

        rows.append({
            "Date": formatted,
            "Pageviews": int(mets[0]) if isinstance(mets[0], (int, str)) else int(mets[0].get("value", 0)),
            "Sessions": int(mets[1]) if isinstance(mets[1], (int, str)) else int(mets[1].get("value", 0)),
            "Avg. Session (s)": round(float(mets[2]) if isinstance(mets[2], (float, str)) else float(mets[2].get("value", 0)), 1),
            "Users": int(mets[3]) if isinstance(mets[3], (int, str)) else int(mets[3].get("value", 0)),
            "New Users": int(mets[4]) if isinstance(mets[4], (int, str)) else int(mets[4].get("value", 0)),
            "Engagement Rate (%)": round(float(mets[5]) * 100 if isinstance(mets[5], (float, str)) else float(mets[5].get("value", 0)) * 100, 1),
            "Bounce Rate (%)": round(float(mets[6]) * 100 if isinstance(mets[6], (float, str)) else float(mets[6].get("value", 0)) * 100, 1),
        })
    return rows


# ============================================================================
# GA4 PAGES — parse raw page+event data
# ============================================================================

def parse_ga4_pages(raw_body):
    api_rows = raw_body.get("rows", [])
    # Aggregate by page: session_start as proxy for pageviews, Whatsapp LPs+Whatsapp, generate_lead
    page_data = {}
    for r in api_rows:
        dims = r.get("dimensions", [])
        mets = r.get("metrics", [])
        page = dims[0] if isinstance(dims[0], str) else dims[0].get("value", "")
        event = dims[1] if isinstance(dims[1], str) else dims[1].get("value", "")
        count = int(mets[0]) if isinstance(mets[0], (int, str)) else int(mets[0].get("value", 0))

        if page not in page_data:
            page_data[page] = {"Pageviews": 0, "Whatsapp LP": 0, "Generate Lead": 0}
        if event == "session_start":
            page_data[page]["Pageviews"] = count
        elif event in ("Whatsapp LPs", "Whatsapp"):
            page_data[page]["Whatsapp LP"] += count
        elif event == "generate_lead":
            page_data[page]["Generate Lead"] = count

    rows = []
    for page, d in page_data.items():
        if d["Pageviews"] == 0 and d["Whatsapp LP"] == 0 and d["Generate Lead"] == 0:
            continue
        rows.append({
            "Page": page,
            "Pageviews": d["Pageviews"],
            "Whatsapp LP": d["Whatsapp LP"],
            "Generate Lead": d["Generate Lead"],
        })
    rows.sort(key=lambda x: x["Pageviews"], reverse=True)
    return rows


# ============================================================================
# GA4 CHANNELS — parse channel base + events data
# ============================================================================

def parse_ga4_channels(channels_raw, events_raw):
    # Base channels
    ch_rows = channels_raw.get("rows", [])
    channel_data = {}
    for r in ch_rows:
        dims = r.get("dimensions", [])
        mets = r.get("metrics", [])
        ch = dims[0] if isinstance(dims[0], str) else dims[0].get("value", "")
        sessions = int(mets[0]) if isinstance(mets[0], (int, str)) else int(mets[0].get("value", 0))
        users = int(mets[1]) if isinstance(mets[1], (int, str)) else int(mets[1].get("value", 0))
        eng_rate = float(mets[3]) if isinstance(mets[3], (float, str)) else float(mets[3].get("value", 0))
        avg_dur = float(mets[4]) if isinstance(mets[4], (float, str)) else float(mets[4].get("value", 0))
        channel_data[ch] = {
            "Channel": ch,
            "Sessions": sessions,
            "Users": users,
            "Whatsapp LP": 0,
            "Generate Lead": 0,
            "Engagement Rate (%)": round(eng_rate * 100, 1),
            "Avg. Session (s)": round(avg_dur, 1),
        }

    # Events overlay
    ev_rows = events_raw.get("rows", [])
    for r in ev_rows:
        dims = r.get("dimensions", [])
        mets = r.get("metrics", [])
        ch = dims[0] if isinstance(dims[0], str) else dims[0].get("value", "")
        event = dims[1] if isinstance(dims[1], str) else dims[1].get("value", "")
        count = int(mets[0]) if isinstance(mets[0], (int, str)) else int(mets[0].get("value", 0))

        if ch not in channel_data:
            channel_data[ch] = {"Channel": ch, "Sessions": 0, "Users": 0, "Whatsapp LP": 0, "Generate Lead": 0, "Engagement Rate (%)": 0, "Avg. Session (s)": 0}

        if event in ("Whatsapp LPs", "Whatsapp"):
            channel_data[ch]["Whatsapp LP"] += count
        elif event == "generate_lead":
            channel_data[ch]["Generate Lead"] = count

    rows = list(channel_data.values())
    rows.sort(key=lambda x: x["Sessions"], reverse=True)
    return rows


# ============================================================================
# RAW DATA
# ============================================================================

# --- CAMPAIGNS 7d ---
campaigns_7d_raw = [{"campaign_name":"[Search] - Noivas","status":"ENABLED","impressions":"911","clicks":"81","cost":"103992373","conversions":4,"ctr":0.0889132821075741,"average_cpc":1283856.4567901234,"cost_per_conversion":25998093.25,"impression_share":0.2252663622526636,"budget_lost_impression_share":0.013191273465246067,"rank_lost_impression_share":0.7615423642820903,"top_impression_percentage":0.7274774774774775,"absolute_top_impression_percentage":0.41216216216216217},{"campaign_name":"[Search] - Institucional","status":"ENABLED","impressions":"69","clicks":"14","cost":"6830617","conversions":1,"ctr":0.2028985507246377,"average_cpc":487901.21428571426,"cost_per_conversion":6830617,"impression_share":0.92,"budget_lost_impression_share":0,"rank_lost_impression_share":0.08,"top_impression_percentage":0.782608695652174,"absolute_top_impression_percentage":0.3695652173913043},{"campaign_name":"Pmax rmkt Noivas","status":"ENABLED","impressions":"2453","clicks":"112","cost":"21096316","conversions":9.972804,"ctr":0.04565837749694252,"average_cpc":188359.9642857143,"cost_per_conversion":2115384.599958046,"impression_share":0.0999,"budget_lost_impression_share":0.03402903811252268,"rank_lost_impression_share":0.9001,"top_impression_percentage":None,"absolute_top_impression_percentage":None},{"campaign_name":"demand Gen - YT Retargeting","status":"ENABLED","impressions":"5656","clicks":"356","cost":"52414157","conversions":5.005484,"ctr":0.06294200848656294,"average_cpc":147230.77808988764,"cost_per_conversion":10471346.427238604,"impression_share":None,"budget_lost_impression_share":None,"rank_lost_impression_share":None,"top_impression_percentage":None,"absolute_top_impression_percentage":None}]

# --- CAMPAIGNS 14d (nested format) ---
campaigns_14d_raw = [{"campaign_name":"[Search] - Noivas","status":"ENABLED","impressions":"4833","clicks":"371","cost":"431812658","conversions":26,"ctr":0.07676391475274157,"average_cpc":1163915.5202156333,"cost_per_conversion":16608179.153846154,"impression_share":0.21681456408379837,"budget_lost_impression_share":0.02662153508370689,"rank_lost_impression_share":0.7565639008324947,"top_impression_percentage":0.7232067510548523,"absolute_top_impression_percentage":0.4413502109704641},{"campaign_name":"[Search] - Institucional","status":"ENABLED","impressions":"435","clicks":"92","cost":"69760823","conversions":7,"ctr":0.21149425287356322,"average_cpc":758269.8152173914,"cost_per_conversion":9965831.857142856,"impression_share":0.8675078864353313,"budget_lost_impression_share":0,"rank_lost_impression_share":0.13249211356466878,"top_impression_percentage":0.7854545454545454,"absolute_top_impression_percentage":0.4218181818181818},{"campaign_name":"Pmax rmkt Noivas","status":"ENABLED","impressions":"12277","clicks":"642","cost":"132194091","conversions":45.971415,"ctr":0.05229290543292335,"average_cpc":205909.79906542055,"cost_per_conversion":2875571.504596933,"impression_share":0.0999,"budget_lost_impression_share":0.141363144608727,"rank_lost_impression_share":0.8305084745762712,"top_impression_percentage":None,"absolute_top_impression_percentage":None},{"campaign_name":"demand Gen - YT Retargeting","status":"ENABLED","impressions":"14079","clicks":"859","cost":"127582894","conversions":18.007148,"ctr":0.06101285602670644,"average_cpc":148524.90570430734,"cost_per_conversion":7085124.973704887,"impression_share":None,"budget_lost_impression_share":None,"rank_lost_impression_share":None,"top_impression_percentage":None,"absolute_top_impression_percentage":None}]

# --- CAMPAIGNS 90d ---
campaigns_90d_raw = [{"campaign_name":"[Search] - Noivas","status":"ENABLED","impressions":"46251","clicks":"4099","cost":"4222102507","conversions":370.996409,"ctr":0.08862511080841495,"average_cpc":1030032.3266650402,"cost_per_conversion":11380440.361620858,"impression_share":0.16496393760658354,"budget_lost_impression_share":0.02158267753492811,"rank_lost_impression_share":0.8134533848584884,"top_impression_percentage":0.7376418633363407,"absolute_top_impression_percentage":0.3859157604824541},{"campaign_name":"[Search] - Institucional","status":"ENABLED","impressions":"3048","clicks":"623","cost":"598796614","conversions":78.974547,"ctr":0.20439632545931757,"average_cpc":961150.2632423756,"cost_per_conversion":7582146.865622413,"impression_share":0.8560851457658492,"budget_lost_impression_share":0.036557149467838966,"rank_lost_impression_share":0.10735770476631189,"top_impression_percentage":0.7843243243243243,"absolute_top_impression_percentage":0.4454054054054054},{"campaign_name":"Pmax rmkt Noivas","status":"ENABLED","impressions":"189184","clicks":"9181","cost":"1601172643","conversions":804.616059,"ctr":0.04852947395128552,"average_cpc":174400.67999128636,"cost_per_conversion":1989983.4524679803,"impression_share":0.0999,"budget_lost_impression_share":0.14283196929944786,"rank_lost_impression_share":0.830579159650703,"top_impression_percentage":None,"absolute_top_impression_percentage":None},{"campaign_name":"demand Gen - YT Retargeting","status":"ENABLED","impressions":"163601","clicks":"8757","cost":"1154798201","conversions":310.18156,"ctr":0.05352656768601659,"average_cpc":131871.4401050588,"cost_per_conversion":3722975.02469199,"impression_share":None,"budget_lost_impression_share":None,"rank_lost_impression_share":None,"top_impression_percentage":None,"absolute_top_impression_percentage":None}]

# --- AD GROUPS 3d ---
adgroups_7d_raw = [{"ad_group_name":"Vestido Casamento","campaign_name":"[Search] - Noivas","status":"ENABLED","impressions":868,"clicks":76,"cost":93.665784,"conversions":4,"ctr":8.755760368663594,"average_cpc":1.2324445263157895,"cost_per_conversion":23.416446},{"ad_group_name":"Branding","campaign_name":"[Search] - Institucional","status":"ENABLED","impressions":69,"clicks":14,"cost":6.830617,"conversions":1,"ctr":20.28985507246377,"average_cpc":0.4879012142857143,"cost_per_conversion":6.830617},{"ad_group_name":"Marcas Vestidos Noivas","campaign_name":"[Search] - Noivas","status":"ENABLED","impressions":43,"clicks":5,"cost":10.326589,"conversions":0,"ctr":11.627906976744185,"average_cpc":2.0653178,"cost_per_conversion":0},{"ad_group_name":"Noivas","campaign_name":"demand Gen - YT Retargeting","status":"ENABLED","impressions":3572,"clicks":247,"cost":34.681996,"conversions":4.003283,"ctr":6.914893617021277,"average_cpc":0.14041293927125506,"cost_per_conversion":8.663388523869035},{"ad_group_name":"Todos","campaign_name":"demand Gen - YT Retargeting","status":"ENABLED","impressions":2084,"clicks":109,"cost":17.732161,"conversions":1.002201,"ctr":5.230326295585413,"average_cpc":0.162680376146789,"cost_per_conversion":17.693218226683072}]

# --- AD GROUPS 14d (nested format) ---
adgroups_14d_raw = [{"ad_group_name":"Vestido Casamento","campaign_name":"[Search] - Noivas","status":"ENABLED","impressions":4683,"clicks":360,"cost":"413989339","conversions":25,"ctr":0.07687379884689302,"average_cpc":1149970.3861111111,"cost_per_conversion":16559573.56},{"ad_group_name":"Branding","campaign_name":"[Search] - Institucional","status":"ENABLED","impressions":435,"clicks":92,"cost":"69760823","conversions":7,"ctr":0.21149425287356322,"average_cpc":758269.8152173914,"cost_per_conversion":9965831.857142856},{"ad_group_name":"Marcas Vestidos Noivas","campaign_name":"[Search] - Noivas","status":"ENABLED","impressions":150,"clicks":11,"cost":"17823319","conversions":1,"ctr":0.07333333333333333,"average_cpc":1620301.7272727273,"cost_per_conversion":17823319},{"ad_group_name":"Noivas","campaign_name":"demand Gen - YT Retargeting","status":"ENABLED","impressions":8015,"clicks":515,"cost":"73472537","conversions":7.006714,"ctr":0.06425452276980662,"average_cpc":142665.12038834952,"cost_per_conversion":10486019.123943122},{"ad_group_name":"Todos","campaign_name":"demand Gen - YT Retargeting","status":"ENABLED","impressions":6064,"clicks":344,"cost":"54110357","conversions":11.000434,"ctr":0.05672823218997362,"average_cpc":157297.54941860464,"cost_per_conversion":4918929.289517122}]

# --- AD GROUPS 90d ---
adgroups_90d_raw = [{"ad_group_name":"Vestido Casamento","campaign_name":"[Search] - Noivas","status":"ENABLED","impressions":42273,"clicks":3765,"cost":3808.620049,"conversions":331.502958,"ctr":8.906394152295793,"average_cpc":1.0115856703851263,"cost_per_conversion":11.48894740480717},{"ad_group_name":"Branding","campaign_name":"[Search] - Institucional","status":"ENABLED","impressions":3048,"clicks":623,"cost":598.796614,"conversions":78.974547,"ctr":20.439632545931758,"average_cpc":0.9611502632423755,"cost_per_conversion":7.582146865622414},{"ad_group_name":"Marcas Vestidos Noivas","campaign_name":"[Search] - Noivas","status":"ENABLED","impressions":3978,"clicks":334,"cost":413.482458,"conversions":39.493451,"ctr":8.396178984414277,"average_cpc":1.2379714311377246,"cost_per_conversion":10.469646169943468},{"ad_group_name":"Noivas","campaign_name":"demand Gen - YT Retargeting","status":"ENABLED","impressions":113836,"clicks":6193,"cost":810.355521,"conversions":221.530964,"ctr":5.440282511683474,"average_cpc":0.13085023752623928,"cost_per_conversion":3.657978579463952},{"ad_group_name":"Todos","campaign_name":"demand Gen - YT Retargeting","status":"ENABLED","impressions":49765,"clicks":2564,"cost":344.44268,"conversions":88.650596,"ctr":5.152215412438461,"average_cpc":0.13433801872074883,"cost_per_conversion":3.8853961004390767}]

# --- ADS DAILY 3d ---
ads_daily_7d_raw = [{"date":"2026-04-30","impressions":"2904","clicks":"149","cost":"53981856","conversions":7.005123,"ctr":0.05130853994490358,"average_cpc":362294.3355704698,"cost_per_conversion":7706053.983634548},{"date":"2026-05-01","impressions":"3345","clicks":"213","cost":"62141528","conversions":6.974008,"ctr":0.06367713004484304,"average_cpc":291744.26291079813,"cost_per_conversion":8910446.905136902},{"date":"2026-05-02","impressions":"2840","clicks":"201","cost":"68210079","conversions":5.999157,"ctr":0.07077464788732395,"average_cpc":339353.62686567166,"cost_per_conversion":11369943.977128787}]

# --- ADS DAILY 90d ---
ads_daily_90d_raw = [{"date":"2026-02-01","impressions":"11762","clicks":"517","cost":"124518798","conversions":42.682844,"ctr":0.0439551096752253,"average_cpc":240848.73887814314,"cost_per_conversion":2917303.214378123},{"date":"2026-02-02","impressions":"15381","clicks":"614","cost":"155029815","conversions":56.414376,"ctr":0.03991938105454782,"average_cpc":252491.55537459283,"cost_per_conversion":2748055.1233962066},{"date":"2026-02-03","impressions":"8729","clicks":"424","cost":"117139712","conversions":40.024504,"ctr":0.04857371978462596,"average_cpc":276272.90566037735,"cost_per_conversion":2926699.9036390306},{"date":"2026-02-04","impressions":"8181","clicks":"403","cost":"107845728","conversions":33.899229,"ctr":0.049260481603715926,"average_cpc":267607.26550868485,"cost_per_conversion":3181362.2663807487},{"date":"2026-02-05","impressions":"10561","clicks":"476","cost":"132049642","conversions":42.069436,"ctr":0.045071489442287664,"average_cpc":277415.21428571426,"cost_per_conversion":3138849.8291253536},{"date":"2026-02-06","impressions":"8587","clicks":"431","cost":"109948441","conversions":27.094787,"ctr":0.050192150925818094,"average_cpc":255100.79118329467,"cost_per_conversion":4057918.6320970156},{"date":"2026-02-07","impressions":"8288","clicks":"405","cost":"97563383","conversions":30.990445,"ctr":0.048865830115830115,"average_cpc":240897.24197530863,"cost_per_conversion":3148176.2523900513},{"date":"2026-02-08","impressions":"8097","clicks":"461","cost":"109881058","conversions":42.002346,"ctr":0.05693466716067679,"average_cpc":238353.704989154,"cost_per_conversion":2616069.540496619},{"date":"2026-02-09","impressions":"8307","clicks":"440","cost":"126266278","conversions":32.680013,"ctr":0.05296737691103888,"average_cpc":286968.81363636366,"cost_per_conversion":3863715.6600886295},{"date":"2026-02-10","impressions":"6026","clicks":"374","cost":"107433083","conversions":37.845899,"ctr":0.062064387653501495,"average_cpc":287254.23262032086,"cost_per_conversion":2838698.1374124577},{"date":"2026-02-11","impressions":"6708","clicks":"438","cost":"106225669","conversions":44.9556,"ctr":0.06529516994633273,"average_cpc":242524.35844748857,"cost_per_conversion":2362901.8186833235},{"date":"2026-02-12","impressions":"6880","clicks":"393","cost":"96551760","conversions":37.979155,"ctr":0.05712209302325581,"average_cpc":245678.7786259542,"cost_per_conversion":2542230.3366149142},{"date":"2026-02-13","impressions":"7818","clicks":"438","cost":"92978121","conversions":29.371947,"ctr":0.056024558710667687,"average_cpc":212278.81506849316,"cost_per_conversion":3165541.630590577},{"date":"2026-02-14","impressions":"9734","clicks":"483","cost":"89379782","conversions":50.024613,"ctr":0.0496198890486953,"average_cpc":185051.30848861285,"cost_per_conversion":1786716.1111271365},{"date":"2026-02-15","impressions":"6203","clicks":"409","cost":"82460508","conversions":30.41167,"ctr":0.06593583749798484,"average_cpc":201614.93398533008,"cost_per_conversion":2711475.8249053736},{"date":"2026-02-16","impressions":"8161","clicks":"495","cost":"98611302","conversions":42.004799,"ctr":0.060654331577012624,"average_cpc":199214.75151515153,"cost_per_conversion":2347619.899335788},{"date":"2026-02-17","impressions":"5739","clicks":"343","cost":"69557860","conversions":31.999661,"ctr":0.05976650984492072,"average_cpc":202792.5947521866,"cost_per_conversion":2173706.1526995553},{"date":"2026-02-18","impressions":"6104","clicks":"347","cost":"96051273","conversions":38.164907,"ctr":0.05684796854521625,"average_cpc":276804.8213256484,"cost_per_conversion":2516743.2741287695},{"date":"2026-02-19","impressions":"4651","clicks":"345","cost":"89506746","conversions":24.090911,"ctr":0.07417759621586756,"average_cpc":259439.84347826088,"cost_per_conversion":3715374.067838282},{"date":"2026-02-20","impressions":"6147","clicks":"378","cost":"124505399","conversions":53.257973,"ctr":0.06149341142020498,"average_cpc":329379.3624338624,"cost_per_conversion":2337779.528334659},{"date":"2026-02-21","impressions":"7750","clicks":"475","cost":"114740442","conversions":35.892827,"ctr":0.06129032258064516,"average_cpc":241558.8252631579,"cost_per_conversion":3196751.317470758},{"date":"2026-02-22","impressions":"7372","clicks":"441","cost":"125636502","conversions":34.847561,"ctr":0.059820944112859466,"average_cpc":284890.0272108844,"cost_per_conversion":3605316.940258746},{"date":"2026-02-23","impressions":"6098","clicks":"389","cost":"140905699","conversions":26.498839,"ctr":0.06379140701869465,"average_cpc":362225.4473007712,"cost_per_conversion":5317429.152273426},{"date":"2026-02-24","impressions":"5965","clicks":"326","cost":"123507305","conversions":16.612417,"ctr":0.05465213746856664,"average_cpc":378856.763803681,"cost_per_conversion":7434637.897664138},{"date":"2026-02-25","impressions":"5870","clicks":"294","cost":"98451648","conversions":11.135889,"ctr":0.05008517887563884,"average_cpc":334869.55102040817,"cost_per_conversion":8840932.951109696},{"date":"2026-02-26","impressions":"6461","clicks":"331","cost":"95913682","conversions":14.918603,"ctr":0.05123045968116391,"average_cpc":289769.4320241692,"cost_per_conversion":6429132.942273483},{"date":"2026-02-27","impressions":"6569","clicks":"331","cost":"90660773","conversions":17.807252,"ctr":0.05038818693865124,"average_cpc":273899.6163141994,"cost_per_conversion":5091227.607718474},{"date":"2026-02-28","impressions":"7856","clicks":"401","cost":"91402397","conversions":15.448626,"ctr":0.05104378818737271,"average_cpc":227936.15211970074,"cost_per_conversion":5916538.920678124},{"date":"2026-03-01","impressions":"10590","clicks":"501","cost":"114539642","conversions":20.199067,"ctr":0.047308781869688385,"average_cpc":228622.03992015967,"cost_per_conversion":5670541.218562224},{"date":"2026-03-02","impressions":"10174","clicks":"519","cost":"124354748","conversions":19.005607,"ctr":0.0510123845095341,"average_cpc":239604.52408477842,"cost_per_conversion":6543055.84662463},{"date":"2026-03-03","impressions":"10811","clicks":"565","cost":"125841548","conversions":22.649652,"ctr":0.05226158542225511,"average_cpc":222728.40353982302,"cost_per_conversion":5556003.597759471},{"date":"2026-03-04","impressions":"11603","clicks":"486","cost":"117570086","conversions":16.80747,"ctr":0.041885719210549,"average_cpc":241913.75720164608,"cost_per_conversion":6995109.079474782},{"date":"2026-03-05","impressions":"6707","clicks":"384","cost":"101312958","conversions":11.002434,"ctr":0.05725361562546593,"average_cpc":263835.828125,"cost_per_conversion":9208231.378620405},{"date":"2026-03-06","impressions":"5310","clicks":"254","cost":"73054164","conversions":10.003939,"ctr":0.04783427495291902,"average_cpc":287614.8188976378,"cost_per_conversion":7302539.929521761},{"date":"2026-03-07","impressions":"7284","clicks":"393","cost":"77668482","conversions":13.992366,"ctr":0.05395387149917628,"average_cpc":197629.7251908397,"cost_per_conversion":5550775.472854269},{"date":"2026-03-08","impressions":"4054","clicks":"248","cost":"70113048","conversions":14.998616,"ctr":0.061174148988653185,"average_cpc":282713.9032258064,"cost_per_conversion":4674634.512944395},{"date":"2026-03-09","impressions":"5055","clicks":"270","cost":"90814142","conversions":11.001439,"ctr":0.05341246290801187,"average_cpc":336348.6740740741,"cost_per_conversion":8254751.219363213},{"date":"2026-03-10","impressions":"4581","clicks":"232","cost":"81236193","conversions":7.004503,"ctr":0.05064396419995634,"average_cpc":350156.0043103448,"cost_per_conversion":11597709.787546668},{"date":"2026-03-11","impressions":"4617","clicks":"226","cost":"102501520","conversions":11.000886,"ctr":0.04894953432965129,"average_cpc":453546.54867256636,"cost_per_conversion":9317569.512128387},{"date":"2026-03-12","impressions":"2949","clicks":"142","cost":"49363774","conversions":11.998382,"ctr":0.04815191590369617,"average_cpc":347632.21126760566,"cost_per_conversion":4114202.5649791784},{"date":"2026-03-13","impressions":"2851","clicks":"188","cost":"78304979","conversions":18.001453,"ctr":0.06594177481585409,"average_cpc":416515.84574468085,"cost_per_conversion":4349925.47546023},{"date":"2026-03-14","impressions":"3125","clicks":"199","cost":"69833419","conversions":11,"ctr":0.06368,"average_cpc":350921.7035175879,"cost_per_conversion":6348492.636363637},{"date":"2026-03-15","impressions":"2158","clicks":"159","cost":"65697049","conversions":15.000242,"ctr":0.07367933271547729,"average_cpc":413188.9874213837,"cost_per_conversion":4379732.606980607},{"date":"2026-03-16","impressions":"2716","clicks":"260","cost":"98800097","conversions":20.000243,"ctr":0.09572901325478646,"average_cpc":380000.3730769231,"cost_per_conversion":4939944.829670319},{"date":"2026-03-17","impressions":"2709","clicks":"175","cost":"70753756","conversions":10.990984,"ctr":0.06459948320413436,"average_cpc":404307.17714285717,"cost_per_conversion":6437435.992992075},{"date":"2026-03-18","impressions":"1383","clicks":"101","cost":"53915559","conversions":9.499408,"ctr":0.0730296456977585,"average_cpc":533817.4158415842,"cost_per_conversion":5675675.684211058},{"date":"2026-03-19","impressions":"2345","clicks":"128","cost":"60559873","conversions":9.5,"ctr":0.05458422174840085,"average_cpc":473124.0078125,"cost_per_conversion":6374723.47368421},{"date":"2026-03-20","impressions":"3648","clicks":"147","cost":"65006067","conversions":5.002066,"ctr":0.04029605263157895,"average_cpc":442218.14285714284,"cost_per_conversion":12995843.517458586},{"date":"2026-03-21","impressions":"1698","clicks":"101","cost":"39176608","conversions":5.998028,"ctr":0.059481743227326266,"average_cpc":387887.2079207921,"cost_per_conversion":6531581.3797468105},{"date":"2026-03-22","impressions":"1876","clicks":"125","cost":"75721287","conversions":9.998357,"ctr":0.06663113006396588,"average_cpc":605770.296,"cost_per_conversion":7573373.005184752},{"date":"2026-03-23","impressions":"2497","clicks":"158","cost":"108916901","conversions":13.000831,"ctr":0.06327593111734081,"average_cpc":689347.4746835442,"cost_per_conversion":8377687.626275582},{"date":"2026-03-24","impressions":"2112","clicks":"178","cost":"139200008","conversions":14.993997,"ctr":0.08428030303030302,"average_cpc":782022.5168539326,"cost_per_conversion":9283715.876427079},{"date":"2026-03-25","impressions":"1876","clicks":"157","cost":"101901474","conversions":12.00358,"ctr":0.08368869936034115,"average_cpc":649053.974522293,"cost_per_conversion":8489256.871699944},{"date":"2026-03-26","impressions":"1790","clicks":"155","cost":"95107429","conversions":15.991485,"ctr":0.08659217877094973,"average_cpc":613596.3161290323,"cost_per_conversion":5947379.433492261},{"date":"2026-03-27","impressions":"1937","clicks":"169","cost":"96517879","conversions":9.998918,"ctr":0.087248322147651,"average_cpc":571111.7100591715,"cost_per_conversion":9652832.336458806},{"date":"2026-03-28","impressions":"1359","clicks":"117","cost":"89617124","conversions":6.99561,"ctr":0.08609271523178808,"average_cpc":765958.3247863248,"cost_per_conversion":12810480.2869228},{"date":"2026-03-29","impressions":"1345","clicks":"95","cost":"67113691","conversions":8,"ctr":0.07063197026022305,"average_cpc":706459.9052631579,"cost_per_conversion":8389211.375},{"date":"2026-03-30","impressions":"1503","clicks":"148","cost":"90152114","conversions":12.999965,"ctr":0.09846972721224219,"average_cpc":609135.9054054054,"cost_per_conversion":6934796.670606421},{"date":"2026-03-31","impressions":"2215","clicks":"160","cost":"89049678","conversions":9,"ctr":0.07223476297968397,"average_cpc":556560.4875,"cost_per_conversion":9894408.666666666},{"date":"2026-04-01","impressions":"2193","clicks":"216","cost":"104349080","conversions":25.997427,"ctr":0.09849521203830369,"average_cpc":483097.5925925926,"cost_per_conversion":4013823.3679817626},{"date":"2026-04-02","impressions":"2745","clicks":"148","cost":"66623373","conversions":8.007192,"ctr":0.05391621129326048,"average_cpc":450157.9256756757,"cost_per_conversion":8320441.548048304},{"date":"2026-04-03","impressions":"1610","clicks":"121","cost":"60752722","conversions":7.024539,"ctr":0.07515527950310559,"average_cpc":502088.6115702479,"cost_per_conversion":8648641.853935184},{"date":"2026-04-04","impressions":"2419","clicks":"127","cost":"65409366","conversions":7.998266,"ctr":0.05250103348491112,"average_cpc":515034.3779527559,"cost_per_conversion":8177943.31921444},{"date":"2026-04-05","impressions":"2553","clicks":"141","cost":"63927919","conversions":6.000571,"ctr":0.055229142185663924,"average_cpc":453389.4964539007,"cost_per_conversion":10653639.295327062},{"date":"2026-04-06","impressions":"1265","clicks":"93","cost":"55190722","conversions":7.999578,"ctr":0.07351778656126483,"average_cpc":593448.623655914,"cost_per_conversion":6899204.183020655},{"date":"2026-04-07","impressions":"2031","clicks":"108","cost":"58442617","conversions":7,"ctr":0.053175775480059084,"average_cpc":541135.3425925926,"cost_per_conversion":8348945.285714285},{"date":"2026-04-08","impressions":"1191","clicks":"89","cost":"48522868","conversions":2.994852,"ctr":0.07472712006717044,"average_cpc":545200.7640449438,"cost_per_conversion":16202092.123417119},{"date":"2026-04-09","impressions":"1642","clicks":"105","cost":"55606127","conversions":8.000277,"ctr":0.06394640682095006,"average_cpc":529582.1619047619,"cost_per_conversion":6950525.213064497},{"date":"2026-04-10","impressions":"2042","clicks":"134","cost":"68884349","conversions":8,"ctr":0.06562193927522038,"average_cpc":514062.30597014923,"cost_per_conversion":8610543.625},{"date":"2026-04-11","impressions":"1638","clicks":"112","cost":"57479584","conversions":8.002992,"ctr":0.06837606837606838,"average_cpc":513210.5714285714,"cost_per_conversion":7182261.834074056},{"date":"2026-04-12","impressions":"1430","clicks":"92","cost":"56699747","conversions":6.009066,"ctr":0.06433566433566433,"average_cpc":616301.5978260869,"cost_per_conversion":9435700.489893105},{"date":"2026-04-13","impressions":"2008","clicks":"120","cost":"82788972","conversions":10.988432,"ctr":0.05976095617529881,"average_cpc":689908.1,"cost_per_conversion":7534193.4135825755},{"date":"2026-04-14","impressions":"1691","clicks":"114","cost":"64427381","conversions":7,"ctr":0.06741573033707865,"average_cpc":565152.4649122807,"cost_per_conversion":9203911.57142857},{"date":"2026-04-15","impressions":"950","clicks":"71","cost":"53547330","conversions":6.00014,"ctr":0.07473684210526316,"average_cpc":754187.7464788732,"cost_per_conversion":8924346.765242144},{"date":"2026-04-16","impressions":"1547","clicks":"102","cost":"61730018","conversions":5,"ctr":0.06593406593406594,"average_cpc":605196.2549019608,"cost_per_conversion":12346003.6},{"date":"2026-04-17","impressions":"1251","clicks":"86","cost":"48694793","conversions":2.000257,"ctr":0.06874500399680256,"average_cpc":566218.523255814,"cost_per_conversion":24344268.261528395},{"date":"2026-04-18","impressions":"1620","clicks":"111","cost":"56767570","conversions":5.999766,"ctr":0.06851851851851852,"average_cpc":511419.5495495495,"cost_per_conversion":9461630.670262806},{"date":"2026-04-19","impressions":"1706","clicks":"110","cost":"57449187","conversions":5,"ctr":0.06447831184056271,"average_cpc":522265.33636363636,"cost_per_conversion":11489837.4},{"date":"2026-04-20","impressions":"1350","clicks":"80","cost":"53116642","conversions":4.999331,"ctr":0.05925925925925926,"average_cpc":663958.025,"cost_per_conversion":10624749.99154887},{"date":"2026-04-21","impressions":"1246","clicks":"64","cost":"36010678","conversions":5.000141,"ctr":0.051364365971107544,"average_cpc":562666.84375,"cost_per_conversion":7201932.505503344},{"date":"2026-04-22","impressions":"1790","clicks":"106","cost":"48986573","conversions":4.002356,"ctr":0.05921787709497207,"average_cpc":462137.4811320755,"cost_per_conversion":12239434.22324251},{"date":"2026-04-23","impressions":"998","clicks":"78","cost":"34038569","conversions":7.00137,"ctr":0.0781563126252505,"average_cpc":436391.91025641025,"cost_per_conversion":4861701.209906061},{"date":"2026-04-24","impressions":"1495","clicks":"109","cost":"47530418","conversions":13.008034,"ctr":0.07290969899665552,"average_cpc":436058.88073394494,"cost_per_conversion":3653927.872574749},{"date":"2026-04-25","impressions":"1596","clicks":"102","cost":"35567189","conversions":7.998218,"ctr":0.06390977443609022,"average_cpc":348697.93137254904,"cost_per_conversion":4446889.16956252},{"date":"2026-04-26","impressions":"2149","clicks":"122","cost":"43519479","conversions":3,"ctr":0.05677059097254537,"average_cpc":356717.04098360654,"cost_per_conversion":14506493},{"date":"2026-04-27","impressions":"2390","clicks":"136","cost":"84969785","conversions":8.002437,"ctr":0.05690376569037657,"average_cpc":624777.8308823529,"cost_per_conversion":10617988.620216565},{"date":"2026-04-28","impressions":"2626","clicks":"162","cost":"64535720","conversions":8.994347,"ctr":0.06169078446306169,"average_cpc":398368.64197530865,"cost_per_conversion":7175142.342184486},{"date":"2026-04-29","impressions":"2940","clicks":"196","cost":"58529621","conversions":8.994041,"ctr":0.06666666666666667,"average_cpc":298620.5153061224,"cost_per_conversion":6507599.976473312},{"date":"2026-04-30","impressions":"2904","clicks":"149","cost":"53981856","conversions":7.005123,"ctr":0.05130853994490358,"average_cpc":362294.3355704698,"cost_per_conversion":7706053.983634548},{"date":"2026-05-01","impressions":"3345","clicks":"213","cost":"62141528","conversions":6.974008,"ctr":0.06367713004484304,"average_cpc":291744.26291079813,"cost_per_conversion":8910446.905136902},{"date":"2026-05-02","impressions":"2840","clicks":"201","cost":"68210079","conversions":5.999157,"ctr":0.07077464788732395,"average_cpc":339353.62686567166,"cost_per_conversion":11369943.977128787}]

# --- GA4 DAILY 3d ---
ga4_daily_7d_raw = {"rows":[{"dimensions":["20260430"],"metrics":["169","123","149.86562432520324","117","79","0.77235772357723576","0.22764227642276422"]},{"dimensions":["20260501"],"metrics":["185","151","131.75831758278147","141","85","0.67549668874172186","0.32450331125827814"]},{"dimensions":["20260502"],"metrics":["171","130","85.3933705153846","125","83","0.61538461538461542","0.38461538461538464"]}]}

# --- GA4 DAILY 90d ---
ga4_daily_90d_raw = {"rows":[{"dimensions":["20260201"],"metrics":["422","329","175.76446683282674","303","211","0.7264437689969605","0.2735562310030395"]},{"dimensions":["20260202"],"metrics":["453","374","153.90457528877005","354","245","0.65508021390374327","0.34491978609625668"]},{"dimensions":["20260203"],"metrics":["330","276","131.743544692029","261","169","0.68478260869565222","0.31521739130434784"]},{"dimensions":["20260204"],"metrics":["330","258","126.21949653875969","243","168","0.67441860465116277","0.32558139534883723"]},{"dimensions":["20260205"],"metrics":["354","301","123.00007701661129","283","189","0.59136212624584716","0.40863787375415284"]},{"dimensions":["20260206"],"metrics":["298","237","83.311199755274259","231","158","0.67510548523206748","0.32489451476793246"]},{"dimensions":["20260207"],"metrics":["323","261","99.154764743295019","245","153","0.67432950191570884","0.32567049808429116"]},{"dimensions":["20260208"],"metrics":["393","303","249.80308963366335","287","189","0.6633663366336634","0.33663366336633666"]},{"dimensions":["20260209"],"metrics":["359","277","111.45440742960288","261","174","0.67148014440433212","0.32851985559566788"]},{"dimensions":["20260210"],"metrics":["333","241","167.02235277593363","235","154","0.67634854771784236","0.32365145228215769"]},{"dimensions":["20260211"],"metrics":["358","284","99.806224440140852","267","162","0.66901408450704225","0.33098591549295775"]},{"dimensions":["20260212"],"metrics":["332","266","110.9069027631579","249","156","0.63533834586466165","0.36466165413533835"]},{"dimensions":["20260213"],"metrics":["359","283","101.12724999293286","266","165","0.70318021201413428","0.29681978798586572"]},{"dimensions":["20260214"],"metrics":["362","289","116.73679415224915","276","177","0.629757785467128","0.370242214532872"]},{"dimensions":["20260215"],"metrics":["348","257","190.53341021789885","249","136","0.642023346303502","0.35797665369649806"]},{"dimensions":["20260216"],"metrics":["428","344","114.37746000581396","315","169","0.67441860465116277","0.32558139534883723"]},{"dimensions":["20260217"],"metrics":["329","251","344.24382082071713","233","150","0.67729083665338641","0.32270916334661354"]},{"dimensions":["20260218"],"metrics":["302","222","163.99840557657657","208","111","0.72522522522522526","0.2747747747747748"]},{"dimensions":["20260219"],"metrics":["256","217","93.447172018433179","205","101","0.66820276497695852","0.33179723502304148"]},{"dimensions":["20260220"],"metrics":["356","253","156.89765750988141","230","124","0.71936758893280628","0.28063241106719367"]},{"dimensions":["20260221"],"metrics":["378","286","144.58004185314687","262","167","0.69580419580419584","0.30419580419580422"]},{"dimensions":["20260222"],"metrics":["395","284","143.27394471126757","265","143","0.67957746478873238","0.32042253521126762"]},{"dimensions":["20260223"],"metrics":["427","297","160.48021379461281","278","183","0.69360269360269355","0.30639730639730639"]},{"dimensions":["20260224"],"metrics":["294","222","77.414916193693713","210","130","0.65315315315315314","0.34684684684684686"]},{"dimensions":["20260225"],"metrics":["278","201","199.75070971144279","188","105","0.76616915422885568","0.23383084577114427"]},{"dimensions":["20260226"],"metrics":["281","229","834.17662012227072","216","119","0.65938864628820959","0.34061135371179041"]},{"dimensions":["20260227"],"metrics":["276","222","186.86088059459459","208","112","0.7072072072072072","0.2927927927927928"]},{"dimensions":["20260228"],"metrics":["300","256","88.497926699218738","242","140","0.63671875","0.36328125"]},{"dimensions":["20260301"],"metrics":["357","301","108.43948874086379","287","177","0.63455149501661134","0.36544850498338871"]},{"dimensions":["20260302"],"metrics":["365","314","130.35618496815286","295","164","0.6560509554140127","0.34394904458598724"]},{"dimensions":["20260303"],"metrics":["465","356","170.88896072752809","335","202","0.6853932584269663","0.3146067415730337"]},{"dimensions":["20260304"],"metrics":["323","275","108.18521395636365","252","162","0.70909090909090911","0.29090909090909089"]},{"dimensions":["20260305"],"metrics":["314","245","128.18977460816328","228","143","0.68163265306122445","0.3183673469387755"]},{"dimensions":["20260306"],"metrics":["235","189","162.52089576719578","174","103","0.63492063492063489","0.36507936507936506"]},{"dimensions":["20260307"],"metrics":["305","248","107.35607839919356","232","130","0.62903225806451613","0.37096774193548387"]},{"dimensions":["20260308"],"metrics":["240","184","87.9866974728261","175","106","0.66304347826086951","0.33695652173913043"]},{"dimensions":["20260309"],"metrics":["261","197","118.07451415228427","180","114","0.67005076142131981","0.32994923857868019"]},{"dimensions":["20260310"],"metrics":["227","177","97.234271220338982","166","98","0.6271186440677966","0.3728813559322034"]},{"dimensions":["20260311"],"metrics":["206","155","117.63214963225806","147","103","0.65806451612903227","0.34193548387096773"]},{"dimensions":["20260312"],"metrics":["149","121","114.18137586776859","114","73","0.65289256198347112","0.34710743801652894"]},{"dimensions":["20260313"],"metrics":["203","148","151.46538179054053","140","109","0.71621621621621623","0.28378378378378377"]},{"dimensions":["20260314"],"metrics":["189","144","120.14199379861108","137","108","0.72916666666666663","0.27083333333333331"]},{"dimensions":["20260315"],"metrics":["177","139","167.16410176258989","135","99","0.73381294964028776","0.26618705035971224"]},{"dimensions":["20260316"],"metrics":["246","195","85.890851671794877","188","139","0.69230769230769229","0.30769230769230771"]},{"dimensions":["20260317"],"metrics":["191","152","101.49528749342105","144","108","0.72368421052631582","0.27631578947368424"]},{"dimensions":["20260318"],"metrics":["145","108","115.96440573148148","103","77","0.85185185185185186","0.14814814814814814"]},{"dimensions":["20260319"],"metrics":["130","107","97.397446775700914","104","73","0.73831775700934577","0.26168224299065418"]},{"dimensions":["20260320"],"metrics":["161","138","134.20981305072462","133","111","0.77536231884057971","0.22463768115942029"]},{"dimensions":["20260321"],"metrics":["103","76","122.70810538157895","72","45","0.75","0.25"]},{"dimensions":["20260322"],"metrics":["138","103","100.01383489320389","98","72","0.75728155339805825","0.24271844660194175"]},{"dimensions":["20260323"],"metrics":["162","136","105.09161043382353","128","101","0.69852941176470584","0.3014705882352941"]},{"dimensions":["20260324"],"metrics":["168","131","75.781293259541982","127","83","0.6717557251908397","0.3282442748091603"]},{"dimensions":["20260325"],"metrics":["150","105","96.46073951428572","103","71","0.74285714285714288","0.25714285714285712"]},{"dimensions":["20260326"],"metrics":["141","102","88.841529009803921","97","61","0.71568627450980393","0.28431372549019607"]},{"dimensions":["20260327"],"metrics":["152","124","78.703204032258043","118","76","0.64516129032258063","0.35483870967741937"]},{"dimensions":["20260328"],"metrics":["137","109","124.00822104587158","100","64","0.65137614678899081","0.34862385321100919"]},{"dimensions":["20260329"],"metrics":["118","90","83.297640433333328","83","47","0.7","0.3"]},{"dimensions":["20260330"],"metrics":["161","126","86.084395460317481","122","87","0.68253968253968256","0.31746031746031744"]},{"dimensions":["20260331"],"metrics":["135","104","132.92238125","100","67","0.63461538461538458","0.36538461538461536"]},{"dimensions":["20260401"],"metrics":["204","171","133.47656884210525","164","120","0.79532163742690054","0.2046783625730994"]},{"dimensions":["20260402"],"metrics":["140","108","139.55769430555554","104","60","0.71296296296296291","0.28703703703703703"]},{"dimensions":["20260403"],"metrics":["129","94","100.83224087234041","90","56","0.62765957446808507","0.37234042553191488"]},{"dimensions":["20260404"],"metrics":["123","98","117.2490955510204","95","62","0.673469387755102","0.32653061224489793"]},{"dimensions":["20260405"],"metrics":["130","104","170.28132645192306","101","74","0.76923076923076927","0.23076923076923078"]},{"dimensions":["20260406"],"metrics":["80","61","136.53676729508197","58","32","0.67213114754098358","0.32786885245901637"]},{"dimensions":["20260407"],"metrics":["115","95","195.49652557894734","88","60","0.70526315789473681","0.29473684210526313"]},{"dimensions":["20260408"],"metrics":["102","84","75.296734452380946","78","56","0.6785714285714286","0.32142857142857145"]},{"dimensions":["20260409"],"metrics":["136","95","135.41538892631579","89","63","0.67368421052631577","0.32631578947368423"]},{"dimensions":["20260410"],"metrics":["144","109","103.1432486972477","107","75","0.73394495412844041","0.26605504587155965"]},{"dimensions":["20260411"],"metrics":["110","83","148.29967189156625","77","57","0.73493975903614461","0.26506024096385544"]},{"dimensions":["20260412"],"metrics":["105","70","293.38666424285714","69","47","0.8","0.2"]},{"dimensions":["20260413"],"metrics":["132","101","86.281477910891084","97","66","0.72277227722772275","0.27722772277227725"]},{"dimensions":["20260414"],"metrics":["108","78","124.19640841025641","77","53","0.69230769230769229","0.30769230769230771"]},{"dimensions":["20260415"],"metrics":["102","79","86.153107949367083","69","46","0.73417721518987344","0.26582278481012656"]},{"dimensions":["20260416"],"metrics":["91","70","86.8961865857143","69","51","0.74285714285714288","0.25714285714285712"]},{"dimensions":["20260417"],"metrics":["75","62","519.46458579032264","59","43","0.64516129032258063","0.35483870967741937"]},{"dimensions":["20260418"],"metrics":["110","84","68.897076142857145","83","67","0.76190476190476186","0.23809523809523808"]},{"dimensions":["20260419"],"metrics":["116","84","1024.7928083809525","81","57","0.75","0.25"]},{"dimensions":["20260420"],"metrics":["111","87","182.93711710344829","80","59","0.7931034482758621","0.20689655172413793"]},{"dimensions":["20260421"],"metrics":["130","71","340.92657950704222","66","48","0.74647887323943662","0.25352112676056338"]},{"dimensions":["20260422"],"metrics":["107","89","98.439864876404485","86","65","0.7528089887640449","0.24719101123595505"]},{"dimensions":["20260423"],"metrics":["116","70","279.9204829","61","37","0.87142857142857144","0.12857142857142856"]},{"dimensions":["20260424"],"metrics":["89","78","75.509563743589737","77","60","0.62820512820512819","0.37179487179487181"]},{"dimensions":["20260425"],"metrics":["134","97","158.11998892783504","89","62","0.75257731958762886","0.24742268041237114"]},{"dimensions":["20260426"],"metrics":["94","71","166.8817728028169","66","38","0.676056338028169","0.323943661971831"]},{"dimensions":["20260427"],"metrics":["156","120","123.72831312500001","112","75","0.7","0.3"]},{"dimensions":["20260428"],"metrics":["146","120","99.833103858333331","109","62","0.6333333333333333","0.36666666666666664"]},{"dimensions":["20260429"],"metrics":["177","134","157.12979208955224","125","85","0.60447761194029848","0.39552238805970147"]},{"dimensions":["20260430"],"metrics":["169","123","149.86562432520324","117","79","0.77235772357723576","0.22764227642276422"]},{"dimensions":["20260501"],"metrics":["185","151","131.75831758278147","141","85","0.67549668874172186","0.32450331125827814"]},{"dimensions":["20260502"],"metrics":["171","130","85.3933705153846","125","83","0.61538461538461542","0.38461538461538464"]}]}

# --- GA4 PAGES 3d ---
ga4_pages_7d_raw = {"rows":[{"dimensions":["/vestidos-de-noivas","session_start"],"metrics":["247","0"]},{"dimensions":["/","session_start"],"metrics":["140","0"]},{"dimensions":["/vestidos-de-noivas","Whatsapp LPs"],"metrics":["33","0"]},{"dimensions":["/vestido-de-festas","Whatsapp LPs"],"metrics":["5","0"]},{"dimensions":["/","Whatsapp LPs"],"metrics":["4","0"]},{"dimensions":["/15anos-teste","Whatsapp LPs"],"metrics":["2","0"]},{"dimensions":["/blank-1","session_start"],"metrics":["2","0"]},{"dimensions":["/vestido-de-festas","session_start"],"metrics":["1","0"]},{"dimensions":["/vestidos-de-noivas","Whatsapp"],"metrics":["1","0"]}]}

# --- GA4 PAGES 14d ---
ga4_pages_14d_raw = {"rows":[{"dimensions":["/vestidos-de-noivas","session_start"],"metrics":["890","0"]},{"dimensions":["/","session_start"],"metrics":["548","0"]},{"dimensions":["/vestidos-de-noivas","Whatsapp LPs"],"metrics":["111","0"]},{"dimensions":["/","Whatsapp LPs"],"metrics":["35","0"]},{"dimensions":["/vestido-de-festas","Whatsapp LPs"],"metrics":["22","0"]},{"dimensions":["/15anos-teste","session_start"],"metrics":["7","0"]},{"dimensions":["/15anos-teste","Whatsapp LPs"],"metrics":["6","0"]},{"dimensions":["/blank-1","session_start"],"metrics":["4","0"]},{"dimensions":["/vestido-de-festas","session_start"],"metrics":["4","0"]},{"dimensions":["/vestidos-de-noivas","Whatsapp"],"metrics":["3","0"]},{"dimensions":["/vestidos-de-noivas","generate_lead"],"metrics":["1","0"]}]}

# --- GA4 PAGES 90d ---
ga4_pages_90d_raw = {"rows":[{"dimensions":["/vestidos-de-noivas","session_start"],"metrics":["11081","0"]},{"dimensions":["/","session_start"],"metrics":["4061","0"]},{"dimensions":["/vestidos-de-noivas","Whatsapp LPs"],"metrics":["843","0"]},{"dimensions":["/vestidos-de-noivas","Whatsapp"],"metrics":["525","0"]},{"dimensions":["/","Whatsapp LPs"],"metrics":["243","0"]},{"dimensions":["/vestido-de-festas","Whatsapp LPs"],"metrics":["168","0"]},{"dimensions":["/","Whatsapp"],"metrics":["166","0"]},{"dimensions":["/15anos-teste","Whatsapp LPs"],"metrics":["57","0"]},{"dimensions":["/15anos-teste","session_start"],"metrics":["55","0"]},{"dimensions":["/vestido-de-festas","session_start"],"metrics":["37","0"]},{"dimensions":["/blank-1","session_start"],"metrics":["32","0"]},{"dimensions":["/vestidos-de-noivas","generate_lead"],"metrics":["20","0"]},{"dimensions":["/15anos-teste","Whatsapp"],"metrics":["10","0"]},{"dimensions":["/vestido-de-festas","Whatsapp"],"metrics":["6","0"]},{"dimensions":["/blank-1","Whatsapp"],"metrics":["4","0"]},{"dimensions":["/blank","session_start"],"metrics":["1","0"]}]}

# --- GA4 CHANNELS 3d ---
ga4_channels_7d_raw = {"rows":[{"dimensions":["Cross-network"],"metrics":["274","248","0","0.63138686131386856","116.75525025912408"]},{"dimensions":["Paid Search"],"metrics":["59","57","0","0.76271186440677963","135.00450155932202"]},{"dimensions":["Direct"],"metrics":["33","32","0","0.81818181818181823","110.60637857575759"]},{"dimensions":["Referral"],"metrics":["23","21","0","0.91304347826086951","182.24424108695649"]},{"dimensions":["Organic Search"],"metrics":["12","12","0","0.91666666666666663","133.55176766666668"]},{"dimensions":["Unassigned"],"metrics":["3","3","0","0","9.8875003333333336"]}]}
ga4_ch_events_7d_raw = {"rows":[{"dimensions":["Cross-network","Whatsapp LPs"],"metrics":["29"]},{"dimensions":["Referral","Whatsapp LPs"],"metrics":["6"]},{"dimensions":["Paid Search","Whatsapp LPs"],"metrics":["5"]},{"dimensions":["Direct","Whatsapp LPs"],"metrics":["3"]},{"dimensions":["Cross-network","Whatsapp"],"metrics":["1"]},{"dimensions":["Organic Search","Whatsapp LPs"],"metrics":["1"]}]}

# --- GA4 CHANNELS 14d ---
ga4_channels_14d_raw = {"rows":[{"dimensions":["Cross-network"],"metrics":["920","756","0","0.67282608695652169","155.08364712608696"]},{"dimensions":["Paid Search"],"metrics":["300","276","0","0.65","124.57759292666667"]},{"dimensions":["Direct"],"metrics":["189","184","0","0.83597883597883593","69.321866238095225"]},{"dimensions":["Organic Search"],"metrics":["43","42","0","0.76744186046511631","231.89896053488374"]},{"dimensions":["Referral"],"metrics":["33","28","0","0.90909090909090906","187.31170542424243"]},{"dimensions":["Unassigned"],"metrics":["13","12","0","0","116.05167307692308"]},{"dimensions":["Organic Social"],"metrics":["1","1","0","1","34.280609"]}]}
ga4_ch_events_14d_raw = {"rows":[{"dimensions":["Cross-network","Whatsapp LPs"],"metrics":["104"]},{"dimensions":["Paid Search","Whatsapp LPs"],"metrics":["30"]},{"dimensions":["Direct","Whatsapp LPs"],"metrics":["28"]},{"dimensions":["Referral","Whatsapp LPs"],"metrics":["7"]},{"dimensions":["Organic Search","Whatsapp LPs"],"metrics":["4"]},{"dimensions":["Cross-network","Whatsapp"],"metrics":["1"]},{"dimensions":["Direct","Whatsapp"],"metrics":["1"]},{"dimensions":["Direct","generate_lead"],"metrics":["1"]},{"dimensions":["Paid Search","Whatsapp"],"metrics":["1"]},{"dimensions":["Unassigned","Whatsapp LPs"],"metrics":["1"]}]}

# --- GA4 CHANNELS 90d ---
ga4_channels_90d_raw = {"rows":[{"dimensions":["Paid Search"],"metrics":["12408","9052","0","0.68020631850419089","136.59276553675048"]},{"dimensions":["Direct"],"metrics":["1579","1490","0","0.85560481317289427","87.183330948068416"]},{"dimensions":["Cross-network"],"metrics":["1073","901","0","0.71388630009319665","233.11713299347622"]},{"dimensions":["Organic Search"],"metrics":["416","346","0","0.66105769230769229","536.18530316586543"]},{"dimensions":["Unassigned"],"metrics":["143","135","0","0.02097902097902098","292.852884013986"]},{"dimensions":["Referral"],"metrics":["39","27","0","0.89743589743589747","398.73971043589739"]},{"dimensions":["Organic Social"],"metrics":["14","10","0","0.6428571428571429","110.16284585714286"]},{"dimensions":["Organic Video"],"metrics":["3","3","0","1","98.314786666666677"]}]}
ga4_ch_events_90d_raw = {"rows":[{"dimensions":["Paid Search","Whatsapp LPs"],"metrics":["825"]},{"dimensions":["Paid Search","Whatsapp"],"metrics":["622"]},{"dimensions":["Direct","Whatsapp LPs"],"metrics":["278"]},{"dimensions":["Cross-network","Whatsapp LPs"],"metrics":["122"]},{"dimensions":["Direct","Whatsapp"],"metrics":["62"]},{"dimensions":["Organic Search","Whatsapp LPs"],"metrics":["50"]},{"dimensions":["Unassigned","Whatsapp LPs"],"metrics":["19"]},{"dimensions":["Referral","Whatsapp LPs"],"metrics":["16"]},{"dimensions":["Cross-network","Whatsapp"],"metrics":["11"]},{"dimensions":["Direct","generate_lead"],"metrics":["9"]},{"dimensions":["Organic Search","Whatsapp"],"metrics":["9"]},{"dimensions":["Paid Search","generate_lead"],"metrics":["9"]},{"dimensions":["Unassigned","Whatsapp"],"metrics":["5"]},{"dimensions":["Referral","Whatsapp"],"metrics":["2"]},{"dimensions":["Organic Social","Whatsapp LPs"],"metrics":["1"]},{"dimensions":["Referral","generate_lead"],"metrics":["1"]},{"dimensions":["Unassigned","generate_lead"],"metrics":["1"]}]}


# ============================================================================
# PROCESS AND SAVE
# ============================================================================

if __name__ == "__main__":
    print("=== Processing campaigns ===")
    save("campaigns", 3, parse_campaigns(campaigns_7d_raw))
    save("campaigns", 14, parse_campaigns(campaigns_14d_raw))
    save("campaigns", 90, parse_campaigns(campaigns_90d_raw))

    print("\n=== Processing ad groups ===")
    save("adgroups", 3, parse_adgroups(adgroups_7d_raw))
    save("adgroups", 14, parse_adgroups(adgroups_14d_raw))
    save("adgroups", 90, parse_adgroups(adgroups_90d_raw))

    print("\n=== Processing ads daily ===")
    save("ads_daily", 3, parse_ads_daily(ads_daily_7d_raw))
    # 14d subset from 90d
    save("ads_daily", 14, parse_ads_daily(ads_daily_90d_raw[-14:]))
    save("ads_daily", 90, parse_ads_daily(ads_daily_90d_raw))

    print("\n=== Processing GA4 daily ===")
    save("ga4_daily", 3, parse_ga4_daily(ga4_daily_7d_raw))
    # 14d subset from 90d
    ga4_90d_rows = ga4_daily_90d_raw["rows"]
    save("ga4_daily", 14, parse_ga4_daily({"rows": ga4_90d_rows[-14:]}))
    save("ga4_daily", 90, parse_ga4_daily(ga4_daily_90d_raw))

    print("\n=== Processing GA4 pages ===")
    save("ga4_pages", 3, parse_ga4_pages(ga4_pages_7d_raw))
    save("ga4_pages", 14, parse_ga4_pages(ga4_pages_14d_raw))
    save("ga4_pages", 90, parse_ga4_pages(ga4_pages_90d_raw))

    print("\n=== Processing GA4 channels ===")
    save("ga4_channels", 3, parse_ga4_channels(ga4_channels_7d_raw, ga4_ch_events_7d_raw))
    save("ga4_channels", 14, parse_ga4_channels(ga4_channels_14d_raw, ga4_ch_events_14d_raw))
    save("ga4_channels", 90, parse_ga4_channels(ga4_channels_90d_raw, ga4_ch_events_90d_raw))

    print("\nDone! All caches saved.")
