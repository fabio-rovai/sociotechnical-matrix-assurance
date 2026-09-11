#!/usr/bin/env python3
"""Dual computation of per-cell verdicts.

Path 1 (set-based Python): read data/records/*.json, apply the rule that an artefact-class cell is
evidenced only when every evidence field that settles it is present.
Path 2 (graph): emit data/records.ttl, validate it with pyshacl against shapes/cell_shapes.ttl,
read the (record, cell) violations back, and require the two sets to be identical.
Path 3 (open-ontologies engine): optional, --engine; runs the same shapes through
~/projects/open-ontologies and compares again.
Exits non-zero on any disagreement. Writes data/verdicts.json and data/records.ttl."""
import json, glob, sys, os, subprocess, datetime
from collections import defaultdict
STM="https://gov.tesseract.academy/def/sociotechnical-matrix#"; STMD="https://gov.tesseract.academy/id/sociotechnical-matrix/"
V=json.load(open("data/verifiability.json"))["cells"]; F=json.load(open("data/evidence_fields.json"))["fields"]
A={cid:v["fields"] for cid,v in V.items() if v["class"]=="A"}
def lit(s): return '"' + str(s).replace("\\","\\\\").replace('"','\\"').replace("\n"," ") + '"'
records=[]
for p in sorted(glob.glob("data/records/*.json")):
    r=json.load(open(p)); r["_file"]=p
    missing=[f for f in F if f not in r["evidence"]]
    if missing: sys.exit(f"{p}: missing evidence fields {missing}")
    bad=[(f,e["status"]) for f,e in r["evidence"].items() if e["status"] not in ("present","partial","absent","not_applicable")]
    if bad: sys.exit(f"{p}: bad statuses {bad}")
    records.append(r)
if not records: sys.exit("no records in data/records/")
# Path 1
py=defaultdict(dict)
for r in records:
    for cid,fields in A.items():
        st=[r["evidence"][f]["status"] for f in fields]
        if all(s=="present" for s in st): v="evidenced"
        elif any(s in ("present","partial") for s in st): v="partially_evidenced"
        else: v="not_evidenced"
        py[r["study"]["pmid"]][cid]=v
py_not_full={(pm,cid) for pm,d in py.items() for cid,v in d.items() if v!="evidenced"}
# Emit records.ttl
out=["@prefix stm: <%s> ."%STM,"@prefix stmd: <%s> ."%STMD,"@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .","@prefix dcterms: <http://purl.org/dc/terms/> .","@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",""]
for r in records:
    s=r["study"]; pm=s["pmid"]
    out.append(f"stmd:study-{pm} a stm:Study ; stm:pmid {lit(pm)} ; dcterms:title {lit(s['title'])} ; dcterms:date {lit(s.get('year',''))} ; stm:selectionRoute {lit(s.get('selection_route','sampled'))}"
               + (f" ; stm:pmcid {lit(s['pmc'])}" if s.get("pmc") else "") + (f" ; stm:doi {lit(s['doi'])}" if s.get("doi") else "") + " .")
    out.append(f"stmd:record-{pm} a stm:EvaluationRecord ; stm:aboutStudy stmd:study-{pm} ; stm:extractedOn {lit(r['extracted_on'])}^^xsd:date ; stm:extractedBy {lit(r['extracted_by'])} ;")
    out.append("  stm:hasEvidence " + ", ".join(f"stmd:evidence-{pm}-{f}" for f in F) + " .")
    for f,e in r["evidence"].items():
        line=f"stmd:evidence-{pm}-{f} a stm:EvidenceItem ; stm:field stmd:field-{f} ; stm:status {lit(e['status'])} ; stm:location {lit(e.get('location','') or 'not found')}"
        if e.get("quote"): line+=f" ; stm:quote {lit(e['quote'])}"
        out.append(line+" .")
    out.append("")
