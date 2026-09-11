#!/usr/bin/env python3
"""Every headline figure in README.md and, when the local checkout exists, in the gov.tesseract.academy
article page must appear verbatim as emitted by pipeline/article_numbers.py. Numbers are matched as
whole tokens so 39 does not match 139."""
import json, re, sys, os
n=json.load(open("data/article_numbers.json"))
targets={"README.md":["A","B","C","studies","median_evidenced","E18_prompt","E34_ci","E08c_language","E35_energy","pct_pairs"]}
page=os.path.expanduser("~/projects/Tesseract-Gov-Website/pages/research/SociotechnicalMatrixEvidence.tsx")
if os.path.exists(page): targets[page]=["A","B","C","studies","median_evidenced","E18_prompt","E34_ci","E08c_language","E35_energy","pct_pairs"]
fails=[]
for path,keys in targets.items():
    if not os.path.exists(path): fails.append(f"{path} missing"); continue
    txt=open(path,encoding="utf-8").read()
    for k in keys:
        v=n[k]; s=f"{v:g}" if isinstance(v,float) else str(v)
        if not re.search(r"(?<![\d.])"+re.escape(s)+r"(?![\d])",txt): fails.append(f"{path}: figure {k}={s} not found")
if fails: print("FAIL"); [print(" -",f) for f in fails]; sys.exit(1)
print("OK: article figures match the data for", ", ".join(targets))
