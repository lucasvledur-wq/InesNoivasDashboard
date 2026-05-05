"""Process and save Google Ads daily data + GA4 channel conversion events for all periods."""
import json
from datetime import date
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent / "data"
TODAY = str(date.today())


def save(name, days, rows):
    path = DATA_DIR / f"{name}_{days}d.json"
    path.write_text(json.dumps({"date": TODAY, "rows": rows}, ensure_ascii=False), encoding="utf-8")
    print(f"  {path.name}: {len(rows)} rows")


def process_ads_daily(raw_list):
    """Convert raw Google Ads daily data (cost in micros) to processed rows."""
    rows = []
    for r in raw_list:
        cost = int(r["cost"]) / 1_000_000 if isinstance(r["cost"], (int, str)) else r["cost"] / 1_000_000
        clicks = int(r["clicks"])
        impr = int(r["impressions"])
        conv = float(r["conversions"])
        rows.append({
            "Date": r["date"],
            "Clicks": clicks,
            "Impressions": impr,
            "Cost (R$)": round(cost, 2),
            "Conversions": round(conv, 1),
            "CTR (%)": round(clicks / impr * 100, 2) if impr > 0 else 0,
            "CPC (R$)": round(cost / clicks, 2) if clicks > 0 else 0,
            "Cost/Lead (R$)": round(cost / conv, 2) if conv > 0 else 0,
        })
    return rows


def parse_ga4_channel_events(ga4_rows):
    """Parse GA4 API rows into channel -> (whatsapp_total, generate_lead) dict."""
    ch_events = defaultdict(lambda: [0, 0])
    for r in ga4_rows:
        dims = r.get("dimensionValues") or r.get("dimensions")
        mets = r.get("metricValues") or r.get("metrics")
        channel = dims[0] if isinstance(dims[0], str) else dims[0].get("value", dims[0])
        event = dims[1] if isinstance(dims[1], str) else dims[1].get("value", dims[1])
        count = int(mets[0] if isinstance(mets[0], str) else mets[0].get("value", mets[0]))
        if event in ("Whatsapp LPs", "Whatsapp"):
            ch_events[channel][0] += count
        elif event == "generate_lead":
            ch_events[channel][1] += count
    return ch_events


def update_channels_cache(days, ga4_rows):
    """Add Whatsapp LP and Generate Lead columns to channels cache."""
    ch_events = parse_ga4_channel_events(ga4_rows)
    ch_path = DATA_DIR / f"ga4_channels_{days}d.json"
    ch_data = json.loads(ch_path.read_text(encoding="utf-8"))
    for r in ch_data["rows"]:
        ch = r["Channel"]
        wlp, gl = ch_events.get(ch, [0, 0])
        r["Whatsapp LP"] = wlp
        r["Generate Lead"] = gl
    ch_data["date"] = TODAY
    ch_path.write_text(json.dumps(ch_data, ensure_ascii=False), encoding="utf-8")
    print(f"  Updated ga4_channels_{days}d.json with events")


# ══════════════════════════════════════════════════════════════════════════
# Google Ads Daily — 30d data (from Zapier API)
# ══════════════════════════════════════════════════════════════════════════
print("=== Google Ads Daily ===")