open("data/records.ttl","w").write("\n".join(out))
# Path 2: pyshacl
import rdflib, pyshacl
data=rdflib.Graph()
for f in ("ontology/stm.ttl","data/matrix.ttl","data/records.ttl"): data.parse(f,format="turtle")
shapes=rdflib.Graph(); shapes.parse("shapes/cell_shapes.ttl",format="turtle"); shapes.parse("shapes/ontology_shapes.ttl",format="turtle")
conforms,report,text=pyshacl.validate(data,shacl_graph=shapes,inference="none",advanced=True)
SH=rdflib.Namespace("http://www.w3.org/ns/shacl#")
sh_not_full=set(); other=[]
for res in report.subjects(rdflib.RDF.type,SH.ValidationResult):
    focus=str(report.value(res,SH.focusNode)); src=str(report.value(res,SH.sourceShape))
    if "/shapes#Cell-" in src and focus.startswith(STMD+"record-"):
        sh_not_full.add((focus.split("record-")[1], src.split("#Cell-")[1]))
    else: other.append((focus,src,str(report.value(res,SH.resultMessage))))
if other:
    print("STRUCTURAL VIOLATIONS:"); [print("  ",o) for o in other]; sys.exit(2)
if py_not_full!=sh_not_full:
    print("DISAGREEMENT python vs pyshacl"); print(" only python:",sorted(py_not_full-sh_not_full)); print(" only shacl:",sorted(sh_not_full-py_not_full)); sys.exit(3)
print(f"pyshacl agrees with python: {len(py_not_full)} (record, cell) pairs not fully evidenced across {len(records)} records and {len(A)} artefact cells")
# Path 3: open-ontologies engine (v1.3.0). Its CLI store is in-memory per process, so load and
# shacl must run inside one `batch`; a shacl run on an empty store returns conforms=null with a
# warning, and that is treated here as a failure, never as agreement.
if "--engine" in sys.argv:
    OO=os.path.expanduser("~/projects/open-ontologies/target/release/open-ontologies")
    dd="data/.oo-store"; os.makedirs(dd,exist_ok=True)
    cmds="load ontology/stm.ttl\nload data/matrix.ttl\nload data/records.ttl\nshacl shapes/cell_shapes.ttl\n"
    p=subprocess.run([OO,"--no-connect","--data-dir",dd,"batch","-"],input=cmds,capture_output=True,text=True)
    steps=[json.loads(l) for l in p.stdout.splitlines() if l.strip().startswith("{")]
    sh=[st for st in steps if isinstance(st,dict) and "violations" in json.dumps(st)]
    if not sh: print("engine produced no shacl step:",p.stdout[:400],p.stderr[:400]); sys.exit(4)
    res=sh[-1]; res=res.get("result",res)
    if res.get("conforms") is None or res.get("focus_nodes",0)==0:
        print("engine result undetermined:",res.get("warning")); sys.exit(4)
    # The engine's violations carry focus_node, message, constraint and severity but no source
    # shape (a defect to file: a SHACL report should name sh:sourceShape). The cell id is
    # recovered from the message text we put in sh:message.
    import re as _re
    eng=set()
    for r_ in res.get("violations",[]):
        focus=str(r_.get("focus_node") or ""); m=_re.search(r"Cell (\S+) is not fully evidenced", str(r_.get("message","")))
        if m and "record-" in focus: eng.add((focus.split("record-")[1], m.group(1)))
    if eng!=py_not_full:
        print("DISAGREEMENT python vs open-ontologies"); print(" only python:",sorted(py_not_full-eng)[:10]); print(" only engine:",sorted(eng-py_not_full)[:10]); print(" violation keys:",list((res.get("violations") or [{}])[0].keys())); sys.exit(5)
    print(f"open-ontologies agrees with python: {len(eng)} pairs (engine violation_count {res.get('violation_count')})")
json.dump({"computed_on":datetime.date.today().isoformat(),"artefact_cells":sorted(A),"verdicts":py},open("data/verdicts.json","w"),indent=1)
print("wrote data/verdicts.json")
