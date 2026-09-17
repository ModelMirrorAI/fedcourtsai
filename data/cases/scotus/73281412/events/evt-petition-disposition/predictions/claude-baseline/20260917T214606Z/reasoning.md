# Why P(grant) = 0.10

## What I read

- The provisioned snapshot `record/snapshots/2026-09-17.json` (payload creation date July 29, 2026): paid petition docketed March 26, 2026 from a published Fifth Circuit judgment (No. 24-10663, 143 F.4th 569, substituted on rehearing at 165 F.4th 309, December 23, 2025) with a dissent by Judge Dennis. The County respondents waived; the petition was distributed for the May 21 conference; on May 12 the Court requested a response; respondents took one extension; two briefs in opposition were filed July 13 (the Taft respondents and the Henderson County respondents); the petition was redistributed July 29 for the September 28 long conference. No reply brief and no cert-stage amicus appear in the payload.
- `record/context.json`: forward mode, `band: elevated` under `sal-v4`, `distribution_count: 2`, no CVSG, Term 2025, `signals_observable: true`.
- `record/documents/`: the questions presented, the full petition (40 pages), and the combined brief-in-opposition file (77 pages, two briefs). All extracted cleanly; none `empty_text`.
- `metrics/statpack.md`: the sal-v4 segment table, the relist and CVSG cuts, and the circuit cut.

## Anchor

The context froze the band at `elevated` under sal-v4, which matches the statpack table's version. Pooling the bracketed `reached` figure for `elevated` over the eight Terms strictly before Term 2025 (OT2017 through OT2024, n = 2,810 weighted) gives about 17.2%. That is the yardstick the evaluator will score this cell against and my starting point.

Two things about how this petition reached `elevated` matter for how much weight the anchor deserves. The second distribution here is not a relist after a conference considered the petition: the petition was pulled from the May 21 conference when the Court called for a response, and the July 29 distribution is its first real conference. The statpack's own caption notes the distribution count is an upper bound on true relists for exactly this reason. On the other hand, a call for response after a waiver is itself a signal that at least one chambers thought the petition deserved an answer, and petitions that draw a call for response are granted at several times the paid-docket rate. So the docket signal is real but weaker than a true relist, and I treat the 17% as a ceiling to adjust from rather than a midpoint.

For comparison, the paid scored segment's relist-count cut puts the grant family (granted plus GVR) at about 13% for terminal bucket 1 and about 6% for the no-CVSG cut; the Fifth Circuit cut sits at about 3.7% grant family over the whole modern docket.

## Adjustments down

