# Smith v. Commissioner, SSA — Tenth Circuit No. 24-6118 (appeal disposition)

**Prediction: affirmance (`denied`), P(granted) = 0.12.** In this event's
vocabulary I read `granted` as the appellant obtaining relief (reversal,
vacatur, or remand, in whole or in part) and `denied` as affirmance of the
judgment below — the same reading used by this predictor's sibling
appeal-disposition cells.

## What the record shows

The provisioned snapshot is thin: the CourtListener docket (id 69180294) for
Tenth Circuit No. 24-6118, *Smith v. Commissioner, SSA*, carries a single
docket entry — No. 26, filed 2024-09-20, described as "Case termination for
order and judgment" — plus a linked opinion cluster. No panel, no argument
date, no nature-of-suit, no party or counsel detail, and no filed-document
text was provisioned.

Two case-type inferences are safe from the caption and docket number alone:

1. **This is a Social Security benefits appeal.** "Smith v. Commissioner,
   SSA" is the standard caption of a 42 U.S.C. § 405(g) disability-benefits
   case in which the claimant lost below and appeals the district court's
   judgment affirming the Commissioner's denial of benefits. The Commissioner
   essentially never appears as an *appellant* in these cases at the circuit
   level; the appellant is virtually always the claimant.
2. **It comes from Oklahoma.** The Tenth Circuit assigns the -6xxx docket
   series to appeals from the Western District of Oklahoma, a district with a
   heavy § 405(g) caseload resolved largely by magistrate judges on consent.

The termination entry also tells me the *form* of disposition (without its
direction): a Tenth Circuit "order and judgment" is the court's unpublished
merits vehicle, typically issued by a three-judge panel after submission on
the briefs. That makes a clerk's-order dismissal (jurisdictional default,
failure to prosecute) or a voluntary withdrawal unlikely labels here, and it
is consistent with the fast track — docketed in 2024, decided within the
year — on which unargued SSA appeals ordinarily travel.

## The legal question and governing standard

In a § 405(g) appeal the circuit reviews the district court's decision de
novo but applies the same deferential standard to the agency: the ALJ's
decision stands if it is supported by **substantial evidence** and the
correct legal standards were applied. *Biestek v. Berryhill*, 587 U.S. 97
(2019), stresses how undemanding that threshold is — "more than a mere
scintilla." The court may not reweigh the evidence or substitute its judgment
for the Commissioner's (*Lax v. Astrue*, 489 F.3d 1080, 1084 (10th Cir.
2007)). Claimants win, when they do, almost exclusively on *legal* error —
an ALJ's failure to discuss significantly probative evidence, inadequate
step-four/five findings, or flawed evaluation of medical-source opinions
(*Clifton v. Chater*, 79 F.3d 1007 (10th Cir. 1996); *Winfrey v. Chater*, 92
F.3d 1017 (10th Cir. 1996)) — and the remedy is a remand for further
proceedings, not an award.

## Why affirmance is the likely outcome

1. **The posture is doubly filtered.** By the time a § 405(g) case reaches
   the court of appeals it has already survived one substantial-evidence
   review: the district court (here, almost certainly a W.D. Okla. magistrate
   judge) affirmed the ALJ. Cases with strong *Clifton*/*Winfrey*-type
   articulation errors are disproportionately caught and remanded at the
   district-court level, which remands a large share of SSA cases; the
   residue that goes up on appeal skews toward weak, fact-reweighing
   arguments.
2. **The standard of review does the rest.** Substantial-evidence review
   plus the bar on reweighing means the appellant must locate a discrete
   legal error. Absent any snapshot evidence of one (no briefs were
   provisioned), the base rate governs.
3. **Base rates.** Claimant success rates in courts of appeals in Social
   Security cases run roughly 10–20% nationally; the Tenth Circuit is
   somewhat more claimant-favorable than average on ALJ-articulation issues,
   which is why I sit at 0.12 rather than lower. The disposition form
   (unpublished order and judgment, no oral argument recorded) further skews
   toward affirmance — panels that intend to reverse argue and publish at a
   higher rate. The corpus statpack's Tenth Circuit cut (34 resolved cells:
   88.2% `other`, 11.8% `denied`, 0% `granted`) is too label-noisy to use
   directly but is at least directionally consistent with a low P(granted).

## Probability allocation

- `denied` (affirmed): ~0.83
- `granted` / `granted-in-part` (reversed/vacated/remanded in whole or part):
  ~0.12
- `dismissed` (jurisdictional or procedural termination): ~0.04 — discounted
  because the termination entry is an order and judgment, the merits vehicle
- `withdrawn` / `other`: ~0.01

`granted = 0`, `probability = 0.12`, `predicted_disposition = denied`.
No panel information is available, so I predict no per-judge votes.

## Caveats and degradations

- **The cell is marked `forward`, but the case is already decided.** The
  snapshot itself shows a termination entry dated 2024-09-20 and a linked
  opinion cluster. I treated the case as undecided, did not open the cluster,
  the termination document, or any search that could surface the disposition,
  and predicted from the pre-decision record plus base rates only. I do not
  know the actual outcome. Flagged in `flags.json`.
- **The CourtListener MCP server was down for this run** (every call returned
  a server-side `REDIS_URL is not set` error), so I could not retrieve the
  pre-decision docket entries, party/attorney detail, or the underlying
  district-court docket. The prediction rests on the provisioned snapshot,
  the committed statpack, and corpus queries.
- **The corpus had no Social Security priors** for the Tenth Circuit (topic
  queries returned nothing), and its generic ca10 priors are label-noisy, so
  the quantitative anchor is domain base rates rather than corpus neighbors.
