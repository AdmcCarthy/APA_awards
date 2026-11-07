"""Numbers quoted in the partnership chapter, checked against data/partners.json and the build."""

import json
from pathlib import Path

import pytest

from subscout.build import build

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "data" / "partners.json").read_text())


def pair(a, b):
    row = next(r for r in P["pairs"]["rows"] if {r["a"], r["b"]} == {a, b})
    return dict(zip(P["pairs"]["years"], row["counts"], strict=True))


@pytest.fixture(scope="module")
def ledger(tmp_path_factory):
    out = tmp_path_factory.mktemp("site")
    rep = build(ROOT, out)
    assert rep.errors == [] and rep.warnings == []
    report = json.loads((out / "build-report.json").read_text())
    return {r["name"]: r["value"] for r in report["ledger"]}


@pytest.mark.parametrize(
    ("year", "groups", "pairs"),
    [("2008", 37, 89), ("2013", 44, 161), ("2019", 26, 88), ("2025", 19, 53)],
)
def test_network_sizes(ledger, year, groups, pairs):
    assert ledger[f"net_{year}_groups"] == str(groups)
    assert ledger[f"net_{year}_pairs"] == str(pairs)


def test_hub_and_pair_facts(ledger):
    assert ledger["hub_in"] == "51"
    assert ledger["n_pairs_shown"] == "14"
    ep = pair("Equinor", "Petoro")
    # "every round since 2004"
    assert all(ep[y] > 0 for y in ep if y >= 2004) and ep[2003] == 0
    assert ledger["ep_rounds"] == "22" and ledger["ep_total"] == "140"
    assert ledger["ad_before_2017"] == "6" and ledger["ad_since_2017"] == "51"
    # "Centrica and DNO, a regular pairing until 2015, have not shared a licence since"
    cd = pair("Centrica Resources", "DNO")
    assert cd[2015] > 0 and all(cd[y] == 0 for y in cd if y > 2015)
