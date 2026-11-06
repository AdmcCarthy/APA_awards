"""Build compact web data for the APA narrative page from raw Sodir layers.

Inputs : data/raw/*.geojson (from fetch_sodir.py), WGS84 lon/lat.
Outputs: web/data/*.json

Notes
-----
* Sodir labels APA rounds "TFO<year>" (tildeling i forhåndsdefinerte områder).
  The awards announced 13 Jan 2026 are round TFO2025, formally granted 20 Mar 2026.
* Areas are Sodir's `prlOriginalArea` in km² (area at award).
* Distances are computed in ETRS89-LAEA (EPSG:3035), in km, polygon edge to
  polygon edge (0 if touching/overlapping).
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.polygon import orient

RAW = Path("data/raw")
OUT = Path("web/data")
ROUND = "TFO2025"
EQUAL_AREA = 3035

# Operators given their own colour slot on the page; everyone else is "Other".
FEATURED = [
    "Equinor Energy AS",
    "Aker BP ASA",
    "Vår Energi ASA",
    "DNO Norge AS",
    "Harbour Energy Norge AS",
    "Wellesley Petroleum AS",
]
SHORT = {
    "Equinor Energy AS": "Equinor",
    "Aker BP ASA": "Aker BP",
    "Vår Energi ASA": "Vår Energi",
    "DNO Norge AS": "DNO",
    "Harbour Energy Norge AS": "Harbour Energy",
    "Wellesley Petroleum AS": "Wellesley",
    "Petoro AS": "Petoro",
    "ORLEN Upstream Norway AS": "ORLEN",
    "INPEX Idemitsu Norge AS": "INPEX Idemitsu",
    "OMV Norge AS": "OMV",
    "OKEA ASA": "OKEA",
    "Japex Norge AS": "Japex",
    "Concedo AS": "Concedo",
    "Source Energy AS": "Source Energy",
    "ConocoPhillips Skandinavia AS": "ConocoPhillips",
    "Repsol Norge AS": "Repsol",
    "Petrolia NOCO AS": "Petrolia NOCO",
    "Pandion Energy AS": "Pandion",
    "TotalEnergies EP Norge AS": "TotalEnergies",
}
AREA_NAME = {"North sea": "North Sea", "Norwegian sea": "Norwegian Sea", "Barents sea": "Barents Sea"}


def short(name: str) -> str:
    """Return a display name for a Sodir company long name."""
    return SHORT.get(name, name.replace(" AS", "").replace(" ASA", ""))


def round_coords(geom_json: dict, nd: int = 3) -> dict:
    """Round GeoJSON coordinates (3 dp ≈ 100 m, ample for page scales)."""

    def rec(c):
        if isinstance(c[0], (int, float)):
            return [round(c[0], nd), round(c[1], nd)]
        return [rec(x) for x in c]

    geom_json["coordinates"] = rec(geom_json["coordinates"])
    return geom_json


def d3_orient(geom):
    """Orient polygon rings clockwise (exterior) as d3-geo's spherical rule expects.

    RFC 7946 uses the opposite winding; d3 would read such rings as 'the whole
    globe minus this polygon'.
    """
    if isinstance(geom, Polygon):
        return orient(geom, sign=-1.0)
    if isinstance(geom, MultiPolygon):
        # drop slivers collapsed by simplification: their winding is ill-defined
        parts = [orient(g, sign=-1.0) for g in geom.geoms if g.area > 1e-7]
        return MultiPolygon(parts) if len(parts) > 1 else (parts[0] if parts else Polygon())
    return geom


def to_fc(gdf: gpd.GeoDataFrame, props: list[str], nd: int = 3) -> dict:
    """GeoDataFrame -> compact FeatureCollection dict."""
    feats = []
    clean = gdf[props].astype(object).where(gdf[props].notna(), None)
    for rec_, geom in zip(clean.to_dict("records"), gdf.geometry):
        if geom is None or geom.is_empty:
            continue
        # snap to the output grid first so rounding cannot create flipped slivers
        geom = d3_orient(shapely.set_precision(geom, 10.0**-nd))
        if geom.is_empty:
            continue
        g = json.loads(gpd.GeoSeries([geom]).to_json())["features"][0]["geometry"]
        feats.append({"type": "Feature", "properties": rec_, "geometry": round_coords(g, nd)})
    return {"type": "FeatureCollection", "features": feats}


def load_licensees() -> pd.DataFrame:
    """Licensee history table with datetimes."""
    rows = [f["properties"] for f in json.loads((RAW / "licensee_hst.geojson").read_text())["features"]]
    h = pd.DataFrame(rows)
    for c in ["prlLicenseeDateValidFrom", "prlLicenseeDateValidTo", "prlOperDateValidFrom"]:
        h[c] = pd.to_datetime(h[c], unit="ms", errors="coerce")
    return h


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lic = gpd.read_file(RAW / "licence_tfo.geojson")
    lic["granted"] = pd.to_datetime(lic.prlDateGranted, unit="ms")
    awd = lic[lic.prlLicensingActivityName == ROUND].copy()
    assert awd.prlName.is_unique, "duplicate licence names in award"
    assert (awd.prlOriginalArea > 0).all(), "non-positive licence area"
    grant_date = awd.granted.min()

    # --- partners at grant -------------------------------------------------
    h = load_licensees()
    h = h[h.prlNpdidLicence.isin(awd.prlNpdidLicence)]
    first = h.groupby("prlNpdidLicence").prlLicenseeDateValidFrom.transform("min")
    at_grant = h[h.prlLicenseeDateValidFrom == first].copy()
    tot = at_grant.groupby("prlNpdidLicence").prlLicenseeInterest.sum()
    assert np.allclose(tot, 100, atol=0.01), "interests at grant do not sum to 100 %"
    at_grant["is_op"] = at_grant.prlOperDateValidFrom.notna()
    later = h[h.prlLicenseeDateValidFrom > grant_date]

    partners = (
        at_grant.sort_values(["prlNpdidLicence", "is_op", "prlLicenseeInterest"], ascending=[True, False, False])
        .groupby("prlNpdidLicence")
        .apply(
            lambda d: [
                {"c": short(r.cmpLongName), "pct": round(float(r.prlLicenseeInterest), 3), "op": bool(r.is_op)}
                for r in d.itertuples()
            ],
            include_groups=False,
        )
    )
    op_at_grant = at_grant[at_grant.is_op].set_index("prlNpdidLicence").cmpLongName
    awd["operator_long"] = awd.prlNpdidLicence.map(op_at_grant).fillna(awd.cmpLongName)
    awd["operator"] = awd.operator_long.map(short)
    awd["group"] = np.where(awd.operator_long.isin(FEATURED), awd.operator, "Other")
    awd["partners"] = awd.prlNpdidLicence.map(partners)
    awd["area_name"] = awd.prlMainArea.map(AREA_NAME)
    awd["kind"] = np.where(awd.prlAdditAreaTo.notna(), "additional", "new")
    awd["strat"] = awd.prlStratigraphical.str.startswith("YES")
    awd["changed"] = awd.prlNpdidLicence.isin(later.prlNpdidLicence)

    # --- distance to nearest producing / approved field ---------------------
    fields = gpd.read_file(RAW / "fields.geojson")
    live = fields[fields.fldCurrentActivitySatus.isin(["Producing", "Approved for production"])]
    a_p = awd.to_crs(EQUAL_AREA)
    f_p = live.to_crs(EQUAL_AREA)
    f_p = f_p[f_p.geometry.notna() & ~f_p.geometry.is_empty]
    f_p["geometry"] = f_p.geometry.make_valid()
    dmat = np.vstack([f_p.distance(g).to_numpy() for g in a_p.geometry])  # licences x fields, m
    assert not np.isnan(dmat).all(axis=1).any(), "licence with no finite field distance"
    dist = pd.Series(np.nanmin(dmat, axis=1) / 1000.0, index=a_p.index)
    nearest = pd.Series(f_p.fldName.to_numpy()[np.nanargmin(dmat, axis=1)], index=a_p.index)
    awd["dist_km"] = dist.round(1).values
    awd["nearest_field"] = nearest.values
    awd["cx"] = awd.geometry.representative_point().x.round(3)
    awd["cy"] = awd.geometry.representative_point().y.round(3)

    awd_out = awd.rename(columns={"prlName": "name", "prlOriginalArea": "km2"})
    props = ["name", "km2", "operator", "group", "partners", "area_name", "kind", "strat",
             "changed", "dist_km", "nearest_field", "cx", "cy", "prlAdditAreaTo", "prlFactPageUrl"]
    (OUT / "awards.json").write_text(json.dumps(to_fc(awd_out.sort_values("km2", ascending=False), props, 4),
                                                ensure_ascii=False))

    # --- company table --------------------------------------------------------
    area = awd.set_index("prlNpdidLicence").prlOriginalArea
    at_grant["net_km2"] = at_grant.prlLicenseeInterest / 100 * at_grant.prlNpdidLicence.map(area)
    comp = (
        at_grant.groupby("cmpLongName")
        .agg(licences=("prlNpdidLicence", "nunique"), operated=("is_op", "sum"),
             net_km2=("net_km2", "sum"), mean_pct=("prlLicenseeInterest", "mean"))
        .reset_index()
    )
    comp["name"] = comp.cmpLongName.map(short)
    comp["featured"] = comp.cmpLongName.isin(FEATURED)
    comp = comp.sort_values(["licences", "operated"], ascending=False)
    comp_rows = comp[["name", "licences", "operated", "net_km2", "mean_pct", "featured"]].round(1).to_dict("records")

    # --- co-licensee pairs ----------------------------------------------------
    pairs = (
        at_grant[["prlNpdidLicence", "cmpLongName"]]
        .merge(at_grant[["prlNpdidLicence", "cmpLongName"]], on="prlNpdidLicence")
        .query("cmpLongName_x < cmpLongName_y")
        .groupby(["cmpLongName_x", "cmpLongName_y"]).size().sort_values(ascending=False)
    )
    pair_rows = [{"a": short(a), "b": short(b), "n": int(n)} for (a, b), n in pairs.items()]

    # --- APA history ------------------------------------------------------------
    orig = lic[lic.prlPartitionFrom.isna()].copy()
    orig["year"] = orig.prlLicensingActivityName.str[3:].astype(int)
    hist = (
        orig.groupby("year")
        .agg(licences=("prlName", "size"), km2=("prlOriginalArea", "sum"),
             active=("prlActive", lambda s: int((s == "Y").sum())),
             award_date=("granted", "min"))
        .reset_index()
    )
    hist["award_date"] = hist.award_date.dt.strftime("%Y-%m-%d")
    by_area = orig.groupby(["year", "prlMainArea"]).size().unstack(fill_value=0).rename(columns=AREA_NAME)

    hist_rows = hist.merge(by_area, left_on="year", right_index=True).to_dict("records")

    summary = {
        "round": ROUND,
        "announced": "2026-01-13",
        "granted": grant_date.strftime("%Y-%m-%d"),
        "n_licences": int(len(awd)),
        "n_offered_announced": 57,
        "n_companies": int(at_grant.cmpLongName.nunique()),
        "n_operators": int(awd.operator.nunique()),
        "total_km2": int(awd.prlOriginalArea.sum()),
        "median_km2": float(awd.prlOriginalArea.median()),
        "by_area": awd.groupby("area_name").agg(n=("prlName", "size"), km2=("prlOriginalArea", "sum")).reset_index().to_dict("records"),
        "n_additional": int((awd.kind == "additional").sum()),
        "n_strat": int(awd.strat.sum()),
        "n_changed_since": int(awd.changed.sum()),
        "dist_le_25": int((awd.dist_km <= 25).sum()),
        "dist_le_50": int((awd.dist_km <= 50).sum()),
        "median_dist": float(awd.dist_km.median()),
        "companies": comp_rows,
        "pairs": pair_rows[:40],
        "history": hist_rows,
        "later_changes": [
            {"licence": r.prlName, "company": short(r.cmpLongName), "pct": float(r.prlLicenseeInterest),
             "from": r.prlLicenseeDateValidFrom.strftime("%Y-%m-%d")}
            for r in later.sort_values("prlLicenseeDateValidFrom").itertuples()
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=str))

    # --- context layers ----------------------------------------------------------
    land = gpd.read_file(RAW / "land.geojson")
    land = land[land.geometry.notna()].copy()
    land["geometry"] = land.geometry.make_valid()
    land = land.clip((-8.0, 53.0, 42.0, 76.0)).explode(index_parts=False)
    land = land[land.geom_type == "Polygon"]
    land = land[land.to_crs(EQUAL_AREA).area > 2e6]  # drop islets < 2 km²
    land["geometry"] = land.geometry.simplify(0.004, preserve_topology=True)
    (OUT / "land.json").write_text(json.dumps(to_fc(land.assign(k=1), ["k"], 3)))

    seab = gpd.read_file(RAW / "sea_boundaries.geojson")
    seab["geometry"] = seab.geometry.simplify(0.005)
    (OUT / "sea_boundaries.json").write_text(json.dumps(to_fc(seab.assign(k=1), ["k"], 3)))

    blocks = gpd.read_file(RAW / "blocks.geojson")
    blocks["geometry"] = blocks.geometry.simplify(0.003, preserve_topology=True)
    blocks["awarded"] = blocks.geometry.intersects(awd.union_all().buffer(-0.001))
    (OUT / "blocks.json").write_text(json.dumps(to_fc(blocks, ["blcName", "blcMainArea", "awarded"], 3),
                                                ensure_ascii=False))
    quads = gpd.read_file(RAW / "quadrants.geojson")
    quads["geometry"] = quads.geometry.simplify(0.003, preserve_topology=True)
    qcols = [c for c in quads.columns if c.startswith("qad") and "Name" in c][:1]
    (OUT / "quadrants.json").write_text(json.dumps(to_fc(quads, qcols, 3), ensure_ascii=False))

    apa_h = gpd.read_file(RAW / "apa_gross_hst.geojson")
    apa = apa_h[apa_h.year == int(ROUND[3:])].copy()
    assert len(apa) == 1, "expected one APA outline for the round year"
    apa["geometry"] = apa.geometry.make_valid().simplify(0.003)
    (OUT / "apa_area.json").write_text(json.dumps(to_fc(apa.assign(k=1), ["k"], 3)))
    summary["apa_area_km2"] = (
        apa_h[["year", "km2"]].dropna().sort_values("year").assign(km2=lambda d: d.km2.round()).to_dict("records")
    )
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=str))

    act = gpd.read_file(RAW / "licence_active.geojson")
    act = act[act.prlLicensingActivityName != ROUND]
    act["geometry"] = act.geometry.simplify(0.002, preserve_topology=True)
    (OUT / "licences_existing.json").write_text(json.dumps(to_fc(act, ["prlName"], 3)))

    live2 = live.copy()
    live2["geometry"] = live2.geometry.make_valid().simplify(0.002, preserve_topology=True).buffer(0)
    live2["cx"] = live2.geometry.representative_point().x.round(3)
    live2["cy"] = live2.geometry.representative_point().y.round(3)
    (OUT / "fields.json").write_text(json.dumps(to_fc(live2, ["fldName", "cx", "cy"], 3), ensure_ascii=False))

    towns = ["Oslo", "Bergen", "Stavanger", "Trondheim", "Kristiansund", "Ålesund", "Florø", "Bodø",
             "Sandnessjøen", "Tromsø", "Hammerfest", "Kirkenes", "Kristiansand", "Haugesund", "Harstad", "Vardø"]
    pn = gpd.read_file(RAW / "place_names.geojson")
    pn = pn[pn.tettstedsn.isin(towns)].sort_values("tot_bef", ascending=False).drop_duplicates("tettstedsn")
    pn["geometry"] = pn.geometry.centroid if pn.geom_type.iloc[0] != "Point" else pn.geometry
    (OUT / "towns.json").write_text(json.dumps(
        [{"n": r.tettstedsn, "x": round(r.geometry.x, 3), "y": round(r.geometry.y, 3)} for r in pn.itertuples()],
        ensure_ascii=False))

    for p in sorted(OUT.glob("*.json")):
        print(f"{p.name:24s} {p.stat().st_size/1e3:8.0f} kB")
    print(json.dumps({k: v for k, v in summary.items() if not isinstance(v, list)}, indent=1))


if __name__ == "__main__":
    main()
