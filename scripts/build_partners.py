"""Partnership history across all APA (TFO) rounds -> web/data/partners.json.

Line-ups are taken at grant (earliest licensee record per licence); the
operator at grant is the licensee whose operatorship starts first. Companies
are grouped into today's corporate families (see companies.py) so that pairs
and shares are comparable across mergers; company *counts* use Sodir entities
as they were at the time.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

from companies import FAMILY_NOTES, family

RAW = Path("data/raw")
OUT = Path("web/data")
NETWORK_YEARS = [2008, 2013, 2019, 2025]
SHARE_FAMILIES = ["Equinor", "Aker BP", "Petoro", "Vår Energi", "DNO", "Harbour Energy"]


def licences_at_grant() -> pd.DataFrame:
    """One row per licensee at grant for every original APA licence."""
    lic = gpd.read_file(RAW / "licence_tfo.geojson")
    lic = lic[lic.prlPartitionFrom.isna()].copy()
    lic["year"] = lic.prlLicensingActivityName.str[3:].astype(int)
    rows = [f["properties"] for f in json.loads((RAW / "licensee_hst.geojson").read_text())["features"]]
    h = pd.DataFrame(rows)
    h = h[h.prlNpdidLicence.isin(lic.prlNpdidLicence)].copy()
    h["vf"] = pd.to_datetime(h.prlLicenseeDateValidFrom, unit="ms")
    g = h[h.vf == h.groupby("prlNpdidLicence").vf.transform("min")]
    g = g.merge(lic[["prlNpdidLicence", "year", "prlName"]], on="prlNpdidLicence", suffixes=("", "_l"))
    tot = g.groupby("prlNpdidLicence").prlLicenseeInterest.sum()
    assert np.allclose(tot, 100, atol=0.05), "interests at grant do not sum to 100 %"
    assert g.prlNpdidLicence.nunique() == len(lic), "licences without a line-up at grant"
    ops = g[g.prlOperDateValidFrom.notna()].sort_values("prlOperDateValidFrom").drop_duplicates("prlNpdidLicence")
    g["op"] = g.index.isin(ops.index)
    assert g.groupby("prlNpdidLicence").op.sum().eq(1).all(), "each licence needs exactly one operator"
    g["fam"] = g.cmpLongName.map(family)
    return g


def network(gy: pd.DataFrame) -> dict:
    """Nodes (families) and weighted edges (shared licences) for one round."""
    lic_f = gy.groupby("prlNpdidLicence").fam.apply(lambda s: sorted(set(s)))
    n = gy.groupby("fam").prlNpdidLicence.nunique()
    op = gy[gy.op].groupby("fam").size()
    edges = pd.Series([pair for fs in lic_f for pair in itertools.combinations(fs, 2)]).value_counts()
    return {
        "nodes": [{"id": f, "n": int(n[f]), "op": int(op.get(f, 0))} for f in n.sort_values(ascending=False).index],
        "edges": [{"a": a, "b": b, "n": int(v)} for (a, b), v in edges.items()],
        "licences": int(len(lic_f)),
    }


def main() -> None:
    g = licences_at_grant()
    L = g.groupby(["year", "prlNpdidLicence"]).agg(n=("cmpNpdidCompany", "size"), fams=("fam", lambda s: sorted(set(s)))).reset_index()
    years = []
    for y, d in L.groupby("year"):
        gy = g[g.year == y]
        years.append({
            "year": int(y),
            "licences": int(len(d)),
            "companies": int(gy.cmpNpdidCompany.nunique()),
            "operators": int(gy[gy.op].cmpNpdidCompany.nunique()),
            "solo": int((d.n == 1).sum()),
            "group": round(float(d.n.mean()), 2),
            "share": {f: round(float(np.mean([f in x for x in d.fams])), 3) for f in SHARE_FAMILIES},
            "opshare": {f: round(float((gy[gy.op].fam == f).mean()), 3) for f in SHARE_FAMILIES},
        })
    pairs = pd.DataFrame([(r.year, a, b) for r in L.itertuples() for a, b in itertools.combinations(r.fams, 2)], columns=["year", "a", "b"])
    piv = pairs.groupby(["a", "b", "year"]).size().unstack(fill_value=0).reindex(columns=range(L.year.min(), L.year.max() + 1), fill_value=0)
    top = piv.sum(axis=1).sort_values(ascending=False).head(14).index
    pair_rows = [{"a": a, "b": b, "counts": [int(v) for v in piv.loc[(a, b)].values], "total": int(piv.loc[(a, b)].sum())} for a, b in top]
    first = g.groupby("fam").year.min()
    out = {
        "years": years,
        "pairs": {"years": [int(c) for c in piv.columns], "rows": pair_rows},
        "networks": {str(y): network(g[g.year == y]) for y in NETWORK_YEARS},
        "families_total": int(g.fam.nunique()),
        "new_families": {int(k): int(v) for k, v in first.value_counts().sort_index().items()},
        "family_notes": FAMILY_NOTES,
    }
    (OUT / "partners.json").write_text(json.dumps(out, ensure_ascii=False))
    print(f"partners.json {(OUT / 'partners.json').stat().st_size / 1e3:.0f} kB; "
          f"{len(years)} rounds, companies {years[0]['companies']}..{max(y['companies'] for y in years)}..{years[-1]['companies']}")


if __name__ == "__main__":
    main()
