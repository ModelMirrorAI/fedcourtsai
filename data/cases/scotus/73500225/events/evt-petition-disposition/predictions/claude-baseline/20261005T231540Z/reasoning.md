# Why 0.18, and not another number

## What I read

Provisioned inputs: `record/snapshots/2026-10-05.json`, `record/context.json` (mode `forward`, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, term 2025, `signals_observable` true), `event.yaml` (stage cert, moment distribution), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (265 pages, text truncated but the full petition body through the conclusion was present; the truncation falls inside the appendix), and `brief-in-opposition.txt` (43 pages, complete). None was `empty_text`.

## The anchor

Band is `elevated` under `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table, so that table is my anchor. Pooling the bracketed `reached` figures over the Term rows strictly before this case's Term (2017 through 2024, all eight prior rows the table renders):

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

Weighted pool: roughly 484 grant-family outcomes over 2,810, about **17.2%**. That is the yardstick my skill is scored against, and I ended within a point of it after adjustments that largely cancel.

Cross-checks from the paid-scored-segment cuts: relist bucket 1 (where the stored `dist-v2` count places this petition, though the second entry is a pre-consideration reschedule, not a relist) shows granted 8.2% + gvr 5.1% = 13.3%; the CVSG `none` bucket shows 4.0% + 2.3%; the CA4 origin cut shows 1.3% + 1.2% over all petitions. The `elevated` terminal-band row shows 6.6% + 3.6%. The caption class is private (gun-rights organizations and individuals against Maryland officials), so no class-floor fallback was needed.

## Adjustments up

- **Vehicle.** Final judgment after cross-motions for summary judgment (the petition stresses this against the preliminary-injunction posture of Antonyuk and Wolford), a published Fourth Circuit opinion (165 F.4th 194) covering eight categories of restriction, and a lengthy partial dissent by Judge Agee that frames exactly the methodological question (Founding era versus later laws) the Court might want.
- **Salience of the question.** Post-*Bruen*, the scope of "sensitive places" is the largest unresolved Second Amendment issue; the Court has taken roughly one Second Amendment case per Term (Rahimi, VanDerStok, Wolford and Hemani) and this is the obvious next candidate.
- **A live GVR hook.** *Wolford v. Lopez* (June 25, 2026, 6-3, Alito, J.) postdates the Fourth Circuit's January 2026 decision, and the petition expressly asks for a GVR in the alternative. The Court has a pattern of GVR-ing pending Second Amendment petitions after each major decision (after *Bruen* in 2022 and after *Rahimi* in 2024).
- **The reschedule.** Pulling the petition before the long conference and redistributing it for October 9 is deliberate handling, consistent with pairing it with Maryland's own petition No. 25-1206, rather than a routine deny-list entry.
- Counsel of record is a repeat Supreme Court Second Amendment advocate (Cooper & Kirk), and an amicus brief supports the petition.

## Adjustments down

- **Revealed reluctance on this exact question.** In October 2025 the Court granted *Wolford* only in part, taking the private-property default rule and leaving the sensitive-places questions behind. It denied *Antonyuk v. James* (June 2025) and *Schoenthal v. Raoul* (April 6, 2026, a transit-ban final judgment from the Seventh Circuit). Schoenthal was denied while *Wolford* was pending rather than held, which tells me the Court did not regard *Wolford* as bearing on sensitive-places rulings; that cuts directly against the GVR route here.
- **The BIO's percolation argument has force.** The en banc Third Circuit has *Koons* under submission (the panel opinions were vacated in September 2025; CourtListener shows no en banc decision as of my retrieval), the Second Circuit has just issued *Christian v. James* (May 2026), and the Fifth and Seventh Circuits have spoken only narrowly. The BIO also fairly shows that the claimed splits reduce to three locations (transit, health care, assemblies) and that Maryland's demonstration statute is idiosyncratic (only Alabama has a comparable one).
- **Messy vehicle for plenary review.** A single broad question spanning eight location categories, several decided on independent grounds (government buildings and schools on *Heller*/*Bruen* dicta, transit on the proprietary doctrine plus history), gives the Court a lot to work around; granting would almost certainly require reformulating the question.
- **The Wolford majority was 6-3 on a narrow issue.** Nothing in the syllabus or the lineup suggests the majority wanted to reach sensitive places, and Justice Kagan and Justice Jackson dissented even on the default rule.

Net: I split the grant family as roughly 0.09 plenary grant and 0.09 GVR, for P(any grant) = 0.18, essentially at the anchor. `predicted_disposition` is `denied` because denial remains the single most likely outcome by a wide margin.

## The other claims

- **relist-increment 0.50.** The petition has never been considered at conference, so from here the forward hazard is that of a first-consideration petition with strong salience: a GVR decision, a plenary grant, or a dissent from denial would each usually produce at least one relist, and the reschedule already shows non-routine handling. The statpack's relist cut buckets by terminal count and cannot be read as this hazard; among paid scored petitions about a quarter are ever relisted, and I roughly double that for this case.
- **cvsg-increment 0.04.** No federal party, no federal statute, and no CVSG practice in the recent state carry cases.
- **summary-disposition-route 0.50.** Conditional on a grant, the GVR-in-light-of-*Wolford* route and plenary review are close to even; the per-Term cert tables put the GVR share of the grant family around half in the Terms where the label is populated, and the case-specific arguments (an express GVR request and a pre-*Wolford* decision below, against the Schoenthal denial and *Wolford*'s narrow holding) roughly cancel.
- **dissent-from-denial 0.45.** Justice Thomas has dissented from denial in several post-*Bruen* cases (Snope v. Brown and Ocean State Tactical in 2025, the former with a Kavanaugh statement); a comprehensive final-judgment vehicle with a strong dissent below makes a separate writing more likely than for the ordinary denial, but not a majority of the time.

## Uncertainties and where to discount me

- I could not confirm whether Maryland's companion petition No. 25-1206 is distributed for the same October 9 conference: CourtListener holds the docket shell (docket id 73281690, not terminated) but no entries, and the corpus service returned no open events for it. My reading of the reschedule as pairing is inference from the snapshot's "Linked with 25A1140" note, the petition's jurisdictional statement, and timing, not from the companion docket itself.
- I could not verify whether the Antonyuk or Schoenthal denials carried dissents; that would move `dissent-from-denial` by perhaps 0.10 either way.
- Whether the Court issued any GVRs in light of *Wolford* in its end-of-Term cleanup is a direct test of the GVR route; a name scan of the 80 most recent GVR rows in the corpus surfaced no Second Amendment case, which weakly supports the lower GVR share, but the scan was by caption only.
- *Wolford* is the decisive forward signal and predates the snapshot; it is legitimate forward context, not leakage, and it is flagged as such in `flags.json`.
- I did not read the Fourth Circuit opinion beyond the parties' characterizations and the appendix excerpts inside the petition text.
