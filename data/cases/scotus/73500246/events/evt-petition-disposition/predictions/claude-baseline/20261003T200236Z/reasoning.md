# Rationale for the numbers: Blanche v. Ozurumba, No. 25-1343

**P(grant) = 0.38, predicted_disposition = denied, granted = 0.**

## Inputs read

- `record/snapshots/2026-10-03.json` (the provisioned baseline, `snapshot_date` 2026-10-03,
  payload creation stamp 10/02/2026): paid petition, docketed June 2, 2026 after two
  extensions; BIO filed August 3, reply August 18, distributed for the 9/28/2026 conference. Last
  entry August 19, 2026.
- `record/context.json`: mode `forward`, `band: federal` under `sal-v4`, `distribution_count: 1`,
  no CVSG, term 2025, `signals_observable: true`, cutoff null.
- `event.yaml`: stage `cert`, moment `distribution`, so the five-claim `cert-v2` set applies.
- **No `record/documents/` was provisioned**: no questions-presented, petition or BIO text. The QP
  is inferred from the Fourth Circuit's published opinion, retrieved from CourtListener (flagged in
  `flags.json`).

## Anchor

The table "Segment base rate by salience band (sal-v4)" matches the context's salience version
and carries a `federal` column. Pooling the bracketed `reached` figures over the Terms strictly
before this case's own (OT2017 to OT2024; the pack renders 10 Terms, all of them shown) gives
about 132 grants over 181 weighted resolved federal-band petitions, roughly **73%**. That is the
yardstick the evaluator scores this cell against. The relist and CVSG cuts (relist-0 terminal
bucket 1.7% grant family; no-CVSG 6.3%) are terminal buckets and do not describe a federal
petition's forward hazard, so I read them for shape only. The Fourth Circuit cut (1.3% granted,
1.2% GVR) is likewise whole-docket and not informative for an SG petition.

## Case-specific reading

Up from the anchor: the petitioner is the Solicitor General, who petitioned deliberately after two
extensions; the decision below is a published 2-1 opinion (Wynn, Berner; Richardson dissenting)
with en banc rehearing denied; the panel's "sufficiently substantial to help the organization
accomplish its terrorist activities" definition conflicts with the BIA's Matter of A-C-M- (no
quantitative floor) and sits uneasily with Second and Third Circuit decisions treating food and
shelter as material support, while adopting the Sixth Circuit's "relevant and significant"
reading; the respondent is represented by Covington & Burling and filed a full BIO, so the
petition was fully contested and still reached conference intact. On that record alone I would
have placed the petition slightly above the band anchor, around 0.72 to 0.75.

Down from the anchor, and decisively: **the petition was not granted in the long-conference grant
tranche.** A corpus query for granted 2020s priors returned neighbouring docket 25-1349 (docketed
one day after this one, one distribution) as granted; its public docket shows "Petition GRANTED"
dated October 1, 2026. This case's own public docket, fetched October 3, 2026 under forward-mode
rules, carries no entry after the August 19 distribution: no grant, no denial, no relist. The
Court's post-long-conference practice is to announce the grants it is ready to make a few days
after the conference, before the first Monday order list, and the SG's petitions are usually in
that set when the Court intends plenary review. Not being there removes the single largest grant
path. Relist entries are normally posted after the Monday order list, so the absence of one as of
October 3 does not distinguish relist from denial.

Conditioning on that: if about two thirds of eventual federal-band grants from the long
conference come in the first tranche, Bayes gives roughly 0.70 x 0.33 / (0.70 x 0.33 + 0.30) =
0.43; a path model (P(relist) 0.55, P(grant | relist) about 0.6, P(grant on the October 5 list
without relist) about 0.1) gives about 0.37. I settled on **0.38**.

Vehicle concerns that plausibly explain the Court's hesitation and support the lower number: the
respondent was removed to Nigeria in April 2025; the panel framed its holding "on this record,"
inviting a fact-bound characterization; the Tier III knowledge exception (clause (dd)) and the
duress argument remain open alternative grounds on remand, so the respondent could prevail
regardless of the answer to the QP; and the panel's Loper Bright discussion is dicta the Court
need not address.

## The other claims

- `relist-increment` 0.55: forecast from a one-distribution state. Most grant paths now run
  through a relist; a minority of denial paths do (a dissent being written).
- `cvsg-increment` 0.01: the SG is the petitioner.
- `summary-disposition-route` 0.15 (conditional on grant): no intervening decision supports a GVR;
  the question is legal, not a substantial-evidence misapplication alone.
- `dissent-from-denial` 0.25 (conditional on denial): a federal petition from a 2-1 published
  decision that the Court did not grant outright is the shape that most often draws a Thomas or
  Alito writing; outright denial on October 5 would more likely be silent.
- `big_case_score` 0.45: a recurring statutory question affecting many asylum applicants, with a
  Loper Bright stare-decisis angle, but not a headline case.

## Where to discount me

- The timing inference rests on (a) the neighbouring docket dating the grant tranche to October 1
  and (b) this case's live docket showing nothing on October 3. If the Court releases a second
  grant tranche before October 5, or the docket update lagged, the conditioning is wrong and the
  right number is near the 0.73 anchor. I put perhaps 5% on that.
- I have no text of the petition, BIO or reply, so the split's framing and any vehicle argument
  the BIO pressed are reconstructed from the opinion below, not read.
- I do not know this case's outcome and did not seek it; no disposition surfaced in any retrieval.
- The corpus query returned mostly emergency applications; it informed nothing beyond surfacing
  the neighbouring docket.
