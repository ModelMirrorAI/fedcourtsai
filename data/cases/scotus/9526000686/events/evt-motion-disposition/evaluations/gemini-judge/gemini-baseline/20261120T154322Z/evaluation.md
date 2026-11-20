# Evaluation — `gemini-baseline` (`scotus/9526000686`, `evt-motion-disposition`)

## Stage and quantitative scoring

This cell is an **interim**-stage arrival evaluation (`stage: interim`, `moment: arrival`) for capital stay application No. 26A686, *Thomas M. Overton v. Florida, et al.* Because `outcome.json` records the finer interim reading (`interim_reading: "denied"`, `interim_granted: 0`, `actual_disposition: "denied"`), quantitative accuracy and Brier scoring follow `outcome.interim_granted`:

- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.008`
- **Outcome:** `interim_reading = "denied"`, `interim_granted = 0` (resolved `2026-11-19`)
- **`correct`:** `1` (`"denied"` is on the ungranted side of `interim_granted = 0`)
- **`brier_score`:** `(0.008 - 0)^2 = 0.000064`

Because this is an interim cell, `segment_base_rate` and `brier_skill_score` (along with `claim_scores` for `interim-v3`) are computed and stamped by the harness from the committed statpack's strictly prior application-Terms rather than written by the evaluator, and `base_rate_basis` is left `null` structurally. The committed statpack's interim section carries ten strictly prior Terms (`OT2016–OT2025`) well above the registered floor, so skill is evaluated against the stamped segment base rate. `vote_accuracy` and `semantic_grades` are omitted as non-merits fields.

## Reasoning quality (`reasoning.md`) — `0.95`

`gemini-baseline` produced the strongest, best-evidenced analysis in the cell (`probability = 0.008`), combining verified Term-level empirical decomposition, on-point current-Term corpus comparators, and granular doctrinal and procedural analysis that anticipated Respondent's November 17 opposition (`application-response.txt`) in remarkable detail:

1. **Recent-Term and Florida-specific empirical grounding.** Rather than stopping at the 10-Term `private × capital` aggregate in `metrics/statpack.md` (which matched the committed statpack build), `gemini-baseline` inspected the per-Term `applicant_cuts` in `metrics/statpack.json` (`0/44` in OT2024, `0/44` in OT2025, and `0/20` in OT2026 to date — `0/108` across the current bench's recent window) and queried the corpus for OT2026 Florida execution-warrant applications. That surfaced `26A623` (*Jesse Guardado v. Florida*, denied November 5, 2026 — just nine days before Overton filed) and `26A524` (*William Reaves v. Florida*, denied October 20, 2026), along with linked cert docket `26-6154`.
2. **Doctrinal and vehicle precision.** Using legitimate forward retrieval on November 15 for the pre-arrival November 12, 2026 Florida Supreme Court disposition summary (`SC2026-1724` / `SC2026-1725`, citing *Guardado v. State*, No. SC2026-1605) and Overton's prior federal habeas ruling (*Overton v. Jones*, 155 F. Supp. 3d 1253 (S.D. Fla. 2016)), `gemini-baseline` pinpointed every legal obstacle that later appeared in Florida's opposition: (a) *Woodard* (523 U.S. 272), *Dumschat* (452 U.S. 458), and *Herrera* (506 U.S. 390) foreclose "zero commutations = sham" claims, as the Court had just confirmed by denying `26A623` (*Guardado*); (b) Overton's clemency proceeding and the 2005 Rule 3.850 hearing underlying his clemency-counsel conflict claim occurred many years earlier, creating an independent and adequate state-law timeliness bar under Fla. R. Crim. P. 3.851(d)(1)–(2) (*Coleman v. Thompson*, 501 U.S. 722, 729 (1991)); (c) there is no federal constitutional right to effective assistance of state-appointed clemency counsel; and (d) Florida's 30-day warrant schedule was uniformly upheld below (*Sweet*, *Hunt*) and posed no *Barefoot* stay ground. All cited federal, state, and corpus authorities verified cleanly.
3. **Exact procedural-signal calibration.** From `26A623` and `26A524`, `gemini-baseline` recognized that Florida's Capital Appeals office routinely files its warrant opposition voluntarily without a formal `Response requested` entry (`response_requested: false`), while Justice Thomas refers the application to the full Court (`referred_to_court: true`).

The only minor limitation documented in `reasoning.md` was that the full slip text of the November 12, 2026 Florida Supreme Court opinion was not yet ingested in CourtListener, leaving exact sub-details of Overton's 2014 clemency interview date inferred rather than read verbatim.

## Predicted reasoning — `0.97`

`gemini-baseline`'s `predicted_reasoning.md` sits at the top anchor (`1.0` range, scored `0.97`) because it committed to highly specific, non-trivial procedural and dispositive calls that a competent reader of the arrival record could plausibly have called otherwise — and every single one held:

1. **Voluntary state opposition on Nov. 16–17 without a Court request, applicant reply, and zero amici (`borne-out`):** Committed specifically that Florida's Attorney General would file an opposition on November 16 or 17, 2026 *without* a docketed `Response requested` entry, followed by a short reply from Overton's CCRC-Middle counsel and zero amicus briefs. On November 17, 2026, Florida filed its uninvited opposition (`response_requested: false`), Overton's CCRC-Middle counsel filed a reply (`application-reply.txt`), and `amicus_briefs` was `0`.
2. **Full-Court referral and simultaneous denial of `26A686` and `26-6154` on Nov. 18–19 (`borne-out`):** Forecast Justice Thomas's referral to the full Court (`referred_to_court: true`) and simultaneous denial of both `26A686` and linked cert petition `26-6154` on November 18 or 19 in an unsigned order whose predicted wording matched the Court's November 19 order nearly verbatim.
3. **No separate writings and no noted dissents (`borne-out`):** Explicitly predicted zero separate opinions and zero noted dissents (`noted_dissent_from_denial: null`, `votes: []`, `writing_roles: null`), anchored in `26A623` and `26A524`.
4. **Silent order over state-law timeliness bars and settled *Woodard*/*Dumschat* posture (`borne-out`):** Accurately stated both that the Court's order would omit substantive reasoning and that the underlying record rested on Rule 3.851(d) timeliness bars, non-cognizable state clemency-counsel claims, and settled *Woodard* precedent — all confirmed in `application-response.txt` and the two-sentence November 19 order.

## Leakage and big-case notes

- **Leakage (`not_applicable`, `leakage_suspected: false`):** `gemini-baseline` ran forward at `20261115T141636Z`, four days before the November 19, 2026 disposition. Its 23 tool calls (`result_capture_coverage = 0.0`, the standing unobserved shape for that engine's telemetry) queried local statpack/corpus artifacts, pre-arrival CourtListener case law, and one candidly logged November 15 web query for the pre-arrival November 12, 2026 Florida Supreme Court decision (`SC2026-1724` / `SC2026-1725`). No outcome existed when the prediction ran.
- **Big-case read (`0.12`):** Despite life-or-death personal stakes, this was a routine, splitless end-stage Florida warrant stay application foreclosed by decade-old state procedural bars, drawing zero amici and an unsigned summary denial without dissent.
