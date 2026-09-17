# Rationale for the numbers: Cummins v. Illinois, No. 25-1030

**P(grant, any form) = 0.07.** Predicted disposition: denied.

## What I read

Provisioned inputs: the snapshot `2026-09-16.json` (eleven docket entries, paid petition, docketed March 2, 2026, distributed for the September 28, 2026 conference), `context.json` (mode `forward`, band `elevated` under `sal-v4`, distribution count 2, no CVSG, Term 2025), `questions-presented.txt`, the full `petition.txt` (a six-page petition plus appendices carrying the Illinois Appellate Court opinion, 2025 IL App (2d) 230516), and the full `brief-in-opposition.txt` filed by the Illinois Solicitor General's office in June 2026. `documents.json` shows all three documents extracted cleanly, none truncated or empty. Beyond those I read the syllabus and opening of Case v. Montana, 607 U.S. 107 (decided January 14, 2026), via the CourtListener MCP server, and ran one `fedcourts query` (see `retrieval.md`).

## Anchor

The context's band is `elevated` under `sal-v4`, matching the statpack's "Segment base rate by salience band (sal-v4)" table, so I anchored on that band's bracketed `reached` rate pooled over the Terms strictly before this case's Term (OT2017 through OT2024): about 17.2 percent on a weighted denominator of about 2,810. The relist-count cut's bucket 1 (13.3 percent grant family) and the CVSG-none cut (6.3 percent) sit either side of it. The modern discretionary-cert base rate is about 2.8 percent grant family.

One reading caveat on the band: the two distribution entries here are the March 4 distribution that the March 16 call for a response pre-empted, and the June 24 redistribution after briefing. The petition has not been relisted in the ordinary sense; it has never been considered at conference. The band table's caption acknowledges that a pre-consideration redistribution counts toward the stored count, and the distribute-then-call-for-response-then-redistribute shape is common enough in the `elevated` population that I treat the 17 percent as a fair population anchor rather than discounting it wholesale. The call for a response after a waiver is itself the positive signal in this record.

## Adjustments down (the bulk of the move)

1. **Finality.** The Illinois Appellate Court reversed a pretrial suppression order on the State's interlocutory appeal; petitioner has not been tried. Under 28 U.S.C. 1257 the Court routinely denies this posture (Florida v. Thomas, 532 U.S. 774, was dismissed for want of jurisdiction on a closely analogous posture), and the BIO cites three recent denials of defendant petitions from state interlocutory suppression reversals. None of the Cox Broadcasting exceptions plausibly applies. This is close to disqualifying for plenary review and weighs against a GVR too.
2. **Error correction, on the petition's own terms.** The petition says it "does not challenge the rule" of Brigham City or Case, only its application to these facts, alleges no division of authority, and runs six pages of argument. Rule 10 disfavors exactly this.
3. **Case v. Montana cuts against the petitioner.** Case, decided this Term before the petition was filed, rejected a probable-cause gloss on the emergency-aid standard and affirmed an entry. The Illinois court's "approximating probable cause" language, if anything, held the State to a stricter standard than Case requires, so the usual GVR logic (an intervening decision the petitioner could benefit from) is weak, and the Court is unlikely to take a second emergency-aid case eight months after deciding one unanimously.
4. **Strong opposition.** The BIO is from the state Solicitor General's office, addresses the GVR possibility head-on, and the petitioner's reply came from a solo practitioner.

## Adjustments up

1. **The call for a response.** The State waived; the Court called for a response anyway on March 16. That is an affirmative act by at least one chambers and is the main reason this petition is above the baseline population at all.
2. **Sympathetic facts.** Officers waited 76 minutes on a noise complaint, saw no one and no signs of struggle, received no report of injury, never called an ambulance before entering, and the entering sergeant testified he had no information anyone was hurt. The record cleanly presents the welfare-check question that Case did not reach, and two Justices wrote concurrences in Case about the exception's limits.
3. **The GVR path is not zero.** The appellate court did use the probable-cause gloss twice, and the Court sometimes GVRs liberally after a clarifying decision even where the direction of benefit is unclear.

Net: I move from about 17 percent to 7 percent. Most of the gap is the finality bar combined with the petition's self-described error-correction framing.

## The other claims

- **relist-increment 0.28.** Grants nearly always involve at least one relist under current practice, so the 7 percent grant mass carries most of a relist. Add roughly 10 to 12 percent for a Justice writing a statement or dissent respecting denial and a few points for other holds.
- **cvsg-increment 0.02.** State criminal case, no federal party; the SG already spoke to the standard in Case.
- **summary-disposition-route 0.6 (conditional on a grant).** Plenary review of this petition is the least likely grant path; a GVR in light of Case or a per curiam is the likelier form of any grant.
- **dissent-from-denial 0.12 (conditional on denial).** The response call and the Case concurrences make a short statement plausible; most called-for-response petitions still die silently.
- **big_case_score 0.2.** Low stakes as framed: a fact-bound application of a settled standard, though the welfare-check question underneath would matter if the Court reached it.

## Where to discount me

- I know Case v. Montana's outcome (unanimous affirmance, January 14, 2026). It predates this snapshot and every docket entry here except the petition's filing, so it is legitimate forward signal, and it is disclosed in `flags.json`.
- I could not verify the empirical grant rate for called-for-response petitions specifically; the statpack carries no such cut, so my sense that a CFR raises the odds severalfold above the waived population is from general knowledge, not the corpus.
- The single `fedcourts query` I ran returned interim applications rather than comparable cert petitions and did not inform the number.
- The relist and dissent claims carry no published baseline; they are stated as held, not tuned to anything.
