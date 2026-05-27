import json
import re
from datetime import date

import httpx

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html",
    "Accept-Language": "es-AR,es;q=0.9",
    "Referer": "https://cordobaturismo.gov.ar/agenda/",
}

with httpx.Client(headers=headers, follow_redirects=True, timeout=60) as c:
    home = c.get("https://cordobaturismo.gov.ar/")
    print("HOME", home.status_code, len(home.content))
    api = "https://cordobaturismo.gov.ar/wp-json/tribe/events/v1/events"
    r = c.get(api, params={"per_page": 50, "page": 1, "start_date": "2026-05-20", "end_date": "2026-12-31"})
    print("API", r.status_code, len(r.content))
    if r.status_code == 200:
        d = r.json()
        print("total", d.get("total"), "page", len(d.get("events", [])))
        for e in (d.get("events") or [])[:5]:
            v = e.get("venue") or {}
            print("-", e.get("title", "")[:60])
            print(" ", e.get("start_date"), e.get("end_date"))
            print(" ", v.get("city"), v.get("address"))
            print(" ", e.get("url"))
    else:
        print(r.text[:200])

    for test in [
        "https://cordobaturismo.gov.ar/events/?ical=1",
        "https://cordobaturismo.gov.ar/?post_type=tribe_events&ical=1",
        "https://cordobaturismo.gov.ar/wp-sitemap-posts-tribe_events-1.xml",
        "https://cordobaturismo.gov.ar/wp-sitemap.xml",
    ]:
        h = c.get(test)
        print(test[:60], h.status_code, len(h.content), h.headers.get("content-type", "")[:40])
        if h.status_code == 200 and b"BEGIN:VCALENDAR" in h.content[:500]:
            print("  -> iCal OK, events", h.text.count("BEGIN:VEVENT"))
        if h.status_code == 200 and b"<urlset" in h.content[:200]:
            locs = re.findall(r"<loc>([^<]+)</loc>", h.text)
            ev = [u for u in locs if "/evento/" in u]
            print("  -> sitemap urls", len(locs), "evento", len(ev))
