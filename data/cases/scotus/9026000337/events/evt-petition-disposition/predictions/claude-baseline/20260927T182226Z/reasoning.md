# Rationale for my numbers: No. 26-337, Child v. Unum

**P(grant) = 0.01; predicted disposition: denied.**

## What I read

- Snapshot `record/snapshots/2026-09-27.json` (the file `context.json` names). Three docket entries: petition filed Sep 9, 2026; respondent's waiver of right to respond filed Sep 16, 2026; distributed for the conference of 10/9/2026 on Sep 23, 2026. Paid docket, Eighth Circuit (No. 24-2347), decision May 11, 2026, rehearing denied June 17, 2026. No related cases.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2026, `signals_observable: true`, cutoff null.
- `record/documents/questions-presented.txt` and `record/documents/petition.txt` (99 pages including the appendix; `documents.json` shows both fetched with text, not truncated). No brief in opposition exists, because respondent waived. I read the petition's introduction, statement, all four reasons for granting, the conclusion, and the Eighth Circuit opinion in Appendix A.

## Anchor

The cert-stage anchor is the statpack's "Segment base rate by salience band (sal-v4)" table, whose version matches my context's `salience_version`. My band is `baseline` and my Term is 2026, so I pooled the bracketed `reached` figure for `baseline` over Terms 2017 through 2025, every prior Term the table renders:

| Pool | Rate | n |
| --- | --- | --- |
| baseline, reached, OT2017–OT2025 | 5.0% | 12,720 |

That is the yardstick my skill is scored against. For shape only, the relist-count cut puts a petition that ends at zero relists at about 1.7% grant-family (1.2% granted, 0.5% GVR), the Eighth Circuit cut at 2.6% grant-family across all paid and IFP filings, and the CVSG-none cut at 6.3% grant-family in the paid scored segment.

## Adjustments from 5% down to 1%

Everything case-specific points down, and most of it points hard.

1. **No split, no conflict.** The petition does not claim a circuit split or a conflict with any state high court. Its own Reason III is that no court anywhere has applied the known-loss doctrine to guaranteed-issue group coverage. A CourtListener opinion search for "known loss" with "guaranteed issue" and "long-term care" returned zero results, consistent with that. Novelty with no conflict is the standard profile of a denial.
2. **The question is state law wearing an Erie costume.** The QP asks whether a federal court "may displace" Iowa's regulation by applying a judge-made doctrine. Stripped of framing, it asks the Court to say the Eighth Circuit predicted Iowa law wrongly. The Court does not grant to correct one circuit's reading of one state's insurance regulation. The Erie cases the petition cites (Semtek, Lehman Bros., Salve Regina) do not create a rule of decision the panel violated.
3. **The panel's primary ground is not the one the petition attacks.** Judge Stras's opinion (published, 174 F.4th 1101, unanimous, en banc denied with no dissent) holds first that the policy's plain terms exclude "existing losses" present on the effective date of coverage, and second that Iowa's 2003 statute permits excluding losses from preexisting conditions that begin within six months of coverage. The "insurance covers future risks, not known losses" line is supporting rationale. A GVR-for-certification would leave the plain-terms holding standing, which makes even the petition's alternative relief a poor fit.
4. **Waiver of response, single distribution.** Respondent, represented by Iowa counsel rather than a Supreme Court practice, saw no need to answer. The petition sits at one distribution with no relist and no call for a response. The `reached` baseline rate already prices in petitions that later climb, so this is not double counting; it is a statement that this petition shows none of the early signs that the climbers show.
5. **Private petitioner, non-repeat counsel, Eighth Circuit.** Counsel of record is a Miami solo practitioner with Iowa co-counsel. The Eighth Circuit is among the lower-granting originating circuits in the statpack.
6. **The alternative ask is exotic.** A McKesson-style vacatur for certification has happened a few times in decades, always where the court of appeals plainly ventured into unsettled state law on a novel theory. Here the panel rested on contract text and a statute.

The one factor pointing up is sympathy: a woman quadriplegic since 1980, enrolled on a guaranteed-issue basis with alleged assurances that her condition would not disqualify her, paid premiums for eighteen years, and was denied at claim time after a health-status review the insurer's own manual scripts. Those facts could earn a call for a response. They do not move the Court to grant on a state-law insurance question, and I have given them a small share of the relist probability rather than the grant probability.

Net: 0.01. I considered 0.02, which would treat this as roughly a median baseline petition net of the climbers, but the absence of any conflict, the waiver, and the mismatch between the QP and the panel's actual primary holding put it well below median.

## The other claims

- **relist-increment 0.12.** From one distribution. The main path is a call for a response (sympathetic facts), which would redistribute the petition after the response; a smaller path is a relist for a statement respecting denial. The statpack's relist cut says roughly a quarter of the paid scored segment sees a second distribution, but that population includes rescheduled and held petitions and every petition with a filed BIO; a waived petition at its first conference sits below it.
- **cvsg-increment 0.01.** No federal interest of any kind.
- **summary-disposition-route 0.6 (conditional on grant).** If the Court acts, the only credible form is a summary vacatur directing certification, so summary beats plenary conditional on a grant. I do not put it higher because the harness resolves this against the order text, and a grant that reformulates the question for argument is not impossible in principle.
- **dissent-from-denial 0.03 (conditional on denial).** Sympathetic facts, but no Justice's known agenda attaches to Erie fidelity in insurance diversity cases, and the panel's primary ground gives little purchase.

## Big-case score 0.10

Stakes, not odds: the ruling matters to guaranteed-issue long-term-care insureds in the Eighth Circuit and to LTC insurers writing group coverage, a narrow niche, with no constitutional or federal-statutory dimension. Low.

## Uncertainty and where to discount me

- I had no brief in opposition, because none was filed. My read of Unum's position comes from the Eighth Circuit opinion and the district court opinion in the appendix, not from Unum's own cert-stage advocacy.
- My relist number is the least anchored: no committed baseline exists for the increment, and the call-for-response rate on waived paid petitions is not a statpack cut.
- Corpus retrieval (two `fedcourts query` calls) returned recent OT2025 dockets ranked by recency rather than substantively similar Erie or insurance petitions; it contributed nothing case-specific and I did not lean on it. The statpack was the base-rate source.
- Statpack vintage: the committed `metrics/statpack.md` as of this checkout; Term 2026 rows are essentially empty (six resolutions), which is why the pool stops at OT2025.
- I do not know this case's outcome. Forward mode; the petition is pending for the October 9, 2026 conference.
