# Reasoning — Alvarez v. Guerrero, No. 26-279 (capital case), cert-stage distribution cell

**Call: denied; P(any grant) = 0.09.**

## What I read
- Snapshot `2026-11-25.json`: paid capital petition from the Fifth Circuit (No. 18-70001, judgment 2025-12-23, rehearing denied 2026-04-30). Two cert-stage amicus briefs (Former Judges and Prosecutors et al.; NACDL), brief in opposition filed 2026-10-30, reply 2026-11-16, **one distribution** (Conference of 12/4/2026). No CVSG, no relist, no record request on the docket.
- `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt` in full; `lower-court-docket.txt` (panel JWE, EHJ, PR; en banc rehearing denied, no dissent noted, and the BIO says denied without a poll). I did not read `decision-below.txt` or `appendix.txt` beyond what the briefs describe; my account of the panel opinions is taken from the parties' characterizations, which agree on the essentials (majority: no clearly established law covering one allegedly sleeping lawyer plus an engaged second lawyer, and insufficient proof; Judge Richman dissenting on Strickland prejudice).
- No `record/related/` and no `same-question.json` were provisioned.

## Anchor
- `context.json`: band `baseline` under `sal-v9`, `cert_anchor.rate` = 0.052 (10 prior Terms, reached-rate). I anchor there. The rendered statpack band table is headed `sal-v8`, not my context's `sal-v9`; the fallback for that mismatch (a private petitioner's class floor = `baseline` reached rate, roughly 4–6% per prior Term) lands on the same figure, so the mismatch does not move my number (flagged as info).
- `cert_amicus_line`: arm `some`, rate 0.163 (n=2318). The prompt cautions this runs high in a weak band. Statpack marginal cuts: 2+ amicus briefs 22.7% grant family (n=1459 resolved); capital-marked paid petitions 13.8% (n=174); CA5 origin is in the ordinary range.

## Adjustments
Up from 5%:
- Two amicus briefs at the cert stage, including one from former judges and prosecutors; top-tier Supreme Court counsel (Seth Waxman as counsel of record).
- A long dissent below by Judge Richman, not a judge who is reflexively favorable to capital habeas petitioners, concluding that Strickland prejudice was shown even under AEDPA.
- Memorable, sympathetic facts (juror affidavits that lead counsel repeatedly slept in a capital trial) and a recent per curiam, Andrew v. White (2025), on which the petition builds a "factual-parity" theory. The Court has occasionally intervened summarily in Texas/Fifth Circuit capital cases.
- The reply's fallback ask for a GVR for an evidentiary hearing gives the Court a low-cost route.

Down toward the anchor:
- The petition is candidly an error-correction request under Rule 10(c). The claimed disagreement among circuits is over how to read Andrew, not a square split on two-lawyer sleeping claims; the BIO lists cases from several courts declining to presume prejudice where co-counsel was present.
- AEDPA deference and the current Court's consistent reluctance to grant relief to state habeas petitioners; the more common summary action in this posture runs in the State's favor.
- Real vehicle problems the BIO presses: disputed proof of when and how long counsel slept, no identified missed objection or question, juror-affidavit admissibility under Rule 606(b), the inadmissible 2019 affidavit, a murky state-court order on which findings were adopted, the co-counsel/local-rule argument arguably underdeveloped below, and "overwhelming" evidence of guilt bearing on prejudice. Rehearing en banc was denied without a poll.
- Circuit Justice Alito denied a second extension to file, a small sign of no special solicitude.

Net: about 9%, a little under double the band anchor and well below the amicus-arm rate. Most of the grant mass is a summary disposition (GVR in light of Andrew or a per curiam vacatur), not plenary review, hence `summary-disposition-route` 0.60 conditional on a grant.

## Other claims
- `relist-increment` 0.42: currently one distribution. Capital cases with a dissent below often draw a record request or a relist while a Justice writes; any dissent from denial or summary action requires at least one more distribution. Straight denial on the 12/7 order list remains the single likeliest path.
- `cvsg-increment` 0.005: state-prisoner habeas, no federal interest.
- `dissent-from-denial` 0.33 (conditional on denial): Justice Sotomayor regularly writes in capital ineffective-assistance cases with a dissent below, and Justice Jackson sometimes does; the `order-writers` numbers (Sotomayor 0.26, Jackson 0.14, others low) are meant to be consistent with that plus a small chance of a dissent from a summary grant by Justices Alito or Thomas.
- `big_case_score` 0.4: life-or-death stakes for the petitioner and a vivid issue, but narrow doctrinal reach.

## Uncertainty and where to discount me
- I relied on the parties' descriptions of the panel opinions rather than reading the 150 KB decision text; if the majority's AEDPA reasoning is weaker (or stronger) than the briefs suggest, my summary-route estimate is the most exposed.
- The relist and dissent numbers are judgment calls with no committed conditional base rate.
- Corpus query added little (the `summary-reversal` filter returned no rows; a lookup of No. 25-690, cited in the petition, showed a denial after two distributions). CourtListener MCP was not used.
