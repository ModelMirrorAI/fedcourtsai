# Reasoning — Parker-Hannifin Corp. v. Johnson, No. 24-1030 (CVSG moment)

**P(grant) = 0.52.**

## What I read
- Snapshot `2025-07-01.json` (provenance `truncated`, cutoff 2025-07-01): petition filed Mar 26 2025; respondents waived; distributed for the May 2 conference; **response requested** Apr 21; BIO and one amicus brief (Encore Fiduciary) May 21; reply Jun 9; distributed for the Jun 26 conference; **CVSG Jun 30 2025**, Justice Alito not participating.
- Provisioned documents: the questions presented and petition (opening, table of contents, introduction), the BIO's outline and its vehicle section headings, and the documents list. I skimmed rather than read the reply and appendix in full; my characterisation of the BIO rests on its headings and introduction.
- `record/context.json`: band `high` (sal-v8), `cert_anchor.rate` 0.332, distribution count 2.

## Base rates
- Frozen anchor for the `high` band, reached basis: **33.2%**.
- Statpack "by CVSG status (paid scored segment)": cvsg n=180 (164 resolved) — granted 29.3% + gvr 5.5% ≈ **34.8%** grant family. The cut pools all Terms, so it is a shape.
- One corpus query (`--court scotus --disposition granted`) returned recent grants of no topical relevance; it did not move the number.

## Adjustments (upward from ~0.34)
- The petition presents an acknowledged conflict: the Sixth Circuit majority held a "meaningful benchmark" is not required to plead an ERISA imprudence claim based on underperformance, over a dissent by Judge Murphy that itself says the decision creates a circuit split with the Seventh, Eighth and Tenth Circuits. A dissent below saying "split" in terms is a strong cert signal.
- The Court called for a response after a waiver, then called for the SG's views: two affirmative acts of attention. The Court has repeatedly taken ERISA fiduciary pleading cases (Dudenhoeffer, Hughes, Cunningham).
- The SG's recommendation is the pivotal unknown. The petitioner is an employer/plan sponsor; the current administration's Labor Department has signalled concern about ERISA class-action pleading standards, so I put the chance of a grant recommendation above one half, and the Court follows SG grant recommendations most of the time. No committed table splits the CVSG population by recommendation, so this is judgement.

## Adjustments (downward)
- Interlocutory posture (reversal of a motion to dismiss), and the BIO argues the Sixth Circuit also held in the alternative that the benchmark pleaded was meaningful, so the question may not be outcome-determinative. The SG could recommend denial on that vehicle ground even while disagreeing with the reasoning below.
- The BIO contests the split as a misreading of the decision below.
- Justice Alito is recused, so four votes must come from eight Justices.

## Candour about contamination
The cell is `forward` mode, but the snapshot is cut at 2025-07-01 and today is well over a year later. I hold an **unverified recollection from training** that the Solicitor General later recommended a grant and that the Court granted certiorari in this case. I did not look it up, did not retrieve the live docket, and tried to rest the number on the pre-cutoff record; on that record alone I would land around 0.45–0.55, and I wrote 0.52 rather than something higher. A reader should nonetheless discount this cell for possible contamination; it is disclosed in `flags.json`.

## Other claims
- `relist-increment` 0.97: after a CVSG the petition is necessarily redistributed once the SG's brief is in, unless it is dismissed or withdrawn first (settlement is the residual risk).
- `cvsg-increment` 0.02: already on the docket; vacuous.
- `summary-disposition-route` 0.05: no intervening decision to GVR on; a grant would be plenary.
- `dissent-from-denial` 0.05: a business ERISA pleading question rarely draws a writing on denial.
- `order-writers`: each small; Alito lowest because recused.

## Retrieval
CourtListener MCP not used; no web search. Statpack plus one corpus query.
