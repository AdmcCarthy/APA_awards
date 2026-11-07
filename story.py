"""Metrics and derived datasets for "Close to home" (APA 2025). Inputs come from data/*.json,
built from Sodir FactMaps by scripts/build_data.py and scripts/build_partners.py."""

import pandas as pd

from subscout import metric

# Featured operators, in identity-palette order. Beyond the palette's slots they fold into "Other".
GROUPS = ["Equinor", "Aker BP", "Vår Energi", "Wellesley", "DNO", "Harbour Energy"]


def datasets(d):
    s, p = d["summary"], d["partners"]
    awards = d["awards"]
    for f in awards["features"]:
        pr = f["properties"]
        pr["partner_list"] = ", ".join(
            f"{x['c']} {x['pct']:g}%{' (op.)' if x['op'] else ''}" for x in pr["partners"]
        )
        pr["area_km2"] = f"{pr['km2']:,} km²"
        pr["distance"] = f"{pr['dist_km']:.1f} km to {pr['nearest_field'].title()}"
    props = d["awards_props"].assign(
        type=lambda x: x.strat.map({True: "Stratigraphic", False: "Full depth"}),
        status=lambda x: x.kind.map({"new": "New", "additional": "Additional area"}),
        operator_group=lambda x: x.operator.where(x.operator.isin(GROUPS), "Other"),
    )
    companies = pd.DataFrame(s["companies"]).assign(
        partner=lambda x: x.licences - x.operated,
        group=lambda x: x.name.where(x.name.isin(GROUPS), "Other"),
    )
    hist = pd.DataFrame(s["history"])
    history = pd.concat(
        [
            hist.assign(series="Still active", n=hist.active),
            hist.assign(series="Relinquished or expired", n=hist.licences - hist.active),
        ]
    )[["year", "series", "n"]]
    years = pd.DataFrame(p["years"])
    club = years.assign(series="Companies")[["year", "series", "companies"]]
    equinor = pd.DataFrame(
        {"year": years.year, "series": "Equinor", "share": [r["share"]["Equinor"] for r in p["years"]]}
    )
    changes = (
        pd.DataFrame(s["later_changes"])
        .sort_values(["from", "licence", "pct"], ascending=[True, True, False])
        .rename(columns={"licence": "Licence", "company": "Company", "pct": "Share", "from": "From"})
    )
    grp = lambda c: c if c in GROUPS else "Other"
    net_nodes = pd.DataFrame(
        [{"year": int(y), "id": n["id"], "n": n["n"], "op": n["op"], "group": grp(n["id"])}
         for y, net in p["networks"].items() for n in net["nodes"]]
    )
    net_edges = pd.DataFrame(
        [{"year": int(y), **e} for y, net in p["networks"].items() for e in net["edges"]]
    )
    pairs = pd.DataFrame(
        [{"pair": f"{r['a']} – {r['b']}", "year": yr, "n": c}
         for r in p["pairs"]["rows"] for yr, c in zip(p["pairs"]["years"], r["counts"])]
    )
    return {"props": props, "companies": companies, "history": history, "club": club,
            "equinor_share": equinor, "changes": changes, "net_nodes": net_nodes,
            "net_edges": net_edges, "pairs": pairs}


def pair_counts(p, a, b):
    """Licences shared by families a and b, per round: {year: n}."""
    row = next(r for r in p["pairs"]["rows"] if {r["a"], r["b"]} == {a, b})
    return dict(zip(p["pairs"]["years"], row["counts"]))


