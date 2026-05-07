"""Build Instagram organic data caches from Windsor raw data."""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

daily_30d = [
    {"date":"2026-04-07","comments":31,"follower_count_1d":70,"likes":1084,"reach":15208,"replies":1,"saves":92,"shares":523,"total_interactions":2310,"views":35601},
    {"date":"2026-04-08","comments":28,"follower_count_1d":59,"likes":1241,"reach":18055,"replies":0,"saves":98,"shares":579,"total_interactions":2581,"views":36074},
    {"date":"2026-04-09","comments":40,"follower_count_1d":66,"likes":1187,"reach":17365,"replies":2,"saves":129,"shares":559,"total_interactions":2540,"views":37340},
    {"date":"2026-04-10","comments":55,"follower_count_1d":66,"likes":1362,"reach":18955,"replies":0,"saves":120,"shares":514,"total_interactions":2614,"views":36182},
    {"date":"2026-04-11","comments":51,"follower_count_1d":67,"likes":1777,"reach":24882,"replies":0,"saves":126,"shares":719,"total_interactions":3466,"views":46908},
    {"date":"2026-04-12","comments":53,"follower_count_1d":82,"likes":1808,"reach":24678,"replies":0,"saves":159,"shares":708,"total_interactions":3530,"views":49710},
    {"date":"2026-04-13","comments":35,"follower_count_1d":74,"likes":1268,"reach":18226,"replies":2,"saves":95,"shares":604,"total_interactions":2668,"views":42352},
    {"date":"2026-04-14","comments":39,"follower_count_1d":73,"likes":914,"reach":15220,"replies":0,"saves":64,"shares":448,"total_interactions":1955,"views":36128},
    {"date":"2026-04-15","comments":50,"follower_count_1d":68,"likes":1151,"reach":18399,"replies":0,"saves":93,"shares":462,"total_interactions":2271,"views":39428},
    {"date":"2026-04-16","comments":41,"follower_count_1d":59,"likes":1070,"reach":17835,"replies":0,"saves":103,"shares":473,"total_interactions":2205,"views":40805},
    {"date":"2026-04-17","comments":34,"follower_count_1d":61,"likes":978,"reach":16464,"replies":1,"saves":70,"shares":436,"total_interactions":1999,"views":33464},
    {"date":"2026-04-18","comments":44,"follower_count_1d":69,"likes":1414,"reach":26645,"replies":0,"saves":89,"shares":610,"total_interactions":2825,"views":57148},
    {"date":"2026-04-19","comments":59,"follower_count_1d":108,"likes":1743,"reach":33837,"replies":0,"saves":151,"shares":827,"total_interactions":3666,"views":66061},
    {"date":"2026-04-20","comments":63,"follower_count_1d":96,"likes":1132,"reach":21511,"replies":0,"saves":103,"shares":577,"total_interactions":2513,"views":48139},
    {"date":"2026-04-21","comments":82,"follower_count_1d":107,"likes":1759,"reach":31489,"replies":0,"saves":160,"shares":993,"total_interactions":4072,"views":63051},
    {"date":"2026-04-22","comments":105,"follower_count_1d":93,"likes":2106,"reach":41693,"replies":0,"saves":148,"shares":1568,"total_interactions":5607,"views":67948},
    {"date":"2026-04-23","comments":62,"follower_count_1d":75,"likes":1452,"reach":30091,"replies":0,"saves":124,"shares":831,"total_interactions":3371,"views":53660},
    {"date":"2026-04-24","comments":63,"follower_count_1d":69,"likes":1302,"reach":27090,"replies":0,"saves":99,"shares":812,"total_interactions":3161,"views":52444},
    {"date":"2026-04-25","comments":63,"follower_count_1d":85,"likes":1772,"reach":35417,"replies":2,"saves":132,"shares":1143,"total_interactions":4317,"views":70833},
    {"date":"2026-04-26","comments":70,"follower_count_1d":82,"likes":1685,"reach":34852,"replies":2,"saves":142,"shares":1350,"total_interactions":4672,"views":66331},
    {"date":"2026-04-27","comments":44,"follower_count_1d":75,"likes":1236,"reach":26137,"replies":1,"saves":88,"shares":808,"total_interactions":3030,"views":51222},
    {"date":"2026-04-28","comments":47,"follower_count_1d":60,"likes":1096,"reach":20755,"replies":0,"saves":69,"shares":577,"total_interactions":2424,"views":41004},
    {"date":"2026-04-29","comments":33,"follower_count_1d":61,"likes":836,"reach":17853,"replies":1,"saves":74,"shares":575,"total_interactions":2137,"views":36428},
    {"date":"2026-04-30","comments":26,"follower_count_1d":69,"likes":823,"reach":15406,"replies":0,"saves":56,"shares":439,"total_interactions":1813,"views":32768},
    {"date":"2026-05-01","comments":44,"follower_count_1d":61,"likes":1207,"reach":22476,"replies":0,"saves":83,"shares":537,"total_interactions":2458,"views":46702},
    {"date":"2026-05-02","comments":55,"follower_count_1d":77,"likes":1382,"reach":24353,"replies":2,"saves":95,"shares":630,"total_interactions":2859,"views":60084},
    {"date":"2026-05-03","comments":46,"follower_count_1d":71,"likes":909,"reach":16978,"replies":0,"saves":86,"shares":495,"total_interactions":2082,"views":41709},
    {"date":"2026-05-04","comments":40,"follower_count_1d":64,"likes":635,"reach":13207,"replies":0,"saves":62,"shares":358,"total_interactions":1485,"views":29756},
    {"date":"2026-05-05","comments":29,"follower_count_1d":61,"likes":703,"reach":12136,"replies":0,"saves":50,"shares":288,"total_interactions":1395,"views":32647},
    {"date":"2026-05-06","comments":19,"follower_count_1d":0,"likes":794,"reach":13006,"replies":1,"saves":58,"shares":301,"total_interactions":1505,"views":34654},
]

