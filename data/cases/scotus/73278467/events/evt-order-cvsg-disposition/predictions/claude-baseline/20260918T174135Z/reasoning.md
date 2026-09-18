# Why P(grant) = 0.52

## What I read

Provisioned inputs: `record/snapshots/2026-07-01.json` (the 9-entry docket through the 6/30/2026 CVSG), `record/context.json` (mode `forward`, band `high` under sal-v4, `distribution_count` 2, `cvsg_date` 2026-06-30, term 2025, cutoff 2026-07-01 under a `date` cut), `event.yaml` (stage cert, moment cvsg), `questions-presented.txt`, the full `petition.txt` (44 pp) and `brief-in-opposition.txt` (34 pp); `documents.json` reports both fetched cleanly with no truncation and no OCR. The committed `metrics/statpack.md` for base rates. Retrieval beyond that is listed in `retrieval.md`.

## Anchors

- **Salience band.** Context freezes `high` under sal-v4, which matches the band table's heading, so the table is the anchor. Pooling the bracketed `reached` figure for `high` over Terms strictly before 2025 (2017–2024, the whole rendered window minus this Term) gives 313.9 weighted grants over n = 898, about **35.0%**. The 2025 row (42.6%, n = 68) is this case's own Term and is excluded.
- **CVSG cut** (paid scored segment): resolved n = 163, granted 29.4% + gvr 5.5% = **34.9%** grant family, denied 62.0%.
- **Relist cut.** The frozen count of 2 corresponds to the "1" bucket (granted 8.2%, gvr 5.1%), but I give it little weight: the second distribution here was the release from a hold for *B.P.J.*, not a relist after consideration, so the bucket's population is not this docket's situation.
- Circuit cut: ca10 grants 2.5% + gvr 1.4%, unremarkable, not used.

Both live anchors sit at 0.35, and the evaluator's yardstick is the high-band reached rate. My 0.52 is a deliberate step above it.

## Adjustments upward

1. **CVSG chosen over GVR or denial on the day *B.P.J.* came down.** The Court held this petition from December to June for *B.P.J.*/*Hecox*. When those were decided (6/30/2026, Kavanaugh, J., 6–3, intermediate scrutiny applied, quasi-suspect status not decided), the routine dispositions of a held case were GVR or deny. The Court instead asked the SG whether the *Turner*-versus-*VMI* question deserves plenary review. That is a stronger interest signal than an ordinary CVSG issued on first consideration, and the CVSG cut's 35% averages over the ordinary kind.
2. **Likely SG alignment.** The SG's office under the current administration has argued that classifications by biological sex are permissible, has appeared as amicus in the Tenth Circuit's *Fowler* remand (the BIO says so), and defends the Bureau of Prisons' biological-sex housing policy in pending litigation (*Doe v. McHenry*, cited by both sides). I put the SG recommending grant or GVR at about 0.6. Historically the Court grants roughly three quarters of CVSG'd petitions where the SG recommends grant and about a fifth to a quarter where it recommends denial; 0.6 × 0.78 + 0.4 × 0.22 ≈ 0.56.
3. **Stakes and support.** Twenty-three states plus the Arizona Legislature filed as amici at the petition stage; the panel dissent (Tymkovich, J.) and a three-judge dissent from denial of rehearing en banc say only this Court can resolve the *Harper*/*VMI* tension; the Court has shown sustained appetite for transgender equal-protection cases (*Skrmetti*, *B.P.J.*, *Chiles*).

## Adjustments downward

1. **Vehicle.** The BIO's strongest points are real: petitioners conceded on appeal that intermediate scrutiny applied (Pet. App. 37a), the panel expressly resolved the *Turner* question on party-presentation grounds (Pet. App. 36a–38a), and the author of the panel opinion called the case "a particularly poor vehicle" when concurring in the en banc denial. The Court "does not ordinarily decide questions not passed upon below," and the SG's office weighs vehicle quality heavily even when it agrees on the merits. This is the main reason I do not go higher than the mid-50s.
2. **Posture.** Rule 12(b)(6) reversal, no record, and the Tenth Circuit disclaimed any view on whether the policies survive heightened scrutiny. *B.P.J.* itself shows a sex classification surviving intermediate scrutiny, which weakens the petition's premise that the standard is outcome-determinative.
3. **Unattractive facts on QP2.** The deputy's alleged conduct during the search, and the fact that the abusive-search claim against him proceeds regardless, make the strip-search question a poor candidate; a grant would likely be QP1 only, which does not change the binary but shows the case is not a clean two-question vehicle.
4. **Split is contestable.** The BIO's argument that the *Turner*-side circuit authority predates *Johnson* (2005) has force; the split the SG would have to credit is between the Eighth/Ninth Circuits and a dissent-plus-older-cases side.

Net: I move from 0.35 to 0.52, weighting the same-day CVSG-over-GVR signal and likely SG support against a genuinely flawed vehicle. `granted` = 1 because the number is above one half, with low confidence (0.45): this is close to a coin flip and I would not be surprised by a denial.

## The other claims

- **relist-increment 0.97.** A CVSG'd petition is redistributed after the SG files; the only paths to no further distribution are a dismissal by agreement or a withdrawal, both rare in a §1983 damages case with a live appeal already decided.
- **cvsg-increment 0.02.** Vacuous for this cell (the CVSG is on the docket); stated as the probability of a second invitation, which essentially never happens.
- **summary-disposition-route 0.12** conditional on a grant. The Court passed on a GVR when it was cheapest; the residual is an SG-recommended GVR after *Fowler*'s remand decision or some other intervening ruling.
- **dissent-from-denial 0.35** conditional on denial. Salient enough for a statement from Justice Alito or Justice Thomas, but a vehicle-based denial after an SG denial recommendation is usually silent.
- **big_case_score 0.6.** Stakes if decided: the standard of review for sex-based policies in every US jail and prison, with the federal BOP directly affected; narrower than *Skrmetti* or *B.P.J.* because bounded to the carceral setting.

## Where to discount me

- The SG-recommendation probability (0.6) is judgment, not data; the statpack publishes no cut conditional on the SG's eventual view. If the SG recommends denial, my number is too high by roughly 0.3.
- The historical follow-the-SG rates I quote are from general knowledge of the CVSG literature, not from a committed artifact, and are stated as approximations.
- Corpus freshness: I did not run `corpus-info`; the two `fedcourts query` pulls returned rows with `last_live_polled` up to 2026-09-11 and were not useful as priors (they ranked recent emergency applications first). The base rates come from the committed statpack, whose per-Term table runs through Term 2026.
- I did not read any prior run's prediction on this event, and nothing under `data/qp-topics/` was read.
