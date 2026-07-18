# Bolanos-Reynoso v. Department of Agriculture, No. 25-1289 — cert prediction

**Prediction: denied. P(any grant, GVR included) ≈ 0.015.**

## The case

Petitioner, a career federal financial manager, alleged whistleblower reprisal
after disclosing fiscal mismanagement in USDA's Office of the Assistant
Secretary for Civil Rights. The MSPB denied corrective action, analyzing her
disclosures only under 5 U.S.C. § 2302(b)(8)(A)(i) (violation of law, rule, or
regulation) and — per the petition — never reaching her § 2302(b)(8)(A)(ii)
(gross mismanagement) theory. The Federal Circuit affirmed **without opinion**
(nonprecedential judgment, Nov. 6, 2025) and denied rehearing en banc
(Jan. 29, 2026). The question presented: whether an employee whose disclosure
is premised on both § 2302(b)(8) categories is entitled to an MSPB decision on
both categories.

Inputs used: the 2026-07-17 docket snapshot, the provisioned
`questions-presented.txt` and `petition.txt` (194 pp., truncated; the petition
body through the conclusion was fully readable), `metrics/statpack.md` base
rates, one `fedcourts query` priors pull, and one CourtListener opinion search
(cell mode: `forward`).

## Base rate anchor

From the committed statpack (modern discretionary-cert slice,
denial-reweighted): overall grant rate ≈ 3%. This is a **paid** petition
(Term 2025 paid class: ~5.4% grant vs ~1.1% IFP), originating in the
**Federal Circuit** (cafc bucket: ~3.0% grant), **no CVSG** (~3.0%), and no
relists yet — it awaits its first conference. Starting anchor: roughly 3–5%.

## Case-specific adjustments (net strongly downward)

1. **Nonprecedential summary affirmance below.** The Federal Circuit issued a
   Rule 36-type judgment with no opinion. The Court almost never grants cert
   to review an unexplained, nonprecedential disposition; there is no reasoned
   holding to correct and antecedent questions (preservation, whether the MSPB
   actually failed to address the (b)(8)(ii) theory) are undeveloped. This is
   the single largest negative.
2. **No circuit split.** The petition frames the case as error correction —
   "the decision below is wrong," "ideal vehicle" — and cites Flynn v. SEC
   (4th Cir. 2017) only as an *analogous* remand, not a square conflict. A
   CourtListener search for opinions on the failure-to-consider-both-categories
   question surfaced only MSPB decisions and nonprecedential Federal Circuit
   dispositions — no developed appellate conflict. The petition's own
   structural argument (Federal Circuit near-exclusivity suppresses splits)
   cuts against the usual grant trigger existing here.
3. **Respondent waived response.** The Solicitor General waived the right to
   respond (Jun. 8, 2026), signaling the government sees no realistic grant
   risk. The Court has not called for a response as of the snapshot; a CFR
   would be the first sign of interest, and none has issued.
4. **Long-conference distribution.** Distributed Jun. 17, 2026 for the
   Sept. 28, 2026 conference — the end-of-summer long conference, where grant
   rates run below the term average.
5. **Fact-bound QP.** Although styled as a procedural entitlement question,
   the dispute reduces to whether *this* record shows the MSPB ignored one
   theory — classic error correction, compounded by the MSPB's largely
   unreviewable credibility findings that the petition itself catalogs.

Modest positives — competent counsel (Gaston & Cooney; Porter Wright), a
genuinely sympathetic record (the OASCR official petitioner named later pled
guilty to wire fraud and conspiracy on the very contracts she flagged, per the
petition), and congressional solicitude for whistleblowers — are the sort of
equities that at most produce a relist or a dissent from denial, not a grant.
No intervening Supreme Court decision exists to support a GVR, and the case is
not moot, so the GVR path is essentially closed.

## Probability

Starting from the ~3–5% paid/cafc anchor and discounting materially for the
splitless, nonprecedential, waived-response, long-conference posture, I place
P(grant, including GVR) at **0.015**, with **denied** as the predicted
disposition. Outright dismissal or withdrawal is improbable (counseled paid
petition, no settlement signal), so denial absorbs nearly all remaining mass.

## Salience

`big_case_score` 0.15: the whistleblower-vindication narrative and USDA fraud
guilty plea give it modest press potential, and the WPA question matters to the
federal workforce, but the QP is narrow MSPB procedure arising from an
unexplained affirmance; the case is not a headline vehicle.
