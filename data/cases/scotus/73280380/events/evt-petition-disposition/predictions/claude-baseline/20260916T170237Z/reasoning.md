# Why 0.12

## What I read

Provisioned inputs only, plus a small amount of forward retrieval listed in
`retrieval.md`: the snapshot `record/snapshots/2026-09-16.json` (as-stored,
no cutoff, `mode: forward`), `record/context.json`, `event.yaml`, and the
three provisioned documents (`questions-presented.txt`, `petition.txt` at
23 pages, `brief-in-opposition.txt` at 38 pages; `documents.json` shows none
truncated or empty). I did not read the earlier predictions under this
event.

## The anchor

`context.json` freezes `band: elevated` under `sal-v4`, which matches the
statpack's per-Term band table heading, so the table is my anchor. Pooling
the bracketed `reached` figure for `elevated` over every Term the table
shows strictly before OT2025 (OT2017 through OT2024) gives **17.2%
(n = 2810)**; the last five Terms alone give 18.1% (n = 1729). The petition
is paid, from CA9 (modern cert grant family for ca9 roughly 3.2% of resolved
petitions: granted 2.1% plus gvr 1.1%), private petitioners against county
officials, no CVSG, distribution count 2, so the elevated band is the right
population label.

## Adjustments down from 17%

1. **The two distributions are not a relist.** The first distribution (for
   3/27/2026) never reached conference: the Court called for a response on
   3/23, the respondents took a two-month extension, and the petition was
   redistributed on 7/8 for the 9/28 long conference. The `elevated` band's
   17% is a population dominated by petitions that were considered at
   conference and carried over. A response request is a genuine positive
   signal (at least one chamber wanted the other side's view), but it is a
   weaker one than a relist, and this petition has not yet survived a single
   conference.
2. **Fact-bound posture.** The sanctions rest on findings that the amended
   complaint falsely implied Arizona does not use paper ballots and that the
   equipment was untested; both courts below applied the Ninth Circuit's
   two-prong Holgate test and abuse-of-discretion review, which Cooter &
   Gell prescribes. The BIO's central point, that the petition never
   contests the specific false statements and instead attacks the "send a
   message" sentence, is fair on my reading of the petition. The Court
   rarely grants to review a discretionary sanctions ruling absent a clean
   legal question, and the QPs are framed as characterizations rather than
   rules.
3. **Weak vehicle on QP 4 and waiver.** The § 1927 award has an independent
   basis (persisting in the paper-ballot allegations after a Rule 11 letter),
   so Purcell is not outcome-determinative, and the Purcell argument was not
   pressed below. The BIO also notes the Court already denied the merits
   petition in Lake v. Fontes, No. 23-1021.
4. **Institutional reluctance.** The case is the sanctions coda to the 2022
   Lake/Finchem voting-machine suit. Taking it, even to vindicate a Rule 11
   principle, puts the Court in the middle of election-denial litigation for
   a $122,200 fee award. That tends to cost votes at the cert stage even
   among Justices sympathetic to the dissenters' concern.
5. **The petition is thin.** Fourteen pages, leads with a request for summary
   vacatur, no developed circuit split (the footnoted "other circuits"
   citations are general Rule 11 statements, not conflicting holdings on
   the construction question).

## Adjustments up

1. **Six-judge published en banc dissent** from prominent Ninth Circuit
   judges, plus a panel dissent by Judge Bumatay. That is the strongest
   thing in the record and the reason this is not a 3% petition.
2. **The response request itself.** The respondents had not filed; the Court
   asked. That is above-baseline attention.
3. **Bost v. Illinois State Board of Elections** (Jan. 14, 2026) gives a
   post-hoc hook: it held candidates have standing to challenge election
   rules in advance, which makes the plaintiffs' standing theory look less
   frivolous, and it post-dates the Ninth Circuit's sanctions opinion. That
   makes a GVR available to a Court that wants to do something small.
4. Experienced Supreme Court counsel (Nathan Lewin) for petitioners.

Net: I land at **0.12**, below the 17% band anchor, because the two
distributions overstate the docket signal and the sanctions posture is one
the Court almost always leaves alone. I would not go below 0.08 given the
en banc dissent and the CFR.

## The other claims

- **relist-increment 0.38.** Roughly P(grant) x ~0.9 (nearly every grant
  follows a relist) plus P(deny) x ~0.28 for a writing-driven or hold-driven
  extra distribution. A reschedule before 9/28 would also count, which
  pushes this up slightly.
- **cvsg-increment 0.03.** No federal interest; CVSGs on Rule 11 disputes
  are essentially unknown.
- **summary-disposition-route 0.5** (conditional on grant). The statpack's
  modern cert table shows GVRs are roughly half of the grant family
  (655 granted vs 577 gvr, resolved), and this case is unusually suited to
  a summary route: the petition asks for it, Bost supplies a GVR hook, and
  a plenary argument over a fee award is the least likely form of grant.
- **dissent-from-denial 0.22** (conditional on denial). A ready-made en banc
  dissent and a theme (sanctions chilling advocacy) some Justices care
  about, against the Court's silence on the related merits petition and the
  political cost of writing.

## Big case score 0.4

Moderate. If decided, it would be the Court's first word in three decades
on how pleadings are construed under Rule 11 and would be read as a signal
about sanctions in election litigation, which is newsworthy. But the direct
stakes are two attorneys and $122,200, and a denial leaves nothing.

## Uncertainty and where to discount me

- I have no view into the pool memo or which chamber requested the response.
  If the CFR came from a Justice already inclined to write, both the relist
  and the dissent-from-denial numbers are too low.
- I know this litigation from general knowledge (the Lake v. Hobbs suit and
  the Ninth Circuit sanctions decisions through August 2025). I do not know
  and did not seek the cert outcome; the first conference is 9/28/2026, after
  this run.
- The band anchor's population is defined by a distribution count that here
  reflects a CFR redistribution rather than a relist. Noted in `flags.json`
  as an informational data-quality point; the band itself is the harness's
  and I used it as instructed.
- The corpus `fedcourts query` returned no rows (the citation column is
  sparse on SCOTUS rows), so no corpus priors informed this number beyond
  the statpack.
