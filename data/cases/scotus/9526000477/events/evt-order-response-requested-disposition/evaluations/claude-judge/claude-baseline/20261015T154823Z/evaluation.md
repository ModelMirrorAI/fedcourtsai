# claude-baseline — P(grant) 0.72, predicted granted

**Cell.** Interim stage (stay application 26A477, NRCC v. Brown). Outcome: `denied` (`actual_granted` 0), resolved 2026-10-14 — the application, referred to the Court, was "denied as moot" in a per curiam, with Justices Sotomayor and Jackson noting they would deny outright. Because this is an interim cell, the segment base rate and Brier skill score are the harness's (stamped from the statpack's interim section by `stamp-cell`); I wrote neither and pooled no rate of my own. Where the stamped rate is null, the pack's interim pool was below its registered floor or absent. `claim_scores` is likewise the harness's. No `semantic_grades`: not a merits cell. `vote_accuracy` omitted (not scored off merits).

**Mootness note.** Under the interim contract any non-grant, including a moot disposition, scores as ungranted, so every "granted" call is `correct` 0 here regardless of how the merits of the stay looked.

**Scores.** correct 0; Brier (0.72 − 0)² = 0.5184.

**Reasoning quality 0.45.** Compact and structured: correct strictly-prior interim anchor (53/549), clearly enumerated upward adjustments (prior stay in the same case, response requested, FCC alignment, Purcell-type stability) and — notably — a named mootness discount ("mootness risk around the Oct. 9 noon deadline … or the FCC acted"), which is the realized route. It also identified that the mandamus orders only a decision. But it read only the application body (not the appendix opinions), inferred the response request from the event's existence rather than evidence, and the listed discounts are not reflected in a number that still puts grant at 0.72; the "FCC aligned with applicants" inference is asserted from the application alone. Sound direction of thought, overconfident conclusion.

**Leakage.** Forward; none. Captured CourtListener docket search for 26A477 returned 0 results; no outcome material.

**Big case (my read) 0.5.** See evaluation.json.
