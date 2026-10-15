# gemini-baseline — scotus/9026000027, evt-petition-disposition

**Prediction:** denied, P(grant) = 0.005. **Correct:** yes. **Brier:** 0.000025.

## Cell

Cert stage (`stage: cert`, distribution moment), forward mode. Outcome: **denied** on 2026-10-13 (`actual_granted` 0), one distribution, no CVSG, no noted dissent. The prediction froze `context.band` = `baseline` under `sal-v4` (Term 2026), so the segment base rate, `base_rate_basis` and Brier skill are the harness's to stamp; I left them null and refer only to "the stamped segment base rate". `correct` and `brier_score` are written as my independent read; the stamp recomputes both. No votes are scored on a cert cell, no semantic set is declared, and `claim_scores` is the harness's.

## Leakage

Forward cell made 2026-10-04, before the October 9 conference and the October 13 order. I checked the log for this case's disposition surfacing as already decided and found none: no retrieved document dated on or after resolution, no query for the petition's disposition, no read inside `data/qp-topics/`. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

Log detail: `result_capture_coverage` is 0.0 (no results reached the log — an engine's standing shape), so calls were graded on their queries: provisioned reads, the statpack, and two CourtListener lookups on the caption / the Fifth Circuit docket number, which the candidate reports hit a rate limit. None targets this petition's disposition.

## Reasoning quality: 0.45

The conclusion is right and the factors named are the right ones — a fact-bound application of Louisiana's statutory-employer doctrine, no alleged split, a pro se petitioner, and a federal-employee framing that does not rise to national importance. But the rationale is a single paragraph: it gestures at the band anchor ("a reached rate under 5%" — the pooled prior-Term reached figure is about 5.0%, so "under" is imprecise) without stating how it was pooled, and it never mentions the decisive vehicle problem in the record, that the FECA/Supremacy Clause theory was raised late and not reached below, nor the unpublished, expressly narrow opinion. The move from ~5% to 0.5% is asserted rather than argued. Sound but thin; it would not let a reader check the number.
