"""Expected-points model (v1) -- stdlib-only, documented, deliberately simple.

Two signals, blended:
  1. Bottom-up model: per-90 xG/xA (FPL's Opta-based data) scaled by a
     minutes projection, plus clean-sheet and save expectations from fixture
     difficulty (FDR), plus a defensive-contributions floor introduced in
     2025-26 (2 pts for 10 CBIT as a defender).
  2. FPL's own `form` field, which captures what xG misses (bonus, BPS
     quirks, penalties won, hauls that came from hustle).

Every weight lives in CONFIG so backtests can tune them. This is v1: honest
about its limits (see README "How accurate is this?"), and already better
than the default strategy of most managers, which is vibes.
"""

CONFIG = {
    "w_model": 0.65,      # weight of the bottom-up model vs FPL form
    "min_floor": 0.30,    # floor on projected minutes share (rotation risk)
    "defcon_def": 1.20,   # pts/GW floor for defenders from DefCon (heuristic)
    "defcon_mid": 0.60,   # same for midfielders (need 12 CBIT+recoveries)
    "attack_fdr_mult": {2: 1.15, 3: 1.00, 4: 0.90, 5: 0.78},
    "cs_prob_by_fdr": {2: 0.42, 3: 0.33, 4: 0.24, 5: 0.16},
}

GOAL_PTS = {1: 6, 2: 6, 3: 5, 4: 4}  # GK, DEF, MID, FWD
POS_NAME = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

# Empirical-Bayes priors: per-90 xG/xA shrink toward these, weighted by
# sample size. Without this, a 0.17 xG in 1 minute of play shows up as an
# absurd "15.3 xG per 90". One match worth of prior (90 mins) is enough.
PRIOR_MATCHES = 1.0
XG_PRIOR_90 = {1: 0.00, 2: 0.05, 3: 0.15, 4: 0.25}
XA_PRIOR_90 = {1: 0.01, 2: 0.05, 3: 0.18, 4: 0.12}


def _f(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def fixture_for_team(fixtures, team_id, event_id):
    for f in fixtures:
        if f.get("event") == event_id and team_id in (f["team_h"], f["team_a"]):
            home = f["team_h"] == team_id
            fdr = f["team_h_difficulty"] if home else f["team_a_difficulty"]
            opp = f["team_a"] if home else f["team_h"]
            return {"home": home, "fdr": fdr, "opponent": opp}
    return None


def project_minutes(p, matches_played):
    """Minutes share proxy from how much of the season they've played so far."""
    if matches_played <= 0:
        return 90.0
    share = _f(p.get("minutes")) / (90.0 * matches_played)
    share = max(CONFIG["min_floor"], min(1.0, share))
    return 90.0 * share


def player_xp(p, fix, matches_played):
    """Expected points for one player in one gameweek. `fix` may be None (blank)."""
    pos = p["element_type"]
    mins = _f(p.get("minutes"))
    # Shrink per-90 rates toward positional priors by sample size.
    equiv = mins + PRIOR_MATCHES * 90.0
    xg90 = (_f(p.get("expected_goals")) + XG_PRIOR_90[pos] * PRIOR_MATCHES) / equiv * 90.0
    xa90 = (_f(p.get("expected_assists")) + XA_PRIOR_90[pos] * PRIOR_MATCHES) / equiv * 90.0
    form = _f(p.get("form"))
    proj = project_minutes(p, matches_played)
    share = proj / 90.0

    if fix is None:  # blank gameweek
        return {"xp": 0.0, "model": 0.0, "form_adj": 0.0, "proj_min": 0.0, "fix": None}

    mult = CONFIG["attack_fdr_mult"].get(fix["fdr"], 1.0)
    home_boost = 1.05 if fix["home"] else 1.0

    # 1) attacking returns
    xp_att = (xg90 * GOAL_PTS[pos] + xa90 * 3.0) * share * mult * home_boost

    # 2) clean sheets (GK/DEF 4 pts, MID 1 pt, needs 60+ mins)
    p_cs = CONFIG["cs_prob_by_fdr"].get(fix["fdr"], 0.3) * (1.05 if fix["home"] else 0.95)
    xp_cs = p_cs * (4 if pos in (1, 2) else (1 if pos == 3 else 0)) * (1.0 if proj >= 60 else 0.0)

    # 3) defensive contributions floor (2025-26 rule, kept for 2026-27)
    xp_defcon = CONFIG["defcon_def" if pos == 2 else "defcon_mid"] * share if pos in (2, 3) else 0.0

    # 4) goalkeeper saves: 1 pt per 3 saves
    xp_saves = 0.0
    if pos == 1 and _f(p.get("minutes")) > 0:
        saves90 = _f(p.get("saves")) / _f(p.get("minutes")) * 90.0
        xp_saves = (saves90 / 3.0) * share

    model = xp_att + xp_cs + xp_defcon + xp_saves
    form_adj = form * share  # form is per-match; scale by minutes share
    xp = CONFIG["w_model"] * model + (1 - CONFIG["w_model"]) * form_adj
    return {"xp": xp, "model": model, "form_adj": form_adj, "proj_min": proj, "fix": fix}


def build_table(boot, fxs, target_gw):
    """Score every player for the target gameweek. Returns list of dicts."""
    matches = len([e for e in boot["events"] if e.get("finished")])
    teams = {t["id"]: t for t in boot["teams"]}
    rows = []
    for p in boot["elements"]:
        fix = fixture_for_team(fxs, p["team"], target_gw["id"])
        r = player_xp(p, fix, matches)
        price = p["now_cost"] / 10.0
        rows.append({
            "id": p["id"],
            "name": p["web_name"],
            "pos": POS_NAME[p["element_type"]],
            "pos_id": p["element_type"],
            "team": teams[p["team"]]["short_name"],
            "price": price,
            "xp": r["xp"],
            "form": _f(p.get("form")),
            "pps": _f(p.get("points_per_game")),
            "sel": _f(p.get("selected_by_percent")),
            "minutes": int(_f(p.get("minutes"))),
            "fixture": ("vs " if fix and fix["home"] else "@ ") +
                       (teams[fix["opponent"]]["short_name"] if fix else "BLANK") if fix else "BLANK",
            "fdr": fix["fdr"] if fix else 0,
        })
    rows.sort(key=lambda r: -r["xp"])
    return rows
