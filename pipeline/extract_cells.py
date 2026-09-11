#!/usr/bin/env python3
"""Extract the 120 question cells of the Ada Lovelace Institute / NICE sociotechnical
evaluation matrix (Rincon and Chowdhury, 2026, CC BY-NC 4.0) from the published
Google Sheet export into data/cells.json. Cell text is reproduced under CC BY-NC 4.0
with attribution; see LICENSE-DATA."""
import zipfile, re, html, json, sys, hashlib
src = "data/sociotechnical-evaluation-matrix.xlsx"
z = zipfile.ZipFile(src)
ss = []
sx = z.read("xl/sharedStrings.xml").decode()
for si in re.findall(r"<si>(.*?)</si>", sx, flags=re.S):
    ss.append(html.unescape("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, flags=re.S))))
wb = z.read("xl/workbook.xml").decode()
sheet_names = re.findall(r'<sheet [^>]*name="([^"]+)"', wb)
STAGE_CODE = {"Design": "DES", "Development": "DEV", "Deployment": "DEP"}
cells = []
for idx, sheet in enumerate(sheet_names, start=1):
    if sheet not in STAGE_CODE: continue
    xml = z.read(f"xl/worksheets/sheet{idx}.xml").decode()
    grid = {}
    # Self-closing empty cells (<c r="F6" s="6"/>) must not swallow the cells after them.
    for m in re.finditer(r'<c r="([A-Z]+)(\d+)"([^>/]*)(?:/>|>(.*?)</c>)', xml, flags=re.S):
        col, row, attrs, inner = m.groups()
        if inner is None: continue
        v = re.search(r"<v>(.*?)</v>", inner, flags=re.S)
        if not v: continue
        val = v.group(1)
        if 't="s"' in attrs: val = ss[int(val)]
        grid[(col, int(row))] = re.sub(r"\s+", " ", val).strip()
    # header row 5: columns B.. hold lifecycle sub-stage names; the sheet repeats them
    # to the right for the response block, so stop at the first repeat.
    cols = []
    for col in "BCDEFGHIJK":
        name = grid.get((col, 5))
        if not name: break
        if name in [c[1] for c in cols]: break
        cols.append((col, name))
    for row in range(6, 16):
        criterion = grid.get(("A", row))
        if not criterion: continue
        for col, colname in cols:
            q = grid.get((col, row))
            if not q: continue
            cid = f"{STAGE_CODE[sheet]}-{col}{row}"
            cells.append({"id": cid, "stage": sheet, "column": colname,
                          "criterion": criterion, "question": q,
                          "sha256": hashlib.sha256(q.encode()).hexdigest()[:12]})
json.dump({"source": "https://www.adalovelaceinstitute.org/resource/sociotechnical-evaluation-matrix/",
           "sheet_id": "11NIShoLv59ZmlrbaOgQTfKPHVLkwLWefRNcs9yNRBxM",
           "authors": "Cam Rincon and Rumman Chowdhury, Ada Lovelace Institute, 8 September 2026",
           "licence": "CC BY-NC 4.0", "cells": cells},
          open("data/cells.json", "w"), indent=1, ensure_ascii=False)
from collections import Counter
print(len(cells), "cells;", Counter(c["stage"] for c in cells))
print(Counter(c["criterion"] for c in cells))
