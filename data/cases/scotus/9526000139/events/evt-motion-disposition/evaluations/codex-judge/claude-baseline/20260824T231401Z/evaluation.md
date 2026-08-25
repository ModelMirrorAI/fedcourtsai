# Evaluation

claude-baseline correctly predicted `denied` with a 0.30 probability of an unqualified grant, producing a Brier score of 0.09.

The reasoning is strong: it anchors to the strictly prior interim pool, distinguishes full grants from partial relief under the denial-first resolver, and weighs concrete merits, scope, election-administration, companion-application, and procedural signals while stating the dominant relief-shape uncertainty. The denial outcome supports the direction, though several qualitative adjustments—especially transfer from recent administration emergency applications—remain necessarily judgmental. The reasoning-quality score is 0.92.

This is an interim cell: the harness owns the pooled baseline, skill score, and mechanical claim scores; `base_rate_basis` remains null. The prediction's null band is the expected interim shape. Votes are not scored at this stage.

Leakage is not applicable. This forward prediction preceded the August 24 resolution. Its retrieval surfaced no outcome material for this application; the later item disclosed in the reasoning concerned separate litigation.
