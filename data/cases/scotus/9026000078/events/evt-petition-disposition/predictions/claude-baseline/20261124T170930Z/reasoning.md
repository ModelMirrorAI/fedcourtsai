# Reasoning — Hunt v. Florida, No. 26-78 (cert, distribution moment)

**P(any grant) = 0.18; call: denied.**

## What I read

Snapshot `2026-11-24.json`; `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt` and `questions-presented.txt` in full; `context.json`; `same-question.json`; `related/26-76.json` (Jackson v. Florida, relation `vided-amicus`, one shared brief). I did not read `appendix.txt` beyond relying on the parties' consistent descriptions of the Florida Supreme Court's opinion. No `decision-below.txt` was staged (state-court case).

Jackson is a real companion, not a text-match accident: the petition says the Florida Supreme Court decided the two together, both were filed the same day by the same counsel, and the BIO cross-references No. 26-76. I treat the two dockets as moving in tandem.

## Anchor

- `context.band` = `elevated` (sal-v9), `cert_anchor.rate` = 0.248. That is the scored yardstick and my starting point.
- `cert_amicus_line.rate` = 0.397 (arm `some`, n=774). I weigh this lightly: the single amicus brief here is a brief filed in both cases ("VIDED"), and it mainly supports the Jackson Sixth/Eighth Amendment question.
- The statpack's band table is headed sal-v8 while my context is sal-v9, so per the prompt that table is not an anchor for my band; I used the frozen `cert_anchor` and noted the mismatch in `flags.json`. For reference, the private-petitioner class floor (`baseline` reached) runs roughly 5% across prior Terms.
- Cross-checks from the statpack (shape only): relist bucket 1 (which is where a two-distribution docket sits) resolves to a grant family of about 13.6% (n=2,546); capital-marked paid petitions about 13.8% (n=174); Supreme Court of Florida petitions overall are 97.6% denied (n=613, mostly IFP).

## Adjusting down from 0.25

1. **The second "distribution" is a reschedule, not a relist.** The docket shows distribution for 12/4, "Rescheduled" the same day (the reply arrived that day), then distribution for 12/11. No conference has yet considered the petition. The elevated band's rate counts true relists alongside reschedules, so it overstates this docket's position.
2. **No real split on the lead question.** On ex post facto, the petition concedes its Louisiana (1899) and Oregon (1934) points are not a conventional conflict, and the parole-board cases (South Carolina, Massachusetts) are an analogy at a higher level of generality. The BIO's "no split" argument is its strongest.
3. **Florida-only and time-limited.** The ex post facto question reaches about a dozen sentenced defendants plus some dozens of pending prosecutions for 2017–2023 crimes.
4. **The Court's recent record in capital cases.** A majority has been unreceptive to new capital-sentencing rules, and McKinney v. Arizona (2020) cuts against the Sixth Amendment unanimity question that this petition shares with Jackson. Justices who would vote to grant may hesitate without a fifth vote on the merits.

## Adjusting up from the ~5% floor

1. **Counsel and presentation.** Stanford's Supreme Court clinic (Jeffrey Fisher) for petitioner, Seth Waxman for amici; a deliberately paired, clean, direct-review vehicle. Florida took three extensions and filed a full BIO through its Solicitor General.
2. **The ex post facto claim is strong on the merits and the vehicle is unusually clean.** The jury voted 10-2; under the law at the time of the crime that vote required a life sentence. The Florida court's "virtually guarantee" gloss on Peugh is hard to defend, and the State's BIO does not defend it, shifting instead to Collins/Dobbert. Carmell's reasoning about lowering the prosecution's burden has appealed to Justices across the usual lines.
3. **Kian v. Florida (No. 25-6623), granted June 15, 2026** on whether the Sixth Amendment requires a 12-person jury, shows at least four Justices currently interested in jury-right questions out of Florida. Both sides cite the Kian briefing. This also opens a hold-then-GVR path, though I think that path is narrow because Kian concerns jury size at the guilt phase, not sentencing unanimity or retroactivity.
4. **Stakes.** Florida's 8-4 rule is the least demanding in the country, and the pair of petitions is the first well-lawyered test of it.

Netting these, I land a bit below the band anchor at 0.18. Most of that mass is a plenary grant (alone on QP2, or together with Jackson); a small part is a hold for Kian followed by a GVR.

## Other claims

- **relist-increment 0.58.** Two distributions on the docket. A further distribution follows from any of: a true relist after 12/11 (the Court's practice before any grant, and usual when a dissent from denial is being written), another reschedule (this pair has already been rescheduled repeatedly), or a hold for Kian and redistribution after it is decided. A straight denial on the first order list after 12/11 is the main way it fails.
- **cvsg-increment 0.02.** State criminal case with no federal interest; a CVSG would be very unusual.
- **summary-disposition-route 0.12** (conditional on a grant). The only realistic cert-order route is a GVR after Kian; a summary reversal on a capital sentencing statute is unlikely.
- **dissent-from-denial 0.40** (conditional on denial). Justice Sotomayor has written repeatedly on nonunanimous and judge-imposed death sentences, and a 10-2 death sentence that the prior law would have barred is the kind of case that draws a statement. I hold this under one half because any writing may be attached to Jackson alone, and because many capital denials draw nothing.
- **order-writers.** Unconditional per-Justice numbers, consistent with roughly 0.8 × 0.40 ≈ 0.32 that someone writes: Sotomayor most likely, then Jackson, then Gorsuch (jury-right and Ex Post Facto interest).

## Uncertainty and where to discount me

- I could not see Jackson's BIO, petition or reply; my view of the Sixth/Eighth Amendment question's strength rests on this petition's summary and the BIO's section I.
- The companion snapshot shows Jackson distributed for 12/4 and rescheduled, with no 12/11 entry yet; the corpus row for 26-76 reports a distribution count of 3, which suggests it has since been set for 12/11 as well, but I did not confirm the conference date.
- I do not know Kian's argument date. If Kian has been argued and the Court is inclined to rule broadly on the jury right, a hold becomes more likely than I have priced.
- Reading reschedules is noisy: here they look administrative (pairing the two petitions, then the reply's timing), but a reschedule can also mean a Justice has asked for time.
- `big_case_score` 0.6 reflects stakes if decided, not the odds.
