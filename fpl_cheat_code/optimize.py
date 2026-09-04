"""Squad optimization and transfer suggestions.

`best_squad` answers: if you picked a 15-man squad from scratch under the
budget, what maximizes total expected points? Per position we solve a small
knapsack (exact quota, budget in GBP 1.0m buckets, which can leave up to
~GBP 0.9m unspent -- fine for a heuristic, and we report the leftover).

`transfer_suggestions` answers the weekly question: with 1 free transfer and
X in the bank, which single swap gains the most expected points?
"""

from .model import POS_NAME

QUOTA = {1: 2, 2: 5, 3: 5, 4: 3}  # GK, DEF, MID, FWD


def _best_for_position(rows, pos_id, budget_whole, quota):
    """Knapsack: exactly `quota` players from this position within budget.
    Budget buckets are GBP 1.0m. Returns (total_xp, chosen_rows) or None."""
    items = [r for r in rows if r["pos_id"] == pos_id]
    items.sort(key=lambda r: r["price"])  # enable early cut-offs
    n_buckets = int(budget_whole) + 1
    # dp[b][k] = (xp, tuple_of_indices); b = budget bucket, k = players chosen
    dp = [[(-1.0, ()) for _ in range(quota + 1)] for _ in range(n_buckets)]
    for b in range(n_buckets):
        dp[b][0] = (0.0, ())
    for i, r in enumerate(items):
        cost = int(r["price"] + 0.999)  # round up to bucket
        if cost >= n_buckets:
            continue
        for b in range(n_buckets - 1, cost - 1, -1):
            for k in range(quota, 0, -1):
                prev = dp[b - cost][k - 1]
                if prev[0] >= 0:
                    cand = prev[0] + r["xp"]
                    if cand > dp[b][k][0]:
                        dp[b][k] = (cand, prev[1] + (i,))
    best = dp[n_buckets - 1][quota]
    if best[0] < 0:
        return None
    return best[0], [items[i] for i in best[1]]


def best_squad(rows, budget=100.0):
    """Best 15-man squad under FPL quotas. Returns (squad_rows, total_xp, leftover)."""
    # Value curves per position: curve[pos][b] = (xp, players) for budget b
    curves = {}
    for pos_id, quota in QUOTA.items():
        curve = []
        for b in range(int(budget) + 1):
            res = _best_for_position(rows, pos_id, b, quota)
            curve.append(res if res else (0.0, []))
        curves[pos_id] = curve

    best = None
    # GK and FWD are cheap-ish: bound their spend to keep the search tiny.
    for gk_b in range(6, 13):
        for def_b in range(15, 36):
            for fwd_b in range(15, 41):
                mid_b = int(budget) - gk_b - def_b - fwd_b
                if mid_b < 15 or mid_b > 65:
                    continue
                gk, de, mi, fw = (curves[p][b] for p, b in
                                  ((1, gk_b), (2, def_b), (3, mid_b), (4, fwd_b)))
                total = gk[0] + de[0] + mi[0] + fw[0]
                if best is None or total > best[1]:
                    squad = gk[1] + de[1] + mi[1] + fw[1]
                    spent = sum(r["price"] for r in squad)
                    best = (squad, total, budget - spent)
    return best


def transfer_suggestions(squad_rows, table, bank=0.0, free_transfers=1, top_n=5):
    """Rank single swaps by expected-point gain. Sell price assumed
    price-0.1 (early-season purchases, price drift small). One transfer per
    suggestion; hits priced at -4 so a swap must gain >4 xp to be a 'hit'."""
    owned = {r["id"] for r in squad_rows}
    start_xi = squad_rows[:11]
    suggestions = []
    for out in start_xi:
        pos_id = out["pos_id"]
        sell = max(3.9, out["price"] - 0.1)
        affordable = (r for r in table
                      if r["pos_id"] == pos_id and r["id"] not in owned and r["price"] <= sell + bank)
        best_in = max(affordable, key=lambda r: r["xp"], default=None)
        if best_in:
            suggestions.append({
                "out": out, "in": best_in,
                "gain": round(best_in["xp"] - out["xp"], 2),
            })
    suggestions.sort(key=lambda s: -s["gain"])
    return suggestions[:top_n]
