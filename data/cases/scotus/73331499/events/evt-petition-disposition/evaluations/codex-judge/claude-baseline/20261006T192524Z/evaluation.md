# Evaluation: claude-baseline

## Outcome and numerical scores

This is a cert-stage petition-disposition evaluation. The provisioned outcome records denial on October 5, 2026, with `actual_granted = 0`. The September 16 prediction names `denied`, so exact-label correctness is **1**. Its grant probability of **0.025** gives Brier **0.000625**. The correct denial does not establish that the Court adopted any proposed doctrinal or vehicle rationale: the outcome supplies no reasons for denying review.

The prediction froze `baseline`, `sal-v4`, and docket-number Term **2025**. The committed statpack's sal-v4 table therefore supplies the **risk-set**, not terminal-band, baseline. Pooling its bracketed reached rates across every displayed strictly prior Term, **2017–2024**, gives approximate weighted grants **592.925** over weighted resolved denominator **11,580**, or **0.05120250431778929**. The published percentages are rounded and denial-reweighted; 592.925 is an implied numerator, not an observed grant count. Terms 2025 and 2026 are excluded. The caption renders **10 of 10** available Terms, so there is no displayed-window truncation to flag. The baseline's Brier is approximately **0.002621696448413231** and `1 - 0.000625 / baseline_Brier` gives skill **0.7616047424642627**. This is one realized comparison, not a claim of general forecast skill.

These are calculations from the supplied committed statpack, not a freshly queried corpus. Corpus-wide newest-pull and newest-snapshot vintage were not independently inspected. The predictor's frozen snapshot date is September 16, 2026; it is not a corpus freshness stamp. The evaluator's decided-docket context is not used to select the candidate's band.

## Reasoning quality: 0.72

The rationale correctly identifies the private-petitioner band despite a State respondent, selects the matching prior-Term reached population, and separates terminal relist/CVSG descriptions from forward probabilities. It engages both questions, distinguishes warrant particularity from subsequent DNA analysis, and openly acknowledges that the lower-court opinion and adversarial response were unavailable. Its modest grant probability remains uncertain rather than treating denial as inevitable.

Several downward adjustments are less well supported than the presentation suggests. The asserted disadvantage of an intermediate-state-court decision, the regional-counsel inference, and the claim about historically letting this kind of unsympathetic case percolate lack a demonstrated comparison group. Alternative good-faith or later-warrant grounds are identified as possibilities, not established holdings. Most importantly, the characterization of the warrant cases as merely fact-pattern divergence does not adequately resolve the petition's concrete Belt comparison: the supplied petition describes missing unique profiles in that case too. The analysis did not obtain the opinion below, so its confident dismissal of the conflict merits qualification. The response-request decomposition is transparent but judgmental, not an empirically estimated transition model.

The second question ends incompletely in both staged texts; claude-baseline identifies that limitation. Attributing it confidently to counsel's drafting rather than the supplied representation exceeds what this record establishes. The cell-level flag preserves the incomplete-input concern without reconstructing missing words.

## Leakage and scoring boundaries

The captured log records **forward** mode and **30/30** result-marked calls captured. The prediction predates resolution. Its own-docket inquiries are ordinary forward retrieval; the log's extracted May 12 date and its account of a June 24 modification supply no indication of an already-decided petition. The logged results are digests, not full responses, so capture coverage alone does not prove their contents. Nevertheless, the queries and rationale show no outcome use. The correctly forecast October 5 order date is prospective text and is not evidence of leakage by itself. Assessment: retrieved outcome material **false**, influence **not_applicable**, suspected leakage **false**.

Only `reasoning.md` is qualitatively graded. The forecast was read for context, not scored. Quantitative claims remain for the harness; no semantic grade set is declared for cert, and cert votes are not scored. No harness-owned stamps or claim scores are supplied.
