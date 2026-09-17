# Why 0.20, and not another number

## Mode, inputs, and freshness

Forward cell (`record/context.json`: mode `forward`, cutoff null, `signals_observable: true`, band `elevated` under `sal-v4`, `distribution_count: 2`, `cvsg_date: null`, term 2025). Snapshot read: `record/snapshots/2026-09-16.json` (docket as stored on 2026-09-16; eleven proceedings entries, the last a July 8 distribution for the September 28, 2026 conference). Documents read: `questions-presented.txt`, `petition.txt` (160 pages, `truncated: true` in `documents.json`, cut inside the appendix after the Tenth Circuit opinion had begun; the petition's own argument was complete), and `brief-in-opposition.txt` (44 pages, complete). No document had `empty_text`. The conference is twelve days after the snapshot, so the petition is genuinely undecided; nothing I retrieved surfaced a disposition.

## The anchor

The band is `elevated` under `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table, so the anchor is that band's bracketed `reached` rate pooled over Terms strictly before OT2025. The table renders OT2017 through OT2024 as the prior rows; their `reached` figures run from 13.8% (OT2019) to 20.5% (OT2021), and pooling them on their stated n gives about 17%. That is the yardstick the evaluator will score against and it already prices the kind of docket signal this petition carries (a call for a response and a second distribution entry). I did not use the relist-count cut's "1 relist" bucket (about 13% grant family), because this petition's two distribution entries are not a relist: the April distribution was superseded by the call for a response before the conference, so the September 28 conference is the first real consideration.

## Adjustments up

- **Call for a response after a waiver.** Respondent waived on April 3; the Court called for a response on April 20. That is an affirmative act by at least one chambers, and it is the exact docket shape of Zorn v. Linton this Term (waiver September 16, 2025, response requested October 2, 2025, summary reversal 6-3 on March 23, 2026). The Court's willingness to summarily reverse qualified-immunity denials, dormant since late 2021, is demonstrably back.
- **Tenth Circuit provenance.** The Court has singled out this circuit before on exactly this ground (City of Tahlequah v. Bond, 2021), and the petition frames the panel as repeating that error.
- **Two organized police amici** (National Sheriffs' Association, National Fraternal Order of Police) at the petition stage, and a published panel opinion (157 F.4th 1326) that petitioners can characterize as extending "reckless creation" liability after Barnes v. Felix reserved that question.

## Adjustments down

- **The facts are the worst possible vehicle for a summary reversal.** Every summary reversal in this line (White v. Pauly, Kisela, Emmons, Rivas-Villegas, Bond, Zorn) involved a suspect with a weapon or a reasonable belief in one, or a minimal pain-compliance hold. Here, on the facts the district court found a jury could accept, the officers were told the decedent was unarmed, tased him within seconds for not dropping a doll and a picture, and shot him while he moved toward the door; two of three witnesses, one of them the co-defendant officer, said he held nothing. A per curiam would have to either recharacterize the facts, which Johnson v. Jones and Tolan forbid, or hold that Garner-line Tenth Circuit precedent does not clearly cover shooting an unarmed misdemeanant. I put that at low probability.
- **The BIO's vehicle arguments are strong and specific.** It shows that the panel decided both prongs at the moment of each use of force and reached the "reckless creation" point only to reject an evidentiary argument, so QP1 is not implicated; that QP2 is a request for error correction; and that QP3 is barely briefed. It also notes petitioners forfeited the Graham prong-one argument below and that their counsel conceded at oral argument that a violation could likely be shown on respondent's facts. Respondent is represented by an experienced Supreme Court litigation shop; petitioners by local Tulsa counsel, and the petition cites no out-of-circuit authority and asserts no split.
- **Comparable Tenth Circuit officer petitions were denied this Term.** Crockett v. Krueger and Craig v. Krueger, fully briefed qualified-immunity petitions from the Tenth Circuit with the same level-of-generality framing, were denied on March 23, 2026, the same day Zorn was reversed. The Court is selective even within the category it is policing.
- **No split, no federal interest, no intervening decision**, so neither plenary review nor a GVR has an ordinary hook.

Net: the docket signal argues for staying near the anchor, the merits and vehicle argue for below it, and the Court's revived summary-reversal appetite argues for above it. I land at **0.20**, a hair above the pooled anchor.

## The other claims

- **relist-increment 0.45.** From a state of two recorded distributions and no conference yet held. Summary reversals are preceded by multiple relists (Zorn was distributed in December and decided in March), dissents from denial cost a relist or two, and the long conference is the one where the Court most often carries over anything it wants to look at again. The statpack's relist cut is a terminal-count cut and does not give this forward hazard; the number is judgment.
- **cvsg-increment 0.02.** No federal party or federal-law question; the statpack's CVSG cut shows how rare a CVSG is even in the paid segment (173 of about 13,900), and § 1983 qualified-immunity petitions are not where they occur.
- **summary-disposition-route 0.70 (conditional on grant).** The prior-Term cert-order share of the grant family in the per-Term table runs roughly 30 to 59% where the `gvr` label was in use; for this category of petition the share is much higher because the summary per curiam is the Court's standard instrument for qualified-immunity correction, and the petition asks for it by name. The 0.30 residual is a plenary grant to reach the Barnes-reserved question or a hold-and-GVR behind some other case.
- **dissent-from-denial 0.15 (conditional on denial).** Dissents from denial in officer-side qualified-immunity petitions are uncommon; the call for a response and the amici raise it above the floor.
- **big_case_score 0.3.** Fact-bound, no split; a summary reversal over an unarmed decedent would draw real coverage and a plenary grant more, but the modal outcome is a quiet denial.

## Where to discount me

- The pooled `elevated reached` rate is a paid-segment grant-family rate; how much of this band's uplift comes from calls for a response versus relists I cannot see, so the anchor may overstate or understate this specific docket shape.
- I have no measured base rate for post-waiver calls for a response; the Zorn analogy is one case, and Crockett/Craig show the same Court denying similar Tenth Circuit petitions.
- The petition text was truncated inside the appendix, so my reading of the Tenth Circuit opinion is through the parties' characterizations plus the portion of the appendix that was present (panel: Matheson, Phillips, Rossman; no dissent; no judge sought an en banc poll).
- Corpus `query` returned no rows for `--disposition summary-reversal` in the 2020s era (the label is a forward convention and the corpus may carry those rows as `granted`) and the `granted` query returned structurally similar rather than topically similar priors, so the corpus priors did not move the number; the statpack did the base-rate work.
