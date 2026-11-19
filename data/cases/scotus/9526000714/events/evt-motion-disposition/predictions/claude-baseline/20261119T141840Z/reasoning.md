# Reasoning: scotus/9526000714, evt-motion-disposition (interim, arrival)

**Probability 0.84** that the requested stay is granted in whole or in part, conditional on the application not being dismissed or denied as moot.

## What I read
- Snapshot `2026-11-18.json`: a single entry, "Application (26A714) for a stay, submitted to Justice Kagan." Federal applicants (Secretary of Homeland Security, DHS, United States), Ninth Circuit No. 25-5724. `context.json`: forward mode, band null (normal for interim), no response requested, no referral, zero amicus briefs.
- `application.txt` (28 pages, not truncated). The appendix was filed as a separate PDF and was not staged, so I have only the government's account of the orders below and of the respondents' position. I did not read any opposition; none exists on the record yet.
- I did not retrieve the live docket or any web material.

## Base rates
- Statpack interim section, "Substantive applications by applicant class" (the scored pool for OT2026, ten prior Terms, finer counts): whole pool 11.7% (156/1337), which is the yardstick. Federal applicant, non-capital cell: 68.4% (39/57); federal margin 70.8% (46/65). I read the federal/unmarked cell as my starting point; the caption class (federal) is correct here.
- From about 0.68 I moved up to the mid-0.80s on case specifics, then held back for the withdrawal path below.

## Case specifics pushing up
- Corpus lookups confirm the application's history: 24A1059 (granted May 19, 2025) and 25A326 (granted Oct. 3, 2025) were both stays for the government in this same case, the second against this very summary-judgment order; 26-48 shows a GVR on Oct. 5, 2026.
- The application says *Mullin v. Doe* (June 2026) held that 8 U.S.C. 1254a(b)(5)(A) bars all non-constitutional challenges to TPS terminations, and that respondents conceded below that their statutory challenges to the termination are no longer cognizable. I cannot verify *Doe* independently (it postdates what I know, and I did not look it up), so I rely on the application's characterisation, discounted slightly because it is one side's brief. The GVR in 26-48 with respondents' agreement is consistent with it.
- The judgment below rests only on APA claims; the equal-protection claim was not part of the summary judgment. That leaves respondents arguing that the vacatur claim survives and affects the termination's effective date, which looks weak against a termination that would have taken effect by Oct. 3, 2026 in any case.
- The Court has twice found the equities favour the government on the same order.

## What holds the number below 0.9
- **Withdrawal risk.** The Ninth Circuit has an administrative stay in place through Nov. 20 and supplemental briefing on *Doe* completed Nov. 10. If it grants a stay or rules for the government before the Court acts, the Solicitor General would likely withdraw the application. A withdrawal scores as ungranted, whereas a dismissal as moot leaves the scored set. I put roughly 15 to 20% on the Ninth Circuit acting first, and assume perhaps half of that resolves as a withdrawal or non-moot denial rather than a moot dismissal.
- A merits denial (about 3 to 5%): possible if the respondents show the vacatur claim has independent force or that the constitutional claim supports interim relief, but I see little sign of that.
- One-sided record: I have only the government's filing.

## Other claims
- `response-requested-increment` 0.88: a response is routine on a government stay application of this weight; the residual is the Ninth Circuit mooting it first or the Court acting without one.
- `referral-increment` 0.82: both earlier applications were decided by the full Court; the residual is withdrawal or a single-Justice disposition.
- `amicus-increment` 0.50: the earlier rounds drew four briefs each per the corpus rows, but this round is compressed and the issue narrower; submitted briefs count.
- `order-writers`: Jackson highest (0.30) given her record of dissenting in this litigation and on the interim docket generally; Sotomayor 0.10; others low. *Doe* being a merits holding reduces the incentive to write.

## Where to discount me
The whole forecast depends on the application's description of *Doe* and of respondents' concession. If either is overstated, the grant probability should be lower, though the two prior stays alone would still support a number well above the federal-applicant base rate.
