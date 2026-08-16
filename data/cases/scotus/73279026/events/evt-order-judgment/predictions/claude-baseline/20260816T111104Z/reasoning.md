# Reasoning — why P(disturbed) = 0.93

## Cell posture

Merits cell, `moment: grant`, **forward** mode (`record/context.json`:
`mode: forward`, no `decided_before`). Certiorari was granted April 20, 2026,
limited to Questions 1 and 2; argument is set for November 3, 2026, so the
judgment does not exist yet and nothing retrievable could leak it. I worked
from the provisioned snapshot (2026-08-16), the provisioned cert-stage
documents (QP section, petition, brief in opposition — all non-empty;
petition and BIO truncated per `documents.json`), and the committed
`metrics/statpack.md`. I did **not** retrieve the merits briefs or argument
commentary: petitioners' merits brief and ~28 supporting amici are on the
docket but respondents' merits brief is not yet filed, and the corpus query
service was unavailable in this cell (see below), so this is a forecast made
largely on the docket skeleton plus the cert-stage filings — a legitimate
forecast, but the reader should know that is what it is.

The context block carries `band: high` under sal-v3. Per the stage rule, the
salience band scores grant likelihood, which is settled — I did not anchor on
it, and no flag is owed for its presence.

## Baseline

The statpack's "The merits docket (granted cases)" section publishes an
`excluded` count (67), so it is quotable and is the registered baseline feed.
The grant Term is **OT2025** (grant date 2026-04-20, from the event's
`opened_at` — not the docket-number Term, though here both are 2025). Pooling
`disturbed` over `parsed` across grant Terms strictly before 2025 within the
ten-Term window (the pack renders 2017–2024; earlier Terms hold no parsed
judgments):

- parsed: 52 + 75 + 54 + 69 + 65 + 72 + 55 + 73 = **515** (≥ 30, so the
  committed baseline exists)
- disturbed: 31 + 50 + 42 + 57 + 46 + 49 + 34 + 50 = **359**
- pooled disturbed rate ≈ **69.7%**

That is the bar the cell's skill is scored against. Coverage beside it: the
pool's Terms are all substantially parsed (worst case 2020: 69 of 85 granted),
so censoring bias in the pooled figure is modest.

## Adjustments from 69.7% up to 0.93

1. **The Court's revealed position in this doctrinal line.** The religious
   claimant has prevailed in every recent free-exercise merits case of this
   family — Trinity Lutheran, Espinoza, Carson, Fulton, Tandon, Kennedy,
   Groff, Catholic Charities v. Wisconsin (2025, 9–0), Mahmoud v. Taylor
   (2025). A grant of a court-of-appeals decision *rejecting* a free-exercise
   claim by Catholic schools, from the side of an acknowledged 7–4 split the
   petition says four circuits occupy, is a strong grant-to-reverse signal.
2. **The limited grant's shape.** The Court took QP1 and QP2 — both framed by
   petitioners against the Tenth Circuit's rule — and declined the
   overrule-Smith question. A Court content with the decision below denies;
   taking the standard question while declining the maximal one signals an
   intent to correct the standard under existing doctrine, which
   Fulton/Tandon comparability supplies.
3. **The Solicitor General filed amicus for petitioners** at the cert stage
   (Jan 30, 2026, uninvited — no CVSG) and again on the merits (Jul 2, 2026).
   SG support for the petitioner is a strong marker of merits success.
4. **Escalation on the cert docket.** Respondents waived; the Court requested
   a response (Dec 31, 2025); three distributions; ~24 cert-stage amici and a
   multistate brief (West Virginia et al.), with 43 Members of Congress at the
   merits stage. All consistent with a Court engaged on petitioners' terms.
5. **Counsel.** Becket Fund (Rassbach, Rienzi) — an elite repeat player that
   largely selects winnable vehicles in exactly this line.

## What holds the number below the high 90s

- **The BIO's comparability argument has real content.** Colorado argues the
  equal-opportunity requirement itself is categorical, with *no* exceptions
  and no discretion to create any — the cited "exemptions" (low-income,
  disability, identity-focused providers) are, on its account, program-design
  features that do not exempt anyone from the nondiscrimination rule. If a
  majority accepts that characterization, the Fulton/Tandon comparators
  disappear and an affirmance is coherent. I price P(affirmed, including by an
  equally divided Court) ≈ 0.06.
- **Procedural exits.** DIG risk is low after a limited grant (≈ 0.01). No
  recusal is apparent, so an equally divided affirmance is negligible.

Net: P(disturbed) = **0.93**, with the disturbed mass mostly on `reversed`
(the Court applying strict scrutiny itself, as in Fulton) and some on
`vacated` (announce the standard, remand for application). `granted = 1` and
the `judgment-disturbed` claim restate the same binary.

## Votes and confidence

6–3 along the Carson/Mahmoud line is modal, but the vote block is my least
certain component: Fulton — the closest doctrinal analogue, also a Catholic
entity vs. an LGBTQ-nondiscrimination condition — was 9–0 in the judgment,
and Kagan in particular could join a narrow majority. I kept Kagan in dissent
because she dissented in both Espinoza and Carson, the benefit-program cases
this one most resembles, and the standard petitioners seek is broader than
Fulton's individualized-exemptions holding. Discount the three liberal-seat
votes accordingly; the six-Justice majority side is high-confidence given a
disturbed judgment. Authorship (Roberts) rests on his authorship of Trinity
Lutheran, Espinoza, Fulton, and Carson; it is a pattern call, not scored.

## Degraded tooling

`fedcourts query` was unavailable in this cell: both the default and
`--corpus-backend service` invocations hung until my timeouts (90s/45s)
killed them, printing no rows and no `ranged corpus reads:` line. I therefore
pulled no corpus priors and anchored base rates on the committed statpack
only, per the degradation rule. The CourtListener MCP surface was not
exercised; the provisioned record was rich enough that I judged further
retrieval unnecessary rather than unavailable.
