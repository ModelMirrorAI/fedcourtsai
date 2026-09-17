# Rationale for the numbers (claude-baseline, run 20260917T181231Z)

## What I read

- `record/snapshots/2026-09-17.json` (the baseline named by `context.json`):
  No. 25-1318, paid docket, Sixth Circuit (No. 24-5932, decided February 23,
  2026), petition filed May 26, 2026, docketed May 28; waiver of the United
  States' right to respond filed June 8, 2026; distributed June 17, 2026 for the
  conference of September 28, 2026. Three docket entries; one distribution, no
  response request, no relist, no CVSG. Related dockets 25-7403 and 25-7477
  (marked "Vide") carry IFP-range numbers and are almost certainly the
  co-defendant appellees Brockway and Carey, who were parties to the same Sixth
  Circuit opinion.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`,
  `distribution_count` 1, `cvsg_date` null, Term 2025, `signals_observable`
  true, no cutoff.
- `record/documents/questions-presented.txt` and `petition.txt` (120 pages,
  `truncated: true`, text extracted, not OCR). I read the QP, introduction,
  statement of the case, the reasons-for-granting sections (the precedent
  argument, the three-way split, the vehicle argument, the egregiousness
  argument), and the head of the appended Sixth Circuit opinion (panel Moore,
  Thapar, Ritz; Ritz writing; no dissent noted). No brief in opposition exists
  because the government waived; `documents.json` lists only the petition and
  its QP cut.
- `metrics/statpack.md`: the modern discretionary-cert section, the relist,
  CVSG and salience-band cuts, the per-Term table, and the segment base rate by
  salience band (sal-v4).

## Anchor

`context.json` gives band `baseline` under `sal-v4`, and the statpack's segment
table is also headed sal-v4, so the table is a valid anchor. Pooling the
bracketed `reached` figure for `baseline` over the Terms strictly before this
case's Term (OT2017 through OT2024, the eight prior rows the table renders):

| pool | reached grant rate | weighted n |
| --- | --- | --- |
| OT2017-OT2024 | 5.1% | 11,580 |
| OT2020-OT2024 only | 5.4% | 7,014 |

So the yardstick is about 0.05. For context, the terminal relist-0 bucket of the
paid segment shows 1.7% grant-family, and the modern-cert docket overall is about
2.7%, but the prompt's reasoning for preferring the `reached` figure applies: this
petition is at its first distribution and could still climb.

## Adjustments and the final number: P(grant) = 0.035

Down from the anchor, on balance.

- **The United States waived, and no response has been requested in the
  fourteen weeks since distribution.** In a federal criminal case the Solicitor
  General waives when it sees no serious prospect of a grant, and the Court
  essentially never grants a waived petition without first calling for a
  response. The band's `reached` rate pools petitions with and without
  oppositions, so a waived-and-unrequested petition sits below the band mean.
  This is the largest single adjustment. A request could still come at or after
  the September 28 conference, which is why the number is not lower.
- **The split is real but soft.** The petition's own taxonomy has three camps,
  with a "factors without a standard" middle group, and many of the cited
  "influence" decisions still permit a government harmlessness showing. The
  Sixth Circuit assumed the most stringent standard without deciding it and
  rested on a fact-bound harmlessness finding. The government would call this a
  dispute about the application of harmless-error review to one record.
- **Fact-bound posture.** The Sixth Circuit's holding turns on its
  characterization of the trial evidence as "considerable." The petition spends
  its final section arguing the evidence was not overwhelming, which reads to the
  Court as error correction.
- **Private petitioner, non-boutique counsel.** Barnes & Thornburg is capable
  appellate counsel but not a repeat Supreme Court practice, which correlates
  with lower grant rates in the baseline band.

Up from the anchor, partly offsetting.

- **A clean, published, unanimous circuit decision on a recurring question.**
  The QP asks what "prejudice" means under Mattox, Remmer and Olano, an issue the
  Court has not addressed since 1993 and that the lower courts have openly
  described as split (the Sixth Circuit itself, per the petition, acknowledged it
  is an outlier on the burden question). Direct federal appeal, issue preserved,
  no AEDPA overlay, no Rule 52 forfeiture problem.
- **Striking facts.** The court itself sent unadmitted exhibits to the jury, the
  error surfaced months after verdict, jurors were recalled and found to have
  considered the material, and the trial judge found fundamental unfairness.
  This is the kind of record that can draw a response request from a Justice
  interested in jury-integrity doctrine.
- **Companion IFP petitions.** The co-defendants' petitions will be considered
  alongside this one, which slightly raises the chance the pool memo treats the
  issue seriously.

Netting these, my belief is a little below the band anchor. Roughly: P(response
requested) about 0.12, times P(grant | response requested) about 0.25, plus a
residual for a grant or GVR without a response, gives about 0.035.

## The other claims

- **relist-increment 0.20.** From one distribution. The dominant path to another
  distribution is a response request followed by redistribution (about 0.12);
  an ordinary hold-over relist after the long conference or a reschedule adds
  the rest. The statpack shows about a quarter of the paid segment ever relists,
  but that pools elevated petitions with oppositions; a waived baseline petition
  is below that.
- **cvsg-increment 0.003.** The respondent is the United States; a CVSG is not
  the Court's instrument here. Near zero, not zero, to respect the scoring rule.
- **summary-disposition-route 0.25** (conditional on grant). Plenary review is
  the natural route for a doctrinal split; the petition's alternative summary
  reversal request on a court-of-first-view theory is credible enough for a
  quarter. No intervening decision supports a GVR.
- **dissent-from-denial 0.05** (conditional on denial). Sympathetic
  jury-integrity facts against a unanimous, harmlessness-based opinion in a
  murder-for-hire case; a statement is possible but not expected.
- **big_case_score 0.3.** Moderate stakes: a real criminal-procedure doctrine
  with wide application, and a fact pattern with national press history, but not
  a marquee dispute.

## Uncertainty and where to discount me

- I could not verify anything live. Both CourtListener MCP calls (a Sixth
  Circuit opinion search and a SCOTUS docket search for 25-1318, 25-7403 and
  25-7477) returned HTTP 429 rate-limit errors with about fourteen minutes until
  reset. I did not retry beyond one later attempt and did not use any other path
  to CourtListener. So the identity of the two related dockets, the Sixth
  Circuit panel's vote, and whether any post-snapshot entry (a response request
  in particular) exists on the live docket are inferences from the provisioned
  record and the petition text, not confirmed facts. A response request landing
  after my snapshot would move P(grant) up materially (to roughly 0.15 to 0.20).
- The petition is 120 pages and `truncated: true`; I read the petition body and
  the opening of the appended Sixth Circuit opinion but not the full opinion or
  the district court order. My read of the Sixth Circuit's reasoning is filtered
  through the petitioner's framing.
- No brief in opposition exists, so the government's counter-arguments
  (fact-boundness, the softness of the split) are my reconstruction.
- The corpus `query` calls returned recency-ranked priors dominated by
  OT2026 emergency applications and unrelated grants; they did not surface any
  Remmer-type petition and did not move the estimate. I record them for the log,
  not as evidence.
- I have no knowledge of this petition's disposition; the event is pending as of
  the snapshot and I did not encounter its outcome anywhere.
