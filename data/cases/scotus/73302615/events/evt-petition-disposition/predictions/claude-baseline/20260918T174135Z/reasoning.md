# Why 0.21, and where to discount me

## What I read

Provisioned inputs: `record/snapshots/2026-09-18.json` (payload created
08/28/2026, provenance `as-stored`), `record/context.json` (mode `forward`,
band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, term 2025,
`signals_observable` true), the event definition, and all three provisioned
documents: `questions-presented.txt`, `petition.txt` (51 pp., full text) and
`brief-in-opposition.txt` (48 pp., full text); `documents.json` shows none
empty or truncated. Beyond that: `metrics/statpack.md`, two `fedcourts query`
calls, and four CourtListener MCP calls (see `retrieval.md`). CourtListener's
docket record shows no termination date, so the cell is correctly forward.

## Anchor

The evaluator scores this cell against the `elevated` band's bracketed
`reached` rate over Terms strictly before OT2025. Pooling the eight rendered
prior Terms (2017 through 2024) in the sal-v4 segment table:

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |
| pooled | 17.2% | 2810 |

So the anchor is about 0.17. The `salience_version` in context (`sal-v4`)
matches the table heading, so no mismatch flag is owed.

Cross-checks from the paid scored segment cuts: relist bucket 1 (two
distributions) runs granted 8.2% + gvr 5.1% = 13.3% grant family; the
no-CVSG bucket runs 6.3%; the D.C. Circuit is the highest-granting originating
circuit in the modern-cert table (granted 5.5% + gvr 2.3%). The relist-bucket
figure understates this docket's position because the second distribution here
followed a call for a response, not a bare relist, and a CFR after a waiver is
a stronger signal than a redistribution.

## Adjustments up (from 0.17 toward the low 0.20s)

- **The Court called for a response after a waiver.** At least one Justice
  wanted to see the opposition. That is the docket's clearest signal.
- **A real, acknowledged split.** The decision below expressly rejects the
  Second and Fifth Circuits' domestic-nexus reading and the Restatement
  (Fourth) already recorded the tension; the New York and Texas high courts are
  on petitioners' side. The BIO's answer is that the split is stale and
  shallow, not that it is illusory.
- **Repeat visitor.** The Court granted in this same litigation in 2016 and
  reversed the D.C. Circuit; it granted in Philipp and Simon on adjacent FSIA
  expropriation questions. Foreign-sovereign expropriation is a subject the
  Court reliably takes.
- **Counsel and clarity.** Vinson & Elkins for petitioners, Gibson Dunn
  (Estrada) for respondent; the QP is a single clean statutory question, the
  facts are undisputed, and a ruling for petitioners ends the case.

## Adjustments down (back toward 0.21 rather than higher)

- **Vehicle.** This is an interlocutory appeal, and the act-of-state defense
  reached the D.C. Circuit only via pendent appellate jurisdiction attached to a
  collateral-order immunity appeal that petitioners no longer contest. The
  Court is skeptical of pendent appellate jurisdiction (Swint) and routinely
  cites interlocutory posture as a reason to wait. This is the strongest point
  in the BIO and I weight it heavily.
- **Importance is thin in practice.** The BIO shows the question has been
  outcome-determinative essentially only in this case in forty years, because
  the FSIA's expropriation exception screens out most foreign-located-property
  suits before act of state arises. Petitioners' "world court" framing is
  overstated.
- **The Court may agree with the D.C. Circuit.** Simon (2025) already
  described the Amendment as lacking the commercial-nexus limitation the FSIA
  has, and the textualist majority is unlikely to be moved by 1964 floor
  statements. A Court that expects to affirm has less appetite to grant to
  resolve a split that the other side's courts may abandon on their own.
- **Petitioner's representation is unsettled.** The August 26 entry is a
  withdrawal letter from petitioner's former counsel and the docket lists no
  attorney for petitioner. I read this against the 2026 political transition in
  Venezuela and the resulting changes in who controls PDVSA, which predate the
  snapshot and are legitimate forward context. It raises the withdrawn or
  dismissed tail (settlement or abandonment) and may make the Court hesitant
  to grant into a docket with no petitioner counsel of record.

Net: 0.21 for the grant family, `predicted_disposition` denied. I hold
roughly 0.72 denied, 0.21 grant family (almost all plenary), 0.07 dismissed or
withdrawn.

## The other claims

- **relist-increment 0.52.** From two distributions. Paths to another
  distribution: a CVSG (which always redistributes later), a relist before a
  grant (now the Court's near-universal practice), and a relist before a denial
  with a statement. The single most likely path, outright denial on October 5,
  is under half.
- **cvsg-increment 0.35.** No CVSG on the docket. The Court invited the SG in
  this case's 2016 trip and in Philipp and Simon; the statute reserves a role
  for the President; the executive has a direct interest in PDVSA litigation in
  2026. Against: the Court already used one step on a CFR and may simply deny
  on vehicle grounds. The statpack's CVSG cut (29.4% granted, 5.5% gvr among
  CVSG'd paid petitions) is why a CVSG here would move my grant number sharply.
- **summary-disposition-route 0.05** (conditional on grant). No intervening
  decision; a fresh split is plenary material. The elevated band's gvr share
  of grants (about a third) reflects GVR-in-light-of cases this docket does not
  resemble.
- **dissent-from-denial 0.13** (conditional on denial). A statement about the
  interlocutory posture or a short dissent on act-of-state grounds is
  plausible for a CFR'd petition with an acknowledged split, but most denials
  after a CFR are bare.

## Uncertainty and where to discount me

- The CFR-conditional grant rate is not a statpack cut; my sense that a CFR
  after waiver roughly doubles the base rate is judgment, not a computed
  figure.
- I cannot see whether new counsel has appeared for petitioner after August
  26; CourtListener's SCOTUS docket coverage does not carry the entries. If
  petitioner is unrepresented at the September 28 conference the dismissal tail
  is larger than I have it.
- My CVSG number leans on pattern in prior FSIA cases and on 2026 political
  context I hold from training rather than from any provisioned document.
- Corpus retrieval was low-value: the `--era 2020s --disposition granted`
  query returned mostly substantive interim applications and unrelated cert
  grants, and the citation filter has near-zero coverage. Priors here rest on
  the statpack and the briefs, not on retrieved analogues.
