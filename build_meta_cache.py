"""One-off script: reads Windsor 30d raw data and writes meta_7d/14d/30d.json caches."""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

RAW_FILE = r"C:\Users\Lucas\.claude\projects\C--Users-Lucas-OneDrive--rea-de-Trabalho-Python-Code-Dashboard-Ines-Noivas\fdffc12c-122a-411a-8db4-bf9b1d3b5482\tool-results\mcp-306cdd32-09eb-4557-aef3-0c736f1843cd-get_data-1778158631834.txt"

with open(RAW_FILE, encoding="utf-8") as f:
    DATA_30D = json.load(f)["result"]


def transform(raw):
    rows = []
    for r in raw:
        camp = r.get("campaign", "")
        is_whatsapp = any(k in camp.lower() for k in ["whatsapp", "wats", "eng whats"])
        clicks = r.get("clicks") or 0
        link_clicks = r.get("link_clicks") or 0
        ctr = r.get("ctr") or 0
        rows.append({
            "Data": r.get("date", ""),
            "Campanha": camp,
            "Conjunto": r.get("adset_name", ""),
            "Investimento (R$)": round(r.get("spend") or 0, 2),
            "Impressões": r.get("impressions") or 0,
            "Alcance": r.get("reach") or 0,
            "Cliques no Link": link_clicks,
            "CTR (%)": round(ctr * 100, 2),
            "Mensagens WhatsApp": clicks if is_whatsapp else 0,
            "Visitas ao Perfil": r.get("instagram_profile_visits") or 0,
            "Seguidores Novos": r.get("actions_like") or 0,
            "Engajamento": r.get("actions_post_engagement") or 0,
        })
    return rows


today = date.today()
cutoff_14 = today - timedelta(days=14)
cutoff_7 = today - timedelta(days=7)

data_14 = [r for r in DATA_30D if datetime.strptime(r["date"], "%Y-%m-%d").date() >= cutoff_14]
data_7 = [r for r in DATA_30D if datetime.strptime(r["date"], "%Y-%m-%d").date() >= cutoff_7]

today_str = str(today)
data_dir = Path(__file__).parent / "data"
for days, raw in [(7, data_7), (14, data_14), (30, DATA_30D)]:
    rows = transform(raw)
    payload = {"date": today_str, "rows": rows}
    path = data_dir / f"meta_{days}d.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Saved {path} with {len(rows)} rows")
