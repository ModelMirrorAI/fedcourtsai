# Why 0.14, and not another number

**P(any grant) = 0.14; modal disposition `denied`.**

## Inputs I read

- `record/snapshots/2026-10-06.json` (the provisioned baseline; `context.json` names it).
- `record/context.json`: forward mode, `band: baseline` under `sal-v4`, `distribution_count: 1`,
  no CVSG, Term 2025, `signals_observable: true`, `cutoff: null`.
- `record/documents/`: `questions-presented.txt` (cleanly cut, three QPs), `petition.txt`
  (136 pages, flagged `truncated: true`; I read the QPs, introduction, statement, and all
  four argument parts), and `brief-in-opposition.txt` (37 pages, complete; read in full).
- `metrics/statpack.md`: modern-cert disposition section, originating-circuit cut, relist
  and CVSG cuts (paid scored segment), and the per-Term salience-band table (sal-v4).
- Retrieval beyond the inputs: see `retrieval.md`. The CourtListener MCP sidecar was
  **rate-limited (HTTP 429)** on the two endpoint calls I needed, so I fell back to the
  corpus tooling, the committed case tree, a web search, and two supremecourt.gov docket
  page fetches, as the prompt's degrade-gracefully rule directs.

## Anchor

The band table matches my context's `sal-v4`, and `baseline` is a column, so the anchor is
the **bracketed `reached` rate for `baseline` pooled over Terms strictly before OT2025**
(OT2017 through OT2024, all eight rendered rows):

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The n-weighted pool is about **5.1%**. That is the rate for a private, paid petition that has
reached the baseline band, and it is the figure my skill will be scored against. Cross-checks:
the CA9 cut gives granted 2.1% + gvr 1.1% over all modern CA9 petitions; the relist cut's
"0" bucket (one distribution, never relisted) gives granted 1.2% + gvr 0.5%, but that bucket
is terminal-count and this petition's one distribution was never acted on, so it is not my
state.

## Adjustments up

1. **Response requested after a waiver** (July 22). A Justice's chambers looked at a
   waived petition and wanted the other side heard. That signal is not in the salience
   scorer, so the frozen `baseline` band understates the posture; petitions with a
   requested response grant at a multiple of the undifferentiated paid rate. On its own I
   would move the anchor to roughly 0.09 to 0.11.
2. **The Robinhood linkage.** The Ninth Circuit itself vacated submission of this appeal to
   await its decision in *Sodha v. Golubowski* (the Robinhood case below) and ordered
   supplemental briefing on its effect. The Court called for the Solicitor General's views
   in *Robinhood Markets v. Sodha*, No. 25-944, on June 1, 2026 (confirmed on the live
   docket page; no SG brief yet). The petition asks in the alternative to be held for
   Robinhood. A hold is the single most likely thing the Court does with this petition,
   and a hold converts into a GVR if Robinhood is granted and the Ninth Circuit is
   reversed or vacated. Because `probability` is P(any grant) and a GVR counts, this path
   carries most of my grant mass.
3. **Court interest in the issue cluster.** Facebook (granted, then DIG'd, OT2024),
   Macquarie (2024), and now the Robinhood CVSG show sustained attention to Ninth Circuit
   disclosure law. Elite counsel on both sides (Morrison & Foerster and Morgan Lewis for
   petitioners, Labaton for respondent).

## Adjustments down

1. **Unpublished memorandum disposition**, expressly non-precedential under Ninth Circuit
   Rule 36-3. The Court very rarely grants plenary review of these; the BIO leads with it.
2. **Interlocutory posture**: reversal of a dismissal with a remand for further proceedings.
3. **The BIO's vehicle argument is strong and specific.** The panel found the risk of
   atypical-customer churn "had started to come to fruition" before the IPO; question 1
   is premised on the risk being unmaterialized. That is the same dispute about what the
   warned-of risk was that produced the Facebook DIG, and the Court will be wary of a
   repeat. The BIO also shows that two surviving statements (customer-base
   representations) and the Item 303 theory would survive a petitioner win on question 1.
4. **Questions 2 and 3 map imperfectly onto Robinhood**, whose QPs are about intra-quarter
   financial data. The overlap is the Ninth Circuit's collapsing of duty and materiality
   under Macquarie, which is real but contestable, so P(hold) is well short of certain.
5. **No cert-stage amicus briefs** here, against three in Robinhood. A business case the
   Chamber and SIFMA skipped is lower-salience than its petition reads.

## How the number was built

Rough decomposition, stated so a reader can disagree with a piece of it:

- P(held pending Robinhood's cert disposition) about 0.55.
- If not held (0.45): decided on its own merits in late 2026; P(grant) about 0.05
  given the unpublished, interlocutory, fact-contested vehicle. Contributes about 0.02.
- If held and Robinhood is denied (0.55 x 0.55): P(grant) about 0.03. Contributes about 0.01.
- If held and Robinhood is granted (0.55 x 0.45; the statpack's CVSG cut gives a 35% grant
  family and Robinhood is a strong CVSG case): P(companion plenary grant) about 0.05;
  otherwise P(Ninth Circuit disturbed) about 0.7 and P(GVR here | disturbed) about 0.6.
  Contributes about 0.11.

Sum about 0.14. GVR-form grants are about 70% of that mass, which is the
`summary-disposition-route` claim.

## Other claims

- `relist-increment` 0.96: the shown distribution predates the response request and was
  never acted on; once the reply is in the petition is redistributed. Only a Rule 46
  dismissal or withdrawal before redistribution defeats this.
- `cvsg-increment` 0.05: the SG's views are already coming in Robinhood on the overlapping
  questions; a second invitation on the Facebook-style question 1 is conceivable only.
- `summary-disposition-route` 0.70 (conditional on a grant): most grant mass is the GVR
  path described above.
- `dissent-from-denial` 0.05 (conditional on denial): securities denials of unpublished
  rulings rarely draw writings.

## Big-case score

0.42. If decided, this is a Facebook-tier securities disclosure case: meaningful to IPO
issuers and underwriters, strict-liability Section 11 exposure, recurring. Not larger
because it is derivative of Robinhood, unpublished below, and drew no amicus interest.

## Where to discount me

- The whole forecast leans on a **hold-for-Robinhood** reading the Court may not share;
  if the Court treats the two as unrelated and denies this petition at its first real
  conference, 0.14 was too high, and a 0.06 to 0.08 number would have been right.
- I could not confirm the current Robinhood docket through the MCP sidecar (rate-limited);
  the supremecourt.gov page fetch stood in for it and showed no entry after June 1, 2026.
- The petition text is flagged `truncated: true` in `documents.json`; I read through the
  Reasons for Granting but the appendix (the opinions below) was not available, so my read
  of the panel's reasoning is through the parties' characterizations.
- I do not know this case's outcome and did not seek it; the live docket page I fetched
  (for post-snapshot entries) matched the snapshot exactly.
