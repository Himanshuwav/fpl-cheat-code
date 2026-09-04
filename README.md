<div align="center">

# fpl-cheat-code

**An open-source decision engine for Fantasy Premier League.**
Expected points, captaincy shortlists, transfer rankings and squad optimization — straight from FPL's own public data, with every heuristic documented and every decision logged.

*Born from a simple bet: a total football newbie, an AI agent, and 38 gameweeks to climb from 1.6 millionth to the top 1%.*

</div>

---

## Why this exists

Most FPL "systems" are vibes with a spreadsheet. This repo does the opposite:

1. **Pulls the same Opta-based data the pros use** — xG, xA, minutes, fixture difficulty — from FPL's public API. No scraping, no paid tools required.
2. **Turns it into expected points (xP)** with a transparent, stdlib-only model (see [`fpl_cheat_code/model.py`](fpl_cheat_code/model.py)). Every weight is a named constant you can argue with.
3. **Answers the only three questions that matter each week**: who do I transfer, who do I captain, and what's the best possible squad if IWildcard'd today.
4. **Logs every decision publicly** in [`docs/DECISIONS.md`](docs/DECISIONS.md) — including the misses. Process over outcomes.

## Quick start

No dependencies. Python 3.10+.

```bash
git clone https://github.com/Himanshuwav/fpl-cheat-code.git
cd fpl-cheat-code

# Top expected-point players for the next gameweek
python3 -m fpl_cheat_code.cli report --top 20

# Captaincy shortlist
python3 -m fpl_cheat_code.cli captain

# Your squad, projected
python3 -m fpl_cheat_code.cli team YOUR_TEAM_ID

# Best free-transfer swaps for your squad
python3 -m fpl_cheat_code.cli transfers YOUR_TEAM_ID

# What you'd pick with a wildcard today
python3 -m fpl_cheat_code.cli best-squad
```

Find your Team ID by opening [fantasy.premierleague.com](https://fantasy.premierleague.com), tapping **Points**, and reading the number after `/entry/` in the URL.

## How the model works (v1)

For each player and the next gameweek:

- **Minutes projection** from share of season minutes played so far (floored at 30% to respect rotation risk).
- **Attacking xP** = shrunken per-90 xG × positional goal points + shrunken per-90 xA × 3, scaled by minutes share and a fixture-difficulty multiplier. Per-90 rates are shrunk toward positional priors with one match of Bayesian shrinkage — otherwise a 1-minute cameo shows up as "15 xG per 90" (this actually happened; see the git history).
- **Clean-sheet xP** from fixture difficulty, **DefCon floor** for the 2025-26 defensive-contributions rule, **save points** for keepers.
- **Blend**: 65% bottom-up model, 35% FPL's own recent `form` field (which captures bonus, BPS quirks and penalty duties that pure xG misses).

The full strategy behind the decisions — chip timing, effective ownership, transfer discipline, price exploitation — is written up in [`docs/ELITE_FPL_STRATEGY.md`](docs/ELITE_FPL_STRATEGY.md).

## How accurate is this? (Honesty section)

**Not 99.999%. Nothing is, and anyone selling you that is lying.** Single-match player scores are dominated by small-sample randomness: deflections, 58th-minute substitutions, penalty takers, referee behaviour. The best commercial models capture only a modest fraction of the possible signal — an academic model published in 2025 ([OpenFPL, arXiv:2508.09992](https://arxiv.org/html/2508.09992v1)) positions itself as *rivaling* commercial tools, not crushing them.

What a good process *does* buy you, and what this repo optimizes for:

- better **minutes risk** management than the average manager (the #1 season-killer),
- **fixture targeting** instead of name-recognition buys,
- **chip timing** around double/blank gameweeks instead of vibes,
- **team value** growth by buying risers before the crowd,
- and zero -4 hits that aren't backed by an expected-gain calculation.

Magnus Carlsen reached world #1 in January 2020 and finished that season OR 10 of 7.5 million — then drifted back to OR ~4k-7k in later seasons. Elite process reliably buys you the top few thousand, not #1 every year. The gap between 500k and 5k is process; the gap between 5k and 1 is mostly luck. We'll take the process.

## Roadmap

- [ ] Backtest harness: score v1 model against finished gameweeks (MAE + rank simulation)
- [ ] Per-player minutes model from lineup history and press-conference news
- [ ] DefCon (CBIT) data integration for the defensive-contributions floor
- [ ] Price-change tracker (the ~140k net-transfers trigger, hourly)
- [ ] Double/blank gameweek planner (Ben Crellin calendar integration)
- [ ] Bonus (BPS) modeling to close the premium-striker xP gap
- [ ] Web dashboard + weekly automated report

## The decision log

Every gameweek's calls — transfers, captaincy, bench order, and the reasoning at decision time — are logged in [`docs/DECISIONS.md`](docs/DECISIONS.md), win or lose. Steal the format for your own league.

## License

MIT. Data courtesy of the FPL public API; not affiliated with the Premier League.
