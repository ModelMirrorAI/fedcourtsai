# Reasoning: Allen v. Singleton, No. 26-118 (relist moment)

**P(grant family) = 0.85; predicted disposition `gvr`. I expect a Munsingwear-style vacatur on mootness grounds, or failing that a summary reversal or a noted probable jurisdiction.**

## Posture
This is a **direct appeal** under 28 U.S.C. §1253 from a three-judge district court (N.D. Ala.), not a discretionary cert petition. The Court must dispose of it on the merits somehow: note probable jurisdiction, summarily affirm or reverse, vacate and remand, or dismiss. On May 26, 2026, on remand after *Louisiana v. Callais*, 146 S.Ct. 1131 (2026), the district court again preliminarily enjoined Alabama's 2023 congressional plan under §2 and the Fourteenth Amendment. It included an intentional-discrimination finding. On June 2, 2026 the Court stayed that injunction in full, in a reasoned order (*Allen v. Milligan*, 146 S.Ct. 1377) saying the panel failed to presume legislative good faith and departed from *Callais*. Per the petition (`record/documents/petition.txt`, statement and reasons sections), the State asks for summary reversal and cites *Abbott v. LULAC* (summarily reversed Apr. 27, 2026).

## The decisive fact: mootness
I read the appellees' motion to dismiss (Sept 18, 2026) from the Court's docket (forward-mode retrieval; not provisioned). It says the injunction "by its own terms, applies only to Alabama's November 3, 2026, congressional general election." That election has now been held under the 2023 Plan, because of the stay. The appellees ask for dismissal as moot, citing *Christian Civic League v. FEC*, 549 U.S. 801 (2006). The appeal is therefore very likely moot now. The docket timing fits: the case was distributed for 10/16, re-distributed on Nov 2 for 11/6, and on Nov 9 for 11/13. That looks like the Court waiting out the election before acting.

When an appellant's appeal becomes moot through happenstance, the Court's usual practice is *Munsingwear* vacatur. That is especially so when the order below contains an intentional-discrimination finding against a State that the Court has already signalled is likely wrong (the stay opinion). The prompt classes a mootness/Munsingwear vacatur as `gvr`. The corpus labels the prior round of this same litigation (No. 25-273, vacated and remanded in light of *Callais*) as `gvr`, so the label mapping looks consistent.

## Probability split
- Vacate and remand (Munsingwear / with instructions to dismiss as moot): ~0.62.
- Summary reversal (if the Court finds a live controversy, e.g. through a continuing effect of the findings): ~0.08.
- Note probable jurisdiction / plenary review: ~0.15.
- Plain dismissal as moot without vacatur, as the appellees ask (non-grant): ~0.12.
- Summary affirmance: ~0.03.

## Anchors
- `cert_anchor.rate` = 0.348 (band `high`, sal-v8, 10 lookback Terms). The statpack's relist-count cut, pooled for buckets 1+: about 8.3+5.2% grant family at 1 relist, about 41% at 2, about 37% at 3+. This docket shows 3 distributions.
- These anchors describe *discretionary cert*. A mandatory appeal is a different population: the Court must decide it, and "deny" isn't an option. That, plus the stay opinion and the mootness posture, is why I sit far above the anchor. The big discount a reader should apply: the scorer's label for a "dismissed as moot" order vs. a "vacated and remanded" order. If the Court just dismisses, I lose badly.

## Uncertainty
- Whether the State's reply asked for Munsingwear vacatur. I didn't read the reply (Sept 29), but vacatur is the standard request.
- Companion dockets 26-116 (Caster, cert before judgment) and 26-117 (Milligan), listed in `record/same-question.json` with score 1.0 and pending, share the same distribution path. I expect a common disposition. Their status as of the cutoff is pending, so they add no outcome information.
- Provisioned documents used: questions-presented.txt and petition.txt (truncated at the cap). The appendix is present but I only skimmed it. No brief in opposition is staged, because the appellees filed a motion to dismiss instead. I fetched that motion from supremecourt.gov.
