# Rationale for the numbers (claude-baseline, run 20260924T182556Z)

## What I read

Provisioned inputs: `record/snapshots/2026-09-23.json` (the baseline named by
`context.json`), `record/context.json` (mode `forward`, band `elevated` under
`sal-v4`, `distribution_count` 2, no CVSG, term 2025, `cutoff` null),
`event.yaml` (kind `petition`, no stage field, so cert-stage, moment
distribution), and all three provisioned documents: `questions-presented.txt`,
`petition.txt` (47 pages, text extracted cleanly), and
`brief-in-opposition.txt`, which concatenates both briefs in opposition (the
Oregon state respondents' brief filed September 4, 2026 and the PeaceHealth
respondents' brief filed September 8, 2026; 51 pages, not truncated). I also
read the committed `metrics/statpack.md` for base rates.

## Anchor

Cert-stage cell with a frozen band, so the anchor is the salience-band table's
bracketed `reached` rate for `elevated` under `sal-v4`, which matches the
context's `salience_version`. Pooling the eight rendered Terms strictly before
OT2025 (OT2017 through OT2024, weighted by the bracketed n):

| pool | reached rate | n |
| --- | --- | --- |
| elevated, OT2017-OT2024 | 17.2% | 2810 |
| baseline, OT2017-OT2024 (for contrast) | 5.1% | 11580 |

That 17.2% is the grant family (plenary grants plus GVRs) among paid petitions
that ever reached `elevated`, and it is the yardstick my skill is scored
against. The relist-count cut (bucket 1: about 8% granted plus 5% GVR) and the
CVSG-none cut (about 4% granted plus 2% GVR) describe the same population from
other angles and sit near or below it.

## Adjustments

**Down, hard, on the merits of the cert case.** Every consideration the Court
ordinarily weighs points to denial, and unusually strongly:

- The Ninth Circuit's decision is an unpublished memorandum disposition that
  applies its own published decision in Curtis v. Inslee, 154 F.4th 678 (9th
  Cir. 2025). Both briefs in opposition state, and the petition itself
  acknowledged Curtis was then pending, that this Court denied certiorari in
  Curtis (No. 25-1119) on June 1, 2026. Curtis involved the same counsel, the
  same PeaceHealth defendants, the same statutory and treaty sources, and the
  same party-presentation argument. The Court also denied Sweeney v. University
  of Colorado Hospital Authority (No. 25-1055) and Horsley v. Kaiser
  (No. 25-1203) the same day, and Health Freedom Defense Fund v. Carvalho
  (No. 25-765) on May 18, 2026. The petition (filed May 4) named all four as
  candidates for consolidated review; all four have since been denied. That
  is public information predating my snapshot and is the single most decisive
  input here.
- The question presented was not decided below. Both the district court and
  the panel resolved the case on the ground that petitioners' own complaint
  pleaded the product was an authorized vaccine, which Jacobson forecloses;
  the "investigational drug" and "waiver of judicial remedies" framing in the
  QP is not what the Ninth Circuit ruled on. The state respondents' brief makes
  this its lead argument and the petition does not squarely contest Jacobson's
  core holding.
- No circuit split. The respondents list uniform authority from the Second,
  Third, Fifth, Sixth, Seventh, Ninth, and Tenth Circuits applying rational
  basis to COVID-19 vaccination requirements, with cert denied in each case
  that reached this Court. The petition claims conflict with this Court's
  precedents (Rutherford, Oakland Cannabis, Cleburne, Sineneng-Smith) rather
  than a circuit conflict, and those analogies are strained.
- Vehicle problems the Ninth Circuit left open: whether PeaceHealth is a state
  actor and whether all respondents have qualified immunity (the district
  court found both against petitioners). The suit is damages-only and the
  mandates were rescinded in 2022 and repealed in 2023.
- The petition's theory rests on the ICCPR, the Belmont Report, Federalwide
  Assurance agreements, and the CDC provider agreement as sources of a
  Fourteenth Amendment right. That is not a theory this Court has shown any
  appetite for, and the petitioner's counsel is a solo practitioner whose
  materially identical petition was just denied.

**Up, modestly, on the docket signals.** The Court called for a response on
June 17, 2026 after both sets of respondents had waived, and did so sixteen
days after denying Curtis. A call for a response is an affirmative act by at
least one chambers and is what put this petition in the `elevated` band; that
the call came after the Curtis denial suggests a Justice saw something in this
petition's PREP Act immunity and compelled-waiver framing that Curtis did not
present, or simply wanted the opposition on file before denying a petition
with an amicus brief coming. The New Civil Liberties Alliance amicus brief
(filed July 17, 2026) is a serious repeat filer and adds some weight. Oregon's
Solicitor General authored the state brief, so the Court has a full
opposition.

## Where I land

P(grant) = 0.06, about a third of the band anchor. The anchor already prices
the call for a response; what it cannot price is that the Court denied the
controlling published decision, from the same circuit and the same counsel,
weeks before this petition was fully briefed. A call for a response is
followed by denial in the large majority of cases even without that history.
I keep the number above the `baseline` floor because a chambers did act on
this petition and because the compelled-waiver angle is at least distinct
from Curtis. `predicted_disposition` is `denied`, `granted` is 0.

## The other claims

- **relist-increment 0.30.** Two distributions shown. A first relist after
  the long conference is common for petitions that drew a call for a response
  and an amicus brief, particularly if a Justice is weighing a statement. The
  hazard from one relist to a second is low, so this is mostly a one-relist
  probability.
- **cvsg-increment 0.02.** No federal interest at the docket level; damages
  suit over repealed state and private measures.
- **summary-disposition-route 0.10** (conditional on grant). No intervening
  decision to GVR against; the cert-order share of grants in the pack is not
  published as a cut I can read directly, and nothing here argues for a
  summary route.
- **dissent-from-denial 0.15** (conditional on denial). The call for a
  response and the amicus brief's Jacobson argument raise this above the
  docket-wide rate, but the Curtis and Carvalho denials drew no noted
  dissent per the briefs in opposition, so I do not expect one here either.

## Uncertainty and where to discount me

- I could not verify anything outside the provisioned record. The CourtListener
  MCP search returned zero results for every query, including a lookup of a
  known SCOTUS docket number, so I treated it as unavailable. My statements
  about the Curtis, Sweeney, Horsley, and Carvalho denials rest on the two
  briefs in opposition (adversarial filings, but on a checkable point both
  respondents state consistently and the petition anticipated).
- `fedcourts query` has no subject filter, so the priors it returned were not
  topically relevant and did not move the number.
- I do not know why the response was called for. If it reflects real interest
  in the PREP Act compelled-waiver theory from a Justice inclined to write, the
  relist and dissent-from-denial numbers are too low; the grant number would
  still be low, because one chambers' interest is not four votes on an
  unpublished vehicle with antecedent immunity problems.
- Corpus-freshness note: the statpack figures are the committed pack's, and the
  OT2025 row of the band table is partly censored; I anchored only on the
  strictly prior Terms as the prompt directs.
