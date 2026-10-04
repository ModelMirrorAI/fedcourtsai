# Why these numbers

**P(grant) = 0.005; predicted disposition: denied.**

## What I read

- Provisioned snapshot `record/snapshots/2026-10-04.json` (the file
  `context.json` names). Paid docket, No. 26-152, Fourth Circuit (No. 25-2451),
  unpublished per curiam affirmance of March 30, 2026, rehearing en banc denied
  April 21, 2026. Petition shows a filed date of May 8, 2026 and a docketed date
  of August 3, 2026; motion to expedite filed; supplemental brief of petitioner
  filed August 14; distributed September 16 for the Conference of October 9,
  2026. No brief in opposition, no waiver, and no call for a response appear.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`,
  `distribution_count` 1, no CVSG, Term 2026, `signals_observable` true.
- `record/documents/`: `petition.txt` (9 pages, text extracted, not truncated)
  and `questions-presented.txt`. No BIO was provisioned because none was filed.
- `metrics/statpack.md`: the modern discretionary-cert disposition table, the
  relist-count and CVSG cuts on the paid scored segment, and the per-Term
  "Segment base rate by salience band (sal-v4)" table.
- Retrieval beyond the provisioned inputs (forward cell, unrestricted): one
  `fedcourts query` for recent SCOTUS priors; CourtListener MCP lookups of the
  district court docket (E.D. Va. 1:25-cv-02117) and the Fourth Circuit docket
  (25-2451). None of these touched this petition's own disposition. Details in
  `retrieval.md`.

## Anchor

The context band is `baseline` and its salience version (`sal-v4`) matches the
statpack's band table, so the table is my anchor. Pooling the bracketed
`reached` figure for `baseline` over every rendered Term strictly before this
case's Term (OT2017 through OT2025; the table renders all ten Terms the pack
holds, and OT2026's row is empty) gives roughly 637 grants over a weighted
risk-set denominator of about 12,720, i.e. **about 5.0%**. That is the rate a
private paid petition that has reached the baseline band actually faces, and it
is what my skill is scored against. For context, the baseline band's leading
figure (petitions that *ended* in baseline) runs 0.6% to 1.8% per Term, the
relist-0 bucket grants 1.2%, and the no-CVSG bucket 4.0%.

## Adjustments down from 5%

Nearly every feature of this petition sits in the far tail of the baseline
population, and all of them point the same way.

1. **No legal question.** The five questions presented ask whether the lower
   courts "properly" denied this petitioner's own motions and whether the Fourth
   Circuit could issue a show-cause order alongside an affirmance. There is no
   circuit split, no statutory or constitutional holding below, and the only
   authority cited is the Fourteenth Amendment (against a private hotel, where
   it has no application) and the jurisdictional statutes. The petition's
   argument runs four pages.
2. **Posture.** The district court never let a complaint be filed: it denied
   leave to file an emergency complaint and an emergency injunction and closed
   the case within two weeks of filing (district docket entries 1, 7, 10, 18,
   20). The Fourth Circuit affirmed in an unpublished per curiam opinion, and
   no judge requested a poll on rehearing en banc. The decision below is not
   in CourtListener's opinion index, consistent with an unpublished
   disposition. An unpublished, non-precedential affirmance of a discretionary
   filing-management ruling is the weakest possible vehicle.
3. **Petitioner.** Pro se, with a litigation history the Fourth Circuit found
   serious enough to issue a show-cause order on a prefiling injunction with
   its merits opinion; the district docket records that the injunction was
   entered on August 4, 2026 (entry 31). That is forward signal about the
   petitioner's filings, not about this petition's disposition, and it
   confirms the sanctions posture the petition itself describes. Pro se paid
   petitions of this shape are denied essentially without exception; the
   realistic grant route for them is a GVR after an intervening decision, and
   no intervening decision bears on this case.
4. **No response and no call for one.** The response was due September 2; the
   respondent filed nothing, not even a waiver, and the Clerk distributed the
   petition without a call for a response. A petition the Court intends to
   grant is never granted without a response having been requested, so any
   grant would require a relist and a call for a response first, and the
   relist number below is already low.
5. **Docketing delay.** The petition carries a May 8, 2026 filed date against
   an August 3 docketed date and a printed caption reading "No. 25-", which is
   the ordinary signature of a petition returned by the Clerk for correction
   under Rule 14.5 and refiled. Mildly consistent with the rest; no weight on
   its own.

No feature pushes the other way. The paid fee class and the printed petition
are the only things that distinguish it from the IFP pro se stream, and those
are already in the paid scored segment the anchor describes.

Taking the anchor's 5% and conditioning on all of the above, I land at
**0.5%**. I considered 1%, the baseline band's leading per-Term figure, but
that figure includes competently counseled petitions with weak-but-real legal
questions, which this is not. I would not go below 0.3%: the Court does, very
rarely, GVR or summarily vacate in pro se cases where a court of appeals'
procedure was irregular, and the simultaneous show-cause order is at least an
irregularity a Justice could notice.

## The other claims

- **relist-increment 0.07.** The docket shows one distribution. In the paid
  scored segment roughly a quarter of petitions pick up a further distribution,
  but that population is dominated by petitions with a response on file; a
  pro se petition with no response and no legal question is relisted mainly by
  administrative reschedule or when a Justice considers a statement, and I see
  no trigger for either.
- **cvsg-increment 0.002.** No federal interest of any kind.
- **summary-disposition-route 0.75**, conditional on a grant. The grant
  scenario I can picture is a summary vacatur on a procedural ground or a GVR,
  not plenary review of a case with no record and a four-page petition. The
  statpack does not publish a conditional cert-order share of grants, so this
  is judgment.
- **dissent-from-denial 0.01**, conditional on denial. No Justice has been
  writing on prefiling-injunction procedure or pro se access of this kind, and
  the facts do not invite a statement.
- **big_case_score 0.02.** A private hotel-guest injury grievance; no stakes
  beyond the parties.

## Uncertainty and where to discount me

- My number is far below the scored anchor, so the cell is a confident call.
  The main way it fails is a procedural GVR or summary vacatur that I have
  rated near zero; the Fourth Circuit's issuance of a sanctions show-cause
  order in the same breath as its merits decision is the one thing a Justice
  might find irregular enough to act on, and it is the reason I did not go
  lower.
- I did not read the Fourth Circuit's opinion or the district court's order
  text; the former is not indexed and I judged the petition's own account,
  corroborated by the district docket entries, sufficient. If the Fourth
  Circuit's opinion said something unusual about the show-cause procedure, I
  would have missed it.
- I did not read the supplemental brief filed August 14; it was not
  provisioned. On this petition's shape it is very unlikely to change the
  call.
- The corpus `query` ranks by recency and returned mostly 26A applications and
  OT2025 grants, none a useful comparator; I did not retry with sparse
  filters. The priors in my reasoning are the statpack's cuts, not retrieved
  comparables.
