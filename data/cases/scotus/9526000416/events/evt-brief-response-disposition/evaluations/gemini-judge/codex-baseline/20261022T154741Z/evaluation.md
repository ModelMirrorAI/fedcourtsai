# Evaluation of `codex-baseline` (`scotus/9526000416` — `evt-brief-response-disposition`)

## Stage and Baseline Rules

This is an **interim-stage** cell (`stage: interim`, moment `response-filed`) scoring the disposition of the Solicitor General's emergency stay application (`26A416`) in *Trump v. Kingdom*. Under the interim-stage evaluation contract:
- `segment_base_rate` and `brier_skill_score` are omitted here and left for `stamp-cell` to compute and stamp from the committed statpack's substantive interim slice over strictly prior application-Terms (which clears the registered 50-resolution floor in `metrics/statpack.md`), and `base_rate_basis` is left `null` structurally because an application is not a salience-band product.
- `vote_accuracy` is omitted (interim votes are never scored, and `codex-baseline` predicted none).
- `claim_scores` is omitted and computed by the harness (`fedcourtsai.pipeline.claims`) over the declared `interim-v1` set.
- `semantic_grades` is omitted (merits cells only).

## Quantitative Accuracy

- **Predicted disposition:** `granted` (`probability` = `0.61`)
- **Actual outcome:** `denied` (`actual_granted` = `0`, resolved October 21, 2026; Justices Thomas and Alito noted they would grant the application)
- **`correct`:** `0`
- **`brier_score`:** `(0.61 - 0)^2 = 0.3721`

## Reasoning Quality (`0.82`)

`codex-baseline` predicted `granted` with `probability = 0.61` (the lowest grant probability and best Brier score among the three candidates, though still on the wrong side of the binary outcome). Its `reasoning.md` demonstrates strong analytical discipline:

1. **Retrieval and Adversarial Balance:** Recognizing that the October 8 opposition brief was referenced in the snapshot but not yet provisioned in `record/documents/`, `codex-baseline` fetched the opposition PDF directly from its supremecourt.gov URL and read its substantive sections. This allowed `codex-baseline` to weigh the respondents' arguments—that BOP ignored its own multi-decade treatment experience under the APA, that the injunction preserved individualized clinical judgment rather than mandating blanket treatment, that the government forfeited its PLRA objections below, and that interrupting ongoing care posed severe harm—against the Solicitor General's APA deference and PLRA scope arguments.
2. **Calibration and Outcome Decomposition:** `codex-baseline` carefully analyzed the statpack's interim baseline, noting the uneven parse coverage across prior Terms and the selection effects of the `response-filed` moment. It decomposed the outcome space into `0.61` full grant, `0.18` mixed partial relief (recognizing that the severability of surgical provisions created a substantial partial-stay risk that resolves as ungranted), `0.19` outright denial, and `0.02` withdrawal/dismissal. While it still gave too much weight to the Solicitor General's posture relative to the record-based APA and forfeiture problems that led the Court to deny the stay in full, its restraint in stopping at `0.61` and its explicit treatment of epistemic limits were well-reasoned.

## Leakage Assessment

- **Mode:** `forward` (prediction created `2026-10-09T14:38:17Z`; event resolved `2026-10-21`).
- **Assessment:** `retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`.
- **Evidence:** The harness-captured `retrieval_log.json` shows local file reads, one unobserved `web-search` attempt on the exact October 8 opposition PDF URL, and Python `urllib` fetches of that same pre-decision opposition PDF (`20261008145929279_2026.10.08 Respondents Opposition to Stay Application - Trump v. Kingdom 26A416.pdf`). A `find data -name AGENTS.md -not -path 'data/qp-topics/*'` command properly excluded `data/qp-topics/`. The application was genuinely open on October 9, 2026, and no outcome-revealing material existed or was retrieved.
