# Evaluation — codex-baseline — Scroggins v. City of Shreveport, No. 26-80 (arrival disposition)

## The cell

Cert stage, arrival moment, forward mode. Outcome: petition **denied** on 2026-10-05 after
one distribution (conference of 9/28/2026), no CVSG, no noted dissent, respondent's response
waived 2026-08-06. The staged opinion slot is absent, which is the ordinary state for a
cert cell and is not a defect; no semantic set is declared on a cert event, so no
`semantic_grades` block is written.

## Scores

| field | value | basis |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` denied == `actual_disposition` denied |
| `brier_score` | 0.000324 | (0.018 − 0)² |
| `segment_base_rate` | null | version mismatch, below |
| `brier_skill_score` | null | follows the omitted rate |
| `base_rate_basis` | null | follows the omitted rate |
| `reasoning_quality` | 0.78 | below |

**Why the rate and skill are omitted.** The prediction froze `context.band = baseline` under
`context.salience_version = sal-v3`. The committed `metrics/statpack.md` table "Segment base
rate by salience band" is headed **sal-v4**. The evaluate prompt's rule for a heading that does
not match the prediction's frozen version is to omit `segment_base_rate` and
`brier_skill_score`, leave `base_rate_basis` null, and flag it, which is what this cell does
(`flags.json`, `data-quality`). For the maintainer's information only, and not written into
the JSON: `fedcourts segment-anchors --term 2026 --salience-version sal-v3` prints the
version-pinned baseline risk-set pool at 5.02% (n=12720, OT2017–OT2025), and the sal-v4
command prints the identical figure, as `docs/salience.md` says it should after the
`dist-v2` rebuild. Had that pool been applied, every candidate here would show strongly
positive skill on a denied outcome; the omission is a contract choice, not a judgment that
the forecast lacked skill.

## What the prediction got right

- The direction and the shape. Denied, no CVSG, one distribution and out: exactly what
  happened. The forecast document (read for context only, not scored) called "one initial
  distribution ... denied after its first listed conference without a repeat relist", which
  is the realized path.
- The anchor was read correctly for the moment. It took the bracketed `reached` figure for
  the weakest band, pooled strictly over prior Terms, and said explicitly why the terminal
  zero-relist rate would be the wrong population for a newly docketed petition. That is the
  right reasoning about which population an arrival cell sits in.
- The discounts are the right ones and are tied to the record: three error-correction
  questions on settled doctrine, no circuit split alleged, a nine-page pro se presentation,
  and the respondent's waiver read as consistent with a quiet denial.
- It correctly read the `relist-increment` claim from a zero-distribution state as
  P(first distribution) rather than P(relist after conference), and explained that
  distinction in its own words. The claims block itself is scored in code and is not graded
  here; the point is that the reasoning understood what it was forecasting.
- Honest about the limits of its retrieval: the Fifth Circuit opinion text could not be
  fetched after a throttled request, and the rationale says it did not infer more than the
  petition states about the dissent.

## What held the score down

- The number. At 1.8% the probability is the highest of the three candidates for a pro se,
  split-free, waived-response error-correction petition. The rationale lists every reason the
  petition sits well below the arrival anchor but does not explain why it lands at 1.8%
  rather than well under 1%; the only upward factor named is a published dissent the
  candidate could not verify. The Brier penalty is tiny on a denial, but the calibration
  argument for the specific landing point is thinner than the rest of the document.
- It does not engage with the one procedural fact that most strongly bounds a grant here:
  the Court does not grant a petition without a response on file, so the grant path runs
  through a call for a response first, and nothing on the docket pointed that way. Another
  candidate made this point; this one treats the waiver only as a general signal.
- The vehicle analysis stops at "presentation is weak". The petition's own text has a
  reporter-citation error for *Tolan* (512 vs 572 U.S. 650) and no record citations at all,
  and the rationale did not notice either, though it had the petition in front of it.

## Leakage

`mode` forward; `retrieved_outcome_material` false; `influenced_prediction`
not_applicable; `leakage_suspected` false. The log carries 13 captured calls, all `shell`
or `other`, with no document dates; the two `other` rows carry credential-shaped
redactions, which are removed text rather than outcome material. The candidate's own
`retrieval.md` discloses a CourtListener opinion search for the decision below (dated
2025-10-17, well before the event) and a throttled follow-up. The case was open on
2026-08-16 (first distribution 2026-08-19, denial 2026-10-05), so this is not a decided
case provisioned forward and the forward default stands after checking.

## Big case

My independent read is 0.03: a single-plaintiff promotion dispute against one city, pure
error correction, waived response, denied without comment. (The predictor's `big_case_score`
sits in the staged `prediction.json`, so I had seen it before writing this; my read was
formed from the petition and docket and is not an agreement number.)

## Reasoning quality: 0.78

A sound, well-organized rationale that read the anchor, the moment and the record correctly,
was candid about what it could not verify, and reached the right answer for the right
reasons. It loses ground on the calibration of its specific number and on two record-level
details it had access to and did not use.
