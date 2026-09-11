# Build report

What was fetched, what was computed, what could not be obtained, and what went wrong on the way.
Numbers about the study set live in `REPORT.md`, which is generated from the data; this file
narrates the build and does not retype them.

## Signal and purpose

On 8 September 2026 the Ada Lovelace Institute published "Care and consideration", a synthesis of
its research collaboration with NICE on AI adoption for internal processes, together with the
sociotechnical evaluation matrix that served as the central analytic tool for examining NICE's
feasibility study of an off-the-shelf large language model for title and abstract screening. The
matrix asks 120 questions and is filled in by the organisation as fully, partially or not
addressed. This repository asks one question of it: which of those 120 answers could anyone
outside the organisation check, and how often does the public evidence base that NICE would draw
on actually carry the evidence.

This is non-commercial research, built to be reused by any public body applying the matrix. It is
not an application for anything.

## Sources and the licence gate

- Report: https://www.adalovelaceinstitute.org/report/care-and-consideration/ (Machirori, Rincon,
  Studman; contributing author Parker). Fetched as HTML and PDF on 11 September 2026. The site
  returns 403 to non-browser user agents; a browser user agent string was used.
- Matrix: https://www.adalovelaceinstitute.org/resource/sociotechnical-evaluation-matrix/ (Rincon
  and Chowdhury). The page embeds a public Google Sheet (id
  `11NIShoLv59ZmlrbaOgQTfKPHVLkwLWefRNcs9yNRBxM`); the sheet was exported as xlsx via the public
  export endpoint, no login. Four tabs: Cover sheet, Design, Development, Deployment.
- Licence: the cover sheet states CC BY-NC 4.0. The question text is therefore reproduced here
  with attribution and this repository is non-commercial. Nothing derived from the matrix may be
  used commercially without the Institute's permission. Our own vocabulary, shapes, classification
  and reports are CC BY 4.0; code is MIT. See `LICENSE`.
- NICE's own feasibility study protocol is not public. The report cites "The Future of HTA with
  AI, NICE report forthcoming" (endnote 42). The checks in this repository therefore run against
  the published evidence base for the same task, not against NICE's protocol. When NICE publishes
  it, `data/records/` accepts it as one more record.

## Extraction of the matrix

`pipeline/extract_cells.py` reads the xlsx directly (zip plus XML, no third-party parser). Bug
found and fixed during the build: self-closing empty cells (`<c r="F6" s="6"/>`) were matched by
a greedy regex and swallowed the following cells, so the first run returned zero cells. The fixed
regex is in the script and the test suite pins the SHA-256 of every question text so a silent edit
fails the build. The response block to the right of each question grid repeats the column
headers; the extractor stops at the first repeated header.

## The verifiability classification

Each of the 120 cells was assigned one class by hand, with a one-line rationale stored next to it
in `data/verifiability.json`:

- A, evaluation artefact: a published evaluation or feasibility study should itself carry the
  evidence (a metric with its confidence interval, a verbatim prompt, a model version string).
- B, governance record: the evidence exists only as organisational documents an auditor could
  inspect (a RACI, a risk register entry, a stage-gate decision, an engagement log).
- C, attestation: a judgement of adequacy, legitimacy or alignment that no artefact settles.

The rule applied at the margin: a question of the form "is X considered" or "is X analysed" is
class B when a document could evidence the consideration, and class C only when the question is
about the quality of a judgement (does involvement enhance legitimacy, do thresholds reflect what
institutions consider acceptable, could communication over-sell). Where a cell bundles a
checkable part with a judgement (DEP-F13 logs plus accessibility), the checkable part decided the
class and the rationale says so. The classification is one person's reading and is open to
challenge by issue; the counts in `REPORT.md` recompute from the file.

Thirty-seven evidence fields (E01 to E35, with E08 split three ways) were then defined so that
every A cell is settled by one or two of them. The definitions are in `data/evidence_fields.json`
and are deliberately strict: a reported sensitivity without an interval leaves E34 absent even if
an interval could be computed; "GPT-4" without a version string leaves E27 partial.

## The study set

- Query: PubMed E-utilities, keyless, query text and timestamp in `data/selection.json` and
  `data/pubmed_query.txt`. 146 identifiers returned, 145 records with metadata.
