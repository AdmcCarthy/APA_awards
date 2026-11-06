"""Map Sodir licensee entity names to today's corporate family.

Used only for long-run continuity charts (pairs and shares over time). The
mapping follows well-known Norwegian-shelf transactions; anything not listed
keeps its own (cleaned) name. Verify before relying on it for anything formal.
"""

from __future__ import annotations

import re

# (regex on Sodir long name, family) — first match wins
FAMILY_RULES: list[tuple[str, str]] = [
    (r"^(Equinor|Statoil|StatoilHydro|Norsk Hydro)", "Equinor"),
    (r"^(Aker BP|Det norske|Det Norske|BP Norge|Lundin)", "Aker BP"),
    (r"^(Vår Energi|Eni Norge|Point Resources|Neptune Energy|ExxonMobil)", "Vår Energi"),
    (r"^(Harbour Energy|Wintershall|DEA Norge|RWE Dea|Premier Oil|Chrysaor)", "Harbour Energy"),
    (r"^(DNO|Faroe Petroleum)", "DNO"),
    (r"^(ORLEN|Orlen|PGNiG|LOTOS)", "ORLEN"),
    (r"^(Japex|Longboat Japex)", "Japex"),
    (r"^(TotalEnergies|Total E&P)", "TotalEnergies"),
    (r"^(INPEX Idemitsu|Idemitsu)", "INPEX Idemitsu"),
    (r"^(Repsol|Talisman)", "Repsol"),
    (r"^OMV", "OMV"),
    (r"^Petoro", "Petoro"),
    (r"^ConocoPhillips", "ConocoPhillips"),
    (r"^(A/S Norske Shell|Shell)", "Shell"),
    (r"^Concedo", "Concedo"),
    (r"^Wellesley", "Wellesley"),
    (r"^OKEA", "OKEA"),
]

# Transactions behind the mapping, for the methods note.
FAMILY_NOTES = {
    "Equinor": "Statoil merged with Norsk Hydro's oil and gas arm in 2007 and was renamed Equinor in 2018.",
    "Aker BP": "Det norske merged with BP Norge in 2016 to form Aker BP, which acquired Lundin's Norwegian business in 2022.",
    "Vår Energi": "Eni Norge and Point Resources merged in 2018; Vår later bought ExxonMobil's (2019) and Neptune's (2024) Norwegian assets.",
    "Harbour Energy": "Harbour formed from Chrysaor and Premier Oil (2021) and took over Wintershall Dea's Norwegian business in 2024.",
    "DNO": "DNO acquired Faroe Petroleum in 2019.",
    "ORLEN": "ORLEN absorbed LOTOS and PGNiG in 2022.",
    "Repsol": "Repsol acquired Talisman in 2015.",
    "Japex": "Longboat Japex is grouped with Japex.",
}


def clean(name: str) -> str:
    """Strip legal suffixes and '(old)' markers from a Sodir company name."""
    n = re.sub(r"\s*\(old\)\s*$", "", name)
    n = re.sub(r"\s*\((Norge|Norway)\)", "", n)
    n = re.sub(r"\s+(Norge|Norway|Norwegian Branch|Norway Branch)?\s*(AS|ASA|A/S|AB)?\s*$", "", n).strip()
    return n or name


def family(name: str) -> str:
    """Corporate family for a Sodir licensee long name."""
    for pat, fam in FAMILY_RULES:
        if re.match(pat, name):
            return fam
    return clean(name)
