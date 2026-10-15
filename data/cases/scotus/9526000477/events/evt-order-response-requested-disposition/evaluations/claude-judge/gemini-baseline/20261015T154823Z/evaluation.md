# gemini-baseline — P(grant) 0.70, predicted granted

**Cell.** Interim stage (stay application 26A477, NRCC v. Brown). Outcome: `denied` (`actual_granted` 0), resolved 2026-10-14 — the application, referred to the Court, was "denied as moot" in a per curiam, with Justices Sotomayor and Jackson noting they would deny outright. Because this is an interim cell, the segment base rate and Brier skill score are the harness's (stamped from the statpack's interim section by `stamp-cell`); I wrote neither and pooled no rate of my own. Where the stamped rate is null, the pack's interim pool was below its registered floor or absent. `claim_scores` is likewise the harness's. No `semantic_grades`: not a merits cell. `vote_accuracy` omitted (not scored off merits).

**Mootness note.** Under the interim contract any non-grant, including a moot disposition, scores as ungranted, so every "granted" call is `correct` 0 here regardless of how the merits of the stay looked.

**Scores.** correct 0; Brier (0.70 − 0)² = 0.4900.

**Reasoning quality 0.30.** Very thin. It gets the anchor right (53/549) and correctly identifies the main risk as the FCC issuing a final order that moots the mandamus — the realized outcome — but then dismisses that risk on the ground that an administrative stay "suggests the Court wants to control the timeline," which is speculation. There is no engagement with the application's argument, the lower-court opinions, the stay standard, or the distinction between compelling a decision and dictating its substance. Its facts beyond the snapshot (an Oct. 8 administrative stay) came from a web search; the response brief in the record corroborates an administrative stay was in place, so that is legitimate forward signal, not fabrication. The 0.70 conclusion is largely asserted.

**Leakage.** Forward; influenced_prediction not_applicable, leakage_suspected false. Its web search for "26A477" ran on 2026-10-14, the resolution date, and every call is unobserved (coverage 0.0), so I cannot tell whether the denial had surfaced; I left retrieved_outcome_material null rather than crediting it with returning nothing. The prose treats the application as pending and the forecast is opposite the outcome, so no influence is plausible. Flagged for the same-day timing.

**Big case (my read) 0.5.** See evaluation.json.