- Screening: every abstract was screened against four content criteria by a local model
  (Qwen3.6-35B-A3B via mlx, thinking disabled, temperature 0) returning JSON. The screening log
  with the model's one-sentence reasons is `data/screen.jsonl`. Seven decisions were overridden
  after reading the abstract; each override and its reason is in `data/selection.json` under
  `decided_by = claude_override`. The overrides were: two research letters that report primary
  evaluations (the model excluded them on publication type), one three-model evaluation the model
  read as a proposal, one paper whose "screening" is study-design classification rather than
  eligibility screening, one topic-relevance classifier paper, one duplicate preprint, and one
  case study whose LLM identity is left to confirm at extraction.
- Fifth criterion: open-access full text in PubMed Central, so that anyone can re-run the
  extraction without a subscription.
- Sample: 12 of the 51 eligible, `random.Random(20260911).sample(sorted(pmids), 12)`.
- Added by design: Khraisha and colleagues (2024), the "GPT-4 across peer-reviewed and grey
  literature in multiple languages" study the report's appendix alludes to. Journal version
  paywalled; the arXiv version (2310.17526) was used and the record is labelled
  `report_referenced`.
- Full texts were fetched from the PMC efetch endpoint as XML and flattened to text under
  `data/pmc_fulltext/` (not committed; regenerable with the identifiers in `data/selection.json`).

## Evidence extraction and its guard

Extraction was done by four language-model agents working from `docs/EXTRACTION_BRIEF.md`, each
on three or four studies, with instructions to read the full text, the supplements and any linked
repository, and to record a verbatim quote and a location for every present or partial field and
what was searched for every absent field. The guard is mechanical: `tests/check_record.py`
string-matches every quote (whitespace-normalised, case-insensitive) against the local full text
and rejects the record if any quote is not found verbatim, unless the location is a supplement or
repository URL. A quote that cannot be found is treated as a fabrication. Records that did not
pass were sent back until they did.

## Verification

Every verdict is computed three ways and the pipeline exits non-zero on any disagreement:

1. Set-based Python over the JSON records (`pipeline/verdicts.py`).
2. SHACL: one shape per artefact cell in `shapes/cell_shapes.ttl`, generated from the
   classification, validated with pyshacl 0.40.1 over `ontology/stm.ttl`, `data/matrix.ttl` and
   `data/records.ttl`. `sh:sparql` constraints use UNION plus BIND rather than VALUES and full
   IRIs rather than prefixes, both of which pyshacl rejects in this position.
3. Our own engine, open-ontologies 1.3.0 (`--engine`).

Two things went wrong on path 3 and both are recorded because they are the point of running it:

- The engine's CLI store is in-memory per process. Running `load` three times and then `shacl`
  as four commands validated an empty store. The engine flagged this correctly (`conforms: null`,
  `focus_nodes: 0`, a warning naming all 39 unmatched shapes) and the harness, which only looked
  at the violation count, read zero violations as agreement. Fixed by running load and shacl in
  one `batch` and by treating an undetermined result as failure. Lesson: a validator that reports
  "nothing matched" must never be summarised by its violation count.
- The engine's violation objects carry `focus_node`, `message`, `constraint` and `severity` but
  not the source shape, which a SHACL validation report is expected to name (`sh:sourceShape`).
  The cell identity had to be recovered from the message text this repository put in
  `sh:message`. Filed as a defect against open-ontologies (contribute-first).

With both fixed, the three paths agree on a synthetic record (35 of 39 cells not fully evidenced)
and on the real records; the counts are in `REPORT.md`.

## What was deliberately not claimed

- No claim is made about NICE's feasibility study, which is not public.
- No claim is made that a "fully addressed" cell in any organisation's completed matrix is false.
  The finding is about checkability, not about honesty.
- The study set is a seeded random sample of the open-access subset of one PubMed query. Rates
  computed from it are estimates for that population, with the sample size stated next to them,
  and are not a systematic review of the field.
- Class assignments are one reading. Moving a handful of cells between B and C, or between A and
  B, changes the counts by that handful and the argument not at all; the file is open to issues.

## Hypotheses carried into the run, and what the data did to them

Stated before extraction, settled by `REPORT.md` section 6.

