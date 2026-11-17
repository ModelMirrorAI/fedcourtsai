# Evaluation — codex-baseline, scotus/9026000210, evt-petition-arrival-disposition

**Stage:** cert (arrival moment). **Outcome:** petition denied on 2026-11-16, after a single distribution (conference of 2026-11-13), with no noted dissent or statement.

## Scores

- Predicted `granted` at P(grant) = 0.78; actual `denied`. `correct` = 0.
- `brier_score` = (0.78 − 0)² = 0.6084.
- `vote_accuracy` omitted (cert cell). The segment base rate, its basis and the skill score are the harness's to stamp and are left null; no semantic set is declared on a cert cell, so there is no `semantic_grades` block.

## Reasoning (`reasoning_quality` = 0.5)

This is a disciplined rationale that reached the wrong answer. The anchor is right and correctly computed: against the statpack build in force when the candidate ran (rebuilt with `statpack-at`, build 02dd6a20fccc — see below), the federal-band risk-set rows for OT2017–OT2025 pool to roughly 143 of 201, the 71.1% it quotes, and it correctly rejects the whole-docket and relist-0 cuts as the wrong populations. Its reasons for stopping short of the high 80s are the right ones — "no developed circuit split," the preliminary-injunction posture, and jurisdictional/remedial/class/mootness vehicle risk — and it candidly names the absent brief in opposition as its largest evidence gap. The weakness is the direction of the adjustment: having listed exactly the considerations that make an interlocutory, split-less petition deniable, it still moved up from an already-high class anchor on the strength of the petition's own (one-sided) framing of importance and conflict with *Rust* and *Finley*. A reader who weighed its own stated caveats would have come in at or below the anchor. It was also the least confident of the three, and its conditional denial-branch estimate (separate writing unlikely, 0.18) matched what happened. Sound method, identified the operative risks, under-weighted them: 0.5.

Base-rate figures were checked against the statpack build the candidate was placed against (`statpack-at`: build 02dd6a20fccc, landed 2026-08-19, no alternative build), not the currently committed pack.

## Predicted reasoning (`predicted_reasoning_quality` = 0.2)

Central claims: grant with plenary review (the document's lead), distribution timing and a possible one-conference hold, the question taken as written and plenary over summary treatment (conditional on a grant; neither credit nor penalty), and, on denial, that no separate writing is the likeliest outcome. The lead call failed, which costs most of the grade. What the outcome did resolve otherwise went this document's way: a single late-2026 distribution (conference of November 13), and a silent denial exactly as its denial branch said was likeliest — a call a reader could plausibly have made the other way on a flagship government petition. The relist language was hedged ("may be held") and so earns little either way; no-CVSG is entailed. The conditional merits forecast never came into play. A failed central call with the secondary, resolvable claims borne out: 0.2.

## Leakage

Forward cell, run the day after docketing and about three months before the denial. Forward cell: predicted 2026-08-20, the day after docketing; the petition was denied 2026-11-16. Log: 24 calls, result capture coverage 1.0, all shell reads of the prompt, schema, provisioned snapshot/petition/context and the committed statpack; no web, MCP or corpus query. No retrieved_doc_date on or after resolution, no read under data/qp-topics/, no order or opinion resolving this petition cited, and the reasoning nowhere presupposes a result (it forecast the opposite). Confirmed genuinely unresolved at prediction time. `influenced_prediction` = `not_applicable`; `leakage_suspected` = false.

## Big case

My own read: 0.6. Solicitor General petition on whether the First Amendment bars viewpoint-based termination of competitive federal research grants; a classwide preliminary injunction against a flagship executive policy, with many parallel suits. The subject matter is nationally significant, but the Court denied review at the first conference with no noted dissent or statement, leaving an interlocutory Ninth Circuit ruling in place and deciding nothing; the question remains open for a later final-judgment vehicle. High-stakes subject, modest realized significance for this docket.
