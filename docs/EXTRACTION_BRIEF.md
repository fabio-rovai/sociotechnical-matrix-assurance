# Evidence extraction brief (one JSON record per study)

You are extracting evidence from published evaluations of large language models used for title and
abstract screening in evidence synthesis. For EACH study assigned to you, fill every one of the 37
evidence fields below with a status and a location, and a verbatim quote wherever the status is
present or partial. This feeds a machine check, so precision matters more than speed.

## Statuses
- present: the evidence is in the paper, its supplement, or a linked repository, and you have a verbatim quote and a location.
- partial: a component of the definition is met but not all of it (say which part is missing in `note`).
- absent: you searched the full text, the supplement list and any linked repository and found nothing that meets the definition. Record in `searched` what you looked for.
- not_applicable: ONLY for E19 when E18 is absent (the prompt text is not available, so its content cannot be checked).

## Rules with teeth
1. A quote must be VERBATIM from the source and no longer than 300 characters. Do not paraphrase inside quotes. Quotes will be string-matched against the full text; a quote that does not match is treated as a fabrication and the whole record is rejected.
2. Location is a section name or heading in the paper ("Methods, Prompt design"), or "Supplement: <file or URL>", or "Repository: <URL>". If you used a supplement or repository, fetch it and confirm it resolves; record the URL you fetched.
3. Do not infer. If a paper reports sensitivity but no confidence interval, E34 is absent even if a CI could be computed. If a model is named as "GPT-4" without a version string or date, E27 is partial with a note.
4. The full text is provided as a local plain-text file. Read all of it, including the discussion and limitations, before deciding any field is absent. Also open the PMC or arXiv page to find supplementary material links, and follow repository links.
5. Verify twice: after filling the record, re-read every field marked present and confirm the quote actually satisfies the definition, not merely the topic.

## Evidence fields
- E01 (metrics_named): Screening performance metrics are named (sensitivity or recall, specificity, precision, accuracy, F1, workload saved).
- E02 (benchmark_dataset_identified): The evaluation dataset is identified: which review(s), how many records, how many included by the human reference.
- E03 (prevalence_reported): Inclusion prevalence (included records over total) is reported or directly derivable from reported counts.
- E04 (workflow_level_metric): At least one end-to-end workflow metric is reported: time saved, workload reduction, cost, or recall after the human step, not only per-record model metrics.
- E05 (role_statement): The intended role of the model is stated (sole screener, second reviewer, triage or pre-screen) together with what remains a human decision.
- E06 (disagreement_handling): How model versus human disagreements, overrides or escalations are handled in the proposed workflow is stated.
- E07 (affected_groups_or_equity): The study names populations, languages, settings or study types at risk of differential exclusion, or states an equity goal for screening.
- E08a (subgroup_check_designed): The evaluation design includes a planned check of performance by subgroup, language, setting or study type.
- E08b (subgroup_results_reported): Performance or error rates are reported disaggregated by at least one subgroup (topic, study type, population, language, source).
- E08c (language_region_results): Performance is measured across records in different languages or from different regions or settings.
- E09 (acceptable_error_defined): An acceptable error or target threshold (for example minimum sensitivity) is stated together with who set it or the norm it follows.
- E10 (user_perspective_evidence): Reviewer, user or professional perspectives are collected as evidence (survey, interview, usability or workload assessment).
- E11 (failure_modes_identified): Critical failure modes are named (missed eligible studies, hallucinated eligibility reasoning, over-confident exclusion, inconsistency across runs).
- E12 (interaction_failure_checks): Over-reliance, automation bias or alert fatigue in the human and model workflow is addressed in the design or discussed with a mitigation.
- E13 (intended_use_scope): Intended use and non-intended use or scope limits of the screening approach are stated.
- E14 (code_or_workflow_published): Code, prompts or the workflow are published in a repository or supplement with a stable reference (URL, DOI, commit or version).
- E15 (model_prior_evidence): A rationale or prior evidence for the choice of model is given.
- E16 (ground_truth_provenance): The reference standard is defined (for example dual independent human screening or final review inclusion) and its provenance stated.
- E17 (config_reported): Decoding or constraint parameters are reported (temperature, top_p, max tokens, seed, structured output).
- E18 (prompt_text_published): The verbatim prompt or prompts are available in the paper, supplement or repository.
- E19 (prompt_reinforces_human_authority): The prompt includes an uncertainty, unsure or escalation option, or instructs deference to human review. Not applicable when E18 is absent.
- E20 (eligibility_criteria_stated): The eligibility criteria supplied to the model are the review's own criteria and are stated or reproduced.
- E21 (recall_prioritised): The configuration, threshold or decision rule explicitly prioritises sensitivity or recall over precision.
- E22 (leakage_contamination_addressed): Data leakage or training contamination is discussed (model knowledge cutoff versus review date, memorisation of included studies) with a mitigation or an explicit limitation.
- E23 (known_failure_modes_tested): Known LLM failure modes (hallucination, prompt injection, specious plausibility, misuse) are documented and at least one is tested.
- E24 (prompt_robustness_tested): Prompt robustness is tested: prompt variants, wording sensitivity, or repeat-run consistency.
- E25 (data_provenance_documented): Dataset source, collection method and limitations are documented (a data card equivalent).
- E26 (model_card_referenced): A model card, system card or equivalent documentation for the chosen model is cited, or model transparency is explicitly considered in model choice.
- E27 (model_version_pinned): An exact model version identifier and the access or run date are reported.
- E28 (realistic_conditions): The evaluation uses the complete record set of a real review (not a curated or balanced subset) under the access route intended for practice.
- E29 (error_analysis): A systematic error analysis of misclassifications is reported (quantitative or qualitative).
- E30 (test_environment_described): The test environment is described (API or user interface, batching, integration with screening software).
- E31 (limitations_and_failure_modes_documented): A limitations section documents failure modes and uncertainties.
- E32 (worst_case_analysis): Missed eligible studies are characterised (which studies, why) or tail and worst-case performance is reported, not only averages.
- E33 (decision_rule_prespecified): A pre-specified decision rule links metrics to a go, no-go or limited-deployment decision.
- E34 (confidence_intervals): Confidence intervals or another uncertainty measure are reported for headline metrics.
- E35 (energy_cost_reported): Energy, compute or environmental cost is measured and disclosed.

## Output
Write ONE file per study at the path given in the assignment: data/records/<pmid>.json, exactly this shape:

{
 "study": {"pmid": "<pmid>", "pmc": "<PMC id or null>", "doi": "<doi>", "title": "<title>", "year": "<yyyy>", "selection_route": "sampled" | "report_referenced", "model_names": ["<models evaluated>"], "task_note": "<one sentence on the screening task and dataset>"},
 "extracted_on": "2026-09-11",
 "extracted_by": "<your agent name>",
 "sources_consulted": ["<local text path>", "<PMC url>", "<supplement or repo urls you fetched>"],
 "evidence": {
   "E01": {"status": "present|partial|absent|not_applicable", "location": "<where>", "quote": "<verbatim, <=300 chars, required for present/partial>", "note": "<optional>", "searched": "<what you looked for, required for absent>"},
   ... every field E01 to E35 including E08a, E08b, E08c ...
 }
}

Then run, from the repository root, `python3 tests/check_record.py data/records/<pmid>.json` and fix anything it reports until it prints OK. Report back: for each study, the counts of present/partial/absent/not_applicable, any field you were unsure about, and every URL you fetched.
