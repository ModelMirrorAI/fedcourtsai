# Why 0.40

## Inputs read

Snapshot `2026-10-03.json` (ten docket entries through the September 23
distribution for the October 9 conference); `context.json` (forward mode,
band `elevated` under sal-v4, `distribution_count` 2, no CVSG, Term 2025);
`event.yaml` (cert stage, moment `distribution`); and all three provisioned
documents: `questions-presented.txt`, `petition.txt` (160 pages, truncated
at 150k characters, which still carried the whole Marks II opinion and the
Stras dissent in Appendix A), and `brief-in-opposition.txt` (40 pages,
complete). Beyond those: the statpack cuts, two corpus `query` calls, and
four CourtListener MCP calls listed in `retrieval.md`.

## Anchor

The context's band is `elevated` under sal-v4, and the statpack's segment
table is also sal-v4, so the band table is the anchor. Pooling the bracketed
`reached` figures over the eight Term rows strictly before this case's Term
(2017 through 2024, n = 2,810) gives about 17%. The relist-count cut agrees:
the docket shows one relist (two distributions), and the relist-1 bucket's
grant family (granted plus GVR) is about 13%. The CA8 marginal (grant family
about 2.6%) is already folded into the band and I did not adjust on it.

## Adjustments up

- **Record requested before the first conference, then a relist.** This is
  the strongest signal on the docket and the statpack has no cut for it. A
  chambers asked for the video record on August 31, four weeks before the
  long conference, and the petition then came out of that conference
  relisted. That is the pattern that precedes a per curiam or a written
  dissent, not an ordinary denial. I weight this heavily.
- **The qualified-immunity summary-reversal template fits.** Officer
  petitioner, interlocutory denial of immunity, a sharp dissent below citing
  White v. Pauly and Kisela, and a court of appeals relying on
  general-standard circuit cases. The Court did exactly this in March 2026
  in Zorn v. Linton (per curiam reversal of CA2, protest arrest, dissent
  below), which I read on CourtListener; it is the current Court's live
  practice, not history.
- **Second visit after a GVR.** The Court already vacated once in light of
  Barnes; the remand panel reinstated its holding on the stated ground that
  it had never applied the moment-of-threat rule. The petition frames that as
  defiance. Whether or not that is fair, it raises the chance that at least
  some Justices want to act.
- The 2024 petition drew two amicus briefs (a police association and the
  municipal lawyers' association, per the petition); institutional interest
  exists even though none has filed yet on this docket.

## Adjustments down

- **The facts are bad for a per curiam.** A nineteen-year-old lost an eye
  to a round fired from five to ten feet with no warning; the officer he had
  struck testified the threat had ended; two prosecutors declined to charge
  him; a bystander had stepped between them. Summary reversals are written on
  records where the officer-favorable reading is clean. This one is not, and
  the panel's statement of facts, which a per curiam would have to accept,
  is written against the officer.
- **Vehicle.** The BIO's Johnson v. Jones point has force: the panel rested
  on genuine fact disputes (aim, distance, whether Marks was grabbing the
  baton to disarm or to balance). The Court's per curiams usually sidestep
  this by taking the facts as stated, but it gives the Justices who prefer
  denial a principled reason.
- **The remand majority was Chief Judge Colloton and Judge Erickson.** A
  panel with the circuit's conservative chief judge in the majority is harder
  to cast as a rogue panel than the petition suggests.
- **No split, no legal rule.** Respondent is right that the petition asks
  for error correction; that only matters for the plenary route, which is
  why I put most of the grant mass on the summary route.
- The BIO cites four recent denials of officer petitions with similar
  framing (Estate of Hernandez, Crockett, Jackson v. Dutra, Pittman);
  record-and-relist dockets do end in silent denials often enough.

## How the number comes together

Starting near 17% and allowing a large upward move for the record request
and the template match, offset by the plaintiff-favorable record and the
Johnson v. Jones posture, I hold roughly: summary reversal 30%, plenary
grant 7%, denial with a writing 28%, silent denial 35%. That gives P(any
grant) 0.40, `granted` 0 and `predicted_disposition` `denied` because
denial in either form is the modal outcome, and `summary-disposition-route`
0.80 as the conditional share of the grant mass that rides the cert order.

`relist-increment` 0.70: a per curiam or a dissent takes several
conferences; only the silent-denial branch ends at the October 9
conference, and I give that branch about a third. `cvsg-increment` 0.02:
no federal interest. `dissent-from-denial` 0.45: conditional on denial, the
record call makes a writing more likely than usual, but silent denials after
record requests are common and I do not want to overfit one signal.

## Uncertainty and where to discount me

The record request carries most of the weight above the anchor, and I have
no corpus base rate for it; my sense of its strength comes from Supreme
Court practice generally, not from a cut I can cite. If record requests are
less predictive than I believe, the right number is closer to 0.25. The
corpus `query` for `--disposition summary-reversal` returned no rows, so I
could not check how the corpus labels past per curiams or pull their
docket shapes. I did not find the 24-616 docket's distribution history
(CourtListener holds no entries for it), so I cannot say whether the first
petition was itself relisted or simply held for Barnes.

`big_case_score` 0.35: a protest-era police shooting and the
qualified-immunity debate give it real salience, but any disposition will
be fact-bound and short.

No leakage concerns: forward cell, the October 9 conference has not
occurred, and nothing I retrieved postdates the snapshot's docket state.
