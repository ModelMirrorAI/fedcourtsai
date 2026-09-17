# Rationale for the numbers

**P(grant) = 0.01; predicted disposition: denied.**

## What this cell is

The docket text is "Petition for a writ of mandamus filed," docketed May 5, 2026 as No. 25-1252, a paid filing captioned *In re Richard Devillier, et al.* This is a Rule 20 extraordinary-writ petition, not a petition for certiorari. The event is nonetheless minted as a cert-stage petition-disposition cell with `band: baseline` under sal-v4, so I follow the cert-stage contract, anchor on the band as instructed, and flag the population mismatch in `flags.json`.

The snapshot (`record/snapshots/2026-09-16.json`, provenance `as-stored`, mode `forward`) shows two entries: the petition (response due June 4, 2026) and a single distribution on June 24, 2026 for the conference of September 28, 2026. No response, no waiver, no amicus, no CVSG. The live supremecourt.gov docket page, fetched today, shows the same two entries, so the baseline is current. The petition is genuinely pending; I encountered nothing suggesting a disposition.

## Posture, from retrieval

No filed-document text was provisioned, and the petition PDF exceeded the fetch tool's size limit, so I did not read the petition. I reconstructed the posture from the district court docket and the magistrate judge's memorandum and recommendation (S.D. Tex. 3:20-cv-00223, Dkt. 186, January 5, 2026), read through the CourtListener MCP:

- After this Court's unanimous 2024 decision (601 U.S. 285), the Fifth Circuit first remanded with instructions to remand to state court, then recalled its mandate and instead remanded for proceedings consistent with the Supreme Court's decision, with Judge Higginbotham writing that the state's removal was "now without jurisdictional legs to stand on."
- Texas moved to remand to state court. The magistrate judge recommended remand for lack of federal-question jurisdiction: the direct Fifth Amendment count is foreclosed by DeVillier's instruction to proceed under Texas law; the due process counts are unripe until the takings claim is adjudicated; the state-law count grounded in the federal Takings Clause fails the Grable/Gunn test. The recommendation is careful, quotes this Court's own language, and acknowledges the hardship of restarting a near-trial-ready case. The district judge adopted it on April 9, 2026.
- The remand rests on lack of subject-matter jurisdiction, so 28 U.S.C. 1447(d) bars appellate review. That explains why the landowners came directly to this Court by mandamus fifteen days later. CourtListener's RECAP index shows no Fifth Circuit docket for these parties filed since 2025, so I cannot confirm whether they sought relief in the Fifth Circuit first; if they did not, Rule 20.1's "no other adequate remedy" requirement is a further obstacle.

## Anchor and adjustments

- **Band anchor.** `context.json` gives `band: baseline`, `salience_version: sal-v4`, `term: 2025`, matching the statpack's "Segment base rate by salience band (sal-v4)" table. Pooling the bracketed `reached` figures over the rows strictly before OT2025 (OT2017 through OT2024, n from 1192 to 1739 per Term) gives a weighted rate of about 5.1%. The modern discretionary-cert base rate is about 2.8% grant family; the relist-0 bucket of the paid scored segment shows about 1.7% grant family, and the no-CVSG bucket about 6.3%.
- **Downward, decisively: the writ form.** Those rates describe cert petitions. The Court's modern practice on Rule 20 mandamus petitions is near-uniform denial; I know of no grant of an original mandamus petition against a lower federal court in recent decades, and the Court's own rule calls the writ "drastic and extraordinary." I could not extract a mandamus population from the corpus (see retrieval.md), so this adjustment rests on general knowledge of the Court's practice rather than a committed figure; I say so plainly.
- **Downward: the merits of the mandamus theory.** The remand order is a reasoned jurisdictional ruling grounded in this Court's own DeVillier language, and the Court's opinion expressly contemplated state courts handling these claims. The Court is unlikely to read the remand as defiance of its mandate. The 1447(d) bar is a deliberate congressional choice, not the kind of usurpation mandamus corrects.
- **Downward: no response requested.** Texas filed nothing and the Court distributed without calling for a response. A petition the Court was inclined to act on would ordinarily draw a response request first.
- **Upward, slightly, to 0.01 rather than lower.** I did not read the petition; the counsel of record (Burns Charest) won unanimously in this Court on this very case; the story of a state removing, losing here, and then securing a remand has some appeal to Justices attentive to takings claims. That is enough to keep the number at 1% rather than a fraction of it.

## Claims

- `disposition` 0.01, equal to the top-level probability.
- `relist-increment` 0.10. From one distribution. The main path to a second distribution is a response request; a bare relist off the long conference is also possible but uncommon for an unopposed mandamus petition.
- `cvsg-increment` 0.005. No federal interest.
- `summary-disposition-route` 0.75, conditional on a grant. Any relief would ride the order or a per curiam; plenary argument on a mandamus petition is very rare. The prior Terms' cert-order share of grants (gvr share of the grant family, 30 to 59% where the label existed) is the published yardstick, and I sit above it because a mandamus grant is by nature an order-stage act.
- `dissent-from-denial` 0.05, conditional on denial. Statements on mandamus denials are rare; the forum-shuffling story gives a small chance of one.

## Big case score

0.25. Nationally known underlying case and an issue the takings bar follows, but the mandamus petition itself resolves nothing beyond these parties' forum.

## Where to discount me

The largest uncertainty is the petition's content: if it identifies a specific instruction in this Court's judgment that the remand contradicts, or documents a refused Fifth Circuit mandamus petition, the Court's interest could be higher than I assume, mainly raising the response-request and relist probabilities rather than the grant probability. My mandamus base rate is from general knowledge, not a corpus figure. I have no independent knowledge of this petition's outcome.
