#!/usr/bin/env python3
"""Snapshot FPL data locally (data/*.json) so you can inspect the raw feed."""

import json
import pathlib

from fpl_cheat_code import api

OUT = pathlib.Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)


def save(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, indent=1))
    print(f"wrote data/{name}.json")


boot = api.bootstrap()
save("bootstrap", boot)
save("fixtures", api.fixtures())
gw = api.target_gameweek(boot)
print(f"target gameweek: {gw['name']} (deadline {gw['deadline_time']})")