media_30d = [
    {"timestamp":"2026-04-11T21:07:13+0000","media_type":"CAROUSEL_ALBUM","media_caption":"Angélica & Guilherme ❤️","media_reach":4569,"media_engagement":169,"media_saved":3,"media_shares":5,"media_views":10376,"media_like_count":155,"media_comments_count":6,"media_permalink":"https://www.instagram.com/p/DXAYFfQAQg1/"},
    {"timestamp":"2026-04-15T21:00:00+0000","media_type":"CAROUSEL_ALBUM","media_caption":"Esse vestido foi criado pensando na essência da Carol.","media_reach":6594,"media_engagement":295,"media_saved":21,"media_shares":19,"media_views":14828,"media_like_count":248,"media_comments_count":7,"media_permalink":"https://www.instagram.com/p/DXKqhXOAVuQ/"},
    {"timestamp":"2026-04-16T20:36:05+0000","media_type":"CAROUSEL_ALBUM","media_caption":"Nossas clientes maravilhosas de Inês Noivas","media_reach":7100,"media_engagement":186,"media_saved":5,"media_shares":10,"media_views":15810,"media_like_count":166,"media_comments_count":4,"media_permalink":"https://www.instagram.com/p/DXNMfx5gV8C/"},
    {"timestamp":"2026-04-18T22:01:19+0000","media_type":"REELS","media_caption":"Vocês amaram, então trouxemos a parte 2! Será que a sua mãe acerta agora?","media_reach":52272,"media_engagement":2605,"media_saved":152,"media_shares":900,"media_views":75916,"media_like_count":1454,"media_comments_count":70,"media_permalink":"https://www.instagram.com/reel/DXSfVeigeqp/"},
    {"timestamp":"2026-04-21T14:07:21+0000","media_type":"IMAGE","media_caption":"Nosso savoir-faire não está apenas na técnica","media_reach":2441,"media_engagement":45,"media_saved":5,"media_shares":1,"media_views":4103,"media_like_count":39,"media_comments_count":0,"media_permalink":"https://www.instagram.com/p/DXZoYMajK8_/"},
    {"timestamp":"2026-04-23T21:03:30+0000","media_type":"CAROUSEL_ALBUM","media_caption":"Um vestido memorável!","media_reach":3407,"media_engagement":110,"media_saved":2,"media_shares":16,"media_views":6597,"media_like_count":86,"media_comments_count":3,"media_permalink":"https://www.instagram.com/p/DXfRMxiAULi/"},
    {"timestamp":"2026-04-24T21:06:59+0000","media_type":"CAROUSEL_ALBUM","media_caption":"Cada cristal carrega tempo.","media_reach":3471,"media_engagement":74,"media_saved":3,"media_shares":1,"media_views":7820,"media_like_count":69,"media_comments_count":1,"media_permalink":"https://www.instagram.com/p/DXh2ZKMgd_T/"},
    {"timestamp":"2026-04-28T20:36:23+0000","media_type":"CAROUSEL_ALBUM","media_caption":"Jordana & Eduardo.","media_reach":1923,"media_engagement":50,"media_saved":4,"media_shares":4,"media_views":4446,"media_like_count":42,"media_comments_count":0,"media_permalink":"https://www.instagram.com/p/DXsGEdVAUFO/"},
    {"timestamp":"2026-05-01T20:37:42+0000","media_type":"CAROUSEL_ALBUM","media_caption":"Larissa & Ahmad ❤️","media_reach":6323,"media_engagement":215,"media_saved":1,"media_shares":5,"media_views":16353,"media_like_count":202,"media_comments_count":7,"media_permalink":"https://www.instagram.com/p/DXz0myYgd3n/"},
    {"timestamp":"2026-05-06T21:09:25+0000","media_type":"CAROUSEL_ALBUM","media_caption":"Letícia & Felipe 🤍","media_reach":1528,"media_engagement":152,"media_saved":9,"media_shares":2,"media_views":3746,"media_like_count":138,"media_comments_count":3,"media_permalink":"https://www.instagram.com/p/DYAwNa6AV2c/"},
]

