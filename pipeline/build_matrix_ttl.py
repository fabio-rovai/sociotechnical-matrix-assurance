#!/usr/bin/env python3
"""Emit data/matrix.ttl: the 120 cells, criteria, stages, columns, verifiability classes and
evidence fields, from data/cells.json, data/verifiability.json and data/evidence_fields.json."""
import json, re
def slug(s): return re.sub(r"[^A-Za-z0-9]+","-",s).strip("-")
def lit(s): return '"' + s.replace("\\","\\\\").replace('"','\\"') + '"'
cells=json.load(open("data/cells.json")); V=json.load(open("data/verifiability.json"))["cells"]; F=json.load(open("data/evidence_fields.json"))["fields"]
CLS={"A":"stm:EvaluationArtefact","B":"stm:GovernanceRecord","C":"stm:Attestation"}
out=["@prefix stm: <https://gov.tesseract.academy/def/sociotechnical-matrix#> .",
     "@prefix stmd: <https://gov.tesseract.academy/id/sociotechnical-matrix/> .",
     "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
     "@prefix dcterms: <http://purl.org/dc/terms/> .",
     "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .","",
     "# Cell text: Cam Rincon and Rumman Chowdhury, Sociotechnical evaluation matrix, Ada Lovelace Institute, 8 September 2026, CC BY-NC 4.0.",
     "# Verifiability classes and rationales: Fabio Rovai, Tesseract Academy, 11 September 2026.","",
     "stmd:matrix a stm:Matrix ; rdfs:label \"Sociotechnical evaluation matrix (Ada Lovelace Institute and NICE, 2026)\" ;",
     f"  dcterms:source <{cells['source']}> ; dcterms:creator \"Cam Rincon\", \"Rumman Chowdhury\" ; dcterms:publisher \"Ada Lovelace Institute\" ; dcterms:issued \"2026-09-08\"^^xsd:date ;",
     "  dcterms:license <https://creativecommons.org/licenses/by-nc/4.0/> .",""]
stages=sorted({c["stage"] for c in cells["cells"]}); cols=sorted({(c["stage"],c["column"]) for c in cells["cells"]}); crits=sorted({c["criterion"] for c in cells["cells"]})
for s in stages: out.append(f"stmd:stage-{slug(s)} a stm:LifecycleStage ; rdfs:label {lit(s)} .")
for s,c in cols: out.append(f"stmd:column-{slug(s)}-{slug(c)} a stm:LifecycleColumn ; rdfs:label {lit(c)} .")
for c in crits: out.append(f"stmd:criterion-{slug(c)} a stm:Criterion ; rdfs:label {lit(c)} .")
out.append("")
for k,f in F.items():
    out.append(f"stmd:field-{k} a stm:EvidenceField ; rdfs:label {lit(f['name'])} ; stm:fieldDefinition {lit(f['definition'])} .")
out.append("")
for c in cells["cells"]:
    v=V[c["id"]]
    lines=[f"stmd:cell-{c['id']} a stm:Cell ; rdfs:label {lit(c['id'])} ; stm:partOf stmd:matrix ;",
           f"  stm:inStage stmd:stage-{slug(c['stage'])} ; stm:inColumn stmd:column-{slug(c['stage'])}-{slug(c['column'])} ; stm:hasCriterion stmd:criterion-{slug(c['criterion'])} ;",
           f"  stm:question {lit(c['question'])} ;",
           f"  stm:verifiabilityClass {CLS[v['class']]} ; stm:classRationale {lit(v['rationale'])}"]
    if v["fields"]: lines.append("  ; stm:settledBy " + ", ".join(f"stmd:field-{f}" for f in v["fields"]))
    out.append("\n".join(lines)+" .\n")
open("data/matrix.ttl","w").write("\n".join(out))
print("wrote data/matrix.ttl", len(cells["cells"]), "cells")