raw_30d = [
    {"date":"2026-04-02","clicks":148,"impressions":2745,"cost":66623373,"conversions":8.007192},
    {"date":"2026-04-03","clicks":121,"impressions":1610,"cost":60752722,"conversions":7.024539},
    {"date":"2026-04-04","clicks":127,"impressions":2419,"cost":65409366,"conversions":7.997923},
    {"date":"2026-04-05","clicks":141,"impressions":2553,"cost":63927919,"conversions":6},
    {"date":"2026-04-06","clicks":93,"impressions":1265,"cost":55190722,"conversions":7.998485},
    {"date":"2026-04-07","clicks":108,"impressions":2031,"cost":58442617,"conversions":7},
    {"date":"2026-04-08","clicks":89,"impressions":1191,"cost":48522868,"conversions":2.994852},
    {"date":"2026-04-09","clicks":105,"impressions":1642,"cost":55606127,"conversions":8.000277},
    {"date":"2026-04-10","clicks":134,"impressions":2042,"cost":68884349,"conversions":8},
    {"date":"2026-04-11","clicks":112,"impressions":1638,"cost":57479584,"conversions":8.002421},
    {"date":"2026-04-12","clicks":92,"impressions":1430,"cost":56699747,"conversions":6.009066},
    {"date":"2026-04-13","clicks":120,"impressions":2008,"cost":82788972,"conversions":10.988432},
    {"date":"2026-04-14","clicks":114,"impressions":1691,"cost":64427381,"conversions":7},
    {"date":"2026-04-15","clicks":71,"impressions":950,"cost":53547330,"conversions":6.00014},
    {"date":"2026-04-16","clicks":102,"impressions":1547,"cost":61730018,"conversions":5},
    {"date":"2026-04-17","clicks":86,"impressions":1251,"cost":48694793,"conversions":2.000257},
    {"date":"2026-04-18","clicks":111,"impressions":1620,"cost":56767570,"conversions":5.999766},
    {"date":"2026-04-19","clicks":110,"impressions":1706,"cost":57449187,"conversions":5},
    {"date":"2026-04-20","clicks":80,"impressions":1350,"cost":53116642,"conversions":4.999331},
    {"date":"2026-04-21","clicks":64,"impressions":1246,"cost":36010678,"conversions":5.000141},
    {"date":"2026-04-22","clicks":106,"impressions":1790,"cost":48986573,"conversions":4},
    {"date":"2026-04-23","clicks":78,"impressions":998,"cost":34038569,"conversions":7.00137},
    {"date":"2026-04-24","clicks":109,"impressions":1495,"cost":47530418,"conversions":13.008034},
    {"date":"2026-04-25","clicks":102,"impressions":1596,"cost":35567189,"conversions":7.998218},
    {"date":"2026-04-26","clicks":122,"impressions":2149,"cost":43519479,"conversions":3},
    {"date":"2026-04-27","clicks":136,"impressions":2390,"cost":84969785,"conversions":8.002437},
    {"date":"2026-04-28","clicks":162,"impressions":2626,"cost":64535720,"conversions":8.994347},
    {"date":"2026-04-29","clicks":196,"impressions":2940,"cost":58529621,"conversions":8.992973},
    {"date":"2026-04-30","clicks":149,"impressions":2904,"cost":53981856,"conversions":7.998993},
    {"date":"2026-05-01","clicks":213,"impressions":3348,"cost":62141528,"conversions":5.972804},
]

rows_30d = process_ads_daily(raw_30d)
save("ads_daily", 30, rows_30d)
save("ads_daily", 7, rows_30d[-7:])
save("ads_daily", 14, rows_30d[-14:])

