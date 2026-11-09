# Reasoning — Rivera-Perez v. Flowers, No. 26-396 (response-requested moment)

**P(any grant) = 0.32; predicted disposition: denied (but with a substantial grant chance).**

## Inputs used
- Snapshot `record/snapshots/2026-10-13.json` (forward mode, date cut 2026-10-14). Docket: paid petition filed Sep 17, 2026 (Federal Defenders Supreme Court Project, with Haynes Boone); SG (federal respondents) waived Sep 30; distributed for the Nov 6, 2026 conference on Oct 7; petitioner's letter Oct 9; **Response Requested Oct 13 (due Nov 12)**. One distribution; no CVSG (and none is possible in substance—the United States is already the respondent).
- `questions-presented.txt`: whether First Step Act time credits can be applied under 18 U.S.C. 3632(d)(4)(C) to reduce a term of supervised release.
- `petition.txt` (truncated at the cap, appendix cut): CA2 published 2-1 decision (171 F.4th 196; Jacobs concurring, Nathan dissenting) holding credits cannot reduce supervised release, and so ordering dismissal as moot. Petition pleads a square split: CA2 + CA6 (*Hargrove v. Healy*, 155 F.4th 530, cert. denied No. 25-818, Apr. 20, 2026), with unpublished CA4/CA11 agreeing, versus CA9 (*Gonzalez v. Herrera*, 151 F.4th 1076), where the government did not seek rehearing. In the *Hargrove* BIO the SG acknowledged the conflict but urged percolation, citing this very litigation. Petition argues this is a cleaner vehicle than *Hargrove* (eligibility undisputed; the question is outcome-determinative of mootness).
- `party-letter.txt`: only the letterhead extracted (1 page, `empty_text: false` but no body text); I cannot tell what the Oct 9 letter said and draw nothing from it beyond its timing four days before the response request.
- No BIO exists yet (response due Nov 12); I do not infer its content.

## Anchor and adjustments
- `cert_anchor.rate` = **5.2%** (band `baseline`, sal-v8, 10-Term lookback). That is the population I am scored against.
- Called-for response: no committed table conditions on it. My judgement: a call for response after a waiver lifts a paid petition several-fold over the baseline floor, but most are still denied.
- Strong upward specifics: (1) an acknowledged, published, square 2–1 (plus unpublished) circuit split, with the government itself having conceded the conflict and asked only for percolation—percolation that this case now supplies; (2) a recurring federal question affecting tens of thousands of prisoners, with the United States as party on one side of a split it lost in CA9 and won in CA2/CA6 (a non-uniform federal-sentencing administration problem the SG typically cares about); (3) a published opinion with a dissent; (4) institutional Supreme Court counsel; (5) the Court's track record of taking FSA interpretation cases (Terry, Concepcion, Pulsifer, Hewitt, and *Maxwell v. Dinis*, No. 25-5930, argued Nov 2, 2026).
- Downward: (1) the Court denied *Hargrove* on the same question only seven months ago at its first conference; (2) the SG will likely oppose again—possibly arguing mootness/vehicle or that the split is shallow or that BOP practice limits the stakes; (3) the base rate for even response-requested paid petitions remains low.
- Hold/GVR channel: *Maxwell* (cognizability of FSA-credit claims under §2241) is pending. Corpus shows a court-appointed amicus defending the judgment below there, consistent with the government agreeing with the petitioner on cognizability, which lowers the chance the SG presses a habeas-vehicle objection, but a hold for *Maxwell* followed by a GVR remains possible and counts as a grant.
- Net: 0.32. Below 0.5 because the most likely single path is still a denial after an SG opposition, as happened in *Hargrove*; well above anchor because the split is now deeper and the government's own percolation argument has been answered.

## Uncertainty
The SG's response is the key unknown; an acquiescence would push this above 0.6, a vehicle objection (e.g., mootness tied to petitioner's status) toward 0.15. I did not retrieve the live docket beyond the snapshot. The petition text is truncated (appendix cut), so I relied on the petition's description of the CA2 opinion.
