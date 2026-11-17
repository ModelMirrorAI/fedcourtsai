# Evaluation of `gemini-baseline`

## Outcome and quantitative summary

This is a **cert-stage** cell (`moment: distribution`) for *Azadeh Khatibi, et al. v. Felix C. Yip, President of the Medical Board of California, et al.*, No. 25-1240. On November 16, 2026, after six distributions, the Supreme Court **denied** certiorari (`actual_disposition: "denied"`, `actual_granted: 0`), with Justice Gorsuch noting he would grant certiorari and Justice Thomas, joined by Justice Alito, dissenting from the denial of certiorari (`noted_dissent_from_denial: true`).

`gemini-baseline` predicted `granted` (`granted: 1`) with grant probability `0.65`, earning `correct = 0` and `brier_score = 0.4225`. `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left to the harness stamp against the stamped segment base rate. Because the committed statpack had refreshed to `sal-v8` after the prediction run, I checked `gemini-baseline`'s base-rate reference against historical statpack build `73762050f49c` (`sha256:345aff2a4fcdad755e6606d092e6c2475966c0bd858d291155914ef722d88fe8`, reconstructed via `uv run fedcourts statpack-at`).

## Reasoning quality (`0.32`)

`gemini-baseline`'s `reasoning.md` starts in the right empirical neighborhood—referencing the prior-Term (OT2017–OT2024) `sal-v4` `elevated` risk-set (`reached`) baseline in build `73762050f49c` (approximated slightly loosely rather than weighted-pooled)—and correctly identifies the headline petition-side signals from the docket and Questions Presented: First Amendment compelled-speech salience (*NIFLA*, *Shurtleff*), Judge VanDyke's three-judge dissent from the denial of rehearing en banc, six cert-stage amicus briefs including Cato and a state coalition, and the Court's call for a response after an initial waiver.

However, the analysis is brief, superficial, and entirely one-sided, leading to an unsubstantiated leap to `0.65`:

- **Complete omission of the Brief in Opposition and merits briefing.** Even though full, untruncated texts of `petition.txt` (29 pages) and `brief-in-opposition.txt` (25 pages) were provisioned on September 18, 2026, `reasoning.md` never engages with a single argument from respondent's brief (consistent with reading only `questions-presented.txt` and docket metadata). As a result, `gemini-baseline` missed that the alleged circuit split compared distinct applications of *Shurtleff*'s holistic test outside CME rather than conflicting appellate holdings on continuing professional education, missed the Ninth Circuit panel's explicit California-specific narrowing, and missed respondent's statutory argument under Cal. Bus. & Prof. Code § 2190.1(e)(2).
- **Missing *Chiles v. Salazar* and salient cert mechanics.** `reasoning.md` never mentions *Chiles v. Salazar* (decided March 31, 2026), which bore directly on both percolation incentives and the plausibility of a GVR (`summary-disposition-route`, brushed off at `0.05` without addressing *Chiles*). Nor did it note that `sal-v4` `elevated` merely reflected mechanical post-response redistribution rather than a discretionary relist, or justify `dissent-from-denial` in prose at all. Dismissing split thinness and vehicle concerns in a single generic sentence ("My main uncertainty is vehicle quality and whether the Court might want to wait for further percolation...") does not support pushing a non-CVSG, non-federal paid petition at its first post-response distribution to `0.65`.

## Predicted reasoning (`0.30`)

`gemini-baseline`'s four-paragraph `predicted_reasoning.md` leans in the wrong primary direction on disposition while getting secondary procedural calls and a hedged fallback note right:

1. **Grant-oriented primary framing** (`not-borne-out`): Never states an explicit standalone disposition probability sentence, instead framing the case around what is "typical for high-profile grants" and calling it a "clean, well-developed First Amendment challenge"—failing on the central disposition when certiorari was denied on November 16, 2026.
2. **At least one or two further relists after September 28, 2026** (`borne-out`): Correctly anticipated further relists after the long conference (`distribution_count = 6`, four additional distributions), although those relists preceded a denial with dissent rather than a grant.
3. **No CVSG** (`borne-out`): Correctly forecast no CVSG on a state regulatory scheme, a straightforward call.
4. **Conditional plenary review on the single question presented** (`unresolved`): Untested because certiorari was denied.
5. **Hedged fallback on dissent from denial** (`borne-out` as hedged): Stated that "[s]hould the Court deny review, a dissent from denial or a statement respecting denial is moderately likely, potentially authored by Justice Thomas or Justice Alito," matching Justice Thomas's dissent joined by Justice Alito on November 16, 2026.

Under the rubric (`0.25`: a central claim failed, with the rest generic or mixed), failing the primary grant-versus-denial posture holds the document near the lower anchor, with modest credit to **`0.30`** for the borne-out relist-increment call and naming Justices Thomas and Alito in the conditional denial paragraph.

## Leakage review

`retrieval_log.json` records `mode: "forward"` on `2026-09-18` (`result_capture_coverage: 0.0`, all 32 calls `unobserved`, reflecting the engine's telemetry shape), nearly two months before the `2026-11-16` disposition. Evaluated on query text per the marker rule, every call accessed only `.github/prompts/predict.md`, `AGENTS.md`, `schemas/prediction.schema.json`, provisioned `scotus/73286452` files, `metrics/statpack.md`, and two `uv run fedcourts query --court scotus --era 2020s` commands, with no web searches, no MCP lookups, and no `data/qp-topics/` access. Thus `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, and `leakage_suspected = false`.
