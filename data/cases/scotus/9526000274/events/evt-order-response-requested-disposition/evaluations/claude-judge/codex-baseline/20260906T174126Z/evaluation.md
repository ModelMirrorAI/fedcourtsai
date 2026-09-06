# Evaluation — codex-baseline

**Cell:** `scotus/9526000274`, `evt-order-response-requested-disposition`,
stage **interim** (emergency stay application 26A274, NRCC et al. v. Brown et
al.). Outcome: `granted` on 2026-09-04 — the Chief Justice referred the
application to the Court the same day and the Court stayed the Fourth
Circuit's mandate pending certiorari, per curiam, Justice Jackson dissenting.

## Headline

- `predicted_disposition` = `granted` vs actual `granted` → **`correct` = 1**.
- `probability` = 0.76, `actual_granted` = 1 → **`brier_score` = 0.0576**.
- `segment_base_rate`, `brier_skill_score`, `base_rate_basis`: **not
  written.** This is an interim cell, so the baseline (the substantive slice's
  grant rate pooled over application-Terms strictly before OT2026) and the
  skill derived from it are the harness's — `stamp-cell` pools them from the
  committed statpack and clears them below the registered floor. For
  orientation only: the pack's strictly-prior rows are Term 2025 (17/226) and
  Term 2024 (14/70), 31/296 ≈ 10.5%, above the floor of 50, so I expect a
  stamped rate rather than a null; if it comes back null, the section itself
  is what to read.
- `vote_accuracy` omitted (interim stage — never scored; the candidate
  elicited no votes anyway). `judgment_correct` null. No `semantic_grades`
  (none declared off the merits stage). `claim_scores` left to the harness.

## What the prediction got right and wrong

This is a well-constructed forecast. The candidate pooled the baseline
correctly (31/296 ≈ 10.5%, matching the committed statpack), said plainly
that it is an unconditioned application-docket rate rather than a
response-requested rate, and declined to manufacture a conditional number
from the pack's right-censored signal columns — using them for direction, not
size. That is exactly the discipline the statpack's own caveats ask for.

It then built the case-specific picture from primary material. With no
filed-document text provisioned, it went to the Fourth Circuit docket
(26-1785) and read the August 25 published opinion, the August 26 emergency
stay motion, and the stay denial, and correctly extracted the levers that
decided the application: a 2–1 panel with a dissent disputing jurisdiction, a
circuit split on Hobbs Act finality (D.C., Third, Eleventh Circuits contra),
the federal respondents' support for a stay, reliance interests in advertising
contracts, and the September 4 effective date. It read the government's
already-filed response off the snapshot and understood its significance. Its
account of the likely ground for relief — a fair prospect of review and
reversal on agency finality and exhaustion, with the equities favoring
preserving the prior practice during an election — tracks the structure of
the actual application (staff-level notice not Commission action; not final;
"use" misconstrued; irreparable harm; equities).

The candidate also stated the residual mass properly: 0.24 covers denial,
partial or administrative-only relief that lapses, withdrawal, or dismissal,
and it noted that the interim resolver reads mixed relief denial-first, so
0.76 is P(unqualified grant). It named its main weaknesses honestly (the
notice governs external conduct now; the respondents face immediate
competitive effects; the panel treated Commission review as constructively
exhausted) and its principal uncertainty (the Supreme Court papers themselves
were not available).

One reservation keeps this off the top of the scale. The reliance on *Trump
v. California* (Aug 24, 2026) as "the most important additional signal" is a
stretch the candidate half-acknowledges: a stay on justiciability grounds
about contingent, non-final executive measures bears on this application's
finality theory only by analogy, and the candidate concedes the FCC notice
"arguably has more immediate external effect". Presenting it as the lead
signal overweights a recent, imperfect comparator relative to the direct
evidence (the SG's support, the split, the dissent) that carried the result.
It is a matter of emphasis rather than error.

Sub-forecasts I do not score (referral 0.96, amicus increment 0.55) are noted
as context only: the docket went on to record both a referral and an
accepted amicus brief before disposition.

## `reasoning_quality` = 0.85

Sound baseline handling with the right caveats; primary-source retrieval that
identified the decisive levers; a properly specified residual; honest
weaknesses; a clear separation between what was provisioned and what was
retrieved. The discount is for the emphasis placed on an analogical
comparator over the direct evidence, and for a small amount of confidence
(0.76, `confidence` 0.78) that the record supports but does not compel.

## Leakage

Mode `forward`. The prediction ran 2026-09-01 against a snapshot ending at the
Aug 31 government response; the disposition did not exist until Sept 4. The
log carries 65 calls at coverage 0.55 — each engine-level call is paired with
an `unobserved` inner-tool row, which is the engine's standing shape. Every
captured CourtListener call is confined to the Fourth Circuit docket
(73519474 / 26-1785: entries 60+, entry 66 opinion dated 2026-08-25, entry
68 stay motion dated 2026-08-26, notice of judgment) and to the *Trump v.
California* opinion (2026-08-24), with the search explicitly bounded
`filed_before: 2026-08-31`. No call queries this application's own SCOTUS
docket beyond the provisioned snapshot, none touches `data/qp-topics/`, and
the latest legible `retrieved_doc_date` is 2026-08-26. `retrieval.md`
discloses the full set and states that no search sought this application's
disposition, which the log corroborates. `retrieved_outcome_material` =
false, `influenced_prediction` = `not_applicable`, `leakage_suspected` =
false. No evidence a decided case was provisioned forward.

## Big-case read

My own read is 0.7 (see `big_case.notes`). The candidate's rationale and score
sat in the same `prediction.json` I read for the headline fields, so I cannot
claim I formed the read before seeing theirs; the basis recorded is my own,
formed from the docket, the disposition, and the stakes described above.
