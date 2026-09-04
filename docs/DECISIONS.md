# Decision Log

Every call we make, and the reasoning **at decision time** — win or lose.
Format: context → decision → alternatives rejected → how we'll know if it was right.

---

## Gameweek 3 (2026-27) — deadline 2026-09-04 17:30 UTC

### Context

| | |
|---|---|
| Team | Paandav (entry 8851240) |
| Season points / OR | 153 pts / 1,667,110 |
| Mini-league | 2nd of 4 in "Naye Khiladiyon ki Toli", 31 pts behind the leader |
| Bank / squad value | £0.0m / £100.2m |
| Chips | All available (WC ×2, FH ×2, BB ×2, TC ×2) — first set expires GW19 |
| Transfers available | 1 free (0 used all season) |

Fixture of the week: **Man City vs Coventry (H, FDR 2)** — the newly promoted side away to the strongest attack in the league.

### Decision 1 — Transfer: Luke Shaw OUT → Semi Ajayi IN (£4.1m, Hull City, DEF)

**Why:**
- Shaw picked up a **thigh injury** in United's 5-2 win over Ipswich (Aug 31) and is a doubt for Everton away; form of 1.5 pts; 15.3% owned.
- Ajayi is the form defender of the season so far: **10.0 form**, scored in Hull's shock 2-0 win at Old Trafford on opening day, nailed starter in every predicted XI, hosts Aston Villa. 10% owned → likely price riser; buying before the rise matters (sell-on-fee rule makes chasing rises later much worse).
- Model cross-check: the engine independently ranks **Shaw → Ajayi at +3.05 xP**, the best gain among defenders on free transfer (Tzolis → Lewis-Potter is +3.39 but Shaw's injury risk is the stronger tiebreaker; the model's 30% minutes floor understates rotation risk).
- Banks £0.4m of value.

**Rejected alternatives:**
- *Roll the transfer*: tempting for a 2-FT week later, but upgrading an injured starter is exactly what free transfers are for.
- *João Pedro → Cherki (quad City stack)*: selling a 69%-owned, in-form, penalty-taking striker before his team's biggest fixture test is a panic move; also unaffordable at £0.0m bank.
- *Bench Janelt / Davis considerations*: bench order set separately (below).

### Decision 2 — Captain: Erling Haaland (C) vs Coventry (H). Vice: Bruno Fernandes.

Best fixture in the league for the best scorer in the game; the consensus #1 captaincy pick across model sites this week. Bruno (form 12.5, xG90 1.05, 25 pts in 2 GWs) is the live alternative and the model's own #1 (8.00 xP) — he stays vice-captain and is the default captain if Haaland is ruled out.

Note on the model gap: our v1 engine ranks Bruno > Haaland because it doesn't yet model bonus points, penalty-share or Haaland's ceiling-vs-floor distribution. When the model and the market disagree this way, the market usually has information we don't (that's why it's on the roadmap). The lesson is in the strategy doc: **use the model to find mispriced assets, use judgment for the armband.**

### Decision 3 — Bench order: Janelt → Davis → van Ewijk → Kinsky

Janelt first: Brentford vs Sunderland is the week's second-easiest fixture and Janelt plays every week. Kinsky (GK) last, as always.

### Decisions NOT made (discipline log)

- **No point hits.** No suggestion in the top-5 gain list clears the -4 bar.
- **No chips.** Chips are for double/blank gameweeks; GW3 has neither. First set expires GW19 — we'll attack the first fixture swing, not spend early.
- **Formation unchanged (3-4-3).** The XI after the transfer:
  Raya; Calafiori, **Ajayi**, Hume; Tzolis, Semenyo, B.Fernandes, Ndiaye; João Pedro, Calvert-Lewin, **Haaland (C)**.

### How we'll know if it was right

- Shaw doesn't start (or plays <60') and Ajayi returns ≥ 2 pts more → move validated.
- Haaland hauls (13+ pts) → captaincy validated. If Bruno outscores him 2× and we lose the week to the leader captaining Bruno, we re-examine nothing — the decision was +EV at kickoff. Process over outcomes, but the log keeps us honest either way.

---

<!-- Next entries: add one section per gameweek, same format. -->
