import json
import urllib.request
from datetime import datetime, timezone

# 1. Fetch all active skaters playing in the current NHL season (2026-2027)
CURRENT_SEASON = "20262027"
ACTIVE_URL = f"https://api.nhle.com/stats/rest/en/skater/summary?limit=-1&cayenneExp=seasonId={CURRENT_SEASON}%20and%20gameTypeId=2"

# 2. Fetch official all-time career totals aggregated across every NHL season
CAREER_URL = "https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=true&limit=-1&cayenneExp=gameTypeId=2"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    print("Fetching current active NHL skaters...")
    active_data = fetch_json(ACTIVE_URL).get("data", [])
    active_map = {}
    for row in active_data:
        pid = row.get("playerId")
        if pid:
            # Keep their most recent team abbreviation if traded mid-season
            teams = str(row.get("teamAbbrevs", "NHL")).split(",")
            active_map[pid] = {
                "team": teams[-1].strip(),
                "pos": row.get("positionCode", "F"),
                "name": row.get("skaterFullName", "")
            }

    print(f"Found {len(active_map)} active skaters this season. Fetching official career totals...")
    career_data = fetch_json(CAREER_URL).get("data", [])

    players = []
    for row in career_data:
        pid = row.get("playerId")
        if pid not in active_map:
            continue

        gp = int(row.get("gamesPlayed", 0))
        points = int(row.get("points", 0))

        # Filter to active skaters with at least 50 career NHL games
        if gp < 50:
            continue

        info = active_map[pid]
        players.append({
            "id": pid,
            "name": info["name"] or row.get("skaterFullName"),
            "team": info["team"],
            "pos": info["pos"],
            "gp": gp,
            "points": points
        })

    # Sort highest points first for easy inspection
    players.sort(key=lambda x: x["points"], reverse=True)

    output = {
        "updatedAt": datetime.now(timezone.utc).strftime("%b %d %H:%M UTC"),
        "count": len(players),
        "players": players
    }

    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(players)} active NHL skaters to players.json!")

if __name__ == "__main__":
    main()