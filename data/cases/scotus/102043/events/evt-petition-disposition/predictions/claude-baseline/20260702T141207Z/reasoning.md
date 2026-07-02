# scotus/102043 — evt-petition-disposition

## What the snapshot shows

The snapshot (`data/cases/scotus/102043/record/snapshots/2026-07-02.json`) is
nearly bare: a caption — *Cincinnati, N. O. & T. P. Ry. Co. v. Interstate
Commerce Commission. Interstate Commerce Commission v. Cincinnati, N. O. & T. P.
Ry. Co.* — the docket number "Nos. 394 and 473", a link to one opinion cluster,
and nothing else. No docket entries, no filing or termination dates, no parties
beyond the caption, no panel.

Three inferences are available from the snapshot alone:

1. **This is not a discretionary certiorari petition.** The paired docket
   numbers and the mirrored caption mark cross-appeals: the railway and the
   Commission each appealed from the decree below. The dual-appeal form places
   the case in the pre-1925 era of largely mandatory Supreme Court appellate
   jurisdiction, where the Court took the case as of right and disposed of it
   on the merits (affirm / reverse / modify) rather than granting or denying
   review.
2. **The case was decided.** The docket links an opinion cluster, so the Court
   reached a merits disposition rather than dismissing the appeals unresolved.
3. **The subject matter is ICC rate regulation** — a railway against the
   Interstate Commerce Commission, i.e. review of an ICC order under the
   Interstate Commerce Act of 1887.

## Governing standard

For a mandatory-jurisdiction cross-appeal of that era there is no
"grant/deny" gate: the operative question is how the Court disposed of the
decree below. In the schema's disposition vocabulary, an affirmance, reversal,
or modification on the merits maps to **other**; "granted"/"denied" fit
discretionary petitions, and "dismissed" fits appeals dismissed for want of
jurisdiction or prosecution.

## Base rates (corpus)

`fedcourts stats --court scotus --resolved-only` over the 296 resolved SCOTUS
cases in the corpus (which skews to this same historical era):

| disposition | share |
|---|---|
| other | 78.4% |
| dismissed | 15.9% |
| denied | 4.4% |
| granted | 1.4% |

The snapshot's evidence that the case produced a merits opinion pushes the
probability mass further toward "other" and away from "dismissed" relative to
the base rate.

## Prediction

- **predicted_disposition: other** — a merits disposition of the cross-appeals
  (affirm/reverse/modify the decree in the ICC enforcement suit), which is how
  the corpus codes this era's decided appeals.
- **granted: 0, probability (P(granted)): 0.02** — near the corpus base rate of
  1.4% for "granted"; the small residual allows for the outcome coder mapping a
  partial win for the appealing party onto "granted"/"granted-in-part".
- **confidence: 0.6** — the disposition *class* is well supported by the
  cross-appeal form, the opinion cluster, and the base rates, but the snapshot
  carries no substantive facts, and how the reconciler codes a
  nineteenth-century merits decree onto this schema's petition-oriented
  vocabulary is the largest source of uncertainty.
- **votes: none** — the snapshot identifies no panel, so per-justice votes
  would be invented.

## Candor notes (also raised in `flags.json`)

- **Historical-outcome leakage.** The caption and docket numbers identify a
  well-known, long-decided case (the 1896 "Social Circle" rate case reported at
  162 U.S. 184, in which the Court held the ICC lacked power to prescribe
  future rates while sustaining its condemnation of the existing rate). Its
  outcome is public history and inside any modern model's training data, so a
  "prediction" here cannot measure genuine forecasting skill. I anchored the
  numbers above on the snapshot and corpus base rates, but the leakage is
  unavoidable and worth weighing when scoring this cell.
- **Scope.** A pre-1925 mandatory-jurisdiction appeal appears to be exactly the
  class the predict scope is documented to exclude (see the scope predicates
  described for `corpus-scope-audit` in `docs/cli.md`), yet this event reached
  the predict matrix as open and predictable. The exclusion latch may not have
  caught this docket.
- **Data quality.** The snapshot has no docket entries and no dates, so any
  predictor sees essentially only the caption.
