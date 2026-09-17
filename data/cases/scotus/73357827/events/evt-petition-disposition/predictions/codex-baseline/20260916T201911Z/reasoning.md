# Rationale for the probabilities

## Information set

This is a forward cert-stage prediction for Wisconsin Voter Alliance, et al. v. Don M. Millis, et al., No. 25-1288. The legacy petition event records no explicit stage or moment; the prompt's petition-default cert rule applies. I read the provisioned `2026-09-16.json` snapshot, `context.json`, the questions presented, document manifest, and substantive petition excerpts, particularly printed pp. 2–20 and 37–38. The manifest describes a 56-page, untruncated, nonempty petition. There is no provisioned BIO; the snapshot affirmatively records a June 11 response waiver, rather than a failed extraction of an opposition brief. The baseline has one distribution, one amicus filing, no CVSG, and a September 15 supplemental submission. [S, P]

I retrieved that specific supplemental brief from its snapshot-provided Supreme Court PDF URL. It discusses intervening August 2026 circuit decisions and is permissible forward-mode information. It also reports cert denials in other PILF litigation, not the disposition predicted here. I did not seek or encounter this petition's own outcome, and I do not know it independently. No later target-docket state or other predictor output informed this forecast. [U]

## Anchor and adjustments

The frozen context supplies `baseline`, `sal-v4`, and Term **2025**. I used those values rather than replacing the Term with the calendar year or upgrading the band because Wisconsin appears in a private organization's name. The committed statpack's sal-v4 table matches the context. Pooling all displayed strictly earlier Terms, **2017–2024**, gives **593 weighted grants / 11,580 weighted resolved = 5.1209%**, using the baseline band's bracketed reached rates and their denominators. I computed this from the exact JSON counterparts, not the rounded percentages. Terms 2025 and 2026 are excluded. This is the published private-petitioner risk-set anchor, not the much lower terminal-baseline rate. [B]

The pack's paid-segment terminal relist cuts show grant-family shares around 1.7%, 13.3%, 40.9%, and 36.8% for buckets 0, 1, 2, and 3+ respectively; the no-CVSG and CVSG shares are about 6.3% and 34.9%. These cuts describe terminal populations, not the forward hazard of another distribution or invitation. I use their shape to distinguish a first-conference petition from a repeatedly considered one, not as numeric estimates for the two increment claims. The whole modern-cert and Seventh Circuit cuts are broader, fee-mixed context, not replacements for the conditioned anchor. [B]

My **3.5%** grant probability is a modest downward adjustment from 5.12%. The main negative is the vehicle: according to the petition's own procedural account, both courts dismissed for lack of concrete injury. QP 1's broad private-enforcement question therefore sits behind an Article III obstacle. The competing HAVA decisions cited by petitioners do not necessarily resolve the same statutory provision or injury. [P, pp. 13–19]

A targeted primary-source check materially reduces the force of the asserted clean split. Sandusky recognizes enforcement of the provisional-ballot entitlement, while Crowley's stated holding concerns section 301 and local-election recounts. Those are different from a right to adjudication under section 402. In particular, Crowley is not, on the retrieved language, an across-the-board rejection of all private HAVA enforcement. This does not prove that no conflict exists; it means I do not credit the petition's circuit tally at face value. [C1, C2]

The supplemental brief strengthens the topical relevance of organizational standing but not decisively the vehicle. Its own account says Wolfe involved a $12,500 pocketbook injury, whereas Simon involved an informational injury without adequate downstream consequences. It expressly acknowledges the Seventh Circuit distinguished the other cases. I infer that these differing outcomes can reflect differing injuries rather than a square conflict over denied administrative adjudication. Its reports of denials in Schmidt and Benson supply modest additional caution, not a rule predicting this separate petition. I did not independently verify those supplemental case descriptions. [U, pp. 1–6]

The positive factors are meaningful: federal election administration, statutory language requiring a hearing and timely decision, an alleged complete remedial dead end, one supporting amicus filing, and the petition's account of DOJ concerns about WEC's process. These keep the probability above a negligible level. But the DOJ letter is described by the petitioner, not a Solicitor General recommendation in this case; statutory noncompliance and Article III injury are distinct issues. The response waiver and absence of a response request in this snapshot also weigh against immediate review. [P, pp. 2–3, 9–14, 20; S]

## Limits and remaining claims

The 17% redistribution and 2.5% CVSG estimates are judgmental forward hazards; no published conditional baseline is available for either. The 15% summary-route and 4% separate-writing probabilities are conditional on grant and denial respectively, not unconditional joint probabilities. I see no identified intervening Supreme Court ruling compelling summary relief. The stakes score, 0.58, measures potentially nationwide enforcement and standing consequences, not grant likelihood. [P; U]

The evidence is still largely petition-side advocacy. I did not obtain the separate lower-court opinion: a citation-specific MCP search returned no match. Web-tool requests returned no visible results. Those limitations do not block a forecast; the provisioned petition describes the adverse grounds, and the primary-source checks test two important split assertions. The supplemental PDF was successfully extracted with the installed Python PDF library after the shell PDF utility proved unavailable. [Retrieval log]

## Sources

- **S:** Provisioned event definition, `record/context.json`, and `record/snapshots/2026-09-16.json`; case-specific vintage is the September 16 snapshot, whose latest listed proceeding is September 15. No live corpus blob was queried or refreshed, and no corpus-wide freshness is asserted.
- **P:** Provisioned `record/documents/petition.txt`, `questions-presented.txt`, and `documents.json`; petition filed May 11, 2026, with text fetched July 17 according to the manifest.
- **B:** Committed `metrics/statpack.md` and `metrics/statpack.json`, particularly sal-v4 baseline reached rows for 2017–2024 and the paid-segment relist/CVSG cuts. These are repository-pack observations, not claims about a newly pulled corpus.
- **C1:** Sandusky County Democratic Party v. Blackwell, 387 F.3d 565 (6th Cir. 2004), CourtListener opinion 788159, retrieved section-1983 excerpts.
- **C2:** Crowley v. Nevada, 678 F.3d 730 (9th Cir. 2012), CourtListener opinion 798771, retrieved section-1983 excerpts.
- **U:** Petitioners' September 15, 2026 supplemental brief, 10 PDF pages / 7 substantive pages, retrieved from the exact filing URL in S; details in `retrieval.md`.
