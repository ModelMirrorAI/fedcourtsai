# Rationale for the numbers

**Headline: P(grant) = 0.06, predicted disposition `denied`.**

## What I read

Provisioned inputs, all read in full: the snapshot `record/snapshots/2026-09-15.json` (the docket of No. 25-1242 as of September 15, 2026), `record/context.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt` (86 pages, including the Eleventh Circuit's published opinion with Chief Judge Pryor's concurrence and Judge Jordan's partial dissent, and the district court's opinion), and `record/documents/brief-in-opposition.txt` (64 pages, including petitioner's own Eleventh Circuit appellee brief as its appendix). `documents.json` reports all three with `empty_text: false`, `truncated: false`. The petitioner's reply brief (docketed July 15, 2026) is on the docket but was not provisioned, so my read of the reply is a gap, noted in `flags.json`.

## Posture as of the snapshot

- Paid petition, docketed May 1, 2026 (OT2025 number), from a published Eleventh Circuit opinion, 166 F.4th 121, decided January 29, 2026, reversing a denial of qualified immunity on a motion to dismiss.
- Respondent took a one-month extension and filed a brief in opposition on July 1, 2026 (no waiver). Petitioner replied July 15. Distributed July 15 for the conference of September 28, 2026. Distribution count: 1. No CVSG. No amicus briefs. No related cases.
- `context.json`: mode `forward`, band `baseline` under `sal-v4`, term 2025, `signals_observable: true`.

## Anchor

The statpack's "Segment base rate by salience band (sal-v4)" table matches my context's `salience_version`, and my band, `baseline`, is a column, so the anchor is the bracketed `reached` figure for `baseline`, pooled over Terms strictly before 2025. The table renders Terms 2017 to 2024 before mine; pooling their bracketed `reached` rates weighted by their `n` gives roughly 593 grant-family outcomes over a risk-set denominator of 11,580, or about **5.1%**. That is the grant-family rate (plenary grants plus GVRs) for a private paid petitioner that has reached the baseline band, which is exactly this petition's situation, and it is the yardstick my skill will be scored against.

Cross-checks from the pack, read as shape rather than anchor: the paid scored segment's relist-count cut puts a never-relisted petition at about 1.7% grant family, but that bucket is the rate among petitions that *ended* undistributed-again, so it understates a live petition's prospects. The CA11 originating-circuit cut sits near the docket average (grant plus GVR about 3.6% over all fee classes).

## Adjustments up from the anchor

1. **A published opinion with a reasoned dissent.** Judge Jordan's partial dissent argues obvious clarity squarely and quotes Browder at length. A dissent below is one of the more reliable grant correlates among counseled paid petitions.
2. **Full adversarial briefing.** The respondent sought an extension and filed a substantial BIO rather than waiving, and a reply followed. Waived-response petitions are almost never granted; this is not one.
3. **Facts that could support a per curiam.** The complaint alleges an off-duty deputy drove drunk, with no lights, at roughly 70 mph in a 25-mph zone, killed a passenger, and fled. If the Court wanted a plaintiff-side obvious-clarity summary reversal in the Taylor v. Riojas mold, this record is at least as stark. That possibility is most of what carries my number above the anchor.
4. **A Gorsuch-authored circuit precedent on the other side.** Browder is then-Judge Gorsuch's opinion, and the petition leans on it. That does not make a grant likely, but it makes a relist or a separate writing somewhat more likely than for a generic qualified-immunity petition.

## Adjustments down

1. **The question is a fact-bound "clearly established" call.** The Eleventh Circuit assumed a constitutional violation and ruled only on prong two of qualified immunity. Whether the law was clearly established is by design a circuit-by-circuit inquiry, so "our circuit's precedent cast doubt" versus "their circuit's precedent gave notice" is not the kind of conflict the Court usually treats as a split. My CourtListener search for published opinions since 2020 on this Browder-based off-duty-officer question found only Dean (CA4, 2020) and Hughes itself. The split, as the petition frames it, is two circuits against one, and each side rested partly on its own earlier precedent.
2. **Vehicle problems the BIO identifies and the record confirms.** (a) The petition's lead theory, that Lewis footnote 13 itself clearly established the right, was not the theory pressed below: petitioner's Eleventh Circuit brief, reproduced in the BIO's appendix, relied only on the obvious-clarity method and did not cite Browder or Dean. The Court is reluctant to grant to fault a lower court for not addressing an argument it never heard. (b) The case is on a motion to dismiss, on complaint allegations, with the district court itself warning that the color-of-law, discretionary-authority, and scope-of-employment questions all needed factual development. (c) Chief Judge Pryor's concurrence expresses doubt that an off-duty drunk driver acted under color of state law at all; the Eleventh Circuit held it lacked interlocutory jurisdiction to decide that, so any judgment for petitioner here could be undone on remand. (d) The Parratt state-remedy question, which Browder itself flagged as open, lurks. These are exactly the features that make a case a poor candidate for either plenary review or a clean per curiam.
3. **The doctrinal direction.** A grant for petitioner would entrench a substantive due-process tort for reckless official driving. The current Court is skeptical of expanding substantive due process (Glucksberg's caution is quoted approvingly in the BIO and in Chief Judge Pryor's concurrence), and its interventions in qualified-immunity cases remain overwhelmingly on the officer's side; the plaintiff-side exceptions have been rare and summary.
4. **No institutional or amicus interest.** No government party, no amici, no Supreme Court specialist as counsel, and a respondent who is a deceased deputy's estate. Petitions that draw grants in this band usually show at least one of those.

## Net

Starting from about 5.1%, the dissent below and the full briefing pull up; the preservation problem, the interlocutory posture with the color-of-law cloud, the thinness of the asserted split, and the Court's disinclination to expand substantive due process pull down. I land at **0.06**, essentially the anchor, and most of that mass is the summary-reversal route rather than plenary review.

## Claims

- `disposition` 0.06: restates the headline.
- `relist-increment` 0.22: from a one-distribution state before the long conference. The paid scored segment's terminal relist buckets imply roughly a quarter of petitions carry at least one further distribution entry (an upper bound, since reschedules count). I sit slightly below that because baseline-band private petitions relist less, and slightly above the low end because a Justice may hold this one for a possible statement.
- `cvsg-increment` 0.02: no federal interest; CVSGs are about 1% of the paid scored segment and this petition has no feature that raises it.
- `summary-disposition-route` 0.45, conditional on grant: plaintiff-side qualified-immunity grants have mostly been per curiam summary reversals, and no GVR trigger exists; but the color-of-law and preservation problems make a clean per curiam harder here, so I stay below one-half.
- `dissent-from-denial` 0.10, conditional on denial: egregious facts, a dissent below, and Justice Sotomayor's record of writing on qualified-immunity denials raise this above the ordinary rate, but most such petitions are still denied silently.

## Where to discount me

- I could not read the reply brief. If it convincingly answers the preservation point (for example by showing the footnote 13 argument was made in the district court), my second downward adjustment is overstated.
- The pooled anchor is a hand computation from the rendered table (weighted by the bracketed `n` values); rounding in the table means it is approximate to a few tenths of a percent.
- My read that plaintiff-side qualified-immunity grants are mostly summary rests on general knowledge of recent Terms, not on a statpack cut; the harness's own baseline for the summary-route claim is the pooled cert-order share of grants, which I did not compute.
- Corpus priors from `fedcourts query` were not topic-matched (the query surface has no subject filter for SCOTUS rows), so they informed the shape of recent grants only loosely.
- I hold no knowledge of this petition's outcome; the first conference is September 28, 2026, after this run.