# Google Ads Daily — 90d data (from Zapier API, 2026-02-01 to 2026-04-30)
raw_90d = [
    {"date":"2026-02-01","clicks":"517","impressions":"11762","cost":"124518798","conversions":42.682844},
    {"date":"2026-02-02","clicks":"614","impressions":"15381","cost":"155029815","conversions":56.414376},
    {"date":"2026-02-03","clicks":"424","impressions":"8729","cost":"117139712","conversions":40.024504},
    {"date":"2026-02-04","clicks":"403","impressions":"8181","cost":"107845728","conversions":33.899229},
    {"date":"2026-02-05","clicks":"476","impressions":"10561","cost":"132049642","conversions":42.069436},
    {"date":"2026-02-06","clicks":"431","impressions":"8587","cost":"109948441","conversions":27.094787},
    {"date":"2026-02-07","clicks":"405","impressions":"8288","cost":"97563383","conversions":30.990445},
    {"date":"2026-02-08","clicks":"461","impressions":"8097","cost":"109881058","conversions":42.002346},
    {"date":"2026-02-09","clicks":"440","impressions":"8307","cost":"126266278","conversions":32.680013},
    {"date":"2026-02-10","clicks":"374","impressions":"6026","cost":"107433083","conversions":37.845899},
    {"date":"2026-02-11","clicks":"438","impressions":"6708","cost":"106225669","conversions":44.9556},
    {"date":"2026-02-12","clicks":"393","impressions":"6880","cost":"96551760","conversions":37.979155},
    {"date":"2026-02-13","clicks":"438","impressions":"7818","cost":"92978121","conversions":29.371947},
    {"date":"2026-02-14","clicks":"483","impressions":"9734","cost":"89379782","conversions":50.024613},
    {"date":"2026-02-15","clicks":"409","impressions":"6203","cost":"82460508","conversions":30.41167},
    {"date":"2026-02-16","clicks":"495","impressions":"8161","cost":"98611302","conversions":42.004799},
    {"date":"2026-02-17","clicks":"343","impressions":"5739","cost":"69557860","conversions":31.999661},
    {"date":"2026-02-18","clicks":"347","impressions":"6104","cost":"96051273","conversions":38.164907},
    {"date":"2026-02-19","clicks":"345","impressions":"4651","cost":"89506746","conversions":24.090911},
    {"date":"2026-02-20","clicks":"378","impressions":"6147","cost":"124505399","conversions":53.257973},
    {"date":"2026-02-21","clicks":"475","impressions":"7750","cost":"114740442","conversions":35.892827},
    {"date":"2026-02-22","clicks":"441","impressions":"7372","cost":"125636502","conversions":34.847561},
    {"date":"2026-02-23","clicks":"389","impressions":"6098","cost":"140905699","conversions":26.498839},
    {"date":"2026-02-24","clicks":"326","impressions":"5965","cost":"123507305","conversions":16.612417},
    {"date":"2026-02-25","clicks":"294","impressions":"5870","cost":"98451648","conversions":11.135889},
    {"date":"2026-02-26","clicks":"331","impressions":"6461","cost":"95913682","conversions":14.918603},
    {"date":"2026-02-27","clicks":"331","impressions":"6569","cost":"90660773","conversions":17.807252},
    {"date":"2026-02-28","clicks":"401","impressions":"7856","cost":"91402397","conversions":15.448626},
    {"date":"2026-03-01","clicks":"501","impressions":"10590","cost":"114539642","conversions":20.199067},
    {"date":"2026-03-02","clicks":"519","impressions":"10174","cost":"124354748","conversions":19.005607},
    {"date":"2026-03-03","clicks":"565","impressions":"10811","cost":"125841548","conversions":22.649652},
    {"date":"2026-03-04","clicks":"486","impressions":"11603","cost":"117570086","conversions":16.80747},
    {"date":"2026-03-05","clicks":"384","impressions":"6707","cost":"101312958","conversions":11.002434},
    {"date":"2026-03-06","clicks":"254","impressions":"5310","cost":"73054164","conversions":10.003939},
    {"date":"2026-03-07","clicks":"393","impressions":"7284","cost":"77668482","conversions":13.992366},
    {"date":"2026-03-08","clicks":"248","impressions":"4054","cost":"70113048","conversions":14.998616},
    {"date":"2026-03-09","clicks":"270","impressions":"5055","cost":"90814142","conversions":11.001439},
    {"date":"2026-03-10","clicks":"232","impressions":"4581","cost":"81236193","conversions":7.004503},
    {"date":"2026-03-11","clicks":"226","impressions":"4617","cost":"102501520","conversions":11.000886},
    {"date":"2026-03-12","clicks":"142","impressions":"2949","cost":"49363774","conversions":11.998382},
    {"date":"2026-03-13","clicks":"188","impressions":"2851","cost":"78304979","conversions":18.001453},
    {"date":"2026-03-14","clicks":"199","impressions":"3125","cost":"69833419","conversions":11},
    {"date":"2026-03-15","clicks":"159","impressions":"2158","cost":"65697049","conversions":15.000242},
    {"date":"2026-03-16","clicks":"260","impressions":"2716","cost":"98800097","conversions":20.000243},
    {"date":"2026-03-17","clicks":"175","impressions":"2709","cost":"70753756","conversions":10.990984},
    {"date":"2026-03-18","clicks":"101","impressions":"1383","cost":"53915559","conversions":9.499408},
    {"date":"2026-03-19","clicks":"128","impressions":"2345","cost":"60559873","conversions":9.5},
    {"date":"2026-03-20","clicks":"147","impressions":"3648","cost":"65006067","conversions":5.002066},
    {"date":"2026-03-21","clicks":"101","impressions":"1698","cost":"39176608","conversions":5.998028},
    {"date":"2026-03-22","clicks":"125","impressions":"1876","cost":"75721287","conversions":9.998357},
    {"date":"2026-03-23","clicks":"158","impressions":"2497","cost":"108916901","conversions":13.000831},
    {"date":"2026-03-24","clicks":"178","impressions":"2112","cost":"139200008","conversions":14.993997},
    {"date":"2026-03-25","clicks":"157","impressions":"1876","cost":"101901474","conversions":12.00358},
    {"date":"2026-03-26","clicks":"155","impressions":"1790","cost":"95107429","conversions":15.991485},
    {"date":"2026-03-27","clicks":"169","impressions":"1937","cost":"96517879","conversions":9.998918},
    {"date":"2026-03-28","clicks":"117","impressions":"1359","cost":"89617124","conversions":6.99561},
    {"date":"2026-03-29","clicks":"95","impressions":"1345","cost":"67113691","conversions":8},
    {"date":"2026-03-30","clicks":"148","impressions":"1503","cost":"90152114","conversions":12.999965},
    {"date":"2026-03-31","clicks":"160","impressions":"2215","cost":"89049678","conversions":9},
    {"date":"2026-04-01","clicks":"216","impressions":"2193","cost":"104349080","conversions":25.997427},
    {"date":"2026-04-02","clicks":"148","impressions":"2745","cost":"66623373","conversions":8.007192},
    {"date":"2026-04-03","clicks":"121","impressions":"1610","cost":"60752722","conversions":7.024539},
    {"date":"2026-04-04","clicks":"127","impressions":"2419","cost":"65409366","conversions":7.997923},
    {"date":"2026-04-05","clicks":"141","impressions":"2553","cost":"63927919","conversions":6},
    {"date":"2026-04-06","clicks":"93","impressions":"1265","cost":"55190722","conversions":7.998485},
    {"date":"2026-04-07","clicks":"108","impressions":"2031","cost":"58442617","conversions":7},
    {"date":"2026-04-08","clicks":"89","impressions":"1191","cost":"48522868","conversions":2.994852},
    {"date":"2026-04-09","clicks":"105","impressions":"1642","cost":"55606127","conversions":8.000277},
    {"date":"2026-04-10","clicks":"134","impressions":"2042","cost":"68884349","conversions":8},
    {"date":"2026-04-11","clicks":"112","impressions":"1638","cost":"57479584","conversions":8.002421},
    {"date":"2026-04-12","clicks":"92","impressions":"1430","cost":"56699747","conversions":6.009066},
    {"date":"2026-04-13","clicks":"120","impressions":"2008","cost":"82788972","conversions":10.988432},
    {"date":"2026-04-14","clicks":"114","impressions":"1691","cost":"64427381","conversions":7},
    {"date":"2026-04-15","clicks":"71","impressions":"950","cost":"53547330","conversions":6.00014},
    {"date":"2026-04-16","clicks":"102","impressions":"1547","cost":"61730018","conversions":5},
    {"date":"2026-04-17","clicks":"86","impressions":"1251","cost":"48694793","conversions":2.000257},
    {"date":"2026-04-18","clicks":"111","impressions":"1620","cost":"56767570","conversions":5.999766},
    {"date":"2026-04-19","clicks":"110","impressions":"1706","cost":"57449187","conversions":5},
    {"date":"2026-04-20","clicks":"80","impressions":"1350","cost":"53116642","conversions":4.999331},
    {"date":"2026-04-21","clicks":"64","impressions":"1246","cost":"36010678","conversions":5.000141},
    {"date":"2026-04-22","clicks":"106","impressions":"1790","cost":"48986573","conversions":4},
    {"date":"2026-04-23","clicks":"78","impressions":"998","cost":"34038569","conversions":7.00137},
    {"date":"2026-04-24","clicks":"109","impressions":"1495","cost":"47530418","conversions":13.008034},
    {"date":"2026-04-25","clicks":"102","impressions":"1596","cost":"35567189","conversions":7.998218},
    {"date":"2026-04-26","clicks":"122","impressions":"2149","cost":"43519479","conversions":3},
    {"date":"2026-04-27","clicks":"136","impressions":"2390","cost":"84969785","conversions":8.002437},
    {"date":"2026-04-28","clicks":"162","impressions":"2626","cost":"64535720","conversions":8.994347},
    {"date":"2026-04-29","clicks":"196","impressions":"2940","cost":"58529621","conversions":8.992973},
    {"date":"2026-04-30","clicks":"149","impressions":"2904","cost":"53981856","conversions":7.998993},
]

