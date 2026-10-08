# Reasoning — why 0.78 and not another number

## What I read
- `record/snapshots/2026-10-07.json` (the provisioned baseline; `context.json` names it); `record/context.json` (`forward`, `band: high` under `sal-v4`, `distribution_count: 2`, `cvsg_date: 2026-05-18`, `term: 2025`, cutoff null).
- Provisioned documents: `questions-presented.txt`; `petition.txt` (truncated; read the introduction, statement, and reasons sections); `brief-in-opposition.txt` (truncated; it concatenates Washington's BIO and the class respondents' BIO, and I read both introductions and the State's full reasons-for-denying section plus the part of the class brief's argument that survived truncation).
- Retrieved from this docket in forward mode: the Solicitor General's CVSG brief (September 15, 2026), the State's supplemental brief and the individual respondents' supplemental brief (September 29, 2026). Also the supremecourt.gov docket page for the companion petition No. 26-71 and the syllabus of Hencely v. Fluor Corp. via the CourtListener MCP. Details in `retrieval.md`.

## Anchor
`band: high` under `sal-v4`, which matches the statpack's band table heading, so the table is my anchor. Pooling the bracketed `reached` figures for `high` over docket Terms strictly before 2025 (2017 through 2024, the whole rendered window) gives 313.9 / 898 = 35.0%. The CVSG cut on the paid scored segment says the same thing from a different direction: 29.4% granted + 5.5% GVR = 34.9% grant family on 163 resolved. Both are unconditional on what the SG actually said, and that is the conditional that matters now.

## Adjustments up
1. **The SG recommends grant and reverse.** The brief, signed by the Solicitor General, the Deputy SG and an Assistant to the SG, says in its interest statement, discussion and conclusion that the petition should be granted; it argues both discrimination-type intergovernmental immunity and a "who decides" conflict preemption theory, asserts a split with the Third Circuit's CoreCivic decision, and calls the case an ideal vehicle (final judgments after trial, state law settled by the certified-question answer). The Court follows an SG grant recommendation most of the time; my working figure is roughly three in four to four in five.
2. **Petition quality and the lower-court record.** Paul Clement for petitioner; seven Ninth Circuit judges dissented from the en banc denial, with opinions by Judges Bumatay and Collins; the panel was divided with a long Bennett dissent; three administrations filed on GEO's side below.
3. **Doctrinal fit with the current Court.** The discrimination theory tracks United States v. Washington (2022), a unanimous decision striking a Washington law that burdened federal contractors at Hanford while sparing state workers. The Court has been receptive to federal-supremacy claims in the immigration-enforcement setting.
4. **The companion petition is paired.** No. 26-71, GEO's petition against Washington's detention-facility regulation statute, was rescheduled on October 6 and redistributed on October 7 for the same November 6 conference as this case. Pairing is consistent with the Court intending to act on the two together, which on this record points toward a grant of at least this one.

## Adjustments down
1. **Hencely v. Fluor Corp. (April 22, 2026, Thomas, J.).** Decided after the petition and BIOs and before the SG's brief, which does not cite it. The holding is that state tort claims against a military contractor were not preempted where the government neither ordered nor authorized the challenged conduct, with a narrow reading of Boyle and language (quoted by respondents) that contractors are not federal agencies and may be regulated on the same terms as any private company absent a statute. It weakens the "contractor steps into the government's shoes" direct-regulation theory the petition leads with. It does not reach the discrimination prong, which is the SG's lead argument, so I treat it as a meaningful but partial counter-signal.
2. **ICE's June 2026 revised detention standards.** The individual respondents' supplemental brief reports that the new standards forbid paying detainees more than the congressional allocation and state that detainees are not entitled to wages under wage laws. That makes the prospective preemption question different from the one this record presents and lets respondents argue only a backward-looking judgment remains. It cuts both ways (the conflict is now sharper for future cases), so a small discount.
3. **Vehicle wrinkles respondents press.** GEO's contract required compliance with state and local labor laws; ICE told GEO there was no maximum; GEO sometimes paid more than $1 per day; and the State and class dispute the SG's premise that Washington never uses private detention contractors (work-release and civil-commitment contractors). These give a Justice who wants to deny a fact-bound reason to.
4. **The split is contested.** The Third Circuit's CoreCivic opinion expressly cited the panel decision here as a different kind of case, and the Second and Fourth Circuit cases are permit and licensing cases.

Net: start near 0.78 to 0.82 from the SG conditional, take a few points off for Hencely and the vehicle issues, and land at **0.78**.

## The other claims
- **relist-increment 0.60.** From two distributions. The Court's relist-before-grant habit plus the paired companion petition make a third distribution more likely than not; a first-conference grant is the main way this resolves no.
- **cvsg-increment 0.01.** A CVSG is on the docket; the claim is vacuous for this cell and the harness masks it.
- **summary-disposition-route 0.05.** Conditional on a grant. No intervening decision favors petitioner, so no GVR; summary reversal is implausible on this record.
- **dissent-from-denial 0.45.** Conditional on denial. SG support and seven dissenting circuit judges raise it well above the ordinary rate, but many such denials are silent.
- **big_case_score 0.60.** Stakes, not odds: immigration federalism, private detention nationwide, SG participation, a companion case; still a wage question with a narrow doctrinal footprint.

## Where to discount me
- I did not read the Hencely opinion beyond its syllabus, and I did not read the Ninth Circuit opinion itself; my view of the lower-court reasoning comes from the petition, BIOs and SG brief.
- The follow rate for SG grant recommendations is from my general knowledge, not a corpus statistic; the statpack carries no cut by SG recommendation.
- The pairing inference about No. 26-71 is a reading of two docket entries, not a stated Court action.
- The BIO text is truncated; I may be missing arguments in the class respondents' brief after its circuit-split section.
- No prior corpus query returned a topically close case; the corpus priors were not informative here beyond the base-rate tables.
