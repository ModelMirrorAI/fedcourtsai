# Reasoning — No. 26-492, Coudrain v. Boehringer Ingelheim Pharmaceuticals

**P(grant) = 0.008; predicted disposition: denied.**

## What I read
- Snapshot `2026-11-18.json` (forward cell, no cutoff): paid petition filed Aug 25 2026 from the Appellate Court of Illinois, First District (No. 1-25-0614; Illinois Supreme Court denied leave to appeal May 27 2026). Both respondent groups (Boehringer Ingelheim, via King & Spalding; Sanofi, via Arnold & Porter) **waived response** on Oct 19. Distributed Nov 17 for the Dec 4 2026 conference — the first distribution of the petition itself (the earlier Oct 9 distribution was of the sealing motion 26M24, granted Oct 13). No amicus briefs, no call for a response, no CVSG.
- `questions-presented.txt` and `petition.txt` (statement and reasons for granting). `appendix.txt` was provisioned (truncated) but I did not rely on it beyond the petition's own description of the decision below. No BIO exists.
- `same-question.json`: empty list — no similar pending or granted petition, so no hold candidate.
- `context.json`: band `baseline`, `distribution_count` 1, `cert_anchor.rate` 0.0517, `cert_amicus_line` (arm `none`) 0.0268.

## Anchor and adjustments
The frozen anchor is the baseline band's reached rate, ~5.2%. That rate pools every petition that ever sat in the baseline band, including those that later drew a response call, relists or amici. The no-amicus line is 2.7%, and the statpack's relist-0 terminal bucket (paid segment) shows ~1.8% grant family. I go well below all of these because this petition has nearly every denial marker:

1. **Response waived and no response requested before distribution.** The Court essentially never grants without a response on file; a grant would require a call for response first, which would show up as a redistribution. The petition went straight to conference on the waivers.
2. **Poor vehicle.** The decision below is an unpublished Rule 23 order (`2026 IL App (1st) 250614-U`) of an intermediate state appellate court; the state high court denied leave without opinion.
3. **Error-correction framing.** The petition invokes Rule 10(c) — a claimed conflict with *Ford Motor* — and asserts a "deepening split" without, in the portion I read, developing a concrete conflict among courts of last resort. The facts (nonresident plaintiffs, who bought and were injured outside Illinois, suing nonresident manufacturers) sit squarely within *Bristol-Myers Squibb v. Superior Court* (2017), which *Ford* expressly preserved. The petitioners' hook — in-state repackaging/labeling contractors and distribution through Walgreens — resembles the McKesson-distributor argument BMS rejected, though the in-forum labeling fact is a somewhat better variant.
4. **No institutional support**: no amici, no top-side Supreme Court specialist counsel, no federal interest suggesting a CVSG.

Countervailing: the BMS/Ford interplay is a real, recurring question, and some Justices (Gorsuch, Alito in *Ford* concurrences; Sotomayor's BMS dissent) have voiced unease with the doctrine. That keeps me off zero, but it argues for some future clean vehicle, not this one.

## Other claims
- `relist-increment` 0.035: a further distribution would require a call for response or a relist; neither is likely. Small allowance for a response call by one interested Justice and for a clerical reschedule.
- `cvsg-increment` 0.002: private dispute over state-court jurisdiction; no federal interest.
- `summary-disposition-route` 0.25 (conditional on grant): no intervening decision is visible, so a GVR would need a new jurisdiction decision landing while the petition is pending; a grant here would more likely be plenary.
- `dissent-from-denial` 0.006 and `order-writers`: a noted dissent on a waived-response petition is very rare; slightly more weight on Sotomayor (BMS dissent), Gorsuch and Jackson.

## Uncertainty / discounting
I did not read the appendix opinion in full, so my vehicle assessment relies on the petition's own account. The corpus query I ran was a generic granted-priors pull and did not inform the number; the estimate rests on the docket posture and the statpack base rates. No outcome information about this case surfaced.
