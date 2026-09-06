# Evaluation — claude-baseline

**Cell:** `scotus/9526000274`, `evt-order-response-requested-disposition`,
stage **interim** (emergency stay application 26A274, NRCC et al. v. Brown et
al.). Outcome: `granted` on 2026-09-04 — the Chief Justice referred the
application to the Court the same day and the Court stayed the Fourth
Circuit's mandate pending certiorari, per curiam, Justice Jackson dissenting.

## Headline

- `predicted_disposition` = `granted` vs actual `granted` → **`correct` = 1**.
- `probability` = 0.62, `actual_granted` = 1 → **`brier_score` = 0.1444**.
- `segment_base_rate`, `brier_skill_score`, `base_rate_basis`: **not
  written.** This is an interim cell, so the baseline (the substantive slice's
  grant rate pooled over application-Terms strictly before OT2026) and the
  skill derived from it are the harness's — `stamp-cell` pools them from the
  committed statpack and clears them below the registered floor. For
  orientation only: the pack's strictly-prior rows are Term 2025 (17/226) and
  Term 2024 (14/70), 31/296 ≈ 10.5%, above the floor of 50, so I expect a
  stamped rate rather than a null; if it comes back null, the section itself
  is what to read.
- `vote_accuracy` **omitted**. The candidate elicited a full nine-Justice
  block (6–3 to grant), but this is an interim cell and interim votes are
  never scored — a pre-registered prohibition, not a gap; the block is
  recorded as elicited and nothing more. For the record, the outcome writer
  recorded no votes either (`votes: []`), though the docket text notes a
  single Jackson dissent. `judgment_correct` null. No `semantic_grades` (none
  declared off the merits stage). `claim_scores` left to the harness.

## What the prediction got right and wrong

A thorough, well-organised forecast. The record section is accurate to the
snapshot in every particular I checked: application number, filing and
response-request dates, the noon Sept 3 deadline, the parties and their
counsel (Elias Law Group for the candidate respondents; the Solicitor General
for the United States and FCC), the government's response already on file
Aug 31, and the CA4 docket number. The frozen context is quoted correctly and
the candidate says explicitly that it anchored on no cert band, which is the
right reading of an interim cell.

The baseline is pooled correctly (Term 2025 17/226 + Term 2024 14/70 = 31/296
≈ 10.5%, matching the committed statpack), checked against the floor of 50,
and carried with the pack's own caveats — the escalation columns are
right-censored and not as-at-prediction, and the scored population is
selected on the very rungs this application had climbed. The candidate also
noticed that the prompt's worked example predates the pack's coverage and
recomputed from the section rather than copying, which is exactly right.

The upward adjustment is argued from the levers that decided the application:
the response request on a three-day clock as an intent-to-decide signal
(quoting the pack's response-requested count for scale, without turning it
into a rate); the Solicitor General's same-day supporting response; the
Wilkinson dissent below and the standing / Hobbs Act finality off-ramps that
let the Court grant without committing on §315(b); and the status-quo framing
created by the immediately-effective mandate on the eve of the pricing window.
That mapping onto the actual argument structure of the application (staff-
level notice not agency action; not final; "use" misconstrued; irreparable
harm; equities) was reached from press coverage, since the filings were not
provisioned and supremecourt.gov refused the fetch — and the candidate said so
and told the reader to discount its merits characterisation accordingly.

The counterweights are real and well-stated: the statutory text is a genuine
obstacle if the Court thinks the panel is right; the harm is economic; the
applicants are private parties, so the recent pattern of SG-application
grants does not transfer in full; and the denial-first resolver makes any
partial shape count against a grant call. The corpus comparator (26A203 —
response requested the day of filing, referred, granted within about two
weeks) is apt and discounted properly for the government-as-applicant
difference. The candidate also named the denial path it might be
underweighting (a denial with a statement pointing to certiorari).

Where the analysis is weaker: at 0.62 the number is more hedged than the
argument the candidate itself lays out. Having identified SG support, a
dissent below, a circuit split, immediate election-window harm, and a
response request on a three-day clock, and having found no strong contrary
comparator, the stated counterweights read as reasons to stop short of 0.8,
not of 0.65. The candidate's own `confidence` of 0.55 signals it felt the
same tension. That is a calibration judgement rather than a flaw in the legal
analysis, and the Brier reflects it.

Sub-forecasts I do not score (referral 0.85, amicus increment 0.50,
disposition timing "Sept 3–8, quite possibly before Sept 4") are noted as
context only: the docket went on to record a referral, an accepted amicus
brief, and a Sept 4 disposition.

## `reasoning_quality` = 0.85

An accurate record read, a correctly pooled and correctly caveated baseline,
case-specific reasoning that identified the decisive levers and the live
counterarguments, an apt corpus comparator, and unusually candid disclosure
of sources and their limits. The discount is for a headline number that
under-reads the candidate's own argument, and for the merits characterisation
resting on secondary coverage — which the candidate flagged, and which turned
out accurate.

## Leakage

Mode `forward`. The prediction ran 2026-09-01 against a snapshot ending at the
Aug 31 government response; the disposition did not exist until Sept 4. The
log carries 27 calls, all `captured` (coverage 1.0). Beyond the provisioned
inputs and the statpack: two `web-search` calls on the application's own
number and caption (made Sept 1 while it was pending — the ordinary forward
shape); three `web-fetch` calls (a SCOTUSblog report on the filing, and two
fetches the candidate discloses were refused 403 / 429 — the government's
response PDF and a trade-press stay-denial article); one `fedcourts query`
for recent application priors (`retrieved_doc_date` 2026-08-31, the corpus
vintage); and one `file-read` of a committed prediction on a *different*
application docket (26A203), evidently as a format example — not this case,
not outcome material, and not a write. No legible date reaches the event, no
call touches `data/qp-topics/`, and `retrieval.md` states the application
"remains pending (response due Sept 3, 2026, after this run)", which the
snapshot corroborates. `retrieved_outcome_material` = false,
`influenced_prediction` = `not_applicable`, `leakage_suspected` = false. No
evidence a decided case was provisioned forward.

## Big-case read

My own read is 0.7 (see `big_case.notes`). The candidate's rationale and score
sat in the same `prediction.json` I read for the headline fields, so I cannot
claim I formed the read before seeing theirs; the basis recorded is my own,
formed from the docket, the disposition, and the stakes described above.
