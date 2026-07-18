#!/usr/bin/env python3
"""
Fetch the real GitHub contribution calendar with NO token and NO GraphQL.

GitHub serves the calendar as public HTML at
    https://github.com/users/<username>/contributions
(the same fragment the profile page embeds). We scrape the day cells, then
derive a few stats and write data/contributions.json.

Run:  python scripts/fetch_contributions.py
"""
import json
import re
from datetime import datetime, date, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "xavibosch"
OUT = Path("data/contributions.json")
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_days():
    r = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (profile-art fetcher)",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "text/html",
        },
        timeout=30,
    )
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # In current GitHub markup the day <td> carries date + level, and the count
    # lives in a separate <tool-tip for="<cell-id>">N contributions on DATE</tool-tip>.
    # Build id -> count from the tooltips first.
    tip_count = {}
    for tip in soup.select("tool-tip[for]"):
        m = re.search(r"(\d[\d,]*)\s+contribution", tip.text)
        n = int(m.group(1).replace(",", "")) if m else 0
        tip_count[tip.get("for")] = n

    days = []
    for cell in soup.select("td.ContributionCalendar-day, td[data-date]"):
        d = cell.get("data-date")
        if not d:
            continue
        level = int(cell.get("data-level", "0") or "0")
        # count sources, in order of reliability
        if cell.get("data-count") is not None:
            count = int(cell.get("data-count"))
        elif cell.get("id") in tip_count:
            count = tip_count[cell.get("id")]
        else:
            txt = cell.get("aria-label") or cell.text or ""
            m = re.search(r"(\d[\d,]*)\s+contribution", txt)
            count = int(m.group(1).replace(",", "")) if m else 0
        days.append({"date": d, "count": count, "level": level})

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"], default={"count": 0, "date": None})

    # streaks (consecutive days with count>0, ending today or earlier)
    longest = cur = 0
    for d in days:
        if d["count"] > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0
    # current streak = trailing run of >0 days
    current = 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        else:
            break

    # per-month totals for the last 12 labels
    months = {}
    for d in days:
        key = d["date"][:7]
        months[key] = months.get(key, 0) + d["count"]

    return {
        "total": total,
        "best_day": {"date": best.get("date"), "count": best.get("count", 0)},
        "current_streak": current,
        "longest_streak": longest,
        "months": months,
    }


def main():
    days = fetch_days()
    if not days:
        raise SystemExit("no contribution cells parsed — GitHub markup may have changed")
    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "stats": derive_stats(days),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {OUT}: {len(days)} days, {payload['stats']['total']} contributions")


if __name__ == "__main__":
    main()
