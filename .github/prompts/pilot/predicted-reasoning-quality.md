# Pilot section: grading `predicted_reasoning.md`

This section is appended to the evaluate prompt only in a pilot run of the
`predicted_reasoning_quality` grade. It is not part of the registered evaluate
prompt, and a registered evaluate cell never reads it. The design it carries
out is `docs/outcome-decomposition.md`, *Grading the forecast document,
design*.

**Where it changes the evaluate prompt, it changes exactly one thing.** The
evaluate prompt tells you not to grade the forecast document. In this run you
grade it, in the two fields below and nowhere else. Every other instruction
stands: `reasoning_quality` still grades `reasoning.md` alone, the claims block
is still the harness's, and nothing you conclude about the forecast document
moves any other field.

## What you grade

Read the forecast document, `predicted_reasoning.md` in the candidate's
`<alias>/` directory, and judge how well its forecast of what the Court would
do and say held up against what the Court did. This is a grade of that
document only. It is not a grade of the prediction's probability, its claims
block, its votes or its rationale, which have their own scores.

**Grade the thrust, not the margins.** Decide for yourself which claims are
central to the document: the disposition and its route, the vote and who
writes, the ground, the procedural path, whatever the document leads with and
gives weight to. Grade those. A minor detail wrong in a forecast whose central
claims held costs little. A confident central call that failed costs most of
the grade. Do not hunt for a detail to dock.

**What you check against is the staged record, and only that.** That is the
committed outcome, the docket record and the order text, and on a merits cell
the opinions staged under `record/opinion/`. Do not fetch opinion text, an
order, or commentary from anywhere else to settle a claim. A claim the staged
record cannot settle is `unresolved`, not a miss and not a guess.

## The rubric

Give `predicted_reasoning_quality` a number in [0, 1], anchored here:

| Grade | Anchor |
| --- | --- |
| 1.0 | The central claims are specific and borne out; the document called what a competent reader of the pre-decision record could plausibly have called otherwise |
| 0.75 | The central claims are specific and mostly borne out; one secondary claim failed, or one central claim held only in part |
| 0.5 | The forecast is right in direction but generic — it commits to little beyond the outcome itself — or a specific forecast is split between borne out and not |
| 0.25 | A central claim failed, with the rest generic or mixed |
| 0.0 | The central claims are specific and failed, or the forecast is wrong in direction |

Use values between the anchors where a document sits between them. Three rules
hold the anchors in place:

- **Specificity earns the top of the scale.** A document that is right but says
  nothing a reader could have been wrong about sits near the middle at best.
  Hedged prose cannot reach the top, because it never commits to the specific
  claims the top requires.
- **Discriminating content only.** A claim entailed by the question presented,
  the syllabus or the standard of review earns no credit however cleanly the
  outcome matches it, because it was never at issue.
- **Length earns nothing.** Grade what the document committed to, not how much
  it wrote.

**Conditional content.** A document often forecasts the next stage only
conditionally ("if granted, the ground is likely …"). Where the condition never
happened, that content earns neither credit nor penalty. But every document
faces something the outcome resolves, at the least the disposition, so a
document whose central claims are all conditional on an event that did not
happen is graded as a generic one, not left ungraded.

**Not gradeable is the record's ground only.** Leave the grade null only where
the staged record is silent on everything the document's central claims turn
on, and say why in `not_gradeable`. Never leave it null because the document
was vague, hedged or conditional: grade that document, and grade it low.

## What you write

In `evaluation.json`, beside the fields the evaluate prompt asks for:

- `predicted_reasoning_quality` — your grade, or null where the record cannot
  grade the document.
- `predicted_reasoning_review` — an object with:
  - `central_claims` — the three to five claims you treated as central, in the
    order the document gives them weight. Each is `{claim, status, basis}`:
    `claim` is the claim as the document committed to it, in a sentence;
    `status` is `borne-out`, `not-borne-out` or `unresolved`; `basis` is what in
    the staged record the status rests on, briefly. Required beside a grade.
  - `not_gradeable` — beside a null grade, the record's ground for it; null
    beside a grade.

The list is never scored. It is the record of what your grade rests on, and a
reader will check it against the document.

In `evaluation.md`, add a short section headed **Predicted reasoning** saying
what drove the grade: which claims you treated as central and why, and where
the document was specific or generic.
