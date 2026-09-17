# Rationale: Farr v. Grant, No. 25-1306

**P(grant) = 0.004.** Predicted disposition: denied.

## What I read

- `record/snapshots/2026-09-16.json` (the provisioned baseline; `context.json` names `snapshot_date` 2026-09-16). Paid petition, docketed May 26, 2026, from the Eighth Circuit (No. 25-1525, per curiam affirmance October 10, 2025, rehearing denied December 17, 2025). Petitioner is pro se and is her own counsel of record. Every respondent waived: the federal parties (the Solicitor General) on June 18, the private respondents on June 22 and 24. Distributed once, July 8, for the September 28, 2026 conference. No relist, no CVSG, not a capital case.
- `record/context.json`: mode `forward`, `band: baseline`, `salience_version: sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`, `cutoff: null`.
- `record/documents/petition.txt` (32 pages, OCR-derived, not truncated) and `questions-presented.txt`. No brief in opposition exists; all respondents waived, so `documents.json` lists only the petition and its QP cut.
- `metrics/statpack.md`: the modern-cert disposition section, the relist and CVSG cuts, and the *Segment base rate by salience band (sal-v4)* table.

## Anchor

The context's band is `baseline` under `sal-v4`, which matches the table's version, so the anchor is the baseline band's bracketed `reached` rate pooled over Terms strictly before OT2025. The table renders OT2017 through OT2024 as prior rows. Pooling those eight rows:

| pooled window | weighted n | pooled reached rate |
| --- | --: | --- |
| OT2017-OT2024, baseline [reached] | ~11,580 | ~5.1% |

That is the rate for a paid petition that reached (and so far has not left) the baseline band, and it is the yardstick the evaluator scores this cell against.

## Adjustments

I adjust far below the anchor, to 0.4%, because nearly every feature of this petition sits at the weak end of the baseline population:

- **Pro se petitioner, serial filer.** The petition itself lists more than a dozen prior federal suits and several prior cert petitions (docket numbers in the 07-, 12-, 15-, and 18- ranges), all of which ended in denial. Pro se paid petitions grant at a small fraction of the counseled paid rate, and the 5.1% pooled anchor is dominated by counseled filings.
- **No legal question.** The eight QPs are grievances about the outcome below, not rules of law. There is no asserted circuit split beyond a bare "inter-circuit conflict" label attached to a venue complaint, no conflict with a decision of this Court identified with any specificity, and the petition's own stated basis for review is that "the matter speaks for itself."
- **Substance of the claims.** The complaint alleges a 25-year conspiracy by the CIA, FBI, DOJ, and Department of Defense with an actor's manager, lawyers, and talent agency, including a claim under 42 U.S.C. 1985 to a right to hold office as President. The district court dismissed on the pleadings and the Eighth Circuit affirmed per curiam. This is the profile of a petition the Court denies without comment.
- **Universal waivers, including the SG.** Every respondent, including the United States, declined to respond and the Court did not call for a response before distributing. A call for a response is the minimal signal that a Justice's chambers saw something; its absence here is consistent with a straight denial.
- **Eighth Circuit origin.** The circuit cut puts CA8 at 1.2% granted plus 1.4% GVR, slightly below the docket's already low rates. A minor factor.
- **Weak vehicle in every sense.** Per curiam unpublished affirmance, pleadings-stage dismissal, and a request for a "remand for trial" that this Court could not order without first finding an error of law the petition never isolates.

Nothing pushes upward. The one feature that in a different petition would matter, a federal party respondent, cuts the other way here: the federal government is a defendant that has waived, not a petitioner.

## Claims

- `disposition` 0.004: equals the top-level probability.
- `relist-increment` 0.06: from one distribution to the long conference. The relist-count cut shows most paid scored-segment petitions ending at zero relists, and this petition has no hold candidate and nothing pending. I leave a small allowance because the stored distribution count also increments on a reschedule, which happens off the long conference occasionally for reasons unrelated to merit.
- `cvsg-increment` 0.002: the SG already represents the federal respondents and has waived; a CVSG is functionally impossible.
- `summary-disposition-route` 0.6: conditional on a grant that I put near zero. If the Court acted at all on a pro se conspiracy petition against federal agencies, the realistic form would be a GVR in the cert order rather than plenary review, so the conditional favors the cert-order route. This number is a weakly held conditional and will almost certainly be masked as vacuous.
- `dissent-from-denial` 0.005: no Justice has written on this petitioner's prior denials and there is no doctrinal hook.

## Big-case score

0.02. Stakes are confined to the parties; the legal questions, such as they are, have no reach.

## Uncertainty and where to discount me

- My number is well below the band anchor on the strength of the petition's own text and the pro se, serial-filer profile. If the reader believes the Court's treatment of paid pro se petitions is closer to the pooled baseline rate than I do, the honest correction is toward 1 to 2%, not higher.
- The petition is OCR-derived. The text is legible enough that I do not believe any argument was lost, but I read it as OCR output.
- Retrieval: I ran one `fedcourts query` for recent granted SCOTUS priors to check whether any granted row resembled this one. The returned rows were counseled applications and petitions with amici and government or state parties on the petitioner side, none comparable, so the query added no upward evidence and did not move the number. I made no CourtListener MCP calls and no web searches; the provisioned record was sufficient and nothing in it suggested the petition is already decided.
- The provisioned snapshot carries a `sJsonCreationDate` of 09/15/2026 and the file is dated 2026-09-16; its last entry is the July 8 distribution for the September 28 conference, which is still in the future as I write, so the cell is a genuine forward cell.
