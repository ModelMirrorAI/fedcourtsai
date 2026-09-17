# Rationale for the numbers

**P(grant) 0.015; predicted disposition: denied.**

## What I read

Provisioned inputs: the snapshot `record/snapshots/2026-09-15.json`, `record/context.json`, `questions-presented.txt`, `petition.txt` (29 pages, full text), and `brief-in-opposition.txt` (16 pages, full text); `documents.json` reports none as empty or truncated. The reply brief (June 15, 2026) is on the docket but was not provisioned and I did not retrieve it.

The docket: a paid petition (`sJsonCaseType: Paid`) from the Court of Appeals for the Armed Forces, which denied review without opinion on January 6, 2026, below a nonprecedential Air Force Court of Criminal Appeals opinion. Filed March 31, docketed April 3, 2026; the Solicitor General took one extension and filed a brief in opposition on June 3; reply June 15; distributed once, June 17, for the September 28, 2026 conference. No CVSG, no amici, no relist. Context: `mode: forward`, `band: baseline` under `sal-v4`, `distribution_count: 1`, `term: 2025`.

## Anchor

The context band is `baseline` and the statpack's "Segment base rate by salience band" table is headed `sal-v4`, so the versions match. The petitioner is a private party (a servicemember; the United States is the respondent, and government-provided appellate defense counsel does not make the petitioner a federal caption), so `baseline` is also the caption-class floor. Pooling the bracketed `reached` figure over the eight rendered Terms strictly before OT2025 (OT2017 to OT2024) gives about 5.1% on a weighted denominator of roughly 11,580. That is the grant-family rate (plain grants plus GVRs) for petitions that reached this band, and it is what the evaluator scores against. Cross-checks: the relist-0 bucket of the paid scored segment shows granted 1.2% plus gvr 0.5%, but that is the terminal-count rate and understates a live petition; the corpus's CAAF originating-court row shows granted 2.6% over 76 resolved petitions, a small sample but pointing the same direction as the adjustments below.

## Adjustments, and why the number ends far below the anchor

1. **The Court has already denied this exact question this Term, repeatedly, over the SG's opposition.** The petition's own footnote 1 and the BIO both record that Schneider v. United States, No. 25-685, consolidating thirteen CAAF cases on this indorsement question, was denied on January 12, 2026, as was United States v. Johnson, No. 25-682, the very CAAF precedent the petition asks the Court to overrule, and Dominguez-Garcia, No. 25-730, consolidating three more. This is the single largest driver. A petition asking the Court to revisit a question it declined eight months earlier, with no intervening change in its favor, sits well below the band's average.
2. **No split is possible and none is claimed.** The CAAF is the only appellate court that reads Article 66(d)(2), and the petition argues error, not conflict. The Court grants CAAF petitions rarely and almost only where a question of general federal law is at stake.
3. **Poor vehicle.** The AFCCA opinion is nonprecedential and disposed of the issue in a sentence; the CAAF denied review without opinion; the petitioner pleaded guilty; the underlying constitutional claim was never adjudicated below.
4. **Mootness of prospective importance.** The Air Force's February 4, 2026 guidance memorandum removed the First Indorsement from court-martial documents, which the BIO presses and the petition concedes in footnote 2. The question's forward-looking significance is shrinking, and the SG identifies alternative remedies (administrative correction, 18 U.S.C. 925(c), a standalone suit).
5. **Modest upward residual.** The petitioner is represented by an institutional appellate defense office, the brief is competent, and the Second Amendment reach of section 922(g) to drug users is an area the Court has been active in, so a hold-and-GVR is conceivable if an intervening decision lands. But the Court did not hold Schneider or Johnson for anything in January, which is strong evidence it sees no such linkage. I keep a floor rather than going to zero.

Net: 0.015, roughly one-third of the anchor. I considered 0.01 and 0.02; the companion denials with SG opposition justify going well below the band rate, and the GVR possibility keeps me above the pure-denial floor.

## Other claims

- `relist-increment` 0.12: paid scored segment shows about a quarter of petitions record a second distribution, but that count includes reschedules and is heavily weighted toward petitions with grant-side signals. This one has none, and a companion (Zhong, No. 25-742) may resolve on the same list. Long-conference logistics leave some reschedule risk.
- `cvsg-increment` 0.005: the SG is already the respondent.
- `summary-disposition-route` 0.55 conditional on grant: the statpack's modern-cert table shows GVRs at roughly 47% of the grant family; for a military-only jurisdictional question with a withdrawn regulation, a GVR in light of an intervening decision is the likelier grant shape than argument.
- `dissent-from-denial` 0.05: existence only. Denials on paid petitions rarely carry a writing; the topic is one where a statement is conceivable, but the companion denials the parties cite carry no noted dissent in their description.
- `big_case_score` 0.12: narrow military-justice paperwork question; the Second Amendment overlay is real but not what the Court would decide.

## Uncertainties and where to discount me

- I did not read the reply brief, so any new argument it raises about post-BIO developments is not reflected.
- I do not know whether Zhong (No. 25-742) has been decided or distributed for the same conference; CourtListener holds no docket entries for it. If Zhong was granted over the summer, this cell is mispriced low. If it was denied, my number is if anything slightly high.
- I do not know whether the January companion denials drew any statement respecting denial; my `dissent-from-denial` figure is a base-rate judgment, not a record read.
- The CAAF originating-court row (n=76 resolved) is thin.
- The salience band table's `reached` figure counts GVRs as grants, which matches the `disposition` claim's binary, so no unit mismatch there.

## Retrieval and tooling notes

Corpus: one `fedcourts query` for granted SCOTUS priors, used only to sanity-check that the corpus reads and to note that the Court's recent Second Amendment grants (e.g., Viramontes v. Cook County, Grant v. Higgins in the returned rows) are merits challenges to state arms bans, not military indexing questions. CourtListener MCP: docket lookups for Nos. 25-742, 25-685, 25-730, and this docket (last modified June 17, 2026; no termination). No web search. The prediction rests on the provisioned documents and the statpack.
