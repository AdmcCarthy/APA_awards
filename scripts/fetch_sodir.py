"""Fetch licence, licensee, block, APA-area and basemap layers from Sodir FactMaps.

All geometries are requested in WGS84 (EPSG:4326); Sodir's native CRS is ED50
(EPSG:4230). The datum shift (~100 m) is irrelevant at the page's map scales.

Usage: python scripts/fetch_sodir.py [out_dir]
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

DATA = "https://factmaps.sodir.no/api/rest/services/DataService/Data/FeatureServer"
BASE = "https://factmaps.sodir.no/api/rest/services/Basemap/Basemap_simple_grey/MapServer"


def query(
    url: str,
    where: str = "1=1",
    out_fields: str = "*",
    geometry: bool = True,
    max_offset: float | None = None,
    page: int = 1000,
) -> dict:
    """Page through an ArcGIS REST layer query and return a GeoJSON FeatureCollection."""
    feats: list[dict] = []
    offset = 0
    while True:
        params = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": str(geometry).lower(),
            "outSR": 4326,
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page,
        }
        if max_offset:
            params["maxAllowableOffset"] = max_offset
        for attempt in range(4):
            try:
                r = requests.get(f"{url}/query", params=params, timeout=120)
                r.raise_for_status()
                d = r.json()
                break
            except (requests.RequestException, ValueError):
                if attempt == 3:
                    raise
                time.sleep(2**attempt)
        if "error" in d:
            raise RuntimeError(f"{url}: {d['error']}")
        batch = d.get("features", [])
        feats += batch
        exceeded = d.get("exceededTransferLimit") or d.get("properties", {}).get(
            "exceededTransferLimit"
        )
        if not batch or (len(batch) < page and not exceeded):
            break
        offset += len(batch)
    return {"type": "FeatureCollection", "features": feats}


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    jobs = {
        # All APA (TFO) licences ever awarded, with geometry (current area).
        "licence_tfo.geojson": (f"{DATA}/3000", "prlLicensingActivityName LIKE 'TFO%'", "*", True, None),
        # All active licences for background context.
        "licence_active.geojson": (f"{DATA}/3000", "prlActive='Y'", "prlName,prlLicensingActivityName,cmpLongName,prlDateGranted", True, 0.002),
        # Licensee history (attributes only) – filtered later to TFO licences.
        "licensee_hst.geojson": (f"{DATA}/3007", "1=1", "*", False, None),
        "blocks.geojson": (f"{DATA}/1001", "1=1", "*", True, None),
        "quadrants.geojson": (f"{DATA}/1002", "1=1", "*", True, None),
        "apa_gross.geojson": (f"{DATA}/3102", "1=1", "*", True, 0.002),
        # Predefined (APA) area by year; the 2025 outline is the one companies applied in.
        "apa_gross_hst.geojson": (f"{DATA}/3107", "1=1", "year,comment,km2", True, 0.003),
        "fields.geojson": (f"{DATA}/7100", "1=1", "fldName,fldCurrentActivitySatus,cmpLongName,fldMainArea", True, 0.002),
        "land.geojson": (f"{BASE}/5", "1=1", "*", True, 0.005),
        "sea_boundaries.geojson": (f"{BASE}/3", "1=1", "*", True, 0.005),
        "place_names.geojson": (f"{BASE}/0", "1=1", "*", True, None),
    }
    for name, (url, where, fields, geom, mo) in jobs.items():
        fc = query(url, where, fields, geom, mo)
        (out / name).write_text(json.dumps(fc))
        print(f"{name}: {len(fc['features'])} features")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw"))
