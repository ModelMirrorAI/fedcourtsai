# Evaluation — gemini-baseline

**Cell.** Cert stage, *Wilkins v. United States* (second petition), forward prediction made 2026-10-03 at one distribution; outcome `denied` (`actual_granted` 0) on 2026-10-13, no noted dissent. The prediction froze `context.band` = `baseline` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp — left null here; read the stamped segment base rate beside the Brier. `claim_scores` is harness-computed and not graded here; no votes are scored at the cert stage; no semantic set is declared on a cert cell.

**Score.** P(grant) 0.04, predicted `denied` → correct = 1, Brier = 0.0016.

**Reasoning quality: 0.55.** The number is sensible, and the anchor (the pooled baseline-band reached rate, ~5%) is the right one for a paid private petitioner, read through correctly. But the analysis is thin. It calls law-of-the-case "generally a fact-bound inquiry" without engaging the petition's actual theory, which is that findings made under a jurisdictional-dismissal standard survived this Court's reversal. It says the case "lacks compelling circuit split dynamics" without saying which conflicts were asserted or why they fail. And it misses the strongest denial driver both briefs set out: the Ninth Circuit's independent de novo affirmance on decades of public use, which makes Question 1 largely academic. It also doesn't mention that *Wilkins I* reserved the on-remand question. The conclusion is right, but for generic reasons rather than case-specific ones.

**Leakage.** Forward, `not_applicable`. Every logged call reads, lists or writes provisioned inputs (all `unobserved`, so they are graded on their arguments). There are no web, MCP or corpus outcome queries and no `data/qp-topics/` read.
