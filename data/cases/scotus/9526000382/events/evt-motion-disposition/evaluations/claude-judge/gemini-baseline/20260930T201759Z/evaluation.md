# Evaluation: gemini-baseline — Strulovitch v. Bain, 26A382 (evt-motion-disposition)

## The cell

Interim stage, forward mode. Application 26A382 for a stay of a New York
preliminary injunction was submitted to Justice Sotomayor on September 17,
2026; a response was requested September 23, Becket filed as amicus September
25, the response arrived September 28, and on September 29 Justice Sotomayor
denied the application in chambers, without prejudice to renewal once state
court remedies are exhausted. `outcome.json`: `actual_disposition` = `denied`,
`actual_granted` = 0, `disposition_basis` = `standard`, referral false, response
requested true, one amicus.

The candidate predicted **granted** at **0.70** on September 27, when the case
was genuinely open.

## Scores

- `correct` = 0: `granted` against `denied`.
- `brier_score` = (0.70 − 0)² = **0.49**.
- `segment_base_rate`, `brier_skill_score`: not written. This is an interim
  cell, so both are the harness's: `stamp-cell` pools the substantive slice's
  grant rate over application-Terms strictly before 2026. From the committed
  statpack that pool is Terms 2024 and 2025 only (the earlier Terms are
  unparsed): 31 grants over 296 resolved, about 0.105, which clears the
  50-resolved floor, so I expect a non-null stamped rate and a strongly
  negative skill for this candidate. If the stamp comes back null, the pack
  section is present and above the floor, so the refusal would be something
  other than a thin pool and worth a look.
- `base_rate_basis` null (structural on interim). No `vote_accuracy`, no
  `judgment_correct`, no `semantic_grades`: none applies off the merits
  stage. `claim_scores` is the harness's.
- The prediction's frozen `context.band` is null, so no cert-band flag.

## Reasoning quality: 0.25

`reasoning.md` is two paragraphs. What it gets right: it identifies the
church-autonomy and compelled-speech character of the order and correctly
quotes the pooled interim baseline (about 10.5%). What sinks it:

- **It resolves the pivotal question wrongly and without analysis.** It
  asserts that "the applicants have satisfied the requirement to seek relief
  in the state courts first" because the Appellate Division motion had been
  pending for months. The order that issued says the opposite: denied without
  prejudice "once state court remedies are exhausted." The exhaustion posture
  was the whole case at the interim stage, and the candidate treated it as a
  settled point in one clause.
- **It never engages the structural obstacles.** No mention of the All Writs
  Act / § 2283 jurisdictional theory, the § 1257 finality problem with an
  interlocutory state preliminary injunction, the Court's reluctance to stay
  state trial-court orders while a state appeal is pending, or Yeshiva
  University v. YU Pride Alliance (2022), the closest analogue, where a stay
  of a New York trial-court order was denied on exactly this untried-state-
  remedies ground. The application itself cites Yeshiva and Malliotakis; the
  candidate read the application (the log shows a 150-line read) but its
  analysis does not reflect the jurisdictional half of it.
- **The lift from baseline is unexplained.** Going from 10.5% to 70% on
  "egregious nature" alone, for a private-party applicant against a state
  interlocutory order, is a seven-fold move justified by merits strength
  only. The candidate's own cited authorities (Hosanna-Tabor, Our Lady of
  Guadalupe) are ministerial-exception cases, a loose fit for a litigant's
  participation in a beis din, and it does not consider that a partial order
  resolves as a denial, that a respondent's account was still to come, or
  that the Circuit Justice could dispose in chambers.
- The "highly protective of religious liberty on its emergency docket"
  premise is true of the pandemic-era cases against government policy but is
  contradicted by the one directly comparable private-party state-court case.

The number was wrong, but the score reflects that the analysis did not
identify the issue on which the application turned, not merely that the
outcome went the other way.

## Leakage

Forward, genuinely open (prediction September 27, denial September 29). The
log carries 27 calls with `result_capture_coverage` 0.0, so every call is
graded on its query: prompt, schema, and provisioned-input reads; a statpack
grep; two generic corpus queries (one failed on a positional argument, one
bare listing with `--limit 5`); the output writes; validate. No query names
this docket beyond its provisioned path, nothing carries a
`retrieved_doc_date`, and the reasoning does not read an outcome off the
snapshot. `retrieved_outcome_material` = false, `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false. The candidate's `flags.json`
is not staged, so the absence of any disclosure carries no weight either way.

## Big case

My own read is 0.3: a real church-autonomy question in a private nursing-home
dispute, disposed of in chambers without referral or separate writing, with
the door left open. Disclosure: the predictor's `big_case_score` (0.80) sits
inside the staged `prediction.json`, which I read in full before forming this
read, so I cannot claim it was formed strictly blind to theirs. It was formed
from the record and outcome and differs from theirs materially.