- H1, fewer than half of the sampled studies publish the verbatim prompt (E18): **dead.** Eleven
  of thirteen publish it, in the article body, a supplement or a repository. Prompt publication
  is the norm in this literature, not the exception.
- H2, fewer than half report confidence intervals on headline metrics (E34): **confirmed.** Two of
  thirteen. Several report an interval only for a kappa, or standard deviations across datasets,
  which the strict definition scores partial.
- H3, no sampled study reports performance by language or region (E08c): **confirmed for the
  sample.** The one study that does is the report-referenced GPT-4 multilingual study, added by
  design; none of the twelve sampled studies does, and one scores partial.
- H4, no study reports energy or compute cost (E35): **confirmed.** Zero present. Seven disclose
  API spend or run time, scored partial under the rule recorded in `data/adjudications.json`.
- H5, no study pre-specifies a go or no-go rule linking a metric to a decision (E33): **dead by
  one.** One study carries a real stop criterion with a demonstrated no-go branch. Five more state
  a target sensitivity somewhere and then do not act on it; one declares 95% the threshold in its
  background and calls 94% satisfactory in its conclusion.
- Not hypothesised, and the strongest single result: **no study pins an exact model version
  together with a run date (E27).** All thirteen are partial. The forms it takes: a rolling alias
  (`gpt-3.5-turbo`) with no date; a dated snapshot with no run date; a version that appears only
  in the deposited notebook and nowhere in the paper; a paper naming one model where its
  repository pins another.

## Contradictions and defects found in the sources

Recorded here because a reproducible defect report is the most useful thing this work can hand
back to an author. All are in the records under the relevant field's note.

- PMID 40567772: Methods and the Table 1 note state temperature 0.7, max tokens 2,048, top p 1.0;
  the supplementary notebook calls the API with temperature 0 and top p 1 and pins
  `gpt-4-1106-preview`, a version the paper never names. Methods report 1,763 records entering
  screening, Results 1,967.
- PMID 41626985: the paper names Gemini 1.5 Pro and Llama 3.3 70B; the repository pins
  `gemini-1.5-flash-8b` and `meta-llama/Meta-Llama-3-70B-Instruct`. The repository prompt carries
  an uncertainty clause the article's printed prompt omits. The Llama call sets temperature 0.7
  next to a claim of high run-to-run reproducibility.
- PMID 42059529: Methods say Gemma 3 8B; the supplement and every results table say Gemma 3 12B.
- PMID 40921065: the OSF link in the paper resolves to a cited third-party preprint on domain
  partitioning, not to the study's artefacts, which live in Multimedia Appendix 1 and a GitHub
  repository that has been pushed since publication.
- PMID 41326830: the Introduction carries the literal unresolved placeholder "[cite]".
- arXiv 2310.17526: the OSF address is printed as "(link)" and PROSPERO as "(Anonymised)"; the
  project was located through the OSF API.

## Extraction gotchas worth keeping

- PMC's own `/bin/` supplement paths return 404 and `/articles/instance/` paths sit behind a
  proof-of-work cookie. The Europe PMC REST endpoint
  `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/supplementaryFiles` returned every
  supplement first time.
- A PMC deposit can be front matter only (`pmc-prop-open-access no`). Europe PMC's
  `?pdf=render` route served the full article for PMID 41326830 when the publisher blocked
  non-browser clients.
- The web-fetch summariser invented model version strings for a notebook that contains none
  (`claude-3-5-sonnet@20241022`, `gemini-2.0-flash`, `meta/llama-2-70b-chat`). Only quotes taken
  from the downloaded raw file were accepted. This is the verify-twice rule paying for itself.
- Per-record `chat.openai.com/share/...` links as a prompt archive are dead for a machine: the
  page is a script shell and the backend returns 403. Prompts archived that way are unverifiable.

## Third-engine result on the real records

pyshacl and the Python computation agree on all 507 study-cell pairs (245 not fully evidenced).
open-ontologies 1.3.0 reports 52: exactly the four cells that fail for every one of the thirteen
records, thirteen times each, and nothing for the other 193 pairs. A minimal reproduction (three
records, one `sh:sparql` shape with `FILTER NOT EXISTS`, one record conformant) is in issue #132.
The engine path stays in `pipeline/verdicts.py` and fails loudly; CI runs the two paths that
agree. The disagreement is a finding about our own tool, not about the data.
