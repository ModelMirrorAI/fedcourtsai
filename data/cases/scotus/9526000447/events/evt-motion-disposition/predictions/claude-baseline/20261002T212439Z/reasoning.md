# Why these numbers

**P(unqualified grant) = 0.04; predicted disposition `denied`.**

## What I read

- `record/snapshots/2026-10-01.json`: a single proceedings entry, "Application (26A447) for a stay, submitted to Justice Gorsuch" (Sep 30 2026). Lower court: Supreme Court of New Mexico, No. S-1-SC-41552. No response requested, no referral, no amici. The snapshot is cut at `arrival-position` (anchor index 0), so that submission entry is the whole baseline.
- `record/documents/application.txt` (176 pages, `truncated: true`, `empty_text: false`): the application body is complete through the signature block; the truncation falls in the appendix, so I read the full argument. The appendix fragment I saw was the New Mexico Supreme Court's August 20, 2026 denial and the superintending-control petition's table of contents.
- `record/context.json`: `mode: forward`, `band: null`, `term: 2026`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, `signals_observable: true`. Band is null as the interim norm expects, so no cert band anchoring and no caption-class floor applies.
- `metrics/statpack.md`, "The interim docket (applications)" section. Its caption already calls the per-Term rows the scored base rate's grounding, so I read the current estimator caption, not the older descriptive-only one.

## The anchor

Application-Term 2026, so the pool is Terms 2016–2025. Only two of those Terms have parsed substantive rows: 2025 (17 granted / 226 resolved, unparsed 0) and 2024 (14 / 70, with 972 of that Term's 1297 applications unparsed). Pooled: **31 / 296 = 10.5%**, which clears the 50-resolved floor, so a published baseline exists and that is what this cell is scored against. Two cautions from the section: the 2024 Term is only partly parsed, and the 2024 vs 2025 spread (20% vs 7.5%) is more likely coverage than behaviour.

## Adjustments from the anchor, and why so far down

The pooled 10.5% is over every substantive application, and in recent Terms the grants are dominated by applications from the federal government and states against lower-court injunctions, plus a handful of capital and election matters. This application is in the weakest stratum of that population on every dimension I can read from the record:

1. **Private civil litigant, interlocutory state discovery order.** The Court essentially does not stay state-court discovery or sanctions proceedings between private parties pending cert. The nominal respondent is a state trial judge; the real parties are wrongful-death plaintiffs.
2. **Finality under § 1257.** The "final judgment" is a summary denial of a petition for superintending control. The application's own authority (*Fisher*, *Madruga* footnotes) is thin for treating that as final when the underlying order is an interlocutory discovery order and the application concedes that appeal from a contempt order is a "familiar procedure." A Circuit Justice will see "reasonable probability of certiorari" as failing here.
3. **No split; novel theory.** The Fourth Amendment particularity attack on a Rule 11-706 examiner is creative and well-briefed but cites no court that has accepted it, and the order below is an unreported discovery ruling. The application's "vehicle" pitch is that the issue is rarely litigated, which cuts against cert as much as for it.
4. **Timing.** The show-cause hearing was set for October 1, the day after submission. Any administrative-stay request was probably overtaken by events, and the plaintiffs have asked the trial court to defer sanctions until this Court acts on the forthcoming petition (application at n.1), which drains the irreparable-harm showing.

Factors pulling up, which keep me off the floor: sophisticated counsel; a substantive constitutional claim pitched at Justice Gorsuch's own Fourth Amendment writing (*Chatrie* concurrence, *Jones*); a corporate applicant that will actually file the petition it promises. Those make a response request or referral plausible but do not make a stay plausible. Net: 0.04, roughly a third of the pooled baseline's weakest-looking slice.

## The three increment claims

All from the frozen state: no response requested, not referred, zero amicus entries.

- **response-requested-increment 0.25.** The statpack's response-requested count (64 of 367 substantive, pending-inclusive and right-censored) is about 17% as shape, not as a conditioned rate. I move up a little because the application is serious enough that a Circuit Justice might want the plaintiffs' account of the October 1 hearing before acting, but a denial on finality needs no response.
- **referral-increment 0.40.** The section shows referral in 178 of 367 substantive applications (2025 Term: 107 of 227), so referral-and-deny is a common shape. I discount below that because single-Justice denials of private civil-litigant stays are routine and this one reads as a quick denial.
- **amicus-increment 0.08.** No amici at arrival, a short expected life, and a discovery dispute with no organized constituency beyond possibly a trucking association.

## Uncertainty and where to discount me

- I did not observe the outcome of the October 1 show-cause hearing or anything after the submission entry; CourtListener returned no record for this docket (searching both the docket id and the docket number), so the forward retrieval added nothing about this case. The forecast rests on the application and the pooled base rate.
- The 10.5% baseline rests on two Terms, one partly parsed; if the true unconditioned rate for private civil applicants is nearer 2–3%, my 0.04 is close to baseline rather than below it.
- Resolver risk: if Justice Gorsuch were to enter a brief administrative stay, the interim resolver could read a later "stay denied" as the terminal entry (correct) or latch the administrative grant (incorrect). I have flagged this as an `ambiguous-event` note rather than priced it; my 0.04 is P(an actual unqualified grant).
- The corpus `query` for granted applications ranked extension grants first and surfaced no substantive grants in its ten rows, so it gave me shape (the docket is dominated by routine extension grants) rather than comparable priors; the denied query returned eight recent substantive denials, several referred-and-denied within days, consistent with the shape I forecast.