1. **No circuit split as framed.** The petition argues that the Fifth Circuit contradicted Estelle, Bell, and Iqbal, and lists other circuits applying Bell's proportionality prong, but it does not identify a court that has adopted the rule it attributes to the Fifth Circuit. The Taft brief in opposition makes a persuasive textual case that QP 1 rests on a misreading: the opinion's line is that medical care "includes" protection from violence or suicide, drawn from Hare v. City of Corinth, not a limitation, and the panel went on to analyze the adequacy of Phlips's care and expressly reserved that "not every actionless visit" passes muster. QP 2's "reasonably related" language is the Fifth Circuit's thirty-year shorthand for the Bell test. QP 3 is an application of the plausibility standard. This is an error-correction petition.
2. **Vehicle defects the petition does not answer.** The Fifth Circuit dismissed the claims against the Taft respondents on deliberate indifference alone, a holding the petition does not challenge, so a grant could not help the petitioner as to them. The panel also held, as an independent ground, that it "matters not whether the officers believed he was suicidal" because jails must protect potentially suicidal detainees; the petition does not confront that alternative holding. Qualified immunity and Monell liability were left unresolved below, so even a win would face further obstacles on remand. The Taft brief lays all of this out; the petition, filed first, could not answer it and no reply appears in the payload.
3. **Unsympathetic core fact.** The petitioner's own complaint says he falsely reported suicidal ideation to force a transfer. The Court is unlikely to want to announce a rule about suicide-watch conditions on a record where the detainee concedes he was not suicidal, and the panel's "minefield" reasoning about second-guessing suicide reports will read as sensible to most of the Court.
4. **Advocacy.** Counsel are Texas practitioners, not repeat Supreme Court advocates; the petition has typographical problems and spreads across three questions of uneven strength. No cert-stage amicus supports it (the prison-law scholars' brief was at the rehearing stage below).
5. **Redistribution timing carries no extra information.** A July 13 BIO is routinely distributed for the long conference; the July 29 entry is the ordinary schedule, not a signal.

## Adjustments up

1. **The call for response.** The Court asked for a response after the County had waived, which means a chambers or the pool read the petition as non-frivolous. This is the main reason I do not go lower than the paid-docket rate.
2. **Published opinion with a substantial dissent, and vivid facts.** Judge Dennis's revised dissent calls the majority's treatment "punishment of a pretrial detainee disguised as suicide watch," and the alleged conditions (no toilet, water, bedding, or hygiene for five days; alleged threats) resemble the Taylor v. Riojas record on which the Court summarily reversed the Fifth Circuit in 2020. The Court has shown it will act summarily on egregious Fifth Circuit prisoner-conditions rulings.
3. **The petition asks for summary reversal**, which lowers the cost of a grant for a Justice inclined to act, and a hold for a writing is plausible.

## Net

Starting from a ceiling of about 17% for the band, the CFR-not-relist reading of the distribution count, the absence of a split, and the unanswered vehicle defects each pull down; the CFR signal and the dissent-plus-facts profile pull up. I land at 0.10, roughly two to three times the paid no-CVSG docket rate and well under the band anchor. My main uncertainty is how much weight the Justices give to the sympathetic conditions relative to the admitted false suicide report; if a Justice sees this as another Taylor v. Riojas, the summary-reversal path opens and the number should be nearer 0.20. If the Court treats it as a routine pleading-stage disagreement, the number should be nearer 0.04.

## Claims

- `disposition` 0.10, restating the above.
- `relist-increment` 0.25: from two distributions, P(at least one more after September 28). Long-conference petitions relist more often than ordinary ones, and a petition with a CFR, a dissent below, and a summary-reversal request is the kind a chambers holds while deciding whether to write. The statpack's terminal shape (about 28% of paid petitions that reach terminal bucket 1 go on to bucket 2 or more) is inflated by reschedules and CFR redistributions like this one, so I sit a little under it.
- `cvsg-increment` 0.01: no federal interest.
- `summary-disposition-route` 0.50, conditional on a grant: no split for plenary review; a Taylor-style per curiam is the likelier form of any grant. The modern-docket GVR-versus-granted split is roughly even, and this case's profile pushes toward the summary side while the petition's own concession that the case as a whole is not summary-reversal-simple pulls back.
- `dissent-from-denial` 0.10, conditional on denial: the facts and the dissent below fit the profile that has drawn writings from Justice Sotomayor or Justice Jackson, but the admitted false report and the vehicle problems make it a poor occasion.

## Where to discount me

- I cannot see whether a reply brief was filed after July 29; the snapshot payload's own creation date is July 29 although the file is dated September 17, so the absence of a reply may reflect either no filing or an unrefreshed payload. A strong reply answering the Taft vehicle arguments would move me up by a point or two, not more.
- The CourtListener docket record carries no entry text for this docket, so the live check added only that the docket is not terminated.
- My sense of grant rates after a call for response is from general knowledge, not a committed statpack cut; the pack does not publish a CFR-conditioned rate.
- The single `fedcourts query` I ran returned recent granted SCOTUS matters ranked by recency, none doctrinally similar, and did not inform the number.

## Retrieval mode

Forward cell, retrieval unrestricted. Nothing I retrieved disclosed this petition's disposition; it is scheduled for the September 28, 2026 conference and no order has issued as of the snapshot.