today = date.today()
cutoff_14 = today - timedelta(days=14)
cutoff_7 = today - timedelta(days=7)
data_dir = Path(__file__).parent / "data"
today_str = str(today)


def transform_daily(raw):
    rows = []
    for r in raw:
        rows.append({
            "Data": r["date"],
            "Alcance": r["reach"],
            "Visualizacoes": r["views"],
            "Curtidas": r["likes"],
            "Comentarios": r["comments"],
            "Salvos": r["saves"],
            "Compartilhamentos": r["shares"],
            "Respostas": r["replies"],
            "Interacoes Totais": r["total_interactions"],
            "Novos Seguidores": r["follower_count_1d"],
        })
    return rows


def transform_media(raw):
    rows = []
    for r in raw:
        caption = r.get("media_caption", "")
        title = caption[:60] if caption else "(sem legenda)"
        rows.append({
            "Data": r["timestamp"][:10],
            "Tipo": r["media_type"],
            "Post": title,
            "Alcance": r["media_reach"],
            "Engajamento": r["media_engagement"],
            "Curtidas": r["media_like_count"],
            "Comentarios": r["media_comments_count"],
            "Salvos": r["media_saved"],
            "Compartilhamentos": r["media_shares"],
            "Visualizacoes": r["media_views"],
            "Link": r["media_permalink"],
        })
    return rows


for days, cutoff in [(7, cutoff_7), (14, cutoff_14), (30, None)]:
    if cutoff:
        daily_f = [r for r in daily_30d if datetime.strptime(r["date"], "%Y-%m-%d").date() >= cutoff]
        media_f = [r for r in media_30d if datetime.strptime(r["timestamp"][:10], "%Y-%m-%d").date() >= cutoff]
    else:
        daily_f = daily_30d
        media_f = media_30d

    path = data_dir / f"instagram_{days}d.json"
    payload = {"date": today_str, "rows": transform_daily(daily_f)}
    path.write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"{path}: {len(daily_f)} rows")

    path2 = data_dir / f"instagram_media_{days}d.json"
    payload2 = {"date": today_str, "rows": transform_media(media_f)}
    path2.write_text(json.dumps(payload2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"{path2}: {len(media_f)} rows")
