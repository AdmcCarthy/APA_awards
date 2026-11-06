"""Assemble the static site for GitHub Pages into _site/.

web/index.html is authored as an Artifact body fragment (no doctype/head);
this wraps it in a full standards-mode document and copies the data files.

Usage: python scripts/build_site.py [out_dir]
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
"""
TAIL = "\n</body>\n</html>\n"


def main(out: Path) -> None:
    src = Path("web")
    body = (src / "index.html").read_text(encoding="utf-8")
    body = body.replace('<meta charset="utf-8">\n', "", 1)
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src / "data", out / "data")
    (out / "index.html").write_text(HEAD + body + TAIL, encoding="utf-8")
    (out / ".nojekyll").touch()
    n = len(list((out / "data").glob("*.json")))
    assert n >= 10, f"expected the 10 data files, found {n}"
    print(f"wrote {out}/index.html and {n} data files")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "_site"))
