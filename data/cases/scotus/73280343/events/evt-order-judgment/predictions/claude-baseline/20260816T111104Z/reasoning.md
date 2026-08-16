# Reasoning — why P(disturbed) = 0.74

## Anchor

The committed statpack's "The merits docket (granted cases)" section
publishes an `excluded` count, so its rate is quotable and is the registered
Brier baseline. This case's grant date is 2026-06-29 (from the event's
`opened_at` and the docket's "Petition GRANTED" entry), which is October Term
2025, so the pool is grant Terms 2015–2024. The table renders every Term the
pack holds; within the ten-Term window only 2017–2024 carry parsed judgments.
Pooling disturbed over parsed across those rows: 359/515 = **69.7%**
(coverage: 515 parsed of 557 granted in those Terms, with 55 excluded by the
pool guard; the 2024 row is the most pendency-censored, 73 parsed of 75
granted but 34 excluded). That clears the 30-parsed-judgment floor
comfortably, so 0.697 is the bar my skill is scored against.

## Adjustments

Up from 0.697 to **0.74**, for these reasons:

- **The Court took the majority-side circuit's case.** The Second Circuit
  (joining the Fourth) held terminated asylees categorically ineligible; the
  Fifth held the opposite. Granting the case that *entrenches* the majority
  rule, over the government's opposition (a BIO filed after three
  extensions), is the classic error-correction posture. The Court denied cert
  in Cela (the Fourth Circuit case) in 2024 while the government urged
  percolation; it granted here once the split deepened exactly as the
  government's Cela brief predicted it would.
- **The petitioners' textual argument is strong on this Court's own
  methods.** Three express continuing-status requirements inside § 1159
  (§ 1159(a)(1)(A), (b)(3), (b)(5)) against a bare "any alien granted asylum"
  in (b)'s prefatory clause; § 1159(b)(2)'s "after being granted asylum" as
  an unambiguous past-event use of the same words two paragraphs later. The
  meaningful-variation/expressio unius structure is the argument form this
  Court's statutory cases reward.
- **The judges are split 6–6 below, and the petitioners' side holds the
  unanimous panel.** Both circuits on the government's side divided (Robinson
  dissenting in the Second, Harris in part in the Fourth); the Fifth was
  unanimous. The government's reading has never commanded an undivided
  panel.

Held back from going higher:

- The government's reading is not frivolous — two circuits and the BIA
  adopted it, and "adjust ... the status" as implying an existing status,
  plus the § 1158(c) neighboring usage and the 1990 Act's statutory note, give
  an affirmance a real textual footing.
- The Court rules for the government in a substantial share of immigration
  statutory cases, and a grant from the majority side of a split is sometimes
  a grant to *ratify* the majority rule nationally.
- Base-rate discipline: 0.74 is only modestly above the 0.697 pool rate,
  which is where a merits forecast should sit absent unusually strong
  case-specific signal.

Residual mass: ~0.25 affirmed, ~0.01 DIG or equally divided (clean vehicle,
no apparent recusal). Within the 0.74 disturbed mass, reversed is the modal
class (~0.45), vacated ~0.20, affirmed-in-part ~0.09 — hence `judgment:
reversed`.

## Coherence of the structured fields

`probability` = 0.74 = the `judgment-disturbed` claim (one belief written
twice). `granted` = 1 because the named judgment (reversed) disturbs.
`predicted_disposition` = `other` per the merits-stage rule. The vote block
is banked, not scored today; it is my honest lineup, not a hedge.

## What I worked from, and where to discount me

- **Forward cell on the docket skeleton plus cert-stage documents.** The
  snapshot is current to 2026-08-16. No merits brief exists yet (petitioners'
  is due 2026-08-24), so this is the grant-moment forecast the cell is
  designed to be: petition, QP, and docket only. The petition text (47 pages)
  was provisioned and read in full through its argument sections.
- **The BIO was fetched but its text could not be extracted**
  (`empty_text: true` in `documents.json` — a scanned filing with no text
  layer). My read of the government's position is inference from the Cela
  history, the decision below, and the petition's characterization, not from
  the BIO's own text. Flagged in `flags.json`. This is my largest evidentiary
  gap; if the BIO contains an unusual concession or vehicle attack, I could
  not see it.
- **The salience band in `record/context.json` (`baseline`) is a cert
  construct** — the petition was banded before the grant — and per the stage
  rule I did not anchor on it. No flag owed.
- **Corpus retrieval added nothing**: one `fedcourts query` citation lookup
  (for Siwe's reporter cite) returned no rows — the citation column holds
  SCOTUS rows' own cites, and Siwe is a Fifth Circuit case. I did not use the
  CourtListener MCP tools; the provisioned record was current and complete
  enough that further retrieval was unlikely to move the number, and the
  merits advocacy I would most want does not exist yet.
- I carry general knowledge of this Court's immigration statutory
  jurisprudence from training; I do not know this case's outcome — none
  exists, the case will be argued no earlier than late 2026.
