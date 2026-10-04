# Rationale for P(grant) = 0.20

## What this cell is

A `forward`, cert-stage, `moment: distribution` cell. Snapshot read: `record/snapshots/2026-10-04.json` (the file `context.json` names). Band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2026, paid docket, Fifth Circuit, private petitioner (a group of insurers). Provisioned documents read in full: `questions-presented.txt`, `petition.txt` (29 pp.), `brief-in-opposition.txt` (54 pp.; its last third is the appendix reproducing the Contract Allocation Endorsement).

## The decisive structure: this is a hold petition

The petition's own question presented says it "presents the same question as the now-pending petition in 25-1383, Indian Harbor Insurance Co. v. Town of Vinton" and asks the Court to **hold** it and dispose of it consistently with Vinton. The Fifth Circuit's decision here is a one-paragraph unpublished per curiam applying Vinton. So the probability of a grant here is essentially

P(grant) ≈ P(Vinton granted) × P(Vinton decided for the insurers | granted) + a small residual for a direct or consolidated grant.

The docket behaves exactly like a hold: distributed for 9/28 on Aug 26, "Rescheduled" on Aug 27, the day after. Vinton, meanwhile, had respondents waive, was distributed for 9/28 on Jul 8, drew two cert-stage amici (American Property Casualty Insurance Association; a group of international-arbitration academics), and on Jul 27 the Court **requested a response**, with the BIO filed Aug 26 and reply Sep 9. As of today neither docket shows a redistribution or a disposition (both supremecourt.gov pages end at Sep 9 and Aug 27 respectively), so the long conference acted on neither.

## Anchors

- **Salience band anchor.** The pack's `sal-v4` segment table matches my context's `salience_version`. Pooling `baseline`'s bracketed `reached` rate over the nine prior Terms shown (2017–2025, weighted n ≈ 12,700) gives **≈ 5.0%**. That is the yardstick my skill is scored against.
- **Relist cut.** Terminal relist-count 1 petitions: granted 8.2%, GVR 5.1%. Not directly my state (the single entry is a first distribution plus a reschedule), but it says a once-distributed paid petition is already well above the docket rate.
- **Summary-route baseline.** The per-Term table's GVR share of the grant family, over Terms whose split is trustworthy (2017–2022, 2025), runs roughly 37–59%, about one half. My conditional is far above it because the only realistic grant route here is a GVR.
- **Circuit cut.** CA5: granted 1.6%, GVR 2.1%, a GVR-heavy originating court, consistent with hold-and-GVR traffic.

## Adjustments from the anchor

Up, substantially, from 5%:

1. **Vinton's Court-side signals.** A call for a response after a waiver is an affirmative act of attention, and two cert-stage amici (one an industry association) raise the stakes profile. The question is one a unanimous Court expressly left open in *GE Energy* (2020), and the Fifth Circuit's published Vinton opinion (161 F.4th 282) squarely holds state law governs, against four circuits applying federal common law. The en banc denial, per the petition, came with a concurrence disclaiming any interest in resolving the split. These are classic grant features. I put P(Vinton granted, including any grant form) at about **0.30**, which is well above the paid-petition rate after a response request but tempered by the vehicle problems below.
2. **If Vinton is granted, this petition rides it.** A hold-then-GVR follows a petitioner-favorable merits decision almost automatically.

Down, from what a clean split would otherwise command:

1. **Vehicle problems the BIO presses.** Respondent dismissed the two foreign insurers with prejudice before removal, and the Contract Allocation Endorsement makes each domestic insurer's policy a separate contract. The BIO's real argument is that the Convention never applies at all (no foreign party, no written agreement to arbitrate that survives La. R.S. 22:868), so the choice-of-law question is antecedent to a threshold the insurers may not clear. The Fifth Circuit in Vinton also held the Convention did not directly apply. The Court may see the Louisiana surplus-lines hurricane docket as a messy place to settle a treaty-implementation question, and McCarran-Ferguson lurks.
2. **Merits direction is not one-sided.** Arthur Andersen and § 208 give a respectable argument that state law governs who is bound even under Chapter 2, and the Louisiana Supreme Court (Police Jury, 2024) has now held Louisiana law forbids this estoppel. I put P(insurers win | Vinton granted) at about **0.6**, below the Court's general reversal rate because the four-circuit majority rule is not obviously the Court's reading of GE Energy.
3. **A CVSG in Vinton** would delay, not change, the arithmetic.

0.30 × 0.6 = 0.18, plus roughly 0.02 for a direct or consolidated grant, gives **0.20**. `predicted_disposition` is `denied` because that is the modal outcome; the grant mass is almost entirely `gvr`.

## Claims

- `disposition` 0.20, as above.
- `relist-increment` 0.97. The docket shows one distribution and a reschedule; the petition cannot be acted on without being redistributed, which adds a second distribution entry under the `dist-v2` reading the pack describes. The residual covers parse oddities only.
- `cvsg-increment` 0.04. A CVSG would issue in Vinton, not here.
- `summary-disposition-route` 0.90, conditional on a grant: the grant path is a GVR in light of Vinton; the residual is a consolidated or plenary grant.
- `dissent-from-denial` 0.05, conditional on denial: writings attach to the lead case, not to a companion hold.

## Big-case score

0.25. The underlying issue matters to the international-arbitration bar and to a large volume of Louisiana insurance litigation, but this docket is a companion that would at most be GVR'd, and the question is technical.

## Uncertainties and where to discount me

- P(Vinton granted) is the whole forecast and I have no committed base rate for "response requested after waiver plus two amici plus an acknowledged split"; 0.30 is judgment, and a reader who thinks the Court is eager to police anti-arbitration state rules under the Convention should move it toward 0.45 and this cell toward 0.28. One who weighs the no-foreign-party vehicle problem heavily should move it toward 0.20 and this cell toward 0.13.
- The corpus does not track Vinton (no `data/cases/scotus/9025001383`), so the decisive signal came from the public docket page and CourtListener's docket record, not from a provisioned input.
- I did not read any earlier prediction for this case (an arrival-moment cell exists on disk); this forecast is from the distribution-moment record alone.
- No outcome material was encountered; both dockets are undisposed as of today.
