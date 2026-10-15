# codex-baseline — P(grant) 0.82, predicted granted

**Cell.** Interim stage (stay application 26A477, NRCC v. Brown). Outcome: `denied` (`actual_granted` 0), resolved 2026-10-14 — the application, referred to the Court, was "denied as moot" in a per curiam, with Justices Sotomayor and Jackson noting they would deny outright. Because this is an interim cell, the segment base rate and Brier skill score are the harness's (stamped from the statpack's interim section by `stamp-cell`); I wrote neither and pooled no rate of my own. Where the stamped rate is null, the pack's interim pool was below its registered floor or absent. `claim_scores` is likewise the harness's. No `semantic_grades`: not a merits cell. `vote_accuracy` omitted (not scored off merits).

**Mootness note.** Under the interim contract any non-grant, including a moot disposition, scores as ungranted, so every "granted" call is `correct` 0 here regardless of how the merits of the stay looked.

**Scores.** correct 0; Brier (0.82 − 0)² = 0.6724.

**Reasoning quality 0.50.** The strongest-documented analysis of the three: it read the application and the Fourth Circuit opinions closely, pooled the interim anchor correctly from strictly-prior Terms (53/549 ≈ 9.65%), checked the stay standard against Hollingsworth v. Perry, and — to its credit — articulated the very counterargument that bore on the outcome: the mandamus only compelled the FCC to *decide*, completing agency review could satisfy rather than evade the prior stay, and it reserved probability for "a procedural termination." It also honestly flagged the stale context (response_requested false despite the event moment). Its weakness is calibration: moving from a ~10% anchor to 0.82 rests almost entirely on the prior September stay, and it did not weigh how likely it was that the October 9 deadline's passage (with an administrative stay or agency action) would leave nothing for the Court to stay — the route the Court actually took. Highest confidence of the three on a wrong call.

**Leakage.** Forward; none. The captured log carries only four 'other' shell calls, while the candidate's retrieval.md discloses web and CourtListener lookups (all on Hollingsworth v. Perry) that the log does not show — a capture gap, flagged, not evidence of misconduct. Nothing indicates this case's disposition was seen.

**Big case (my read) 0.5.** See evaluation.json.
