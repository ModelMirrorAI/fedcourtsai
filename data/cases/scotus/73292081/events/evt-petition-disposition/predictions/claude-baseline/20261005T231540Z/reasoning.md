# Why 0.14, and why the other numbers

Mode: **forward** (`record/context.json`), no cutoff; snapshot `2026-10-05.json`.
Conditioning frozen by the harness: `band: baseline` under `sal-v4`,
`distribution_count: 1`, `cvsg_date: null`, `term: 2025`, `signals_observable: true`.

## Anchor

The statpack's "Segment base rate by salience band (sal-v4)" table matches my context's
salience version and carries a `baseline` column. Pooling the bracketed `reached`
figures over every rendered Term strictly before OT2025 (OT2017 through OT2024, weighted
by their `n`) gives roughly **5.1%** (the per-Term values run 4.5% to 5.9%). That is the
grant-family rate for a paid private petition that had reached the baseline band, and it is
the yardstick this cell is scored against. For shape only: the relist-count cut puts a
petition that ends at one distribution at 8.2% granted + 5.1% GVR, and the capital-case
marking cut puts paid capital petitions at 11.8% granted + 5.6% GVR against 6.5% for
unmarked ones (a marginal split, correlated with everything else, read as an upper bound).

## What moved me up from the anchor

- **Capital case with unusually strong equities.** Both State forensic witnesses (the
  toxicologist and the medical examiner) have recanted; the toxicology report is
  internally contradictory on its face; two successive elected Nueces County DAs have said
  relief is warranted. The reply cites Newberry v. Texas, No. 25-862 (GVR, June 22, 2026),
  as a recent instance of the Court sending a Texas capital case back to consider the DA's
  position, which shows a live GVR route that does not depend on the AG's agreement.
- **Record requested on August 11, 2026**, before the conference. In a capital case this
  usually means at least one chambers is looking past the pool memo, whether toward a
  grant, a GVR, or a dissent from denial.
- **The 2244(b)(3)(E) bar does not reach the lead question.** The December 4, 2025 Fifth
  Circuit ruling affirmed a second-gate dismissal of an *authorized* successive petition
  (COA granted sua sponte), so Question 1 is reviewable on certiorari; the State's
  jurisdictional argument is aimed at Question 3 only.
- **Experienced counsel, a coherent split narrative** (Fifth and Eleventh imputing a
  reasonable attorney's knowledge against the Sixth's applicant-focused test, plus the
  § 2244(d)(1)(D) analogues), and the Fifth Circuit's own footnote conceding its cases take
  "somewhat different approaches."
- **The companion petition, No. 26-353,** gives the Court a cleaner vehicle on the
  successiveness question; if it takes that one, this petition likely gets a GVR, which
  counts as a grant on the scored axis.

## What held me down

- **Unpublished per curiam** opinion, and an **unchallenged alternative holding** that
  Vasquez fails the § 2244(b)(2)(B)(ii) innocence prong. The petition never engages it; the
  reply's answer (the Fifth Circuit skipped second-gate review) is clever but is a
  reply-brief argument the State will call waived. A pool memo would lead with this.
- **The split is contestable.** The Fifth Circuit framed counsel's awareness as
  "relevant," said the petition fails "under any of these standards," and footnoted that
  Vasquez did not contend a reasonable attorney would not have been on notice. The State's
  "manufactured split" argument is credible enough to lose a fourth vote.
- **The current Court's AEDPA posture** (Shinn v. Ramirez, Jones v. Hendrix, Bowe) runs
  against expanding access through the successive-petition gate, and the agency-law
  "rogue agent" theory for Question 1 reads as an equitable exception dressed as
  statutory construction.
- **State factual findings** that the cocaine evidence was reliable and the negative
  screen likely clerical, adopted by the CCA, would get § 2254(e)(1) deference and blunt
  the "false evidence" framing. Question 4 has preservation problems and the Texas
  Supreme Court denied mandamus on the AG/DA authority question in June 2026.
- The band is `baseline`, not `elevated`, which tells me the salience scorer saw nothing in
  the docket beyond an ordinary once-distributed paid petition.

Net: roughly 2.5x to 3x the anchor, i.e. **0.14** for any grant including a GVR, with
`denied` as the modal disposition.

## The other claims

- `relist-increment` 0.85: the September 17 letter asks the Court to consider No. 26-353
  (response due October 16) alongside this petition; holds of this kind are redistributed
  when the companion is ripe. The residual is the chance the Court simply denied at the
  long conference or disposes of the hold without a fresh distribution entry.
- `cvsg-increment` 0.02: no federal interest.
- `summary-disposition-route` 0.5 (conditional on grant): the GVR path (Newberry-style,
  or in light of No. 26-353) is as plausible as plenary review of Question 1; the pack's
  prior-Term GVR share of the grant family is in the same neighborhood.
- `dissent-from-denial` 0.38: Justice Sotomayor has written on exactly the Question 3
  issue (Storey v. Lumpkin statement; Bernard v. United States dissent), the equities are
  the kind that draw a statement, and the record request is consistent with one.

## Uncertainties and where to discount me

- I did not read the Fifth Circuit's opinion in No. 26-70008 or the State's response to
  the motion to defer (its PDF had no text layer), only the petitioner's account of each.
- `petition.txt` is truncated (155 pages): the appendix with the DA statements and the
  first-gate authorization order is missing, so my read of the DA concessions is from the
  petition body and the BIO.
- I am inferring the hold posture from the filings and the absence of any post-September
  28 entry; if the snapshot was captured before the October 5 order list posted, a denial
  could already exist that I cannot see.
- The capital-case cut and the record-request signal overlap with the relist signal, so
  stacking them risks double counting; I have tried to treat them as one adjustment.

## Inputs used

Provisioned: the snapshot, `questions-presented.txt`, `petition.txt` (truncated),
`brief-in-opposition.txt`, `documents.json`, `context.json`, `event.yaml`. Retrieved in
forward mode: the reply brief, the motion to defer, the September 17 letter (all from
this docket's own filings), the No. 26-353 docket page, two CourtListener opinion searches
(no hits), one `fedcourts query`, and the committed `metrics/statpack.md`.