rows_90d = process_ads_daily(raw_90d)
save("ads_daily", 90, rows_90d)

# ══════════════════════════════════════════════════════════════════════════
# GA4 Channel Conversion Events — all periods
# ══════════════════════════════════════════════════════════════════════════
print("\n=== GA4 Channel Events ===")

# 7d events
events_7d = [
    {"dimensionValues": ["Cross-network", "Whatsapp LPs"], "metricValues": ["41"]},
    {"dimensionValues": ["Unassigned", "Whatsapp LPs"], "metricValues": ["16"]},
    {"dimensionValues": ["Direct", "Whatsapp LPs"], "metricValues": ["13"]},
    {"dimensionValues": ["Paid Search", "Whatsapp LPs"], "metricValues": ["12"]},
    {"dimensionValues": ["Referral", "Whatsapp LPs"], "metricValues": ["2"]},
    {"dimensionValues": ["Cross-network", "Whatsapp"], "metricValues": ["1"]},
    {"dimensionValues": ["Direct", "Whatsapp"], "metricValues": ["1"]},
    {"dimensionValues": ["Direct", "generate_lead"], "metricValues": ["1"]},
    {"dimensionValues": ["Organic Search", "Whatsapp LPs"], "metricValues": ["1"]},
]
update_channels_cache(7, events_7d)

