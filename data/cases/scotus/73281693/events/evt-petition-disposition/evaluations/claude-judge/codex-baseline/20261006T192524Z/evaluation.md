# Evaluation of codex-baseline — scotus/73281693, evt-petition-disposition

**Cell.** Cert stage, forward mode. Outcome: petition **denied** on the 2026-10-05 order list after a single conference (2026-09-28), no relist, no noted dissent from denial, two distributions total (the second a redistribution after the June 2 call for response). Supplemental briefs from both sides were filed and distributed 2026-09-29.

**Prediction.** `denied`, P(grant) = 0.26.

## Scores

| field | value | how |
| --- | --- | --- |
| correct | 1 | `denied` == `denied` |
| brier_score | 0.0676 | (0.26 − 0)² |
| segment_base_rate | 0.1724 | `elevated` band, sal-v4, bracketed `reached` rate pooled resolved-weighted over Terms 2017–2024 (eight rows, 2810 weighted n) |
| base_rate_basis | risk_set | prediction froze `band: elevated` with `salience_version: sal-v4`; the statpack heading names sal-v4 |
| brier_skill_score | -1.2744 | 1 − brier / (base − 0)² |

Base rate from the prediction's frozen context, pooled from the rendered statpack table (all ten pack Terms rendered; Terms 2025 and 2026 excluded). The candidate computed the same pool from `statpack.json` at 0.1722; the rounded table gives 0.1724, an immaterial difference.

## What the reasoning got right and wrong

This is the most disciplined of the three rationales. It states its information set precisely (snapshot vintage, which documents were read, that the reply was not provisioned), anchors on exactly the pooled figure the scoring rule uses and says why the terminal and relist-bucket cuts are not substitutes, and correctly reads the second distribution as a post-response redistribution rather than a relist, discounting the harness's count of two. On the merits it does the one thing the other rationales do less well: it takes the brief in opposition seriously, identifying the cross-citation argument, the actual-hardship language in the Ninth Circuit opinion, and the medical-record entanglement as reasons the Justices could see a fact-bound application rather than a rival standard. Its stated modal path, a silent denial off the September 28 conference in early October, is what happened, and its stated reason for denial (the split is entangled with the evidentiary record) is the most plausible account of it.

Where it loses credit is the magnitude of the upward move. From 17% to 26% it credits the call for response and the amicus bloc, both legitimate, but the document's own analysis of the vehicle problems is strong enough that the net move reads as under-discounted; the rationale concedes the contrary evidence is "persuasive" and still moves up by half the anchor. It also does not weigh the Court's post-pandemic pattern on vaccine-mandate petitions, which gemini-baseline and claude-baseline both named and which is the cleanest external prior pointing to denial. The Brier penalty reflects the number; the reasoning behind it is balanced, honest about limits, and would have been credited similarly had the petition been granted.

Net: careful, well-sourced, correct about the mechanism, somewhat generous on the upward adjustment. **reasoning_quality 0.80.**

## Leakage

Forward cell; prediction created 2026-09-18, petition denied 2026-10-05. Log (28 calls, 93% captured) shows reads of the provisioned snapshot, briefs, statpack.md/json, and the predict contract; two provider-side web-search rows are unobserved and are graded on their queries, both of which target the 2023 Groff v. DeJoy opinion, not this petition; the candidate reports they returned nothing usable. No MCP or corpus calls, no qp-topics read, no query for this docket's disposition. No outcome material retrieved. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The two unobserved web-search rows are graded on their queries per the capture rule; neither targets this docket. The candidate's own `flags.json` is not staged, so an absence of disclosure there is not evidence.

## Big-case read

Independent read 0.55 (see `big_case.notes`).

## Not scored here

The forecast document and the `claims` block are the harness's (`claim_scores`); `vote_accuracy` is omitted on a cert cell; no semantic set is declared on a cert event, so no `semantic_grades` block is written.
