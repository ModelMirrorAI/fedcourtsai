# Evaluation of `gemini-baseline` — *Novotny v. Moore* (`scotus/73500225`, `evt-order-relist-disposition`)

## Summary of Scores

- **Stage & outcome:** Certiorari stage (`relist` moment, opened `2026-11-09`), resolved `2026-11-16` as **`denied`** (`actual_granted = 0`, `noted_dissent_from_denial = true`, `signals.distribution_count = 5`, `signals.cvsg_date = null`), with `record/snapshots/2026-11-16.json` recording *"Petition DENIED. Statement of Justice Thomas respecting the denial of certiorari."*
- **Quantitative read:** `correct = 1` (`predicted_disposition = "denied"`), `brier_score = 0.0484` (`probability = 0.22`). `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left `null` for harness stamping; `vote_accuracy` and `semantic_grades` are omitted on this cert-stage cell.
- **Qualitative grades:** `reasoning_quality = 0.84`, `predicted_reasoning_quality = 0.76`.
- **Big-case read:** `big_case.evaluator_score = 0.68`.
- **Leakage:** `leakage_suspected = false` (`mode = "forward"`, `influenced_prediction = "not_applicable"`).

---

## Assessment of `reasoning.md` (`reasoning_quality = 0.84`)

### Base-rate verification (`statpack-at` build `ca0c9e1a49e2`)
`gemini-baseline`'s base-rate citations were verified against reconstructed statpack build `ca0c9e1a49e2` (`sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`, landed `2026-11-09T14:37:29Z`), rather than the later committed statpack. Every marginal and bucket figure cited in `reasoning.md` matches `ca0c9e1a49e2` exactly: the `relist >= 1` pool (`20.7%`, `n = 3,510`), the individual relist buckets (`13.5%` at `1` with `n = 2,532`; `41.2%` at `2` with `n = 495`; `37.3%` at `3+` with `n = 483`), `CVSG = none` (`6.4%`, `n = 13,550`), `1` amicus brief (`14.9%`, `n = 1,159`), and `ca4` (`2.6%`, `n = 3,425`). One minor methodological slip in `Section 1.A` was illustrating the rendered `sal-v8` table across `OT2017–OT2025` (`n = 772`), which includes the petition's own `OT2025` docket Term, though `gemini-baseline` properly anchored on `context.json`'s strictly prior 10-Term `cert_anchor` rather than on that `OT2025`-inclusive sum.

### Legal, procedural, and calibration analysis
`gemini-baseline` produced the sharpest, best-calibrated strategic analysis of the three candidates (`probability = 0.22`, `brier_score = 0.0484`, substantially beating the stamped segment base rate):
- **Granular decomposition of the Fourth Circuit's rulings and vehicle overbreadth:** Unlike the other candidates, `gemini-baseline` precisely separated the Fourth Circuit's unanimous 3–0 holdings (invalidating the private-property "vampire rule" in `§ 6-411(d)`, and upholding firearm bans in government buildings, school grounds, and health care facilities with Judge Agee concurring) from its 2–1 holdings (upholding bans in state parks and forests, mass transit, amusement venues, alcohol-serving establishments, and within 1,000 feet of public demonstrations). Highlighting that Petitioners' single omnibus Question Presented swept in three categories upheld 3–0 below—including *Heller*/*Bruen*'s core "schools and government buildings" safe harbor—was a compelling vehicle diagnosis.
- **High-value comparative SCOTUS evidence:** `gemini-baseline` combined the BIO with corpus and CourtListener checks to surface two directly on-point SCOTUS certiorari actions: (1) in *Wolford v. Lopez* (No. 24-1046), the Court granted review *only* on Hawaii's private-property default rule while denying certiorari on parks and alcohol-serving establishments, and Justice Barrett's concurrence (joined in Part II-B by Justices Thomas and Gorsuch) explained why the 1791-versus-1868 timeframe remained open; and (2) in *Schoenthal v. Raoul* (No. 25-541, `scotus/73278986`), the same Counsel of Record sought review of the Seventh Circuit's public-transit carry ban and was **denied certiorari on April 6, 2026 after four distributions**.
- **Spot-on diagnosis of the separate writing and GVR posture:** `gemini-baseline` rightly discounted a *Wolford* GVR (`summary-disposition-route = 0.12`) because *Wolford* had already been decided in June 2026 and fully briefed, and it correctly inferred that three pre-conference reschedules plus one post-conference relist on a splitless post-*Bruen* petition pointed toward a separate writing on denial (`dissent-from-denial = 0.55`) authored by Justice Thomas (`Thomas = 0.38`, coherently bounded below `0.78 * 0.55 = 0.429`).

Two flaws keep `reasoning_quality` at **`0.84`** rather than higher:
1. **Overlooking that *Koons* was vacated on rehearing en banc (`brief-in-opposition.txt` pp. v, 34; `cert-reply.txt` pp. 1–2, 4):** `gemini-baseline` cited the Third Circuit panel decision in *Koons v. Attorney General New Jersey* as an operative decision reconciling *Lara* and aligning with the Fourth Circuit, missing that the Third Circuit had granted rehearing en banc and **vacated** the panel opinions (`162 F.4th 100 (3d Cir. 2025)`, argued en banc Feb. 11, 2026)—which also caused it to miss the active Third Circuit en banc percolation point. Alongside that substantive oversight, three Federal Reporter page citations carried transcription slips (`165 F.4th 459` vs. `165 F.4th 194` in `petition.txt` p. 3; `156 F.4th 213` vs. `156 F.4th 210`; and `150 F.4th 898` vs. `150 F.4th 889` in `brief-in-opposition.txt` pp. v–vi).
2. **Overpredicting `relist-increment` (`0.62`):** `gemini-baseline` expected two to four more conferences after November 13 to draft and circulate a separate writing, overlooking that the three pre-conference reschedules (`9/24`, `10/6`, `10/13`) plus the `11/9` relist had already afforded nearly two months for Justice Thomas's statement to be prepared before the November 13 conference.

---

## Assessment of `predicted_reasoning.md` (`predicted_reasoning_quality = 0.76`)

Evaluated strictly against `outcome.json` and `record/snapshots/2026-11-16.json` (with `record/opinion/` absent, leaving the text and any joinders of Justice Thomas's detached statement `unresolved`):
1. **Further relists (`not-borne-out`):** Predicted at least one further distribution (`0.62`, most likely two to four more conferences) after November 13; instead, certiorari was denied immediately on November 16, 2026 with `signals.distribution_count` remaining at `5`.
2. **CVSG (`borne-out`):** Decisively and accurately predicted no CVSG (`0.01`).
3. **Disposition (`borne-out`):** Decisively and accurately predicted certiorari denial (`0.22` grant probability).
4. **Conditional grant scope and route (`unresolved`):** Conditional narrowing of the QP and the `88%` plenary / `12%` summary-disposition split were never tested given denial.
5. **Separate writings on denial (`borne-out`):** Expressly predicted (`0.55` conditional on denial) that at least one Justice would author *"a dissent from (or statement respecting) the denial of certiorari"* and named Justice Thomas (`0.38`) as the likeliest author—matching `outcome.json` (`noted_dissent_from_denial: true`) and `2026-11-16.json` (*"Statement of Justice Thomas respecting the denial of certiorari"*).

Under the forecast-document rubric, getting the disposition, no-CVSG call, and both the existence and specific author of the statement respecting denial right—with one meaningful procedural miss on `relist-increment`—sits right at the `0.75` anchor (**`0.76`**).

---

## Leakage and Big-Case Notes

- **Leakage (`leakage_suspected = false`):** `retrieval_log.json` confirms `forward` mode on `2026-11-09` (`22:01Z–22:12Z`, `result_capture_coverage = 0.0`), seven days prior to `resolved_at` (`2026-11-16`). Even `gemini-baseline`'s `fedcourts query --court scotus --docket-number 25-1324` call ran on `2026-11-09`, before the November 13 conference or November 16 order existed.
- **Big-case read (`0.68`):** *Novotny* posed a sweeping facial Second Amendment challenge to Maryland's post-*Bruen* sensitive-places framework across everyday public locations, though the Court's denial left the issue to percolate further without a national merits ruling, punctuated by Justice Thomas's solo statement respecting denial.
