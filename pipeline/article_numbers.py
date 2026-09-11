#!/usr/bin/env python3
"""Emit data/article_numbers.json: every figure the README and the gov.tesseract.academy article
are allowed to state, derived from the data. tests/test_article_numbers.py then checks that each
figure appears verbatim in those texts, so a typed number that drifts from the data fails."""
import json, glob, statistics
from collections import Counter
V=json.load(open("data/verifiability.json"))["cells"]; F=json.load(open("data/evidence_fields.json"))["fields"]
sel=json.load(open("data/selection.json")); ver=json.load(open("data/verdicts.json"))
recs={json.load(open(p))["study"]["pmid"]:json.load(open(p)) for p in sorted(glob.glob("data/records/*.json"))}
A=[c for c,v in V.items() if v["class"]=="A"]; pms=list(recs)
cls=Counter(v["class"] for v in V.values())
per_study={pm:sum(1 for c in A if ver["verdicts"][pm][c]=="evidenced") for pm in pms}
per_cell={c:Counter(ver["verdicts"][pm][c] for pm in pms) for c in A}
fp={f:sum(1 for pm in pms if recs[pm]["evidence"][f]["status"]=="present") for f in F}
pairs=sum(per_cell[c]["evidenced"] for c in A)
never=[c for c in A if per_cell[c]["evidenced"]==0]
n={"cells":120,"A":cls["A"],"B":cls["B"],"C":cls["C"],"B_plus_C":cls["B"]+cls["C"],
   "pct_A":round(100*cls["A"]/120,1),"pct_B":round(100*cls["B"]/120,1),"pct_C":round(100*cls["C"]/120,1),"pct_B_plus_C":round(100*(cls["B"]+cls["C"])/120,1),
   "hits":sel["hits"],"included":sel["counts"]["included_I1_I4"],"eligible":sel["counts"]["eligible_I1_I5"],"sample":sel["sample"]["size"],"seed":sel["sample"]["seed"],
   "studies":len(pms),"median_evidenced":statistics.median(per_study.values()),"min_evidenced":min(per_study.values()),"max_evidenced":max(per_study.values()),
   "pairs_evidenced":pairs,"pairs_total":39*len(pms),"pct_pairs":round(100*pairs/(39*len(pms)),1),
   "never_evidenced_cells":len(never),"never_list":never,
   "E18_prompt":fp["E18"],"E27_version":fp["E27"],"E34_ci":fp["E34"],"E08b_subgroup":fp["E08b"],"E08c_language":fp["E08c"],"E35_energy":fp["E35"],"E33_decision_rule":fp["E33"],"E22_leakage":fp["E22"],"E14_code":fp["E14"],"E29_error_analysis":fp["E29"],"E32_worst_case":fp["E32"],"E17_config":fp["E17"],"E16_ground_truth":fp["E16"],"E21_recall":fp["E21"],"E05_role":fp["E05"],
   "per_study":per_study,"field_present":fp}
json.dump(n,open("data/article_numbers.json","w"),indent=1); print(json.dumps({k:v for k,v in n.items() if k not in ("per_study","field_present","never_list")},indent=1))
