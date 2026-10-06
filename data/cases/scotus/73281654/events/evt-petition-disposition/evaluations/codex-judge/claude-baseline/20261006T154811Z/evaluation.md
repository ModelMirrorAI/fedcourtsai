# Evaluation: claude-baseline

## Outcome and scores

This cert-stage outcome records denial on October 5, 2026 and `actual_granted = 0`. claude-baseline's September 18 prediction called denial with P(any grant) = 0.04. Exact-label correctness is 1 and Brier loss is `(0.04 - 0)^2 = 0.0016`.

The prediction's frozen elevated band, sal-v4, and docket Term 2025 match the committed statpack's band heading. The risk-set baseline pools every displayed prior Term's bracketed reached figure, 2017–2024: `(17.5%,400), (15.9%,347), (13.8%,334), (16.1%,397), (20.5%,342), (19.0%,300), (17.5%,354), (17.9%,336)`. Resolved-weighting gives 484.386 / 2,810 = 0.17237935943060498. The fractional numerator reconstructs rounded, denial-reweighted rates, not exact grant counts. The caption says all ten of ten Terms are rendered; 2025 and 2026 are excluded. Brier skill is `1 - 0.0016 / baseline^2 = 0.9461544946048972`. The evaluator's terminal band was not used. This calculation describes the committed pack, not freshly queried corpus state or generalizable aggregate performance.

## Reasoning quality: 0.80

The analysis is substantively grounded and explains a large downward adjustment rather than merely reciting denial's prevalence. It reconstructs the response-request chronology, distinguishes the two distributions from a strong post-consideration relist signal, and treats terminal relist and circuit cuts as descriptive rather than transition probabilities. It correctly identifies the published appellate decision and distinguishes the CFC's independent barriers from the appellate water-duty holding. It also addresses the petition's proposed distinction from the cited precedent and explains the claimed regulation's weakness through the opposition's account.

The score is moderated by several unsupported or overstated steps. Its high-single-digit response-request class rate is explicitly remembered general knowledge, not a committed conditional estimate; the exact adjustment to 4% therefore has limited quantitative support. The docket chronology supports caution about interpreting distributions, but does not itself prove the categorical assertion that zero conferences considered the petition. Counsel size and an asserted lack of wider litigation are weakly supported proxies for certworthiness. The statement that the petition alleges no conflict with this Court is also broader than its own recognition that the petition invokes Supreme Court trust precedents; absence of a persuasive conflict should be distinguished from absence of an argument. Alternative grounds are substantial obstacles, not adjudicated proof that a favorable answer changes nothing.

These limitations do not erase the sound record-based vehicle analysis. The candidate also candidly acknowledges its unsourced conditional-rate assumption and lack of a full appellate-opinion read. The bare denial is consistent with its bottom line, not confirmation that the Court accepted its doctrinal explanation. This grade concerns `reasoning.md` only, not accuracy of the forecast prose or structured auxiliary claims.

## Leakage and scope

The harness log records forward mode and 32 captured calls. I inspected all query slices and capture markers. The substantive retrieval includes aggregate priors, this docket's header and entries, and the earlier Federal Circuit decision; the legible document dates precede the October 5 resolution. The reasoning reports a docket with no termination date, which is not conclusive proof of pendency by itself, but neither log nor prose reveals an already-decided petition. With the prediction dated September 18 and no contradictory outcome exposure, retrieved outcome material is false, influence not applicable, and leakage suspected false. Its forward case-specific retrieval was permitted.

The evaluator's post-resolution snapshot was not used to reconstruct the candidate's baseline. No vote score is written for cert. No semantic set is declared, the forecast document remains unscored, and mechanical claim scores are reserved to the harness. Optional independent stakes grading is omitted because the candidate's score had already been seen.
