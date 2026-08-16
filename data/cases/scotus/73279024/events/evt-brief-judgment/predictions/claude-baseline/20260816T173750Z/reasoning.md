# Why 0.84 — rationale for my own numbers

## The scored baseline

The committed statpack's "The merits docket (granted cases)" section publishes
an `excluded` count (67), so it is quotable and is the bar my Brier skill is
scored against. This case's grant date is March 9, 2026 (the docket's
"Petition GRANTED" entry; the evt-order-judgment sibling opened then), so the
grant Term is OT2025 and the pool is grant Terms 2015–2024. The table renders
every Term the pack holds; 2015 and 2016 carry no parsed judgments, so the
pool is the 2017–2024 rows: 515 parsed judgments, 359 disturbed — **69.7%**,
comfortably past the 30-parsed floor. My 0.84 is +14 points on that baseline.

## What moved me up

- **The Solicitor General is the petitioner, and the Court granted.** The
  Court rarely takes a government petition to affirm; the grant itself — after
  only three distributions, no CVSG needed (the SG is already the petitioner) —
  is the strongest single signal in the record.
- **The decision below is a divided Ninth Circuit panel** (Berzon, joined by
  Miller; VanDyke dissenting at both panel and en banc stages), the
  most-disturbed circuit, with a detailed dissent that reads as a roadmap for
  reversal on QP1 ("submission of an application is a far cry from final
  agency action") and warns of "massive implications" — the vehicle the
  current Court routinely takes to reverse.
- **Two independent questions, either sufficient.** The government wins on
  QP1 (no final agency action) or QP2 (RCRA displaces NEPA at the application
  stage); respondent must win both to hold its judgment. That disjunctive
  structure compounds the government's advantage.
- **Doctrinal wind.** Seven County Infrastructure Coalition v. Eagle County
  (2025) — cited by both sides — shows a Court (unanimous in judgment) intent
  on cutting back NEPA litigation; the petition's Bennett/Franklin argument on
  QP1 is orthodox and the claimed circuit conflicts (Alabama ex rel. Siegelman,
  the separate-actor finality cases) give a conventional error-plus-conflict
  frame.

## What held me back from higher

- **Respondent's QP2 textual argument is strong.** The 2023 Fiscal
  Responsibility Act codified exactly two displacement routes at 42 U.S.C.
  4336(a)(2)–(3); the government's "functional equivalence" theory is a
  lower-court gloss never applied by this Court, and extending it to a
  non-regulator agency is novel. A textualist Court could balk on QP2 — which
  is partly why I expect the finality exit instead.
- **Respondent's finality reframing is not frivolous**: the challenge as pled
  targets the Air Force's consummated decision to continue OD operations, and
  the application's automatic continuation of the 2018 permit is a concrete
  legal consequence (Sackett, Hawkes, Biden v. Texas all lean respondent's
  way on "mere possibility of revision"). Earthjustice's merits team briefed
  it well. This keeps a genuine affirmance path alive, ~10–15%.
- Residual mass on a DIG or another undisturbed exit is small (~2%).

0.84 ≈ 69.7% baseline, shifted up for the SG-petitioner grant posture, the
divided panel below, and the disjunctive QP structure, less the real
affirmance path respondent's textual and record arguments keep open.

## Votes and judgment label

`reversed` over `vacated`: both QPs resolve as legal error and the petition
asks for reversal outright; a remand-for-reconsideration posture has no
obvious trigger. The 7–2 lineup is my modal single lineup, but it is the
least certain part of this forecast: a unanimous reversal on finality (or
8–1, or liberal concurrences in the judgment as in Seven County) is nearly as
likely as the 7–2 I committed. Discount the per-Justice calls accordingly;
Sotomayor/Jackson as dissenters is a coin-flip-plus, not a strong signal.

## Inputs, retrieval, and where to discount me

- **Mode: forward.** The judgment does not exist; argument is set for
  October 7, 2026. No outcome-revealing material surfaced.
- **CourtListener MCP was rate-limited (HTTP 429) on my first call**, so I
  made no live retrieval; per the prompt I degraded to the provisioned inputs
  and corpus tooling (flagged in `flags.json`).
- **What I actually read:** the docket snapshot; the QP text; the cert
  petition (whose appendix includes the full Ninth Circuit opinion and
  VanDyke dissent); and the provisioned respondent file, which concatenates
  the BIO *and* respondent's July 20, 2026 merits brief — so respondent's
  merits-stage argument was on my desk. **Petitioners' merits brief (filed
  May 22, 2026) was not provisioned and I could not retrieve it**; I read its
  themes through the cert petition and respondent's responses to "Pet. Br."
  citations. The government-side merits advocacy is therefore inferred from
  cert-stage papers — a real gap, though the SG's merits brief rarely departs
  from its petition.
- One `fedcourts query` (citation lookup for Seven County) returned no rows —
  the citation column is sparse (161 of ~590k scotus rows) — so no corpus
  priors informed this cell beyond the statpack.
- I know the Ninth Circuit decision (February 2025) and this litigation from
  training (pre-cutoff public material); that predates the snapshot and is
  legitimate forward signal, and I know no outcome because none exists.
- The salience band in my context (`federal`) is a cert construct; per the
  merits-stage rule I did not anchor on it and no flag is owed.
