"""Minimal stdlib-only client for the Fantasy Premier League public API.

No auth required for any endpoint used here. Rate-limit friendly: every call
is a single request; callers should batch what they need.
"""

import json
import urllib.request

BASE = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "fpl-cheat-code/0.1"}


def _get(path):
    req = urllib.request.Request(f"{BASE}{path}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def bootstrap():
    """All players, teams, gameweek events and positions. The core dataset."""
    return _get("/bootstrap-static/")


def fixtures(event=None):
    """Fixtures with difficulty ratings, optionally filtered to one gameweek."""
    suffix = f"?event={event}" if event else ""
    return _get(f"/fixtures/{suffix}")


def entry(entry_id):
    """Manager profile: name, overall points/rank, favourite team."""
    return _get(f"/entry/{entry_id}/")


def entry_history(entry_id):
    """Per-gameweek history: points, transfers, hits, squad value, bank, chips."""
    return _get(f"/entry/{entry_id}/history/")


def entry_picks(entry_id, event):
    """The 15 picks (order, captain, vice) a manager fielded in one gameweek."""
    return _get(f"/entry/{entry_id}/event/{event}/picks/")


def entry_transfers(entry_id):
    """Every transfer the manager has made, with gameweek and timestamp."""
    return _get(f"/entry/{entry_id}/transfers/")


def classic_league(league_id, page=1):
    """Classic (points) mini-league standings, 50 managers per page."""
    return _get(f"/leagues-classic/{league_id}/standings/?page_standings={page}")


def last_finished_event(boot):
    """The most recent gameweek where all matches have finished."""
    finished = [e for e in boot["events"] if e.get("finished")]
    return max(finished, key=lambda e: e["id"]) if finished else None


def target_gameweek(boot):
    """The gameweek we predict next: the upcoming one after the last finished."""
    nxt = [e for e in boot["events"] if e.get("is_next")]
    if nxt:
        return nxt[0]
    cur = [e for e in boot["events"] if e.get("is_current")]
    if cur:
        return cur[0]
    unfinished = [e for e in boot["events"] if not e.get("finished")]
    return unfinished[0] if unfinished else boot["events"][0]


def current_squad(entry_id, boot):
    """The manager's current 15 players: last finished GW's picks + any
    transfers made since. (Current-GW picks require auth, so we reconstruct.)
    Returns (picks_json, gameweek_they_came_from)."""
    last = last_finished_event(boot)
    picks = entry_picks(entry_id, last["id"]) if last else None
    return picks, (last["id"] if last else None)
