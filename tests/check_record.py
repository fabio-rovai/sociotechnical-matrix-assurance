#!/usr/bin/env python3
"""Structural and quote-grounding check for one evidence record. Every present/partial quote must
appear verbatim (whitespace-normalised, case-insensitive) in the study's local full text, unless its
location starts with Supplement or Repository, in which case it must carry a URL."""
import json, sys, re, glob, os
def norm(s): return re.sub(r"[^a-z0-9]+"," ",s.lower()).strip()
path=sys.argv[1]; r=json.load(open(path)); F=json.load(open("data/evidence_fields.json"))["fields"]
pmid=r["study"]["pmid"]; errs=[]
txts=glob.glob(f"data/pmc_fulltext/{pmid}_*.txt")
full=norm(" ".join(open(t,encoding="utf-8",errors="ignore").read() for t in txts)) if txts else ""
if not full: errs.append("no local full text found for quote grounding")
missing=[f for f in F if f not in r["evidence"]]; extra=[f for f in r["evidence"] if f not in F]
if missing: errs.append(f"missing fields {missing}")
if extra: errs.append(f"unknown fields {extra}")
for f,e in r["evidence"].items():
    st=e.get("status")
    if st not in ("present","partial","absent","not_applicable"): errs.append(f"{f}: bad status {st}"); continue
    if not e.get("location"): errs.append(f"{f}: location missing")
    if st=="not_applicable" and f!="E19": errs.append(f"{f}: not_applicable is only allowed for E19")
    if f=="E19" and st=="not_applicable" and r["evidence"].get("E18",{}).get("status")!="absent": errs.append("E19 not_applicable requires E18 absent")
    if st in ("present","partial"):
        q=e.get("quote","")
        if not q: errs.append(f"{f}: quote required for {st}"); continue
        if len(q)>300: errs.append(f"{f}: quote longer than 300 chars")
        loc=e.get("location","")
        if loc.lower().startswith(("supplement","repository")):
            if "http" not in loc and "http" not in e.get("note",""): errs.append(f"{f}: supplement/repository location must carry a URL")
        elif full and norm(q) not in full:
            errs.append(f"{f}: quote not found verbatim in local full text: {q[:80]!r}")
    if st=="absent" and not e.get("searched"): errs.append(f"{f}: 'searched' required for absent")
if errs:
    print("FAIL", path); [print("  -",x) for x in errs]; sys.exit(1)
print("OK", path)
