"""Tests for geometry helpers in scripts/build_data.py."""

import sys
from pathlib import Path

from shapely.geometry import MultiPolygon, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_data import d3_orient, round_coords, short  # noqa: E402


def test_d3_orient_makes_exterior_clockwise():
    ccw = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert ccw.exterior.is_ccw
    assert not d3_orient(ccw).exterior.is_ccw


def test_d3_orient_drops_slivers():
    big = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    sliver = Polygon([(5, 5), (5 + 1e-5, 5), (5, 5 + 1e-5)])
    out = d3_orient(MultiPolygon([big, sliver]))
    assert isinstance(out, Polygon) and out.area == big.area


def test_round_coords_nested():
    g = {"type": "Polygon", "coordinates": [[[1.23456, 2.34567], [3.0, 4.0]]]}
    assert round_coords(g, 2)["coordinates"] == [[[1.23, 2.35], [3.0, 4.0]]]


def test_short_names():
    assert short("Vår Energi ASA") == "Vår Energi"
    assert short("Unknown Oil AS") == "Unknown Oil"
