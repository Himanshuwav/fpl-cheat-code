"""Command line interface. Run `python3 -m fpl_cheat_code.cli --help`.

  report            top expected-point players for the next gameweek
  captain           captaincy shortlist by expected points
  team ENTRY_ID     your squad with modelled expected points
  transfers ENTRY_ID  best free-transfer swaps for your squad
  best-squad        the optimal 15-man squad from scratch (useful on wildcard)
"""

import argparse

from . import api
from .model import build_table
from .optimize import best_squad, transfer_suggestions


def _load():
    boot = api.bootstrap()
    gw = api.target_gameweek(boot)
    fxs = api.fixtures()
    return boot, gw, fxs, build_table(boot, fxs, gw)


def cmd_report(args):
    boot, gw, _, rows = _load()
    print(f"== Expected points, {gw['name']} (deadline {gw['deadline_time']}) ==\n")
    hdr = f"{'player':<16}{'team':<5}{'pos':<4}{'PS':>5}{'xP':>6}{'form':>6}{'sel%':>7}  fixture"
    print(hdr)
    for r in rows[: args.top]:
        print(f"{r['name']:<16}{r['team']:<5}{r['pos']:<4}{r['price']:>5}{r['xp']:>6.2f}"
              f"{r['form']:>6.1f}{r['sel']:>6.1f}%  {r['fixture']} (FDR {r['fdr']})")


def cmd_captain(args):
    _, gw, _, rows = _load()
    print(f"== Captaincy shortlist, {gw['name']} ==\n")
    for i, r in enumerate(rows[: args.top], 1):
        print(f"{i:>2}. {r['name']:<16} ({r['team']}, {r['pos']}) xP {r['xp']:.2f} "
              f"| owned {r['sel']:.1f}% | {r['fixture']}")
    print("\nSafe pick = highest xP premium. Differential pick = high xP + low owned "
          "(only when chasing a mini-league gap).")


def cmd_team(args):
    boot, gw, fxs, rows = _load()
    by_id = {r["id"]: r for r in rows}
    picks, from_gw = api.current_squad(args.entry_id, boot)
    hist = api.entry_history(args.entry_id)
    last = hist["current"][-1]
    e = api.entry(args.entry_id)
    print(f"== {e['name']} ({e['player_first_name']} {e['player_last_name']}) == "
          f"OR {e['summary_overall_rank']:,} | pts {e['summary_overall_points']} | "
          f"bank {last['bank']/10:.1f} | value {last['value']/10:.1f}\n")
    print(f"Squad from GW{from_gw} (+transfers since), projected for {gw['name']}:\n")
    squad = []
    for pk in picks["picks"]:
        r = by_id[pk["element"]]
        squad.append(r)
        tag = " C" if pk["is_captain"] else (" V" if pk["is_vice_captain"] else "")
        slot = "XI " if pk["position"] <= 11 else "BENCH"
        print(f"{slot} {r['name']:<16} {r['team']:<4} {r['pos']:<4} PS {r['price']:<5} "
              f"xP {r['xp']:.2f}  {r['fixture']}{tag}")
    xi_xp = sum(r["xp"] for r in squad[:11])
    print(f"\nXI expected points: {xi_xp:.1f} (captain doubling excluded; "
          f"best captain: {max(squad[:11], key=lambda r: r['xp'])['name']})")


def cmd_transfers(args):
    boot, gw, fxs, rows = _load()
    by_id = {r["id"]: r for r in rows}
    picks, from_gw = api.current_squad(args.entry_id, boot)
    hist = api.entry_history(args.entry_id)
    bank = hist["current"][-1]["bank"] / 10.0
    squad = [by_id[pk["element"]] for pk in picks["picks"]]
    print(f"== Transfer suggestions, {gw['name']} (bank {bank:.1f}, {args.free} free transfer(s)) ==\n")
    sugg = transfer_suggestions(squad, rows, bank=bank, free_transfers=args.free)
    for s in sugg:
        out, inn = s["out"], s["in"]
        print(f"{out['name']:<16} ({out['xp']:.2f} xP) -> {inn['name']:<16} "
              f"({inn['xp']:.2f} xP, PS {inn['price']})  gain +{s['gain']:.2f}  [{out['fixture']} -> {inn['fixture']}]")
    best = sugg[0] if sugg else None
    print("\nRule of thumb: use your free transfer if the top gain is meaningful "
          "(+1.0 xP or more); take a -4 hit only if gain > 4 over the holding period.")


def cmd_best_squad(args):
    _, gw, _, rows = _load()
    squad, xp, leftover = best_squad(rows, budget=args.budget)
    print(f"== Optimal 15 for {gw['name']} (budget {args.budget:.1f}) == total xP {xp:.1f}, "
          f"leftover ~{leftover:.1f}\n")
    for r in sorted(squad, key=lambda r: (r["pos_id"], -r["xp"])):
        print(f"{r['pos']:<4} {r['name']:<16} {r['team']:<4} PS {r['price']:<5} xP {r['xp']:.2f}  {r['fixture']}")
    xi = sorted(squad, key=lambda r: -r["xp"])[:11]
    print(f"\nBest XI of the 15: {[r['name'] for r in xi]}")


def main():
    ap = argparse.ArgumentParser(prog="fpl-cheat-code",
                                 description="Data-driven FPL decisions (v1 model).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("report", help="top expected-point players")
    p.add_argument("--top", type=int, default=20)
    p.set_defaults(fn=cmd_report)
    p = sub.add_parser("captain", help="captaincy shortlist")
    p.add_argument("--top", type=int, default=8)
    p.set_defaults(fn=cmd_captain)
    p = sub.add_parser("team", help="your squad with xP")
    p.add_argument("entry_id", type=int)
    p.set_defaults(fn=cmd_team)
    p = sub.add_parser("transfers", help="best free-transfer swaps")
    p.add_argument("entry_id", type=int)
    p.add_argument("--free", type=int, default=1, help="free transfers available")
    p.set_defaults(fn=cmd_transfers)
    p = sub.add_parser("best-squad", help="optimal 15 from scratch (wildcard mode)")
    p.add_argument("--budget", type=float, default=100.0)
    p.set_defaults(fn=cmd_best_squad)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
