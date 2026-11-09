# Reasoning — Allen v. Milligan, No. 26-117 (relist moment)

**P(grant family) = 0.90; predicted disposition: summary reversal.**

## What the record shows
- This is a **direct appeal** under 28 U.S.C. §1253 from a three-judge district court's
  preliminary injunction (N.D. Ala., May 26, 2026), filed as a jurisdictional statement.
  Snapshot `2026-11-09.json`. The Court has to dispose of the appeal on the merits: it can
  note probable jurisdiction, reverse or vacate summarily, or summarily affirm or dismiss.
  A cert denial is not an option. Only the first three count as a "grant" here
  (granted / summary-reversal / gvr).
- Per the jurisdictional statement (`petition.txt`, `questions-presented.txt`): in Spring 2026
  the Court decided *Louisiana v. Callais*, 146 S.Ct. 1131 (2026). It then vacated and remanded
  the earlier Alabama injunction in light of *Callais*. On remand the district court enjoined the
  2023 Plan again, on both §2 and intentional-discrimination grounds. **On June 2, 2026, this
  Court stayed that injunction** (*Allen v. Milligan*, 146 S.Ct. 1377). According to the
  appellants, the stay gave reasons: the lower court failed to presume legislative good faith,
  departed from *Callais*, and accepted alternative maps that did not meet the State's
  nonracial criteria. The State asks for summary reversal, citing *Abbott v. LULAC* (summarily
  reversed Apr. 27, 2026), or in the alternative for probable jurisdiction to be noted.
- Appellees moved to dismiss or affirm on Sept. 18. I did not have that motion's text (it was
  not provisioned), so my read of the opposition comes from the docket alone.
- Distributions: 10/16, 11/6 and 11/13 (count 3, band `high`). The case has gone through
  conferences without action and was distributed again. On a direct appeal with a stay
  already granted, that pattern fits a per curiam or a dissent being written.
- Companions 26-116 (Singleton, JS) and 26-118 (Caster, cert before judgment) are pending
  (`same-question.json`, score 1.0). They are near-identical filings and will almost certainly
  be disposed of together.
- The live docket on supremecourt.gov (checked once) shows nothing after the 11/9 distribution.

## Anchors
- `cert_anchor.rate` = 0.348 (band `high`, sal-v8, 10-Term lookback). The relist-count cut
  for 2 and 3+ buckets gives a grant family (granted + gvr) of about 37–41%.
- Both anchors describe discretionary cert petitions. This case is a mandatory appeal in which
  the Court has already stayed the judgment below. A stay requires a fair prospect of
  reversal, and here the stay order apparently said the district court misapplied *Callais*.
  That signal is far stronger than any cut in the statpack. In mandatory appeals, a summary
  affirmance after a stay was granted is very rare.

## Adjustments and uncertainty
- Main risk for an ungranted outcome: the Court summarily affirms, or dismisses as moot or for
  lack of a final question. I see no mootness route. The injunction is preliminary but governs
  future elections, so the November 2026 election passing does not moot it. If mootness were
  argued, a Munsingwear vacatur would still score as a grant (gvr). I put about 10% on an
  ungranted outcome.
- Split within the grant family: summary reversal or vacatur (about 60%) vs. noting probable
  jurisdiction for plenary review (about 40%). Repeated relisting suggests something is being
  written. The *Abbott v. LULAC* precedent from the same Term, and a stay order that already
  laid out the errors, both point to a summary disposition. The case is large enough that the
  Court may want argument instead.
- Corpus `query` calls returned generic priors only. The `--docket-number` lookups returned
  usage text. Neither moved the number.
- Where I could be wrong: I did not read the motion to dismiss or affirm, and I rely on the
  appellants' characterization of the stay order.
