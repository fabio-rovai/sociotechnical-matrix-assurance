# Sociotechnical Matrix Assurance

**Which cells of a sociotechnical AI evaluation matrix can anyone outside the organisation check,
and how often does the published evidence base actually carry the evidence. Measured.**

Maintained by [Tesseract Academy](https://gov.tesseract.academy). Built on the
[Sociotechnical evaluation matrix](https://www.adalovelaceinstitute.org/resource/sociotechnical-evaluation-matrix/)
that Cam Rincon and Rumman Chowdhury developed for the Ada Lovelace Institute's research
collaboration with NICE, published on 8 September 2026 with the report
[Care and consideration](https://www.adalovelaceinstitute.org/report/care-and-consideration/)
(Machirori, Rincon, Studman). The matrix is the best-constructed instrument of its kind we have
seen and this repository adds one thing to it: an evidence layer.

## The finding

The matrix asks 120 questions across ten sociotechnical criteria and twelve lifecycle columns, and
an organisation answers each as fully, partially or not addressed. We classified every cell by
what could settle it.

- **39 cells (32.5%)** can be settled by inspecting a published evaluation: a metric with its
  interval, a verbatim prompt, a pinned model version, a subgroup breakdown.
- **75 cells** can only be settled by organisational records that no publication carries: a RACI,
  a risk register entry, a stage-gate decision, an engagement log.
- **6 cells** are judgements that no artefact settles.

So 81 of the 120 traffic lights in a completed matrix are, to anyone outside the organisation,
assertions. That is not a criticism of the matrix. It is the reason a matrix needs an evidence
layer, and the 39 checkable cells are where one can start.

We then ran the 39 checkable cells against **13 published evaluations of large language models
for title and abstract screening**, the exact task NICE's feasibility study addresses: 12 drawn
at random (seed 20260911) from the 51 open-access primary studies a recorded PubMed query
returned, plus the GPT-4 multilingual study the Ada report itself alludes to.

- A published evaluation fully evidences a **median of 20 of the 39** checkable cells (minimum 13,
  maximum 28). Pooled, 262 of 507 study-cell pairs are fully evidenced, **51.7%**.
- **11 of 13** publish the verbatim prompt. Our pre-registered hypothesis that fewer than half
  would is dead, and is reported as such.
- **0 of 13** pin an exact model version together with a run date. Every study is partial on this
  field: a version string without a date, or a rolling alias, or a version in the repository that
  the paper never states.
- **2 of 13** report confidence intervals on their headline metrics.
- **1 of 13** measures performance by language or region, the concern the Ada report's appendix
  raises about who gets excluded from the evidence base. That one study is the report-referenced
  one; none of the 12 sampled studies does.
- **0 of 13** report energy or compute cost, and **0 of 13** collect reviewer or user perspectives.
- Four cells are evidenced by no study in the set: user perspectives as evidence (DES-E10),
  logged prompt and model versions (DEV-D13), reporting detail sufficient to interpret claims with
  a pinned version (DEP-F6), and energy cost (DEP-E13).

The evidence base a public body would draw on to justify adopting screening automation is
therefore strong on what the model was asked and what it was scored against, and thin on the
things that make a result reproducible a year later or fair across languages.

## Also found on the way

- In two studies the deposited code pins a different model or a different decoding temperature
  from the one the paper reports. In one, a parameter the paper gives as 0.7 is 0 in the notebook.
- One repository link in a paper resolves to a cited third-party preprint, not to the study's
  artefacts; one preprint prints its data link as the literal placeholder "(link)"; one published
  paper carries an unresolved "[cite]".
- Our own web-fetch summariser invented model version strings for a notebook that contains none.
  The extraction rule that every quote must string-match the downloaded source caught it.
- Our own engine, open-ontologies 1.3.0, under-reports `sh:sparql` violations when only some focus
  nodes fail; pyshacl and the set-based Python computation agree with each other on all 507 pairs.
  Filed as issues [#131](https://github.com/fabio-rovai/open-ontologies/issues/131) and
  [#132](https://github.com/fabio-rovai/open-ontologies/issues/132).

Full tables, every cell with its class and rationale, every study with every field, and the
per-cell verdicts: [`REPORT.md`](REPORT.md). How it was built, what could not be obtained and
what went wrong: [`BUILD_REPORT.md`](BUILD_REPORT.md).

## How it is verified

- Every quote supporting a present or partial field is string-matched against the downloaded full
  text by `tests/check_record.py`; a quote that does not match rejects the record.
- Every cell verdict is computed set-based in Python and again by SHACL validation with one shape
  per cell (pyshacl); the script exits non-zero on any disagreement.
- `REPORT.md` and `data/article_numbers.json` are generated from the data, and the test suite
  checks that every figure in this README appears verbatim in that file.
- The SHA-256 of every question text is pinned so a silent edit to the matrix fails the build.

## Contents

| | |
|---|---|
| `data/cells.json`, `data/matrix.ttl` | The 120 cells with identifiers (CC BY-NC 4.0, Ada Lovelace Institute). |
| `data/verifiability.json` | The A, B, C class of every cell with a one-line rationale. |
| `data/evidence_fields.json` | The 37 evidence fields that settle the 39 artefact-class cells. |
| `data/selection.json`, `data/screen.jsonl` | The PubMed query, every screening decision with its reason, the seed and the sample. |
| `data/records/` | One evidence record per study: status, location and verbatim quote per field. |
| `data/adjudications.json` | The cross-record consistency rules and the two changes they caused. |
| `ontology/stm.ttl` | The OWL 2 vocabulary. |
| `shapes/` | SHACL layer 1 (matrix well-formedness) and layer 2 (one shape per artefact cell). |
| `pipeline/` | Extractor, graph and shape generators, three-way verdicts, report and figure generators. |
| `tests/` | Known-answer tests, the quote-grounding checker, the figure-consistency test. |

## Run it

```
python3 -m venv .venv && ./.venv/bin/pip install rdflib==7.6.0 pyshacl==0.40.1
./.venv/bin/python pipeline/extract_cells.py
./.venv/bin/python pipeline/build_matrix_ttl.py
./.venv/bin/python pipeline/build_shapes.py
./.venv/bin/python tests/test_known_answers.py
./.venv/bin/python pipeline/verdicts.py            # add --engine if open-ontologies is installed
./.venv/bin/python pipeline/build_report.py
./.venv/bin/python pipeline/article_numbers.py && ./.venv/bin/python tests/test_article_numbers.py
```

To add a study, write `data/records/<pmid>.json` following `docs/EXTRACTION_BRIEF.md`, put its
full text under `data/pmc_fulltext/<pmid>_*.txt`, and run the checker. To apply the partition to
your own completed matrix, the class of every cell is in `data/verifiability.json`.

## Licence

Code MIT. The matrix question text is CC BY-NC 4.0 (Ada Lovelace Institute; Rincon and Chowdhury
2026) and this repository is non-commercial research; commercial use of anything derived from the
matrix needs the Institute's permission. Our vocabulary, shapes, classification, records and
reports are CC BY 4.0. See `LICENSE`.

## Contact

If you are applying the matrix, or any self-scored AI evaluation framework, to an internal use
case, a bounded first engagement is a two-week evidence audit: we take your completed matrix,
partition it into the cells that inspectable evidence can settle and the cells that rest on
records or judgement, run the checks that can be run against your evaluation artefacts, and hand
back the evidence with the method. Fabio Rovai, fabio@thetesseractacademy.com.
