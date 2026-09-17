# Reasoning — why P(grant) = 0.02

## What I read

Provisioned inputs: `record/context.json` (forward mode, band `baseline` under sal-v4, one distribution, no CVSG, Term 2025), the snapshot `record/snapshots/2026-09-17.json`, `record/documents/questions-presented.txt`, and `record/documents/petition.txt` (47 pages, text extracted cleanly; I read the introduction, the statement of the Napue ruling, and both "Reasons for Granting" parts). There is no brief in opposition because the government waived its response on June 9, 2026. Beyond the provisioned inputs I read the committed `metrics/statpack.md`, ran four `fedcourts query` calls, and used the CourtListener MCP server to read the Ninth Circuit's amended opinion (United States v. Holmes, Nos. 22-10312, 22-10338, 23-1040, 23-1166, 23-1167, filed Feb. 24, 2025, amended Dec. 22, 2025; opinion by Judge Nguyen, joined by Judges Schroeder and R. Nelson). Nothing I retrieved touched this petition's own disposition, which does not exist yet.

## The anchor

The context's band is `baseline` under sal-v4, and the statpack's "Segment base rate by salience band (sal-v4)" table is computed under the same version, so its bracketed `reached` figure is the yardstick. Pooling the baseline column's `reached` rates over the Terms strictly before this one (2017 through 2024, weighted by the bracketed n): about 593 grants over 11,580 petitions, or roughly 5.1%. That is the rate a paid private petition faces on reaching the baseline band, before any case-specific information.

Cross-checks from the pack: the relist-count cut puts the paid scored segment's relist-0 bucket at 1.2% granted plus 0.5% GVR, and the terminal `baseline` band at 0.8% plus 0.4%, but those are terminal-state figures that assume the petition never moves again, so I do not anchor on them. The originating-circuit cut has ca9 at 2.1% granted plus 1.1% GVR across all fee classes.

## Adjustments

**Down, hard: the government waived and no response has been called for.** The Solicitor General's office waived on June 9, eight days before distribution, and in the three months since, over the summer recess window when chambers flag waived petitions they want briefed, no call for a response has been entered. The Court does not grant a petition without a response, so a grant here requires the Court to request one at or after the September 28 conference, receive a brief in opposition, and redistribute. Each step is possible but each is unlikely on this record. This is the dominant signal and it takes the estimate from the 5% anchor to the low single digits.

**Down: the split on Question 1 is weaker than described, and the vehicle is poor.** The petition's four circuits (Second, Fifth, Eighth, Eleventh) are cited for the proposition that a prosecutor who capitalizes on false testimony violates due process regardless of what the defense could have done. None of the cited cases, as described in the petition itself, holds that an *unpreserved* Napue claim escapes plain-error review; several are preserved direct appeals and two are habeas cases. The panel's holding was narrower still: it found the claim unpreserved because the defense's pretrial objection invoked the best evidence rule and the rule of completeness rather than Napue, assumed without deciding that a duty to correct existed, said the record was unclear whether the testimony was more than a mistaken recollection, and found no effect on substantial rights. A Court interested in the standard of review for Napue claims would want a case where the violation was actually found. The petition's reliance on Glossip is a stretch, since Glossip involved a confessed violation on state postconviction review, not the preservation question.

**Down: Question 2 is a harmless-error holding.** The Ninth Circuit agreed some lay testimony crossed into Rule 702 territory and held any error harmless. The petition reframes this as a rule that credentials alone satisfy Rule 702, but the opinion I read does not announce such a rule; the word "gatekeep" does not appear in it. That makes Question 2 fact-bound error correction.

**Down: a unanimous, ideologically mixed panel, published, with no en banc vote requested.** The order accompanying the amended opinion records that no judge of the Ninth Circuit requested a vote on rehearing en banc. The panel spanned Judges Schroeder, Nguyen, and R. Nelson. There is no dissent anywhere in the 55-page opinion to point the Court at a problem.

**Up, modestly: a counseled paid petition in a famous case, with a colorable framing.** The petition is competently written, invokes a recent decision of this Court, presents the Napue question as a pure question of law on the panel's own findings, and offers the Holmes trial as a comparative anchor (the same prosecutors played the recording there and the jury acquitted on the patient-fraud counts). The Theranos name guarantees the petition gets read. This is why I sit at 2% rather than at the 1% or below that a waived, uncalled petition from an anonymous defendant would deserve.

**Up, slightly: the residual chance of a post-conference call for a response.** If a response is called for, the case moves into a population where grants are far more common. I put that at roughly 8%, and the conditional grant probability given a response and redistribution at perhaps 20%, which is where most of the 2% comes from. The rest is a small allowance for a Justice-driven summary route I do not see.

Net: P(any grant) = 0.02, predicted disposition `denied`.

## The other claims

- `relist-increment` 0.13: one distribution shown. Any further distribution requires a post-conference call for a response (about 8%), a reschedule before first consideration (which the pack notes counts as a distribution entry), or a relist while a Justice considers a statement. None is likely on a waived petition.
- `cvsg-increment` 0.002: the United States is the respondent; a CVSG is structurally unavailable. I did not write zero because the claim is a probability over the resolver's reading of the docket, not over the legal possibility.
- `summary-disposition-route` 0.30: conditional on a grant. No intervening decision supports a GVR; a summary reversal on plain-error framing is conceivable but the Court would more likely set the Napue question for argument. The pack's recent-Term GVR share of the grant family runs 30% to 59% where the label is populated, and I sit at the bottom of that range because the GVR arm is missing here.
- `dissent-from-denial` 0.03: conditional on denial. A well-resourced white-collar defendant with an assumed-not-found violation and a unanimous affirmance is not the profile that draws a statement, though the prosecution-exploits-false-testimony theme occasionally does.

## Big case score

0.45. The stakes if decided are real: the Theranos prosecution is among the most covered white-collar cases of the decade, and a ruling on plain-error review of Napue claims would apply in every criminal trial. But the questions are procedural and mid-sized, not constitutional landmarks, so I place the case in the middle of the scale rather than the top.

## Uncertainties and where to discount me

- I did not find a companion Holmes petition on CourtListener's SCOTUS docket index, but that index is sparse for the Supreme Court (it did not return this docket either), so I cannot say whether Holmes has filed. A Holmes petition on overlapping questions with a government response would change the picture somewhat, and I would have flagged it if I could confirm it.
- My estimate that a post-conference call for a response is around 8% is judgment, not a corpus figure. The corpus rows carry a `response_filed_at` field but it was null on every granted prior the query returned, so I could not measure the waiver-to-grant rate from the corpus and relied on the structural point that the Court does not grant without a response.
- `fedcourts query` has no filter for respondent identity, lower-court ruling type, or question theme, so the four queries I ran characterized the corpus's shape rather than surfacing close priors. The corpus reads are recorded in `retrieval.md`.
- I know the Theranos prosecutions from training and I read the Ninth Circuit's opinion, both pre-decision material. I do not know this petition's outcome and did not seek it.
