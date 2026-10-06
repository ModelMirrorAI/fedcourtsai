# Rationale for the numbers

**P(grant) = 0.22; predicted disposition `denied`; granted = 0.**

## Inputs I used

- Snapshot `record/snapshots/2026-10-05.json` (the file `context.json` names): 13 docket entries, one distribution (Conference of 9/28/2026), response requested the same day after the County's waiver, six cert-stage amicus briefs, BIO filed October 1, 2026. Paid docket; CA4; unpublished per curiam below (February 23, 2026), rehearing en banc denied March 23, 2026.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2026, `signals_observable: true`.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (50 pp., full text), `brief-in-opposition.txt` (23 pp., full text). None flagged `empty_text`.
- The committed `metrics/statpack.md` for base rates.
- Retrieval listed in `retrieval.md`: one corpus query for shape, a CourtListener search for the companion petition (no hit), two web searches, and three fetches (the two public SCOTUS dockets and one practitioner blog post).

## Anchor

The context freezes band `baseline`. The segment table carries `sal-v4`, matching the context, so the anchor is the bracketed **`reached`** rate for `baseline` pooled over the Terms strictly before OT2026 that the table shows (OT2017 through OT2025): about **5.0%** over a weighted n of roughly 12,700 petitions. For comparison, the relist-count cut's terminal relist-1 bucket is 8.2% granted plus 5.1% GVR (13.3% grant family), and the CVSG-none bucket is 4.0% granted plus 2.3% GVR; neither is a row I can look up for this petition's forward hazard, and I did not adopt either.

## Adjustments up (from ~5% to ~22%)

1. **The Court called for a response after a waiver.** The band does not see this (it keys on relists and CVSG), so the anchor understates the petition. A CFR is an affirmative act of attention by at least one chambers; historically CFR'd paid petitions are granted at several times the overall paid rate. This is the largest single adjustment.
2. **Six cert-stage amicus briefs** (National Association of Realtors et al., Manhattan Institute, New York Apartment Association, California Rental Housing Association, Advancing American Freedom, Atlantic Legal Foundation). A dense amicus slate is a strong grant correlate, discounted here because it is a coordinated property-rights campaign filed identically on the companion petition, which weakens it as an independent signal of the Court's interest.
3. **Repeat-player counsel in a favored subject area.** Pacific Legal Foundation has won a string of takings cases in this Court (Knick, Pakdel, Tyler, Sheetz), including a summary reversal on a finality question (Pakdel), and this Court has shown a consistent appetite for correcting lower courts that stack ripeness hurdles on takings plaintiffs.
4. **The companion petition.** Tedford's Tenancy (No. 26-110) was distributed for the same conference, drew the same CFR a week later, and now has its response due November 10. The Court is treating the pair as a unit; that raises the chance it takes at least one, and Walls, from a federal court of appeals, is the more conventional vehicle for the shared question. A grant in Tedford's alone would also likely yield a hold-and-GVR here, which counts as a grant for this event.
5. **A thin BIO.** The County's brief (its own Office of Law) argues largely that Walls never formally applied for the waiver, misstates Palazzolo as a certiorari standard, and effectively concedes that the Fourth Circuit's position is shared by some courts and rejected by others. It does not seriously contest the existence of the splits.

## Adjustments down (why not higher)

1. **Vehicle problems.** The decision below is an unpublished per curiam; the district court and the Fourth Circuit rested on different grounds (no final waiver decision versus legislative exhaustion); and the BIO's factual point that Walls made only an informal inquiry and never filed a waiver application gives the Court an easy fact-bound reason to see the finality question as muddy. The petition's own footnote (the Fourth Circuit did not require a further waiver application) helps, but a Justice looking for a reason to pass has one.
2. **The Question 1 split is weak as splits go.** It is mostly state intermediate appellate decisions, several three to four decades old, with one unpublished federal decision on the "exhaustion required" side. The Court usually wants a conflict among federal circuits or state high courts.
3. **Question 2 asks the Court to settle the status of prudential ripeness**, something it has pointedly declined to do in Driehaus, Lexmark, Knick, and Pakdel. The Court may again prefer to decide finality on narrower terms, which cuts toward denying or toward a narrow summary disposition rather than plenary grant.
4. **Base rate discipline.** Even CFR'd, amicus-heavy, repeat-player petitions are denied most of the time; the Court denied the 2024 New York rent-stabilization petitions despite comparable backing, and PLF's own ripeness petitions have been denied more often than granted.

Netting these, I land at 0.22. I would not be surprised by a denial (the modal outcome) and I would not be shocked by a grant; a per curiam summary reversal is the grant shape I consider most under-priced by the band anchor.

## Other claims

- **relist-increment = 0.96.** The CFR removed the petition from the September 28 conference before any vote, so the snapshot's single distribution will almost certainly be followed by a redistribution once the reply is in (or once Tedford's is fully briefed). The residual is withdrawal or an unusual docketing path.
- **cvsg-increment = 0.07.** Slightly above the roughly 1% paid-docket CVSG rate because the question concerns a doctrine the United States litigates as a takings defendant and because the Court is looking at two petitions together, but the respondent is a county and the Court's recent finality cases proceeded without the Solicitor General.
- **summary-disposition-route = 0.35 (conditional on grant).** Two live summary routes (a Pakdel-style per curiam against an unpublished ruling; a hold-and-GVR behind Tedford's) against the plenary route Question 2 invites.
- **dissent-from-denial = 0.15 (conditional on denial).** Most such denials are silent; a Thomas statement or dissent is plausible given his Arrigoni and Knick-era writing on Williamson County.
- **big_case_score = 0.35.** Doctrinally meaningful for takings litigants and land-use practice, low public salience.

## Where to discount me

- I have no as-at-prediction grant rate conditioned on a CFR or on cert-stage amicus count from the committed statpack; those adjustments rest on general knowledge of the Court's practice and on the published cuts' shape, not on a corpus figure.
- The companion-petition reasoning assumes the Court continues to handle the two together; if Walls is redistributed and decided in late October on its own, the hold-and-GVR path disappears and my grant number should read somewhat lower.
- I did not read the Fourth Circuit opinion or the district court transcript directly; my account of the grounds below comes from the petition's appendix description and the BIO, which agree on the essentials but are advocacy.
- The corpus query I ran returned only recent 2020s grants and applications for shape; it did not surface a ripeness-specific prior set, and I did not rely on it for a number.
