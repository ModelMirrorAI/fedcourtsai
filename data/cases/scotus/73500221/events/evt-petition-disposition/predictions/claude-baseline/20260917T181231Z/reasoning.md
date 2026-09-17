# Rationale for the numbers

**P(grant) = 0.01; predicted disposition: denied.**

## What I read

- `record/snapshots/2026-09-17.json` (the provisioned baseline): paid petition
  No. 25-1320, docketed May 28, 2026, from the Tenth Circuit (No. 25-5039,
  decided February 17, 2026). Three proceedings entries: the petition (May 18),
  the City's waiver of response (June 8), and one distribution, for the
  Conference of September 28, 2026 (June 24). No amicus, no CVSG, no response
  requested.
- `record/context.json`: forward mode, `band: baseline` under `sal-v4`,
  `distribution_count: 1`, `cvsg_date: null`, `term: 2025`,
  `signals_observable: true`.
- `record/documents/questions-presented.txt` and `petition.txt`
  (37 pages, extracted cleanly per `documents.json`). No brief in opposition
  exists; the City waived.
- `metrics/statpack.md`: the sal-v4 segment table, the relist and CVSG cuts,
  and the Term table.

## Anchor

The frozen band is `baseline` and the statpack's segment table is computed
under the same `sal-v4`, so the table is the anchor. Pooling the baseline
column's bracketed `reached` rate over the Terms strictly before this case's
Term (2025), that is OT2017 through OT2024, gives about 5.1% on a weighted
denominator of roughly 11,600 petitions (per-Term figures run 4.5% to 5.9%).
That is the grant-family rate for a private paid petition that has reached
the weakest band, and it is the yardstick the evaluator scores this cell
against.

## Adjustments, and why the number sits far below the anchor

Nearly every cert-worthiness signal points down, and none points up:

- **No circuit split, no conflict claimed.** The petition's "Reasons for
  Granting" are an error-correction argument that the Tenth Circuit misread an
  Oklahoma judgment. It cites no conflicting appellate authority on the
  question presented and identifies no lower-court division.
- **The dispositive question is state-law preclusion.** Whether the Oklahoma
  Court of Civil Appeals' judgment was "on the merits" for purposes of
  Oklahoma's savings statute (12 O.S. § 100), and so whether the federal refile
  was timely, is a question the federal courts answered by reading Oklahoma
  law. The Court does not grant to review that, and the petition's own
  Section IV concedes tolling is a state-law matter.
- **Unpublished order below.** The appendix lists a Tenth Circuit "Order and
  Judgment," that court's unpublished form; the Court treats unpublished
  dispositions as poor vehicles.
- **Waiver of response.** The City waived. A grant essentially never issues
  without a response, so the first step toward any grant would be a call for a
  response, which is itself uncommon for a petition of this shape.
- **Fact-bound and procedurally tangled record.** The claim arises from a 2011
  cease-and-desist order and fence, litigated in state court from 2014, with a
  stay for a second administrative hearing, a state appellate affirmance in
  2023, and a federal refile. The petition itself acknowledges the state court
  also rested on exhaustion, and the Tenth Circuit treated the state court's
  "no taking as a matter of law" footnote as a merits ruling.
- **Representation and support.** Solo-practitioner counsel of record, no
  amicus support, and one distribution for the long conference.

The one feature that cuts the other way is subject matter: the Court has been
receptive to takings petitions since Knick, and the underlying grievance (six
years of uncompensated physical occupation, ended by voluntary rescission with
no compensation ever adjudicated) is the kind of narrative that has drawn per
curiam attention before. That is why the number is 1% rather than the floor,
and why the summary-disposition-route conditional is above one half.

Within the population data, the relist-count cut's relist-0 bucket (the
terminal bucket for petitions that ended at one distribution) shows a grant
family of about 1.7% (granted 1.2%, gvr 0.5%). This petition is weaker than
the typical member of that bucket, which includes petitions with a response
and a claimed split. I land at 0.01.

## The other claims

- **relist-increment 0.10.** From a state of one distribution. Across the paid
  scored segment about a quarter of petitions record more than one
  distribution, but that share is driven by the strong petitions; for a
  waived-response, no-split petition at the long conference the routes to a
  second distribution are a reschedule or a call for a response, which I put
  together at roughly one in ten.
- **cvsg-increment 0.005.** No federal interest of any kind.
- **summary-disposition-route 0.55.** Conditional on the unlikely grant. The
  statpack notes the cert-order share of the grant family runs 30% to 59% by
  Term; this petition's error-correction shape and the short unpublished order
  below make a per curiam more plausible than argument if the Court acted at
  all. No intervening decision supports a GVR.
- **dissent-from-denial 0.02.** Above the docket-wide rate for a paid petition
  because takings is an area where individual Justices do occasionally write on
  denials, but the preclusion posture and the waived response make this a poor
  vehicle for a statement.
- **big_case_score 0.10.** Stakes are local and personal. A decision could
  touch how state-court exhaustion or mootness dismissals interact with later
  federal takings suits after Knick, but as framed the case would reach few
  beyond the parties.

## Retrieval, degraded

The CourtListener MCP server returned HTTP 429 (hourly rate limit exhausted,
roughly 14 minutes to reset) on both lookups I attempted: the Tenth Circuit
opinion and the SCOTUS docket. I did not retry and proceeded on the provisioned
inputs plus the corpus tooling, as the contract directs. Consequences: I have
not read the Tenth Circuit's order itself and rely on the petition's account
and appendix listing for its content and unpublished status; and I have not
checked the live docket for entries after the provisioned snapshot (an amicus
filing or a response request between June 24 and today would move the
relist-increment number, though not the disposition). Two `fedcourts query`
pulls (recent granted and recent denied 2020s SCOTUS rows) were run for
shape; the recency ranking surfaced mostly emergency applications and
government-party grants, so they informed nothing specific here.

## Where to discount me

The main uncertainty is the Court's appetite for takings error correction. If a
Justice reads the Oklahoma footnote the way the petition does, as a
voluntary-cessation ruling dressed as a merits holding, a call for a response
is the first thing that would happen, and my relist-increment figure would be
too low. I hold no outcome knowledge about this case; the conference has not
yet occurred.
