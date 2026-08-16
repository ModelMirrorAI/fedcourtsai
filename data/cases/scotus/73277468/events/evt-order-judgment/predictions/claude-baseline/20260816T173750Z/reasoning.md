# Rationale for the numbers

**P(disturbed) = 0.72; judgment = `vacated`; votes = 9–0 majority.**

## Anchor

The committed `metrics/statpack.md` carries a "The merits docket (granted
cases)" section that publishes an `excluded` count (67 pool-guard exclusions),
so its rate is quotable and is the baseline my skill is scored against. This
case's grant date is 2026-03-30 (the event's `opened_at`), so its **grant Term
is OT2025** and the pool is grant Terms 2015–2024, strictly before mine. The
table renders parsed rows for Terms 2017–2024 only (Terms with no parsed
judgment are omitted, and unlike the cert tables it renders every Term the
pack holds, so 2015–2016 contribute nothing); pooling `disturbed` over
`parsed` across those rows gives **359/515 = 69.7%** (n=515, well over the
30-parsed floor). I anchored there and adjusted up modestly to **0.72**.

## What moved me off the anchor

Up from 69.7%:

- **The textual case for disturbance is strong and cross-camp.** Rule 8(c)(1)
  says a party "must" plead "any" affirmative defense; the Eleventh Circuit's
  *Hassan* rule lets a defendant skip the answer, skip Rule 15(a)(2) leave,
  outlast the Rule 16(b)(4) scheduling deadline, and then face only a
  prejudice inquiry. That structure — a lenient judge-made bypass reading two
  Rules out of the book — is the shape the current Court most reliably
  reverses in Federal Rules cases.
- **Even the intermediate rule disturbs.** The petition's own taxonomy is
  3-3-5: three circuits bar the maneuver outright, three add an
  undue-delay/diligence screen, five (including the Eleventh) ask prejudice
  only. On this record — counsel admitted he found the defense while drafting
  the summary-judgment motion, a year past the amendment deadline — adopting
  *either* stricter position disturbs. Only wholesale adoption of the most
  lenient rule affirms.
- **The grant itself.** The BIO's lead argument was factbound (the answer's
  "personal staff" admission gave notice), and the Court granted anyway after
  a call for response and three distributions, which reads as interest in the
  split, not the vehicle quibble.
- Petitioner's counsel of record is Eric Schnapper, a repeat and successful
  Supreme Court advocate in employment cases, which correlates with careful
  vehicle selection.

Down, keeping the adjustment small:

- **The equities run hard the other way.** The magistrate judge called the
  personal-staff exemption a "slam dunk" ("the facts screamed it"), found no
  prejudice, and offered to reopen discovery, which Younge declined to use.
  The Court sometimes takes the sympathetic-facts case precisely to bless the
  lenient rule, and the respondent's merits team (Jones Day; Stephen Petrany,
  a former Georgia Solicitor General) briefs a serious function-over-form
  line: Rule 61's harmless-error command, the Rules' deliberate omission of a
  waiver consequence for Rule 8(c) (contrast Rule 12(h)), Dolan, Day v.
  McDonough, Dupree, and Parrish (2025).
- The prejudice-only camp is the plurality position among the circuits, so
  affirmance would not be a doctrinal earthquake.
- A DIG is a live if small exit (~0.03) if the pleaded-notice dispute comes to
  dominate argument.

Net: 0.72, a small push above a baseline that already encodes the Court's
grant-to-reverse habit.

## Label and votes

Conditional on disturbance I weight `vacated` over `reversed` (0.40 vs 0.28 of
total mass): the likeliest opinion corrects the standard and remands for its
application (whether the DA's Office can satisfy Rule 15/16, or whether the
motion should be construed as one to amend), rather than holding the defense
forfeited itself. The all-nine `majority` lineup maximizes expected
intersection-only vote accuracy: each Justice's marginal probability of
landing majority-side exceeds one half when the modal outcomes are a unanimous
vacatur or a lopsided affirmance, and recent FRCP decisions (Dupree, Fort
Bend, Jones v. Bock — all unanimous) support the shape. I flag Alito and
Kavanaugh as the likeliest dissenters if the case splits; `confidence` 0.6
reflects that the lineup is the softest part of this forecast.

## What I worked from, and where to discount

- Cell mode `forward` — the judgment does not exist yet, so nothing retrieved
  can leak it. I worked from the provisioned snapshot (docket through
  2026-08-16, argument set 2026-11-02), the provisioned questions-presented,
  petition, and brief-in-opposition texts, and — because the provisioned
  `brief-in-opposition.txt` bundles it — the **respondent's merits brief**
  (filed August 2026). I did **not** retrieve the petitioner's merits brief or
  the amicus briefs (WLF supporting neither party; West Virginia + 16 states,
  Prof. Derek Muller, and Michael Showalter, all filed at the respondent's
  deadline), so my read of the merits advocacy is one-sided toward the
  respondent; discount the affirm-side weighting accordingly — I have seen the
  respondent's best case but only the cert-stage form of the petitioner's.
- The salience band in `record/context.json` (`high`) scores the settled cert
  grant and I did not anchor on it, per the stage rule.
- One corpus `fedcourts query` (for Dupree v. Younger as a prior by citation)
  returned nothing — the citation column is sparse (161 of 590,339 SCOTUS rows) —
  so no case-level priors informed the number; the statpack pool is the only
  quantitative anchor.
- No CVSG occurred; distributions (3) fed the grant and are spent. No
  outcome-revealing material surfaced — the case is genuinely pending.
