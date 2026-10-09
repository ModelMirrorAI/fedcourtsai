# Rationale for the numbers

**P(unqualified grant) = 0.04.**

## Anchor

This is an interim cell (`stage: interim`, `moment: response-filed`), so the salience band is not an input (`band: null`, as expected). The anchor is the statpack's "The interim docket (applications)" section. Its caption already calls the per-Term rates the ground of the scored base rate (not descriptive-only), so I read the estimator version. Application Term 2026; the pool is Terms 2016–2025 strictly before it. Only two of those rows carry parsed substantive applications: Term 2025 (226 resolved, 17 granted) and Term 2024 (75 resolved, 14 granted). Pooled: 31 / 301 = 10.3%, which clears the 50-resolved floor, so a published baseline exists and that is the yardstick. Term 2024 is 937-row unparsed, so the pool rests partly on a Term the poller reached only in part; I treat the 10% as a shape rather than a precise figure. The section's cautions apply: the escalation-signal counts are not as-at-prediction, and the predicted population is selected on the escalation ladder, so this cell sits higher on that ladder than the cohort behind the 10%.

## Adjustments from the anchor

Down, substantially, for these reasons, in order of weight:

1. **The applicant is a criminal defendant seeking a stay of a pretrial detention order from the Supreme Court.** The pooled 10% grant rate is dominated by government and institutional applicants (the emergency-docket grants of the last two Terms are overwhelmingly federal-government applications against lower-court injunctions). Private criminal defendants seeking release pending cert almost never obtain stays. The anchor overstates this applicant's chance.
2. **Cert likelihood is weak, and the SG says so with a precedent.** The opposition (read via the Court's docket PDF) cites Gray v. United States, No. 22-5113, where the Court denied review of the same standard-of-review split in 2022, and argues all circuits defer on facts and review law de novo, so the split is narrow. The Sixth Circuit's own stay-denial order (Judge Hermandorfer, quoted in the application) said the standard was not outcome-determinative here.
3. **Mootness vehicle problem.** Trial is now set for January 12, 2027 (applicant's October 6 letter). The SG argues a stay would do nothing to prevent the trial from mooting the issue, and that the applicant has delayed trial repeatedly to keep the issue alive, so the harm is self-inflicted. The Court has been receptive to the self-inflicted-harm framing on the emergency docket.
4. **Equities and facts.** The Sixth Circuit opinion (read via CourtListener, cluster 10946076) recites calls for armed resistance, a Signal exchange about killing a former official, fund-raising to evade law enforcement, failures to appear in state court, and a second District of Minnesota indictment for conspiracy to impede federal officers. Even Justices sympathetic to deference would hesitate to order release on this record.

Up, modestly:

1. **The Circuit Justice requested a response**, an affirmative act of attention. But a response call on a counseled application with a 44-page brief by a major firm is routine and is not strong evidence of a grant inclination.
2. **The applicant's October 6 letter** reports that the District of Minnesota has now ordered release in the second case, so the Sixth Circuit's order is the sole basis for detention; this removes one of the stay-denial order's reasons. Marginal.
3. The dissent below (Judge Bloomekatz) is detailed, and the split is genuine and acknowledged by Stern & Gressman. This bears on cert more than on the stay.

Net: about 0.04. I would not go below 0.02 because the Court does occasionally act in individual-liberty detention cases, and a four-Justice bloc might see the split as worth resolving; I would not go above 0.07 because the vehicle and equities arguments are, on this record, as strong as the emergency docket sees.

## Ladder claims

- **response-requested-increment = 0.02.** The record already shows a response requested (October 2) and filed (October 8), so this rung has fired and the harness will resolve it as vacuous. The number is nominal.
- **referral-increment = 0.65.** Not yet referred (`referred_to_court: false`). A response call by Justice Kavanaugh is usually followed by referral to the full Court, and that is my modal path. But a Circuit Justice can deny alone after reading a response, and on a weak application that happens often enough that I hold back from 0.8. The statpack's referral counts (25 of 88 substantive in 2026; 107 of 227 in 2025) are over all applications and right-censored, so they shape rather than set this.
- **amicus-increment = 0.08.** Zero amicus entries now. Resolution is likely within weeks, amici on application dockets are uncommon, and the natural amici (criminal-defense organizations) would file on the cert docket 26-391, which does not count toward this docket's entries. The political salience of the underlying prosecution keeps this above a few percent.

## Big-case score

0.3. The facts are newsworthy (anti-ICE speech during the Minneapolis enforcement operation, a self-described Antifa member, a DOJ press release), but the stay ruling is interim and the legal issue is an appellate standard-of-review question.

## What I read and what I could not

- Provisioned: snapshot `2026-10-08.json`, `context.json`, and `documents/application.txt` (the full 44-page stay application; `documents.json` reports it complete, not truncated).
- Retrieved (forward mode, unrestricted): the current 26A446 docket page (no disposition as of this run), the 26-391 cert docket (petition filed September 18; SG waived response October 2; distributed for the November 6, 2026 conference; motion to expedite pending), the SG's stay opposition PDF and the applicant's October 6 letter PDF from the Court's docket, the Sixth Circuit's published opinion via CourtListener, the SCOTUSblog case page, and the corpus `fedcourts query` for recent application priors.
- Not read: the applicant's reply, if any (none on the docket), and the Sixth Circuit stay-denial order itself (I relied on the application's and opposition's quotations of it).

## Where to discount me

The single biggest uncertainty is not the disposition but the **referral** path: whether Justice Kavanaugh acts alone or refers. On the disposition, the risk to my number is that the Court treats the liberty interest of a presumptively innocent detainee as weightier than I expect and uses the stay to signal interest in the split; I think that is unlikely on these facts, but it is the scenario in which 0.04 is badly wrong. The pooled baseline rests on two parsed Terms with uneven coverage, so my sense of the "population" rate is rough.
