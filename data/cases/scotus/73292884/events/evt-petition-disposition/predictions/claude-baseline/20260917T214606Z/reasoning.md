# Reasoning — why P(grant) = 0.14

## Inputs read

- `record/snapshots/2026-09-17.json` (the provisioned baseline; the docket as of
  the September 17, 2026 poll, 15 proceedings entries, last one the August 12
  distribution for the September 28 conference).
- `record/context.json`: mode `forward`, band `elevated` under `sal-v4`,
  `distribution_count` 2, no CVSG, Term 2025, paid docket.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (36 pp.) and
  `brief-in-opposition.txt` (41 pp.), all fully extracted (`empty_text: false`,
  not truncated). No reply brief was provisioned; the docket shows one filed
  August 10, 2026, so my read of the reply is inference from the docket only.
- `metrics/statpack.md`, the cert sections and the `sal-v4` band table.
- The Tenth Circuit opinion header via CourtListener (panel: Federico writing,
  Hartz concurring, Eid dissenting), see `retrieval.md`.

## Anchor

The frozen band is `elevated` under `sal-v4`, which matches the statpack's
band table heading, so the table is my anchor. Pooling the bracketed
**reached** rate over the Terms strictly before OT2025 that the table renders
(OT2017 through OT2024) gives **17.2%** (about 484 grants over a weighted
risk-set denominator of 2,810). That is the evaluator's yardstick for this
cell. Under `sal-v4` the band encodes only the distribution tier, so the
response request and the amicus count below are adjustments on top of it, not
double counting.

For shape, not as anchors: the relist-count cut puts a paid petition at two
distributions at roughly 41% grant-family, but that bucket is terminal
(petitions that *ended* at two) and this docket's second distribution is the
ordinary redistribution after a requested response, not a relist after
consideration, so I do not read it as a two-relist petition. The Tenth Circuit
originating-court cut (about 3.9% grant-family) sits near the docket-wide
rate and moves nothing.

## Adjustments up

1. **Response requested after a waiver** (May 26, 2026). The Court does not
   call for a response unless at least one Justice wants the petition briefed.
   This is the strongest fact on the docket and the main reason I do not sit
   below the anchor.
2. **Four amicus briefs** (Randy Elf; National Taxpayers Union Foundation and
   People United for Privacy; Americans for Prosperity Foundation and the
   Manhattan Institute; Advancing American Freedom). A real stakes signal,
   though all from one side of the issue and from the usual repeat filers.
3. **A published, divided Tenth Circuit opinion** with a substantive Eid
   dissent on narrow tailoring, a Hartz concurrence openly uncomfortable with
   the governing precedent, and an en banc denial over a dissent joined by
   Judge Tymkovich. The Court likes a dissent below that has already done the
   work.
4. **Subject-matter appetite.** Since *AFPF v. Bonta* several Justices have
   signalled interest in the limits of compelled donor disclosure, and Justice
   Thomas has long argued for strict scrutiny. The petitioner's counsel
   (Liberty Justice Center) is a competent repeat Supreme Court litigant.

## Adjustments down

1. **No circuit split, and none claimed.** The petition argues error and
   importance only. The BIO points this out, and the split amici assert
   (major-purpose test) rests on pre-*Citizens United* decisions. The
   Court's disclosure grants have generally come with a split or a federal
   party.
2. **Vehicle problems the BIO develops well.** The panel construed §(3)(c) to
   reach only advertisements reasonably interpreted as advocacy; the petition
   does not challenge that state-law construction and instead treats the
   statute as reaching "mere mention" of a candidate. The panel also said the
   Freedom Index, with its red/green scoring, is likely functional-equivalent
   advocacy under §(3)(b), which the petition does not contest, so the State
   can argue there is no live controversy over §(3)(c) at all. The challenge
   is facial, the record on chill is thin (no instance of retaliation in the
   organization's history), and QP 2's "major purpose" framing was arguably
   not raised below. Any one of these is the kind of defect the Court uses to
   deny an otherwise interesting question.
3. **Revealed preference.** From memory rather than retrieval: the Court has
   denied a run of post-*AFPF* petitions challenging state and local
   electioneering or ballot-measure disclosure laws (the Rhode Island, Wyoming
   and San Francisco cases) without taking any of them. That pattern says the
   Court is content to let *AFPF* percolate, and this petition's premise
   (disclosure may never reach non-express advocacy) asks it to cut back the
   disclosure paragraph of *Citizens United*, a large ask on a 27-page
   petition that concedes the passage exists.
4. **NRSC v. FEC (June 30, 2026).** I could not retrieve the opinion text; the
   BIO characterizes it as endorsing disclosure as the less restrictive
   alternative in campaign-finance regulation. If that is right, the most
   recent word from the current majority favors disclosure, which lowers the
   odds that five Justices want this vehicle now.
5. The response request came at the *first* distribution, before three of the
   four amici had filed, so it reflects one or two chambers' interest rather
   than a Court-wide appetite, and response-requested petitions are still
   denied far more often than granted.

## Net

Anchor 17%; the response request and the dissent below push up, the absence of
a split, the vehicle defects and the Court's recent denials in this area push
harder down. I land at **0.14**, a little under the anchor. I would not be
surprised by a grant; I would be surprised by a grant *without* a relist first.

## Other claims

- **relist-increment 0.33.** Roughly P(grant) x 0.75 (the Court now relists
  almost every petition it grants at least once) plus P(deny) x 0.25 (a Thomas
  dissent from denial is plausible and takes a relist to write; the long
  conference also produces more relists than an ordinary one).
- **cvsg-increment 0.04.** No federal party or federal statute; CVSGs on state
  campaign-finance disclosure are rare.
- **summary-disposition-route 0.05** (conditional on grant). No intervening
  decision favors the petitioner, so no GVR path; a grant here is plenary.
- **dissent-from-denial 0.20** (conditional on denial). Thomas is the natural
  writer; the response request and amici raise the chance above the ordinary
  paid petition, but most disclosure denials in this period have been silent.
- **big_case_score 0.55.** Decided, this would govern the pre-election
  disclosure regimes of many states and the federal electioneering rules'
  state analogues. Significant, not a headline case.

## Where to discount me

- The recent-denials pattern and the NRSC characterization are memory-based
  or second-hand (the BIO); the CourtListener docket searches for the
  comparable petitions returned nothing and the NRSC opinion body was
  unavailable. If NRSC in fact contained language questioning disclosure, my
  number is a few points too low.
- I did not read the reply brief; if it squarely engages the §(3)(c)
  construction and the standing point, the vehicle discount is overstated.
- No corpus cut conditions on response-requested, so the size of that
  adjustment is judgment, not a measured rate.
- The two generic `fedcourts query` pulls surfaced no disclosure-law priors;
  they contributed nothing beyond confirming the corpus service was reachable.
