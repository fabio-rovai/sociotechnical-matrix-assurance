#!/usr/bin/env python3
"""Emit two SHACL layers.
Layer 1 shapes/ontology_shapes.ttl: the matrix graph is well formed (one class per cell, artefact
cells carry evidence fields, other classes carry none, evidence statuses closed).
Layer 2 shapes/cell_shapes.ttl: one shape per artefact-class cell; an evaluation record violates
it when any required evidence field is not present. The validation report is the findings table."""
import json
V=json.load(open("data/verifiability.json"))["cells"]
STM="https://gov.tesseract.academy/def/sociotechnical-matrix#"; STMD="https://gov.tesseract.academy/id/sociotechnical-matrix/"
head=["@prefix sh: <http://www.w3.org/ns/shacl#> .","@prefix stm: <https://gov.tesseract.academy/def/sociotechnical-matrix#> .",
      "@prefix stmd: <https://gov.tesseract.academy/id/sociotechnical-matrix/> .","@prefix stms: <https://gov.tesseract.academy/def/sociotechnical-matrix/shapes#> .",
      "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .","@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",""]
L1=head+["""stms:CellShape a sh:NodeShape ; sh:targetClass stm:Cell ;
  sh:property [ sh:path stm:verifiabilityClass ; sh:minCount 1 ; sh:maxCount 1 ; sh:in ( stm:EvaluationArtefact stm:GovernanceRecord stm:Attestation ) ] ;
  sh:property [ sh:path stm:question ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:string ] ;
  sh:property [ sh:path stm:classRationale ; sh:minCount 1 ] ;
  sh:property [ sh:path stm:inStage ; sh:minCount 1 ; sh:maxCount 1 ] ;
  sh:property [ sh:path stm:hasCriterion ; sh:minCount 1 ; sh:maxCount 1 ] .

stms:ArtefactCellNeedsFields a sh:NodeShape ; sh:targetClass stm:Cell ;
  sh:sparql [ sh:message "An artefact-class cell must name at least one evidence field that settles it." ;
    sh:select \"\"\"SELECT $this WHERE { $this <https://gov.tesseract.academy/def/sociotechnical-matrix#verifiabilityClass> <https://gov.tesseract.academy/def/sociotechnical-matrix#EvaluationArtefact> .
      FILTER NOT EXISTS { $this <https://gov.tesseract.academy/def/sociotechnical-matrix#settledBy> ?f } }\"\"\" ] .

stms:NonArtefactCellHasNoFields a sh:NodeShape ; sh:targetClass stm:Cell ;
  sh:sparql [ sh:message "Only artefact-class cells may name evidence fields." ;
    sh:select \"\"\"SELECT $this WHERE { $this <https://gov.tesseract.academy/def/sociotechnical-matrix#settledBy> ?f ; <https://gov.tesseract.academy/def/sociotechnical-matrix#verifiabilityClass> ?c .
      FILTER (?c != <https://gov.tesseract.academy/def/sociotechnical-matrix#EvaluationArtefact>) }\"\"\" ] .

stms:EvidenceItemShape a sh:NodeShape ; sh:targetClass stm:EvidenceItem ;
  sh:property [ sh:path stm:field ; sh:minCount 1 ; sh:maxCount 1 ; sh:class stm:EvidenceField ] ;
  sh:property [ sh:path stm:status ; sh:minCount 1 ; sh:maxCount 1 ; sh:in ( "present" "partial" "absent" "not_applicable" ) ] ;
  sh:property [ sh:path stm:location ; sh:minCount 1 ] .

stms:PresentNeedsQuote a sh:NodeShape ; sh:targetClass stm:EvidenceItem ;
  sh:sparql [ sh:message "An evidence item marked present must carry a quote." ;
    sh:select \"\"\"SELECT $this WHERE { $this <https://gov.tesseract.academy/def/sociotechnical-matrix#status> "present" .
      FILTER NOT EXISTS { $this <https://gov.tesseract.academy/def/sociotechnical-matrix#quote> ?q } }\"\"\" ] .

stms:RecordShape a sh:NodeShape ; sh:targetClass stm:EvaluationRecord ;
  sh:property [ sh:path stm:aboutStudy ; sh:minCount 1 ; sh:maxCount 1 ; sh:class stm:Study ] ;
  sh:property [ sh:path stm:extractedOn ; sh:minCount 1 ; sh:datatype xsd:date ] ;
  sh:property [ sh:path stm:hasEvidence ; sh:minCount 37 ; sh:maxCount 37 ] .
"""]
open("shapes/ontology_shapes.ttl","w").write("\n".join(L1))
L2=list(head)
n=0
for cid,v in sorted(V.items()):
    if v["class"]!="A": continue
    n+=1
    binds=" UNION ".join("{ BIND(<%sfield-%s> AS ?field) }"%(STMD,f) for f in v["fields"])
    L2.append(f"""stms:Cell-{cid} a sh:NodeShape ; sh:targetClass stm:EvaluationRecord ; rdfs:label "{cid}" ; stm:forCell stmd:cell-{cid} ;
  sh:sparql [ sh:message "Cell {cid} is not fully evidenced: a required evidence field is not present." ;
    sh:select \"\"\"SELECT DISTINCT $this ?field WHERE {{ {binds}
      FILTER NOT EXISTS {{ $this <{STM}hasEvidence> ?e . ?e <{STM}field> ?field ; <{STM}status> "present" . }} }}\"\"\" ] .
""")
open("shapes/cell_shapes.ttl","w").write("\n".join(L2))
print("layer 1 written; layer 2 shapes:",n)
