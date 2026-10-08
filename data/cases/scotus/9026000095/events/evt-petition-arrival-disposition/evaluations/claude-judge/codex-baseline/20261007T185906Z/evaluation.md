# Evaluation — codex-baseline — scotus/9026000095 — evt-petition-arrival-disposition

## Outcome and scores

Cert-stage arrival cell. The petition (Zhong v. Superior Court of California,
No. 26-95, pro se) drew a brief in opposition from the City of Diamond Bar on
August 20, 2026, was distributed once for the September 28 conference, and was
**denied on October 5, 2026** with no noted dissent (`actual_disposition:
denied`, `actual_granted: 0`).

- `correct` = 1: codex-baseline predicted `denied`.
- `brier_score` = (0.004 − 0)² = 0.000016.
- `segment_base_rate`, `brier_skill_score` **omitted**, `base_rate_basis` null.
  The prediction froze `band: baseline` under `salience_version: sal-v3`; the
  committed `metrics/statpack.md` renders its band table under **sal-v4**. Under
  the prompt's version-mismatch rule the rate and skill are omitted together and
  the mismatch is flagged (see the cell's `flags.json`); the cell is not
  relabelled `terminal`. For the reader only, not as a scored baseline: the
  pack's JSON `alt_segments` carry sal-v3 for every Term with baseline-band
  risk-set figures identical to sal-v4's (pooled OT2017–OT2025 reached rate
  5.02%, n=12,720). The candidate quoted 6.556% (863/13,163) from the table as
  rendered on August 16; the pack has evidently been re-rendered since, so the
  two figures are different vintages of the same pool rather than an
  arithmetic error.
- `vote_accuracy` omitted (cert stage; never scored).
- `claim_scores` not written (harness-computed). The forecast document and the
  claims block were read for context only and are not scored here.

## Leakage

`mode: forward`; prediction created 2026-08-16, denial 2026-10-05. The log has
18 calls, all `captured` (coverage 1.0): shell reads of the prompts, the
provisioned record and snapshot, `metrics/statpack.md` and `statpack.json`, and
a few jq pooling computations. Two `other` calls carry a harness-redacted
credential-shaped marker; that is removed text at capture, not outcome
material. The candidate's `retrieval.md` discloses a CourtListener opinion
search that returned HTTP 429 with no results and a corpus citation lookup for
Caperton that returned no rows; neither appears as a dated retrieval in the
log and neither could carry this case's outcome. No `retrieved_doc_date`, no
query touching this docket's disposition, no `data/qp-topics/` read. The
rationale states that it saw the post-arrival stay activity on the snapshot and
deliberately did not use it. `retrieved_outcome_material: false`,
`influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Reasoning quality — 0.84

Strengths:

- **Correct anchor, correctly justified.** It takes the sal-v3 baseline band's
  bracketed `reached` rate pooled over OT2017–OT2025, explains why the terminal
  rate and the relist-zero rate would condition on the petition's future, and
  treats the originating-court slice (8/153) as a secondary check from a small
  heterogeneous bucket. That is exactly the leakage-safe reading the pack asks
  for.
- **The vehicle analysis anticipated the brief in opposition.** The rationale
  identifies the still-pending enforcement action and the review-of-summary-
  extraordinary-relief posture as "serious finality, record, and vehicle
  concerns"; the City's BIO led with the §1257 finality problem (Jefferson,
  Cox, Atlantic Richfield) and the absence of any reasoned state decision. It
  also reads Murchison/Caperton/Williams correctly as a substantive floor for
  exceptional bias, not a source of a reasoned-ruling duty — the BIO's Rule 10
  and merits sections make the same point.
- **Discipline about the input set.** It notes the snapshot is dated August 16
  for a July 21 arrival event, says it did not use the later stay activity or
  the August 11 supplemental brief to move the number, and flags the
  Dec 2025 / Jul 2026 filing-date inconsistency without over-reading it. It
  also records that no BIO was yet available and what that prevented it from
  testing.
- Honest about failed retrieval (429, empty corpus lookup) rather than
  padding the rationale.

Weaknesses:

- It did not pick up the preservation problem the BIO ultimately made its
  strongest ground: the petition asserts the federal question was "expressly
  raised and preserved" with no Rule 14.1(g) record cite, which a careful
  reader of the nine-page petition could have flagged as a vehicle risk on its
  face.
- The rationale's second half is devoted to the claims block (distribution,
  CVSG, summary route, dissent). That material is harness-scored and not
  graded here; it neither helps nor hurts this number, but it crowds out a
  sentence or two on why 0.004 rather than, say, 0.01 given that the grant
  family includes GVR.
- The `confidence: 0.82` field is asserted without a stated basis.

A sound, well-sourced rationale whose central vehicle judgments were confirmed
by the opposition brief and the denial.

## Big case

My independent read is 0.03 (formed from the record before consulting the
candidate's score): local pro se code-enforcement dispute, no split, no
institutional petitioner, stay denied twice, denied without comment. The
candidate's 0.22 reflects the nationwide-rule framing of the question
presented; I record no agreement number.
