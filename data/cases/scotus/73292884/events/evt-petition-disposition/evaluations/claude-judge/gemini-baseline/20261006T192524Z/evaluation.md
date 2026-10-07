# Evaluation — gemini-baseline

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`), forward mode. The petition in
*Rio Grande Foundation v. Toulouse Oliver*, No. 25-1248, was **denied** on the
October 5, 2026 order list after the September 28 long conference, with two
distributions on the docket and no noted dissent (`outcome.json`:
`actual_disposition` denied, `actual_granted` 0, `distribution_count` 2).

| Field | Value | Basis |
| --- | --- | --- |
| `correct` | 1 | predicted `denied` against actual `denied` |
| `brier_score` | 0.1225 | (0.35 − 0)² |
| `segment_base_rate` | 0.1722 | sal-v4 `elevated`, bracketed `reached` figure, pooled resolved-weighted over OT2017–OT2024 |
| `base_rate_basis` | `risk_set` | the prediction froze `band` elevated **and** `salience_version` sal-v4; the statpack table heading names sal-v4 |
| `brier_skill_score` | −3.129 | 1 − 0.1225 / 0.1722² |
| `reasoning_quality` | 0.40 | see below |

**Baseline detail.** The prediction's frozen context is band `elevated`,
`salience_version` `sal-v4`, Term 2025. The committed `metrics/statpack.md`
band table is headed `(sal-v4)`, so the version matches and the risk-set
basis applies. The table renders the most recent 10 of 10 Terms; the Terms
strictly before 2025 carrying a sal-v4 elevated row are OT2017–OT2024, the
pack holds nothing earlier, so the rendered window and the in-code ten-Term
lookback coincide and no window divergence needs flagging. Pooling the
bracketed figures weighted by their `n` gives 484 weighted grants over 2,810,
or 0.1722 (0.172242 from the unrounded `prefix_*` fields in
`statpack.json`, the figure recorded). No `vote_accuracy`,
`judgment_correct`, or `semantic_grades`: all are off-stage on a cert cell.

## What the prediction got right and wrong

The disposition label was right: `denied`. But the probability of 0.35 was
roughly double the band anchor the author itself quotes, and the outcome was
a silent denial with no further distribution. The Brier of 0.1225 is more
than six times the two 0.14 candidates', and the skill score is deeply
negative: a forecaster that simply parroted the 17% band rate would have
done far better. The `correct` bit and the skill score point in opposite
directions here, and the skill score is the one that reflects the quality
of the forecast.

## Reasoning quality (0.40)

Graded on `reasoning.md` alone, which is a single short paragraph.

- **The anchor is identified but then abandoned without a mechanism.** The
  author quotes about 18% for the elevated reached figure and then
  "adjusts up significantly" to 0.35 on three signals (the response
  request, four amici, subject-matter appetite). Under sal-v4 the band
  encodes the distribution tier, so those signals are legitimate
  adjustments on top of it, but nothing in the document sizes them or
  explains why together they should double the rate. The only brake
  offered is that "the overall baseline grant rate is still quite low",
  which is the anchor the author had already set aside.
- **It mischaracterizes the docket.** The document describes the petition
  as "once-relisted (distribution count 2)". The second distribution
  followed a requested response and a full round of briefing; it is a
  redistribution, not a relist after conference consideration, and both
  other candidates read it that way. Treating a response-request
  redistribution as a relist imports a much stronger grant signal than
  the docket carries.
- **It engages with none of the opposition.** The BIO's points, no claimed
  circuit split, the Tenth Circuit's narrowing construction of the statute,
  the forfeited major-purpose argument, the facial challenge on a thin
  record, are absent. The only concession to a denial is that "the Court
  might find vehicle issues", unspecified. A reader cannot tell whether the
  author read the opposition at all, though the log shows the provisioned
  documents directory was listed.
- **The amici are over-read.** Four one-sided briefs from repeat filers are
  presented as signalling "vehicle quality to the Justices"; they signal
  organized interest on one side, which is a weaker thing.
- **Internally, the forecast and the number disagree.** The companion
  forecast document says the author expects the petition "will likely be
  granted" while the prediction is `denied` at 0.35. That document is not
  scored, but the inconsistency shows the number was not the product of a
  settled analysis.

What earns the grade it gets: the author did locate the right band and the
right (reached) figure, correctly declined to predict a CVSG, and
correctly identified Justices Thomas and Alito as the plausible dissenters
had there been one. The direction of every adjustment was defensible; the
magnitude and the omissions were not.

## Leakage

Forward cell. The provisioned snapshot was dated 2026-09-17 with the
August 12 distribution as its last entry; the October 5 denial did not yet
exist when the cell ran. Every marker-carrying call in the log is
`unobserved`, which is this engine's standing capture shape rather than a
defect, so the calls are graded on their queries: directory listings and
reads of the provisioned record and statpack, then the output writes and a
validate run. No web search, no MCP call, no corpus query, and nothing names
this petition's disposition. `retrieved_outcome_material` false,
`influenced_prediction` not_applicable, `leakage_suspected` false. The
candidate's `flags.json` is not staged, so this rests on the log and the
prose.

## Big-case read

My own read is 0.45: a real but mid-band case whose realized disposition was
a silent denial. The predictor's 0.70 is not graded here; the leaderboard
grades it by rank-agreement.