# 14d events
events_14d = [
    {"dimensionValues": ["Cross-network", "Whatsapp LPs"], "metricValues": ["78"]},
    {"dimensionValues": ["Direct", "Whatsapp LPs"], "metricValues": ["30"]},
    {"dimensionValues": ["Paid Search", "Whatsapp LPs"], "metricValues": ["26"]},
    {"dimensionValues": ["Unassigned", "Whatsapp LPs"], "metricValues": ["16"]},
    {"dimensionValues": ["Organic Search", "Whatsapp LPs"], "metricValues": ["4"]},
    {"dimensionValues": ["Referral", "Whatsapp LPs"], "metricValues": ["2"]},
    {"dimensionValues": ["Cross-network", "Whatsapp"], "metricValues": ["1"]},
    {"dimensionValues": ["Direct", "Whatsapp"], "metricValues": ["1"]},
    {"dimensionValues": ["Direct", "generate_lead"], "metricValues": ["1"]},
    {"dimensionValues": ["Paid Search", "Whatsapp"], "metricValues": ["1"]},
]
update_channels_cache(14, events_14d)

# 30d events
events_30d = [
    {"dimensionValues": ["Paid Search", "Whatsapp LPs"], "metricValues": ["141"]},
    {"dimensionValues": ["Cross-network", "Whatsapp LPs"], "metricValues": ["91"]},
    {"dimensionValues": ["Direct", "Whatsapp LPs"], "metricValues": ["70"]},
    {"dimensionValues": ["Unassigned", "Whatsapp LPs"], "metricValues": ["20"]},
    {"dimensionValues": ["Organic Search", "Whatsapp LPs"], "metricValues": ["14"]},
    {"dimensionValues": ["Paid Search", "Whatsapp"], "metricValues": ["6"]},
    {"dimensionValues": ["Paid Search", "generate_lead"], "metricValues": ["4"]},
    {"dimensionValues": ["Referral", "Whatsapp LPs"], "metricValues": ["2"]},
    {"dimensionValues": ["Cross-network", "Whatsapp"], "metricValues": ["1"]},
    {"dimensionValues": ["Direct", "Whatsapp"], "metricValues": ["1"]},
    {"dimensionValues": ["Direct", "generate_lead"], "metricValues": ["1"]},
    {"dimensionValues": ["Organic Social", "Whatsapp LPs"], "metricValues": ["1"]},
]
update_channels_cache(30, events_30d)

# 90d events
events_90d = [
    {"dimensionValues": ["Paid Search", "Whatsapp LPs"], "metricValues": ["822"]},
    {"dimensionValues": ["Paid Search", "Whatsapp"], "metricValues": ["622"]},
    {"dimensionValues": ["Direct", "Whatsapp LPs"], "metricValues": ["275"]},
    {"dimensionValues": ["Cross-network", "Whatsapp LPs"], "metricValues": ["99"]},
    {"dimensionValues": ["Direct", "Whatsapp"], "metricValues": ["62"]},
    {"dimensionValues": ["Organic Search", "Whatsapp LPs"], "metricValues": ["50"]},
    {"dimensionValues": ["Unassigned", "Whatsapp LPs"], "metricValues": ["19"]},
    {"dimensionValues": ["Cross-network", "Whatsapp"], "metricValues": ["11"]},
    {"dimensionValues": ["Referral", "Whatsapp LPs"], "metricValues": ["11"]},
    {"dimensionValues": ["Direct", "generate_lead"], "metricValues": ["9"]},
    {"dimensionValues": ["Organic Search", "Whatsapp"], "metricValues": ["9"]},
    {"dimensionValues": ["Paid Search", "generate_lead"], "metricValues": ["9"]},
    {"dimensionValues": ["Unassigned", "Whatsapp"], "metricValues": ["5"]},
    {"dimensionValues": ["Referral", "Whatsapp"], "metricValues": ["2"]},
    {"dimensionValues": ["Organic Social", "Whatsapp LPs"], "metricValues": ["1"]},
    {"dimensionValues": ["Referral", "generate_lead"], "metricValues": ["1"]},
    {"dimensionValues": ["Unassigned", "generate_lead"], "metricValues": ["1"]},
]
update_channels_cache(90, events_90d)

print("\nAll done!")
