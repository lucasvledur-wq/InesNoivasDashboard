"""Rebuilds meta_7d/14d/30d.json and meta_creatives_7d/14d/30d.json from Windsor raw data."""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

RAW_ADG_FILE = r"C:\Users\Lucas\.claude\projects\C--Users-Lucas-OneDrive--rea-de-Trabalho-Python-Code-Dashboard-Ines-Noivas\fdffc12c-122a-411a-8db4-bf9b1d3b5482\tool-results\mcp-306cdd32-09eb-4557-aef3-0c736f1843cd-get_data-1778161922981.txt"
RAW_AD_FILE  = r"C:\Users\Lucas\.claude\projects\C--Users-Lucas-OneDrive--rea-de-Trabalho-Python-Code-Dashboard-Ines-Noivas\fdffc12c-122a-411a-8db4-bf9b1d3b5482\tool-results\mcp-306cdd32-09eb-4557-aef3-0c736f1843cd-get_data-1778161959650.txt"

with open(RAW_ADG_FILE, encoding="utf-8") as f:
    DATA_ADG_30D = json.load(f)["result"]

with open(RAW_AD_FILE, encoding="utf-8") as f:
    DATA_AD_30D = json.load(f)["result"]


def transform_adgroup(raw):
    rows = []
    for r in raw:
        ctr = r.get("ctr") or 0
        msgs = r.get("actions_onsite_conversion_messaging_conversation_started_7d") or 0
        rows.append({
            "Data": r.get("date", ""),
            "Campanha": r.get("campaign", ""),
            "Conjunto": r.get("adset_name", ""),
            "Investimento (R$)": round(r.get("spend") or 0, 2),
            "Impressões": r.get("impressions") or 0,
            "Alcance": r.get("reach") or 0,
            "Cliques no Link": r.get("link_clicks") or 0,
            "CTR (%)": round(ctr * 100, 2),
            "Mensagens WhatsApp": msgs,
            "Visitas ao Perfil": r.get("instagram_profile_visits") or 0,
            "Seguidores Novos": r.get("actions_like") or 0,
            "Engajamento": r.get("actions_post_engagement") or 0,
        })
    return rows


def transform_creatives(raw):
    rows = []
    for r in raw:
        ctr = r.get("ctr") or 0
        msgs = r.get("actions_onsite_conversion_messaging_conversation_started_7d") or 0
        rows.append({
            "Data": r.get("date", ""),
            "Anúncio": r.get("ad_name", ""),
            "Campanha": r.get("campaign", ""),
            "Conjunto": r.get("adset_name", ""),
            "Investimento (R$)": round(r.get("spend") or 0, 2),
            "Impressões": r.get("impressions") or 0,
            "Alcance": r.get("reach") or 0,
            "Cliques no Link": r.get("link_clicks") or 0,
            "CTR (%)": round(ctr * 100, 2),
            "Mensagens WhatsApp": msgs,
            "Engajamento": r.get("actions_post_engagement") or 0,
        })
    return rows


today = date.today()
cutoff_14 = today - timedelta(days=14)
cutoff_7  = today - timedelta(days=7)

today_str = str(today)
data_dir = Path(__file__).parent / "data"

for days, cutoff in [(7, cutoff_7), (14, cutoff_14), (30, None)]:
    if cutoff:
        adg = [r for r in DATA_ADG_30D if datetime.strptime(r["date"], "%Y-%m-%d").date() >= cutoff]
        ads = [r for r in DATA_AD_30D  if datetime.strptime(r["date"], "%Y-%m-%d").date() >= cutoff]
    else:
        adg, ads = DATA_ADG_30D, DATA_AD_30D

    # adgroup-level cache
    path = data_dir / f"meta_{days}d.json"
    payload = {"date": today_str, "rows": transform_adgroup(adg)}
    path.write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Saved {path} ({len(adg)} rows)")

    # creative-level cache
    path2 = data_dir / f"meta_creatives_{days}d.json"
    payload2 = {"date": today_str, "rows": transform_creatives(ads)}
    path2.write_text(json.dumps(payload2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Saved {path2} ({len(ads)} rows)")
