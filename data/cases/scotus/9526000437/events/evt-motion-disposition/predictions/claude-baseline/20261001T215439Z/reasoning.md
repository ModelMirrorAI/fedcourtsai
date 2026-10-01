# Why these numbers

**P(unqualified grant) = 0.01; predicted disposition `denied`.**

## What the record shows

The provisioned snapshot (`record/snapshots/2026-09-29.json`, cut `arrival-position` at anchor index 0) carries a single proceedings entry: "Application (26A437) for an injunction pending appeal, submitted to The Chief Justice." dated Sep 28 2026. The caption is *In Re Nikolay M. Valov, Applicant*; counsel of record is the applicant himself at a residential Alexandria, Virginia address, with no prisoner id and no capital-case marking. The lower court is the Circuit Court of Virginia, Mecklenburg County, case CL25-2218 — a county trial-level civil matter, with no state appellate court identified. `context.json`: mode `forward`, `band: null`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, `term: 2026`, `signals_observable: true`. The snapshot's `DocketedDate` reads September 30, 2026, a day after the cutoff; that is a header field rather than a proceedings entry, so it does not disturb the arrival-position baseline, and I did not treat it as information beyond the snapshot.

The one provisioned document, `application.txt`, is recorded in `documents.json` as `empty_text: true` (a 73-page scanned PDF with no text layer, filename marked `scan`). I therefore have **no view of the application's substance** — what is being appealed, what the injunction would restrain, or what the claimed federal question is. That is a content-unavailable input, not an absent one, and the forecast rests on the docket shell plus priors.

## Anchor

The committed `metrics/statpack.md` carries "The interim docket (applications)". For an application-Term 2026 cell the scored pool is application-Terms 2016–2025, strictly before mine. The table's substantive resolved counts in that window are Term 2025: 226 resolved, 17 granted, and Term 2024: 70 resolved, 14 granted (Terms 2016–2023 are entirely `unparsed`, 0 resolved). Pooled: **31 / 296 = 10.5%**, which clears the pre-registered floor of 50, so that is the published baseline. The section's caption describes the rate as grounding the scored base rate (not the older descriptive-only wording). Caveats the caption attaches and that matter here: Term 2024 is only partly parsed (972 of 1297 applications unparsed), and the pooled cohort is unconditioned on the escalation ladder while predicted cells are selected on it.

## Adjustments from the anchor

I move far below the 10.5% pool, to 0.01, because that pool is dominated by a population this application is not in:

- **Every granted substantive application `fedcourts query` returned** (14 rows, Terms 2025–2026) was filed by a government or institutional applicant represented by counsel — the Solicitor General, state secretaries of state, a warden, pharmaceutical companies, a national party committee — and all 14 had been referred to the full Court, most with a response requested and several with multiple amici. This application sits on none of those rungs and is pro se.
- **The denied substantive priors** include the shape this record matches: pro se or small-party civil applications (e.g. *Givey v. Givey*, *Robalino v. U.S. Bank*, *Arsenis v. M&T Bank*, *Evans v. Federal Home Loan Mortgage*, *Golden v. Transunion*, *Chen*, *Randolph v. Bath & Body Works*, *Aderemi*, *Cheleden*), each denied by the Circuit Justice within zero to seven days of filing with no response requested, no referral, and no amici. The referrals among the denied rows are overwhelmingly capital-case stay applications, which are referred as a matter of course and are not this case.
- **Legal posture.** The application seeks an injunction pending appeal from a *county trial court* civil case, with no decision of Virginia's highest court identified. The Court's jurisdiction over state cases runs to final judgments of the highest state court in which a decision could be had, and an injunction from a single Justice requires a right that is indisputably clear. On the record disclosed, the application is defective in jurisdiction before it is weak on the merits.
- An *In re* caption and a county "CL" (civil law) docket number suggest a self-initiated civil matter; the applicant's Alexandria address against a Mecklenburg County court suggests a property, estate, or similar dispute, but I cannot read the application and I treat this as unknown.

I do not put the number at zero because the application's content is unread and the Court's interim docket occasionally surprises, but a conditional-on-pro-se-state-trial-court grant rate is a small fraction of one percent in my judgment, and 0.01 is the rounded honest figure.

## The three increments

- **response-requested-increment 0.03.** None requested on the record. Among the comparably shaped denied priors, a response was requested in none; requests cluster on government and institutional applications. Small residual for the Chief Justice wanting the opposing side's account before acting.
- **referral-increment 0.10.** Not referred on the record. The Chief Justice ordinarily disposes of pro se civil applications alone. A referral is the likeliest of the three steps because some Circuit Justices refer broadly and because a referral costs nothing, but the denied-prior pattern for this shape is non-referral, so I keep it low. A previous claude-baseline interim cell on a pro se mandamus-posture application put this at 0.35; I think that was too high for the pro se civil shape and have not anchored on it.
- **amicus-increment 0.01.** Zero entries now; no plausible filer.

## Uncertainty and where to discount me

- The application text is unavailable (`empty_text: true`), so I cannot rule out that the state proceeding touches a live federal question (election, land use, free-exercise) that would raise stakes and the referral probability. If a maintainer can read the scan, the referral and big-case numbers are the ones most sensitive to it.
- The pooled baseline rests on two parsed Terms, one of them 75% unparsed; the 10.5% figure is a coarse yardstick, and my distance from it is driven by the applicant class rather than by the pool's precision.
- CourtListener retrieval (four searches) found no docket, opinion, or RECAP record for this applicant, so there is no litigation history to read habits from; the Supreme Court application docket itself is not on CourtListener, so I could not check for an already-landed disposition — nothing I saw indicates the matter is decided.

I did not read `data/qp-topics/`, did not seek this case's disposition, and have no prior knowledge of this applicant or matter.
