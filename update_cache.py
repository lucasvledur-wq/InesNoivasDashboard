"""Update caches: real 90d data + events columns on all periods' pages."""
import json
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
TODAY = str(date.today())


def save(name, days, rows):
    path = DATA_DIR / f"{name}_{days}d.json"
    path.write_text(json.dumps({"date": TODAY, "rows": rows}, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  {path.name}: {len(rows)} rows")


# (Whatsapp LPs, Whatsapp, generate_lead) per page per period
EVENTS = {
    7: {"/vestidos-de-noivas": (52, 2, 1), "/": (21, 0, 0), "/vestido-de-festas": (10, 0, 0), "/15anos-teste": (1, 0, 0)},
    14: {"/vestidos-de-noivas": (84, 3, 1), "/": (35, 0, 0), "/vestido-de-festas": (17, 0, 0), "/15anos-teste": (6, 0, 0)},
    30: {"/vestidos-de-noivas": (224, 8, 5), "/": (79, 0, 0), "/vestido-de-festas": (45, 0, 0), "/15anos-teste": (11, 0, 0)},
    90: {"/vestidos-de-noivas": (834, 556, 20), "/": (239, 167, 0), "/vestido-de-festas": (163, 6, 0), "/15anos-teste": (56, 10, 0), "/blank-1": (0, 4, 0)},
}


def add_events(rows, period):
    evts = EVENTS.get(period, {})
    for r in rows:
        page = r["Page"]
        wlp, wha, gl = evts.get(page, (0, 0, 0))
        r["Whatsapp LP"] = wlp + wha
        r["Generate Lead"] = gl


# ── Update 7d, 14d, 30d pages with events ──
for p in [7, 14, 30]:
    path = DATA_DIR / f"ga4_pages_{p}d.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    add_events(data["rows"], p)
    data["date"] = TODAY
    path.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Updated ga4_pages_{p}d.json with events")

# ══════════════════════════════════════════
# 90 DAYS — Real data from Zapier API
# ══════════════════════════════════════════
print("\n=== 90 DAYS ===")

# ── Campaigns 90d ──
save("campaigns", 90, [
    {"Campaign": "[Search] - Noivas", "Status": "ENABLED", "Impressions": 45608, "Clicks": 4037,
     "CTR (%)": 8.85, "CPC (R$)": 1.03, "Cost (R$)": 4143.70, "Conversions": 369.0,
     "Cost/Conv (R$)": 11.23, "Conv. Rate (%)": 9.14,
     "Impr. Share (%)": 16.4, "Lost IS Budget (%)": 2.2, "Lost IS Rank (%)": 81.4,
     "Top IS (%)": 73.8, "Abs. Top IS (%)": 38.6},
    {"Campaign": "[Search] - Institucional", "Status": "ENABLED", "Impressions": 3004, "Clicks": 616,
     "CTR (%)": 20.51, "CPC (R$)": 0.97, "Cost (R$)": 596.14, "Conversions": 78.0,
     "Cost/Conv (R$)": 7.65, "Conv. Rate (%)": 12.66,
     "Impr. Share (%)": 85.5, "Lost IS Budget (%)": 3.7, "Lost IS Rank (%)": 10.8,
     "Top IS (%)": 78.5, "Abs. Top IS (%)": 44.7},
    {"Campaign": "Pmax rmkt Noivas", "Status": "ENABLED", "Impressions": 187756, "Clicks": 9109,
     "CTR (%)": 4.85, "CPC (R$)": 0.17, "Cost (R$)": 1589.54, "Conversions": 797.6,
     "Cost/Conv (R$)": 1.99, "Conv. Rate (%)": 8.76,
     "Impr. Share (%)": 10.0, "Lost IS Budget (%)": 14.6, "Lost IS Rank (%)": 82.7,
     "Top IS (%)": None, "Abs. Top IS (%)": None},
    {"Campaign": "demand Gen - YT Retargeting", "Status": "ENABLED", "Impressions": 159531, "Clicks": 8484,
     "CTR (%)": 5.32, "CPC (R$)": 0.13, "Cost (R$)": 1117.14, "Conversions": 307.2,
     "Cost/Conv (R$)": 3.64, "Conv. Rate (%)": 3.62,
     "Impr. Share (%)": None, "Lost IS Budget (%)": None, "Lost IS Rank (%)": None,
     "Top IS (%)": None, "Abs. Top IS (%)": None},
])

# ── Ad Groups 90d ──
save("adgroups", 90, [
    {"Ad Group": "Vestido Casamento", "Campaign": "[Search] - Noivas",
     "Impressions": 41658, "Clicks": 3707, "CTR (%)": 8.90,
     "CPC (R$)": 1.01, "Cost (R$)": 3739.44, "Conversions": 329.5,
     "Cost/Conv (R$)": 11.35, "Conv. Rate (%)": 8.89},
    {"Ad Group": "Branding", "Campaign": "[Search] - Institucional",
     "Impressions": 3004, "Clicks": 616, "CTR (%)": 20.51,
     "CPC (R$)": 0.97, "Cost (R$)": 596.14, "Conversions": 78.0,
     "Cost/Conv (R$)": 7.65, "Conv. Rate (%)": 12.66},
    {"Ad Group": "Marcas Vestidos Noivas", "Campaign": "[Search] - Noivas",
     "Impressions": 3950, "Clicks": 330, "CTR (%)": 8.35,
     "CPC (R$)": 1.23, "Cost (R$)": 404.26, "Conversions": 39.5,
     "Cost/Conv (R$)": 10.24, "Conv. Rate (%)": 11.97},
    {"Ad Group": "Noivas", "Campaign": "demand Gen - YT Retargeting",
     "Impressions": 110955, "Clicks": 5989, "CTR (%)": 5.40,
     "CPC (R$)": 0.13, "Cost (R$)": 782.85, "Conversions": 219.5,
     "Cost/Conv (R$)": 3.57, "Conv. Rate (%)": 3.66},
    {"Ad Group": "Todos", "Campaign": "demand Gen - YT Retargeting",
     "Impressions": 48576, "Clicks": 2495, "CTR (%)": 5.14,
     "CPC (R$)": 0.13, "Cost (R$)": 334.29, "Conversions": 87.6,
     "Cost/Conv (R$)": 3.81, "Conv. Rate (%)": 3.51},
])

# ── GA4 Daily 90d (91 rows: Jan 31 - Apr 30) ──
daily_raw = [
    ("2026-01-31", 303, 231, 114.1, 0, 220, 135, 71.9, 28.1),
    ("2026-02-01", 422, 329, 175.8, 0, 303, 211, 72.6, 27.4),
    ("2026-02-02", 453, 374, 153.9, 0, 354, 245, 65.5, 34.5),
    ("2026-02-03", 330, 276, 131.7, 0, 261, 169, 68.5, 31.5),
    ("2026-02-04", 330, 258, 126.2, 0, 243, 168, 67.4, 32.6),
    ("2026-02-05", 354, 301, 123.0, 0, 283, 189, 59.1, 40.9),
    ("2026-02-06", 298, 237, 83.3, 0, 231, 158, 67.5, 32.5),
    ("2026-02-07", 323, 261, 99.2, 0, 245, 153, 67.4, 32.6),
    ("2026-02-08", 393, 303, 249.8, 0, 287, 189, 66.3, 33.7),
    ("2026-02-09", 359, 277, 111.5, 0, 261, 174, 67.1, 32.9),
    ("2026-02-10", 333, 241, 167.0, 0, 235, 154, 67.6, 32.4),
    ("2026-02-11", 358, 284, 99.8, 0, 267, 162, 66.9, 33.1),
    ("2026-02-12", 332, 266, 110.9, 0, 249, 156, 63.5, 36.5),
    ("2026-02-13", 359, 283, 101.1, 0, 266, 165, 70.3, 29.7),
    ("2026-02-14", 362, 289, 116.7, 0, 276, 177, 63.0, 37.0),
    ("2026-02-15", 348, 257, 190.5, 0, 249, 136, 64.2, 35.8),
    ("2026-02-16", 428, 344, 114.4, 0, 315, 169, 67.4, 32.6),
    ("2026-02-17", 329, 251, 344.2, 0, 233, 150, 67.7, 32.3),
    ("2026-02-18", 302, 222, 164.0, 0, 208, 111, 72.5, 27.5),
    ("2026-02-19", 256, 217, 93.4, 0, 205, 101, 66.8, 33.2),
    ("2026-02-20", 356, 253, 156.9, 0, 230, 124, 71.9, 28.1),
    ("2026-02-21", 378, 286, 144.6, 0, 262, 167, 69.6, 30.4),
    ("2026-02-22", 395, 284, 143.3, 0, 265, 143, 68.0, 32.0),
    ("2026-02-23", 427, 297, 160.5, 0, 278, 183, 69.4, 30.6),
    ("2026-02-24", 294, 222, 77.4, 0, 210, 130, 65.3, 34.7),
    ("2026-02-25", 278, 201, 199.8, 0, 188, 105, 76.6, 23.4),
    ("2026-02-26", 281, 229, 834.2, 0, 216, 119, 65.9, 34.1),
    ("2026-02-27", 276, 222, 186.9, 0, 208, 112, 70.7, 29.3),
    ("2026-02-28", 300, 256, 88.5, 0, 242, 140, 63.7, 36.3),
    ("2026-03-01", 357, 301, 108.4, 0, 287, 177, 63.5, 36.5),
    ("2026-03-02", 365, 314, 130.4, 0, 295, 164, 65.6, 34.4),
    ("2026-03-03", 465, 356, 170.9, 0, 335, 202, 68.5, 31.5),
    ("2026-03-04", 323, 275, 108.2, 0, 252, 162, 70.9, 29.1),
    ("2026-03-05", 314, 245, 128.2, 0, 228, 143, 68.2, 31.8),
    ("2026-03-06", 235, 189, 162.5, 0, 174, 103, 63.5, 36.5),
    ("2026-03-07", 305, 248, 107.4, 0, 232, 130, 62.9, 37.1),
    ("2026-03-08", 240, 184, 88.0, 0, 175, 106, 66.3, 33.7),
    ("2026-03-09", 261, 197, 118.1, 0, 180, 114, 67.0, 33.0),
    ("2026-03-10", 227, 177, 97.2, 0, 166, 98, 62.7, 37.3),
    ("2026-03-11", 206, 155, 117.6, 0, 147, 103, 65.8, 34.2),
    ("2026-03-12", 149, 121, 114.2, 0, 114, 73, 65.3, 34.7),
    ("2026-03-13", 203, 148, 151.5, 0, 140, 109, 71.6, 28.4),
    ("2026-03-14", 189, 144, 120.1, 0, 137, 108, 72.9, 27.1),
    ("2026-03-15", 177, 139, 167.2, 0, 135, 99, 73.4, 26.6),
    ("2026-03-16", 246, 195, 85.9, 0, 188, 139, 69.2, 30.8),
    ("2026-03-17", 191, 152, 101.5, 0, 144, 108, 72.4, 27.6),
    ("2026-03-18", 145, 108, 116.0, 0, 103, 77, 85.2, 14.8),
    ("2026-03-19", 130, 107, 97.4, 0, 104, 73, 73.8, 26.2),
    ("2026-03-20", 161, 138, 134.2, 0, 133, 111, 77.5, 22.5),
    ("2026-03-21", 103, 76, 122.7, 0, 72, 45, 75.0, 25.0),
    ("2026-03-22", 138, 103, 100.0, 0, 98, 72, 75.7, 24.3),
    ("2026-03-23", 162, 136, 105.1, 0, 128, 101, 69.9, 30.1),
    ("2026-03-24", 168, 131, 75.8, 0, 127, 83, 67.2, 32.8),
    ("2026-03-25", 150, 105, 96.5, 0, 103, 71, 74.3, 25.7),
    ("2026-03-26", 141, 102, 88.8, 0, 97, 61, 71.6, 28.4),
    ("2026-03-27", 152, 124, 78.7, 0, 118, 76, 64.5, 35.5),
    ("2026-03-28", 137, 109, 124.0, 0, 100, 64, 65.1, 34.9),
    ("2026-03-29", 118, 90, 83.3, 0, 83, 47, 70.0, 30.0),
    ("2026-03-30", 161, 126, 86.1, 0, 122, 87, 68.3, 31.7),
    ("2026-03-31", 135, 104, 132.9, 0, 100, 67, 63.5, 36.5),
    ("2026-04-01", 204, 171, 133.5, 0, 164, 120, 79.5, 20.5),
    ("2026-04-02", 140, 108, 139.6, 0, 104, 60, 71.3, 28.7),
    ("2026-04-03", 129, 94, 100.8, 0, 90, 56, 62.8, 37.2),
    ("2026-04-04", 123, 98, 117.2, 0, 95, 62, 67.3, 32.7),
    ("2026-04-05", 130, 104, 170.3, 0, 101, 74, 76.9, 23.1),
    ("2026-04-06", 80, 61, 136.5, 0, 58, 32, 67.2, 32.8),
    ("2026-04-07", 115, 95, 195.5, 0, 88, 60, 70.5, 29.5),
    ("2026-04-08", 102, 84, 75.3, 0, 78, 56, 67.9, 32.1),
    ("2026-04-09", 136, 95, 135.4, 0, 89, 63, 67.4, 32.6),
    ("2026-04-10", 144, 109, 103.1, 0, 107, 75, 73.4, 26.6),
    ("2026-04-11", 110, 83, 148.3, 0, 77, 57, 73.5, 26.5),
    ("2026-04-12", 105, 70, 293.4, 0, 69, 47, 80.0, 20.0),
    ("2026-04-13", 132, 101, 86.3, 0, 97, 66, 72.3, 27.7),
    ("2026-04-14", 108, 78, 124.2, 0, 77, 53, 69.2, 30.8),
    ("2026-04-15", 102, 79, 86.2, 0, 69, 46, 73.4, 26.6),
    ("2026-04-16", 91, 70, 86.9, 0, 69, 51, 74.3, 25.7),
    ("2026-04-17", 75, 62, 519.5, 0, 59, 43, 64.5, 35.5),
    ("2026-04-18", 110, 84, 68.9, 0, 83, 67, 76.2, 23.8),
    ("2026-04-19", 116, 84, 1024.8, 0, 81, 57, 75.0, 25.0),
    ("2026-04-20", 111, 87, 182.9, 0, 80, 59, 79.3, 20.7),
    ("2026-04-21", 130, 71, 340.9, 0, 66, 48, 74.6, 25.4),
    ("2026-04-22", 107, 89, 98.4, 0, 86, 65, 75.3, 24.7),
    ("2026-04-23", 116, 70, 279.9, 0, 61, 37, 87.1, 12.9),
    ("2026-04-24", 89, 78, 75.5, 0, 77, 60, 62.8, 37.2),
    ("2026-04-25", 134, 97, 158.1, 0, 89, 62, 75.3, 24.7),
    ("2026-04-26", 94, 71, 166.9, 0, 66, 38, 67.6, 32.4),
    ("2026-04-27", 156, 120, 123.7, 0, 112, 75, 70.0, 30.0),
    ("2026-04-28", 146, 120, 99.8, 0, 109, 62, 63.3, 36.7),
    ("2026-04-29", 177, 134, 157.1, 0, 125, 85, 60.4, 39.6),
    ("2026-04-30", 169, 123, 149.9, 0, 117, 79, 77.2, 22.8),
]
save("ga4_daily", 90, [
    {"Date": d[0], "Pageviews": d[1], "Sessions": d[2], "Avg. Session (s)": d[3],
     "Conversions": d[4], "Users": d[5], "New Users": d[6],
     "Engagement Rate (%)": d[7], "Bounce Rate (%)": d[8]}
    for d in daily_raw
])

# ── GA4 Pages 90d + events ──
pages_90d = [
    {"Page": "/vestidos-de-noivas", "Pageviews": 13912, "Avg. Session (s)": 134, "Conversions": 0},
    {"Page": "/", "Pageviews": 4877, "Avg. Session (s)": 151, "Conversions": 0},
    {"Page": "/vestido-de-festas", "Pageviews": 646, "Avg. Session (s)": 74, "Conversions": 0},
    {"Page": "/15anos-teste", "Pageviews": 616, "Avg. Session (s)": 82, "Conversions": 0},
    {"Page": "/blank-1", "Pageviews": 40, "Avg. Session (s)": 92, "Conversions": 0},
    {"Page": "/blank", "Pageviews": 1, "Avg. Session (s)": 25, "Conversions": 0},
]
add_events(pages_90d, 90)
save("ga4_pages", 90, pages_90d)

# ── GA4 Channels 90d ──
save("ga4_channels", 90, [
    {"Channel": "Paid Search", "Sessions": 12590, "Users": 9159, "Conversions": 0, "Engagement Rate (%)": 68.3, "Avg. Session (s)": 136.0},
    {"Channel": "Direct", "Sessions": 1577, "Users": 1488, "Conversions": 0, "Engagement Rate (%)": 85.6, "Avg. Session (s)": 86.6},
    {"Channel": "Cross-network", "Sessions": 883, "Users": 751, "Conversions": 0, "Engagement Rate (%)": 74.3, "Avg. Session (s)": 261.8},
    {"Channel": "Organic Search", "Sessions": 414, "Users": 344, "Conversions": 0, "Engagement Rate (%)": 65.9, "Avg. Session (s)": 538.8},
    {"Channel": "Unassigned", "Sessions": 143, "Users": 135, "Conversions": 0, "Engagement Rate (%)": 2.1, "Avg. Session (s)": 293.6},
    {"Channel": "Referral", "Sessions": 18, "Users": 9, "Conversions": 0, "Engagement Rate (%)": 88.9, "Avg. Session (s)": 732.9},
    {"Channel": "Organic Social", "Sessions": 14, "Users": 10, "Conversions": 0, "Engagement Rate (%)": 64.3, "Avg. Session (s)": 110.2},
    {"Channel": "Organic Video", "Sessions": 3, "Users": 3, "Conversions": 0, "Engagement Rate (%)": 100.0, "Avg. Session (s)": 98.3},
])

print("\nAll 90d cache files updated with real data!")
print("All pages caches updated with Whatsapp LP + Generate Lead events!")