def metrics(d):
    s, p = d["summary"], d["partners"]
    a = d["props"]
    comp = d["companies"].set_index("name")
    years = {r["year"]: r for r in p["years"]}
    hist = pd.DataFrame(s["history"])
    old = hist[hist.year <= 2015]
    ns, nws, bs = (a[a.area_name == n] for n in ("North Sea", "Norwegian Sea", "Barents Sea"))
    solo = a[a.partners.map(len) == 1]
    far = a[a.dist_km > 50]
    remote = a.loc[a.dist_km.idxmax()]
    sodir, obs, der = "sodir", "observed", "derived"
    nets = p["networks"]
    hub = {"Equinor", "Aker BP", "Petoro"}
    hub_in = int(a.partners.map(lambda ps: any(x["c"] in hub for x in ps)).sum())
    ep = pair_counts(p, "Equinor", "Petoro")
    ad = pair_counts(p, "Aker BP", "DNO")
    net_m = {}
    for y in ("2008", "2013", "2019", "2025"):
        net_m[f"net_{y}_groups"] = metric(len(nets[y]["nodes"]), f"Company families winning APA {y} licences (grouped by today's owner)", sodir, der)
        net_m[f"net_{y}_pairs"] = metric(len(nets[y]["edges"]), f"Distinct pairs of families sharing at least one APA {y} licence", sodir, der)
        if y in ("2008", "2013"):
            net_m[f"net_{y}_licences"] = metric(nets[y]["licences"], f"Licences in APA {y}", sodir, obs)
    return {
        **net_m,
        "n_pairs_shown": metric(len(p["pairs"]["rows"]), "Family pairs in the partnership timeline (most shared licences, 2003-2025)", sodir, der),
        "hub_in": metric(hub_in, "APA 2025 licences that include Equinor, Aker BP or Petoro", sodir, der),
        "ep_total": metric(sum(ep.values()), "Licences shared by Equinor and Petoro, APA 2003-2025", sodir, der),
        "ep_rounds": metric(sum(1 for v in ep.values() if v), "APA rounds in which Equinor and Petoro shared a licence", sodir, der),
        "ad_since_2017": metric(sum(v for y, v in ad.items() if y >= 2017), "Licences shared by Aker BP and DNO, APA 2017-2025", sodir, der),
        "ad_before_2017": metric(sum(v for y, v in ad.items() if y < 2017), "Licences shared by Aker BP and DNO, APA 2003-2016", sodir, der),
        "n_licences": metric(len(a), "Licences in round TFO2025 (APA 2025)", sodir, obs),
        "n_offered": metric(s["n_offered_announced"], "Offers in the ministry's announcement, 13 January 2026", "ministry", obs),
        "near_1km": metric(int((a.dist_km <= 1).sum()), "Licences ≤ 1 km from a producing or approved field (edge to edge)", sodir, der),
        "near_25km": metric(int((a.dist_km <= 25).sum()), "Licences ≤ 25 km from a producing or approved field", sodir, der),
        "median_dist": metric(float(a.dist_km.median()), "Median distance to the nearest field, km", sodir, der, "km"),
        "n_companies": metric(years[2025]["companies"], "Legal companies holding APA 2025 licences at award", sodir, obs),
        "companies_2013": metric(years[2013]["companies"], "Legal companies holding APA 2013 licences at award", sodir, obs),
        "equinor_share": metric(years[2025]["share"]["Equinor"], "Share of APA 2025 licences that include Equinor", sodir, der),
        "equinor_share_2013": metric(years[2013]["share"]["Equinor"], "Share of APA 2013 licences that include Equinor (incl. Statoil, Hydro)", sodir, der),
        "equinor_operated": metric(int(comp.loc["Equinor", "operated"]), "Licences operated by Equinor", sodir, obs),
        "equinor_in": metric(int(comp.loc["Equinor", "licences"]), "Licences with an Equinor stake", sodir, obs),
        "equinor_partner": metric(int(comp.loc["Equinor", "partner"]), "Licences where Equinor is a partner, not operator", sodir, der),
        "aker_operated": metric(int(comp.loc["Aker BP", "operated"]), "Licences operated by Aker BP", sodir, obs),
        "aker_in": metric(int(comp.loc["Aker BP", "licences"]), "Licences with an Aker BP stake", sodir, obs),
        "petoro_in": metric(int(comp.loc["Petoro", "licences"]), "Licences with a Petoro (SDFI) stake", sodir, obs),
        "petoro_share": metric(years[2025]["share"]["Petoro"], "Share of APA 2025 licences that include Petoro", sodir, der),
        "top2_share": metric((comp.loc["Equinor", "operated"] + comp.loc["Aker BP", "operated"]) / len(a),
                             "Share of licences operated by Equinor or Aker BP", sodir, der),
        "ns_n": metric(len(ns), "North Sea licences", sodir, obs),
        "ns_median_dist": metric(float(ns.dist_km.median()), "Median distance, North Sea licences, km", sodir, der, "km"),
        "ns_strat": metric(int(ns.strat.sum()), "Stratigraphic North Sea licences", sodir, obs),
        "ns_additional": metric(int((ns.kind == "additional").sum()), "North Sea licences that add area to an existing licence", sodir, obs),
        "nws_n": metric(len(nws), "Norwegian Sea licences", sodir, obs),
        "nws_far": metric(int((nws.dist_km > 60).sum()), "Norwegian Sea licences more than 60 km from a field", sodir, der),
        "bs_n": metric(len(bs), "Barents Sea licences", sodir, obs),
        "remote_km": metric(float(remote.dist_km), f"Distance from licence {remote['name']} to {remote.nearest_field.title()}, km", sodir, der, "km"),
        "n_solo": metric(len(solo), "Licences with a single owner", sodir, obs),
        "n_far50": metric(len(far), "Licences more than 50 km from any field", sodir, der),
        "aker_far50": metric(int((far.operator == "Aker BP").sum()), "Of those, operated by Aker BP", sodir, der),
        "n_strat": metric(s["n_strat"], "Stratigraphic licences", sodir, obs),
        "old_total": metric(int(old.licences.sum()), "Licences from APA rounds up to 2015", sodir, obs),
        "old_active_share": metric(old.active.sum() / old.licences.sum(), "Share of those still active, November 2026", sodir, der),
        "harbour_operated": metric(int((a.operator == "Harbour Energy").sum()), "Licences operated by Harbour Energy (all stratigraphic)", sodir, obs),
        "harbour_strat": metric(int(((a.operator == "Harbour Energy") & a.strat).sum()), "Harbour-operated stratigraphic licences", sodir, obs),
        "n_changed": metric(s["n_changed_since"], "Licences with ownership changes registered after the grant", sodir, obs),
    }
