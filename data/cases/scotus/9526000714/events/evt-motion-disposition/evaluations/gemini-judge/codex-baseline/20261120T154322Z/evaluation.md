# Evaluation of `codex-baseline` — `scotus/9526000714` (`evt-motion-disposition`)

## Stage and quantitative scoring

This is an **interim-stage** cell (`stage: interim`, `kind: motion`, `moment: arrival`) for *Markwayne Mullin, Secretary of Homeland Security, et al. v. National TPS Alliance, et al.*, No. 26A714, filed November 18, 2026 and voluntarily withdrawn by the Solicitor General on November 19, 2026. `outcome.json` records `actual_disposition = "withdrawn"`, `actual_granted = 0`, `interim_reading = "withdrawn"`, and `interim_granted = 0`, with `interim_signals` unchanged from arrival (`response_requested = false`, `referred_to_court = false`, `amicus_briefs = 0`).

Under the finer interim reading recorded in `outcome.json` (`interim_granted = 0`):

- `codex-baseline` predicted `predicted_disposition = "granted"` (`granted = 1`) and `probability = 0.95`.
- Because `"granted"` lies on the granted side of the binary while `"withdrawn"` lies on the ungranted side (`interim_granted = 0`), `correct = 0`.
- `brier_score = (0.95 - 0)^2 = 0.9025`.

Per the interim-stage contract, `segment_base_rate`, `brier_skill_score`, and `claim_scores` (`interim-v3`) are computed and stamped by the harness from the committed statpack's substantive interim pool over application Terms strictly before OT2026, and `base_rate_basis` remains `null` structurally because interim applications carry no salience band. The committed `metrics/statpack.md` carries a populated interim section over OT2016–OT2025 sufficient to support the harness stamp.

## Rationale assessment (`reasoning_quality = 0.55`)

`codex-baseline`'s `reasoning.md` did solid primary-source verification on the Supreme Court's prior rulings in the dispute, but suffered from severe overconfidence (`0.95`) caused by treating the prediction almost purely as an abstract merits vote while neglecting both the live Ninth Circuit remand docket and the non-moot procedural exits that govern arrival-moment emergency applications:

1. **Strengths in Supreme Court precedent verification.** Unlike a purely brief-dependent read, `codex-baseline` retrieved and verified the slip opinion in *Mullin v. Doe* (`No. 25-1083`) and the October 2025 stay order and dissent in `25A326`, confirming *Doe*'s holding on 8 U.S.C. § 1254a(b)(5)(A), the October 2, 2026 expiration of the vacated TPS extension, and why Justice Jackson (author of the lone separate dissent in `25A326`) was likelier than Justices Sotomayor or Kagan to write separately if an order issued. It also properly consulted `metrics/statpack.md` and `metrics/statpack.json` for the substantive interim pool and federal applicant cuts, as well as the corpus rows for `24A1059` and `25A326`.
2. **Neglect of voluntary withdrawal and GVR procedural dynamics (`0.95` overconfidence).** Pushing the probability to `0.95` left only a 5% combined budget for *every* non-moot ungranted outcome (`denied`, `withdrawn`, and non-moot `dismissed`). Even on the face of `application.txt` (p. 14), supplemental GVR remand briefing in the Ninth Circuit had already been completed on November 10 and the Government had moved below for either a prompt merits ruling or an order extending the administrative stay seven days past publication of the panel's judgment. Yet `reasoning.md` never modeled voluntary withdrawal (`withdrawn`, which scores `0` on the finer interim reading) at all, attributing its entire 5% residual solely to "institutional reluctance to pre-empt the GVR remand before the Ninth Circuit writes."
3. **Missed live lower-court development in forward mode.** Although `codex-baseline` ran live web checks on `supremecourt.gov` and had CourtListener MCP available, it never checked the underlying Ninth Circuit remand docket (`CA9 No. 25-5724`) on RECAP. Four hours after `26A714` arrived on November 18—and well before `codex-baseline` ran on November 19—the Ninth Circuit panel entered `DE 109` granting the Government's seven-day post-judgment administrative stay, eliminating the November 20 expiration cliff on which `codex-baseline` staked its urgency analysis and prompting the Solicitor General's withdrawal later that day. In addition, `reasoning.md`'s jump to a 38% separate-writing probability for Justice Jackson anchored heavily on a single prior order (`25A326`) without disciplining that estimate against the statpack's much lower Justice-level interim authorship rates.

## Predicted reasoning (`predicted_reasoning_quality = 0.0`)

`codex-baseline`'s two-paragraph `predicted_reasoning.md` committed unconditionally to rapid procedural escalation and a stay grant without flagging any withdrawal or Ninth Circuit administrative-stay contingency:

- **Procedural escalation and timing (central, `not-borne-out`).** The document forecast that Justice Kagan would request a prompt response, refer the application to the full Court, draw 1–2 amicus briefs, and act (via an administrative bridge or final order) within about a week "because the Ninth Circuit's administrative stay expires November 20." In fact, the November 20 cliff had already been superseded below on the evening of November 18, the Solicitor General withdrew `26A714` on November 19, and none of those procedural steps occurred (`response_requested = false`, `referred_to_court = false`, `amicus_briefs = 0`).
- **Disposition (central, `not-borne-out`).** The forecast committed to a stay grant pending appeal and certiorari; the application resolved as `withdrawn`.
- **Order ground/format and separate dissenting writing (central conditional claims, `unresolved`).** The predictions of a terse unsigned stay order under *Mullin v. Doe* and Justice Jackson as the likeliest dissenting author were never tested because no Court order issued.

Because every resolved central claim failed in direction and the document included no discriminating caveat or counterfactual covering voluntary withdrawal or Ninth Circuit bridge relief, it lands at the `0.0` rubric anchor ("The central claims are specific and failed, or the forecast is wrong in direction").

## Leakage review

`retrieval_log.json` (`mode: "forward"`, `result_capture_coverage: 0.415` across 53 calls between `2026-11-19T14:33:07Z` and `14:53:48Z`) shows local file reads, corpus queries on historical dockets, fetches of the *Doe* and `25A326` PDFs, and two live reads of `supremecourt.gov/rss/cases/json/26A714.json` (`14:36Z` and `14:39Z`), which returned only the November 18 submission entry. The Solicitor General's withdrawal letter was filed more than six hours later (`15:55:58 ET` / `20:55:58Z` on November 19). No outcome material existed at prediction time (`influenced_prediction = "not_applicable"`, `leakage_suspected = false`).
