# Evaluation — codex-baseline, scotus/9026000066, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The
petition in *Smith v. Smith*, No. 26-66, was denied on 2026-10-05 after one
distribution for the 2026-09-28 long conference, with no noted dissent
(`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`).

| Field | Value |
| --- | --- |
| `predicted_disposition` / `correct` | `denied` / 1 |
| `probability` / `brier_score` | 0.006 / 0.000036 |
| `segment_base_rate` (`risk_set`) | 0.0502 (n = 12,720) |
| `brier_skill_score` | 0.9857 |
| `reasoning_quality` | 0.84 |

**Base rate.** The prediction froze `band: baseline` under `salience_version:
sal-v4`, matching the statpack table's heading, so the basis is `risk_set`:
the bracketed `reached` figure pooled resolved-weighted over the rendered
Terms strictly before 2026 (2017–2025; the caption renders 10 of 10 Terms, so
no window divergence). From `metrics/statpack.json`: 638.0 / 12,720 = 0.05016.
The candidate pooled the same JSON fields and reports the same 638 / 12,720.

## What the prediction got right and wrong

Right on every scored axis: an ordinary denial in October without a
writing, no further distribution. The 0.6% forecast is the highest of the
three and scores accordingly, but it sits well inside the range the record
supports.

## Reasoning quality (0.84)

A careful, well-sourced rationale whose legal analysis is correct and whose
main weakness is proportion.

Strengths:

- **The anchor is computed exactly and framed correctly.** It pools the
  baseline `reached` rate from the statpack JSON over 2017–2025, states that
  it is the risk-set anchor rather than the terminal rate, and declines to
  substitute the zero-relist terminal cut or a Ninth Circuit bucket for a
  state-court petition. Those are precisely the mis-pairings the two bases
  exist to prevent, and the document avoids each by name.
- **The vehicle analysis is right.** The three questions are read as what
  they are — fact-bound grievances about one Arizona panel's waiver,
  harmlessness, and missing-record rulings — with no conflict shown and
  the memorandum-decision posture noted. It correctly treats the cited
  precedents (*Lee*, *Long*, *Mullane*, *Goldberg*, *Logan*) as the advocate's
  framework rather than independent support, and correctly identifies
  Question 1 as the only reason not to go to zero.
- **The information boundary is handled honestly.** It notes that the
  conference date has passed without an order in the snapshot and refuses to
  infer either a hold or a denial from that silence, which is the right
  reading of a forward cell.

What holds the score down:

- **Proportion.** A substantial share of the document is about process
  rather than law — artifact vintages, which dates mean what, what was and was
  not retrieved, what a flag records. Much of that is disclosure the contract
  asks for, and it is welcome, but it crowds the legal analysis, which is
  shorter than claude-baseline's on the same facts.
- **It does not use the docket's strongest negative signal.** The absence of
  a brief in opposition, waiver, or call for a response is mentioned only as
  "absence of a positive signal in this record, not proof that an omitted
  event never occurred." That is true as far as it goes, but a petition the
  Court distributes without ever asking the respondent to answer is a real,
  directional fact, and the document declines to draw the inference.
- **The stakes read is high.** `big_case_score` 0.18 for a pro se divorce
  procedural appeal is hard to square with the document's own description of
  it as individual and fact-dependent. That is the big-case dimension and is
  not folded into this score, but the same instinct — holding open a
  "potentially recurring" significance the record does not show — is visible
  in the 0.6% grant number and the 35% plenary-review conditional.

## Leakage

Mode `forward`; the prediction (2026-10-04) predates the resolution
(2026-10-05). Capture coverage 0.9; the three `web-search` class calls are
the unobserved ones, so they are graded on their queries: a generic Supreme
Court Rule 10 query and two fetches of the Court's rules-guidance page,
none naming this case, docket, or party, and the candidate reports they
returned no content. No corpus query, no CourtListener call. The remaining
calls are shell reads of the provisioned record, the statpack, and the
contract, plus the agent's own writes and validation. `retrieved_outcome_material:
false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My independent read is 0.02: a two-party divorce appeal from an unpublished
state memorandum decision, denied without a writing. Formed from the record
and the outcome before consulting the candidate's own score.

## Not applicable on this cell

No `vote_accuracy` (cert stage), no `judgment_correct`, no `semantic_grades`
(no semantic set on a cert event; `record/opinion/` absent as expected), no
`claim_scores` (harness-computed). The forecast document was read for
context only and is not scored.
