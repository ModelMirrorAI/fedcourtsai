# Evaluation — claude-baseline

**Cell:** scotus/9026000087 (Stevens-Reynolds v. Wilshire Insurance Co., No. 26-87), `evt-petition-disposition`, stage `cert`, forward. **Outcome:** denied on 2026-11-09 after one distribution (conference of 11/6/2026), no CVSG, no noted dissent. The segment base rate, its basis and the Brier skill score are the harness's stamp; I write none of them and quote no rate of my own.

## Score
- Predicted `denied`, P(grant) = 0.004 → **correct = 1**, **Brier = 0.000016**.

## Reasoning quality — 0.82
The analysis is sound and specific to this record. It starts from the sal-v4 baseline reached rate, pooled over Terms before 2026. It then makes a well-reasoned move far below that rate, with concrete markers: the petitioner is pro se (as the docket shows); the CA5 affirmance is an unpublished summary-calendar per curiam with en banc denied and no poll; the dispute is first-party Louisiana insurance; the BIO raises a preservation objection; and the split is weak because it mixes dismissal-sanction standards with Rule 37(c)(1) exclusion. It reads the voluntary BIO correctly, as no signal of Court interest. It also flags the docket's date anomaly without over-reading it. One small weakness: it says "in my judgment the circuits do not actually conflict" without checking the cases.

## Predicted reasoning — 0.70
Central claims: denial at the 11/6/2026 conference with no relist; no relist; no CVSG; no separate writing. Each was borne out, and the denial came on the 11/9 order list after that conference. Naming the conference adds some specificity, but for a once-distributed baseline petition, all of these claims are the expected path. The conditional content about a grant (narrowed QP 1, summary route) was never tested. The document is specific and fully borne out, but it has little discriminating content.

## Leakage
Forward cell; the snapshot is dated 2026-10-12. The log has six captured calls, all reads of the prompt, the provisioned case files and the statpack. There were no corpus, web or MCP lookups. Grade: `not_applicable`, not suspected.
