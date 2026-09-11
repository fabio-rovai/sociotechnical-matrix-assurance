#!/usr/bin/env python3
"""Offline known-answer tests. Run from the repository root: python3 tests/test_known_answers.py"""
import json, glob, subprocess, sys, re, hashlib
fails=[]
def check(cond,msg):
    if not cond: fails.append(msg)
cells=json.load(open("data/cells.json"))["cells"]; V=json.load(open("data/verifiability.json"))["cells"]; F=json.load(open("data/evidence_fields.json"))["fields"]
check(len(cells)==120, f"expected 120 cells, got {len(cells)}")
from collections import Counter
c=Counter(v["class"] for v in V.values())
check(c=={"A":39,"B":75,"C":6}, f"class counts {dict(c)}")
check(set(V)=={x["id"] for x in cells}, "verifiability ids differ from cell ids")
for cid,v in V.items():
    check((v["class"]=="A")==bool(v["fields"]), f"{cid}: fields present iff class A")
    check(all(f in F for f in v["fields"]), f"{cid}: unknown field")
used={f for v in V.values() for f in v["fields"]}; check(used==set(F), f"unused fields {set(F)-used} or undefined {used-set(F)}")
# the cell text hashes must match the published sheet as extracted (guards silent edits)
for x in cells: check(hashlib.sha256(x["question"].encode()).hexdigest()[:12]==x["sha256"], f"{x['id']}: question text changed since extraction")
# stage x criterion grid is complete
grid=Counter((x["stage"],x["criterion"]) for x in cells)
check(all(n in (3,4,5) for n in grid.values()) and len(grid)==30, "stage x criterion grid incomplete")
# outward-facing text carries no em dashes
for path in ["README.md","REPORT.md","BUILD_REPORT.md","docs/EXTRACTION_BRIEF.md","LICENSE","ontology/stm.ttl","data/evidence_fields.json","data/verifiability.json"]:
    try: txt=open(path,encoding="utf-8").read()
    except FileNotFoundError: continue
    check("—" not in txt, f"{path}: em dash found")
# every record passes the structural and quote-grounding checker
recs=sorted(glob.glob("data/records/*.json"))
for r in recs:
    p=subprocess.run([sys.executable,"tests/check_record.py",r],capture_output=True,text=True)
    check(p.returncode==0, f"{r}: checker failed\n{p.stdout}")
# the dual computation agrees (pyshacl path; the engine path is run separately where the binary exists)
if recs:
    p=subprocess.run([sys.executable,"pipeline/verdicts.py"],capture_output=True,text=True)
    check(p.returncode==0, f"verdicts.py failed:\n{p.stdout}{p.stderr}")
    V2=json.load(open("data/verdicts.json"))
    check(len(V2["artefact_cells"])==39, "verdicts do not cover 39 artefact cells")
    # known answer: DEV-D13 is evidenced iff E18 and E27 are both present
    for r in recs:
        d=json.load(open(r)); pm=d["study"]["pmid"]; ev=d["evidence"]
        exp="evidenced" if ev["E18"]["status"]=="present" and ev["E27"]["status"]=="present" else ("not_evidenced" if ev["E18"]["status"] in ("absent","not_applicable") and ev["E27"]["status"] in ("absent","not_applicable") else "partially_evidenced")
        check(V2["verdicts"][pm]["DEV-D13"]==exp, f"{pm}: DEV-D13 verdict {V2['verdicts'][pm]['DEV-D13']} expected {exp}")
if fails:
    print("FAIL"); [print(" -",f) for f in fails]; sys.exit(1)
print(f"OK: 120 cells, 39/75/6, {len(recs)} records checked")
