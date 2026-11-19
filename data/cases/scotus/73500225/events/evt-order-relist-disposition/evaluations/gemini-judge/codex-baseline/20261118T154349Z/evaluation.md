# Evaluation of `codex-baseline` — *Novotny v. Moore* (`scotus/73500225`, `evt-order-relist-disposition`)

## Summary of Scores

- **Stage & outcome:** Certiorari stage (`relist` moment, opened `2026-11-09`), resolved `2026-11-16` as **`denied`** (`actual_granted = 0`, `noted_dissent_from_denial = true`, `signals.distribution_count = 5`, `signals.cvsg_date = null`), with `record/snapshots/2026-11-16.json` recording *"Petition DENIED. Statement of Justice Thomas respecting the denial of certiorari."*
- **Quantitative read:** `correct = 1` (`predicted_disposition = "denied"`), `brier_score = 0.1936` (`probability = 0.44`). `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left `null` for harness stamping; `vote_accuracy` and `semantic_grades` are omitted on this cert-stage cell.
- **Qualitative grades:** `reasoning_quality = 0.78`, `predicted_reasoning_quality = 0.58`.
- **Big-case read:** `big_case.evaluator_score = 0.68`.
- **Leakage:** `leakage_suspected = false` (`mode = "forward"`, `influenced_prediction = "not_applicable"`).

---

## Assessment of `reasoning.md` (`reasoning_quality = 0.78`)

### Base-rate verification (`statpack-at` build `ca0c9e1a49e2`)
Because a metrics update landed between the prediction run (`20261109T212928Z`) and evaluation, `codex-baseline`'s base-rate citations were checked against reconstructed statpack build `ca0c9e1a49e2` (`sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`, landed `2026-11-09T14:37:29Z`). Every figure in `reasoning.md` reproduces cleanly against that build: the strictly prior `OT2017–OT2024` `high` risk-set count (`246` grant-family outcomes across `712` weighted resolved petitions), the pooled `relist >= 1` slice (`726 / 3,510 = 20.7%`), the `3+` relist bucket (`180 / 483 = 37.3%`), the CVSG split (`34.8%`, `n = 164` vs. `6.4%`, `n = 13,550`), and the single-amicus slice (`14.9%`, `n = 1,159`). Importantly, `codex-baseline` treated the marginal terminal cuts as context checks rather than multiplying them onto the band anchor, and properly excluded `OT2025` and `OT2026` from its anchor check.

### Legal, procedural, and calibration analysis
`codex-baseline` delivered an accurate, disciplined reading of the docket and primary filings:
- **Procedural decomposition:** It rightly unpacked `distribution_count = 5` on `2026-11-09.json` into three pre-conference `Rescheduled` entries (`9/28`, `10/9`, and `10/16` conferences) followed by a first actual conference on `11/6` and a single post-conference relist on `11/9` for `11/13`.
- **Precedent and vehicle posture:** Using the staged briefs, CourtListener (`Wolford v. Lopez`, opinion `11347760`), and `fedcourts query` (`Moore v. Kipke`, No. 25-1206), `codex-baseline` verified that *Wolford* (decided June 25, 2026) invalidated only Hawaii's private-property affirmative-consent default rule—an issue already removed from this dispute when Maryland dismissed its cross-petition in No. 25-1206—and did not resolve targeted sensitive-place bans. It also accurately identified the pending Third Circuit en banc proceedings in *Koons*, the facial-challenge burden emphasized below, and the overbreadth of Petitioners' proposed "comprehensive government security" rule across an omnibus set of locations.

Where `reasoning.md` fell short was in the **direction and magnitude of its probability adjustments**:
1. **Upward adjustment to `0.44` (`brier_score = 0.1936`):** Despite establishing that three of the five distributions were pre-conference reschedules (meaning the raw `distribution_count = 5` overstated post-conference momentum relative to typical `high`-band petitions), that *Koons* remained pending en banc, that *Wolford* had already been briefed in the BIO and Reply, and that the omnibus facial vehicle was unwieldy, `codex-baseline` adjusted **upward** above the stamped segment base rate to `0.44`—leaving its Brier score worse than a naive prediction at the stamped segment base rate. In particular, assigning `16.7%` unconditional (`38%` conditional) to a cert-order GVR in light of *Wolford* was overgenerous when *Wolford* predated the BIO by nearly two months and addressed only the already-severed private-property default rule.
2. **Underweighting the separate-writing explanation for the relist:** `codex-baseline` assigned only `0.32` conditional on denial to any dissent or statement respecting denial (and `0.60` to further distributions), missing the strong institutional pattern in splitless post-*Bruen* Second Amendment petitions—where pre-conference reschedules followed by a relist frequently reflect a Justice preparing a statement or dissent accompanying denial rather than four votes coalescing for review. It also missed the closely analogous public-transit denial in *Schoenthal v. Raoul* (No. 25-541, denied April 6, 2026 after four distributions), which reinforced the denial call. Even so, its unconditional `order-writers` probabilities (`Thomas: 0.14`, ahead of `Alito: 0.065` and `Gorsuch: 0.045`) were internally coherent with its `0.56 * 0.32 = 0.179` joint denial-writing probability and correctly identified Justice Thomas as the top writer.

---

## Assessment of `predicted_reasoning.md` (`predicted_reasoning_quality = 0.58`)

Graded strictly against `outcome.json` and `record/snapshots/2026-11-16.json` (`record/opinion/` is absent, so the detached text of Justice Thomas's statement is not staged and its internal reasoning and any joinders are `unresolved`):
1. **Disposition (`borne-out`):** Correctly predicted certiorari denial (`44%` grant probability), leaving the Fourth Circuit's judgment undisturbed without a merits opinion.
2. **Further relists and timing (`not-borne-out`):** Forecast at least one additional distribution (`60%`) and disposition in late November or December 2026; in reality, the Court denied the petition immediately after the November 13 conference on November 16, 2026 (`signals.distribution_count = 5`).
3. **CVSG (`borne-out`):** Correctly forecast no CVSG (`2%`).
4. **Conditional grant scope and route (`unresolved`):** Conditional narrowing of the QP and the `62%` plenary / `38%` cert-order split were untested given denial.
5. **Writings on the denial order (`not-borne-out`):** Committed to a **silent denial** as the most likely denial branch (`32%` conditional probability of any noted dissent or statement respecting denial), whereas Justice Thomas issued a statement respecting the denial of certiorari (`noted_dissent_from_denial = true`). Within the writing branch, however, `codex-baseline` explicitly included a "statement respecting denial" and rightly named Justice Thomas as the leading author.

Getting the top-line denial, absence of a CVSG, and lead writer conditional on a writing right—while missing two of the four checkable elements (the immediate post-11/13 resolution with zero further relists and the existence of a separate writing on denial) alongside a hedged `44%` grant probability—places the forecast document moderately above `0.50` at **`0.58`**.

---

## Leakage and Big-Case Notes

- **Leakage (`leakage_suspected = false`):** `retrieval_log.json` confirms `forward` mode on `2026-11-09` (`22:04Z–22:10Z`, `result_capture_coverage = 0.955`), seven days before `resolved_at` (`2026-11-16`). All retrieved external and corpus items predated the `2026-11-10` cutoff.
- **Big-case read (`0.68`):** *Novotny* posed a sweeping facial Second Amendment challenge to Maryland's post-*Bruen* sensitive-places framework across everyday public locations, though the Court's denial left the issue to percolate further without a national merits ruling, punctuated by Justice Thomas's solo statement respecting denial.
