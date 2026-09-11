#!/usr/bin/env python3
"""Regenerate data/pmc_fulltext/ (not committed: the full texts are the publishers' copyright) from
keyless public endpoints, so that tests/check_record.py can ground every quote on a fresh clone.
Sources, in the order tried per study: PMC efetch XML (flattened to text); Europe PMC PDF render
(pdftotext) when the PMC deposit is front matter only; arXiv PDF for the report-referenced study."""
import json, os, re, html, subprocess, sys, urllib.request, glob
OUT="data/pmc_fulltext"; os.makedirs(OUT,exist_ok=True)
UA={"User-Agent":"Mozilla/5.0 (research; sociotechnical-matrix-assurance)"}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=120).read()
def flatten(xml):
    t=re.sub(r"<[^>]+>"," ",xml); return html.unescape(re.sub(r"\s+"," ",t))
def pdf_to_text(pdf_path,txt_path):
    subprocess.run(["pdftotext",pdf_path,txt_path],check=True)
recs=[json.load(open(p)) for p in sorted(glob.glob("data/records/*.json"))]
for r in recs:
    s=r["study"]; pm=s["pmid"]; pmc=s.get("pmc")
    if glob.glob(f"{OUT}/{pm}_*.txt"): print(pm,"present"); continue
    if pmc:
        xml=get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc}&retmode=xml").decode("utf-8","ignore")
        body=flatten(xml); open(f"{OUT}/{pm}_{pmc}.txt","w").write(body); print(pm,pmc,"efetch",len(body),"chars")
        if len(body)<10000:   # front matter only: fall back to the Europe PMC PDF render
            pdf=f"{OUT}/{pm}_{pmc}.pdf"; open(pdf,"wb").write(get(f"https://europepmc.org/articles/{pmc}?pdf=render"))
            pdf_to_text(pdf,f"{OUT}/{pm}_publisher.txt"); print(pm,"europepmc pdf render",os.path.getsize(f"{OUT}/{pm}_publisher.txt"),"chars")
    elif s.get("arxiv") or pm=="38484744":
        arx=s.get("arxiv","2310.17526"); pdf=f"{OUT}/{pm}_arXiv{arx}.pdf"; open(pdf,"wb").write(get(f"https://arxiv.org/pdf/{arx}"))
        pdf_to_text(pdf,f"{OUT}/{pm}_arXiv{arx}.txt"); print(pm,"arxiv",os.path.getsize(f"{OUT}/{pm}_arXiv{arx}.txt"),"chars")
    else: sys.exit(f"{pm}: no source route")
print("done")
