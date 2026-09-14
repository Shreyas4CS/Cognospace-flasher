#!/usr/bin/env python3
"""
Build (and audit) the firmware folder tree for the Coggy Flasher.

The catalogue and the table list both live inside index.html, so this reads
them from there rather than keeping a second copy that can drift.

    python3 scaffold.py              # create every missing folder
    python3 scaffold.py --check      # report only, create nothing
    python3 scaffold.py --grade 8    # limit to one grade
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.html")


def load(index_path):
    with open(index_path, encoding="utf-8") as fh:
        src = fh.read()

    catalog_m = re.search(
        r'<script type="application/json" id="catalog">(.*?)</script>', src, re.S
    )
    if not catalog_m:
        sys.exit("Could not find the catalogue block in index.html")
    catalog = json.loads(catalog_m.group(1))

    tables = re.findall(r"\{\s*id:\s*'(T\d+)'\s*,\s*name:\s*'([^']*)'", src)
    if not tables:
        sys.exit("Could not find the TABLES list in index.html")

    return catalog, tables


def targets(catalog, tables, grade_filter=None):
    """Yield (relative_path, grade, code, table_id) for every build."""
    for grade in catalog["grades"]:
        if grade_filter and str(grade["grade"]) != str(grade_filter):
            continue
        for activity in grade["activities"]:
            parts = activity.get("parts") or [{"file": activity.get("file")}]
            for part in parts:
                template = part.get("file")
                if not template:
                    continue
                for table_id, _name in tables:
                    path = template.replace("{table}", table_id).lstrip("/")
                    yield path, grade["grade"], activity["code"], table_id


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, create nothing")
    ap.add_argument("--grade", help="limit to one grade, e.g. 8 or resources")
    ap.add_argument("--index", default=INDEX, help="path to index.html")
    args = ap.parse_args()

    catalog, tables = load(args.index)
    rows = list(targets(catalog, tables, args.grade))

    made, present, missing = 0, 0, []
    for path, _grade, code, table_id in rows:
        folder = os.path.dirname(path)
        if os.path.isfile(path):
            present += 1
        else:
            missing.append((code, table_id))
            if not args.check and not os.path.isdir(folder):
                os.makedirs(folder, exist_ok=True)
                made += 1

    # Static folders the page also expects.
    if not args.check:
        for folder in ("assets", "vendor/esptool-js"):
            os.makedirs(folder, exist_ok=True)

    print(f"{len(rows)} builds referenced by the catalogue "
          f"({len(tables)} tables)")
    print(f"  present : {present}")
    print(f"  missing : {len(missing)}")
    if not args.check:
        print(f"  folders created: {made}")

    if missing:
        by_code = {}
        for code, table_id in missing:
            by_code.setdefault(code, []).append(table_id)
        print("\nMissing firmware.bin:")
        for code in sorted(by_code):
            tabs = by_code[code]
            shown = "all tables" if len(tabs) == len(tables) else ", ".join(tabs)
            print(f"  {code}: {shown}")


if __name__ == "__main__":
    main()
