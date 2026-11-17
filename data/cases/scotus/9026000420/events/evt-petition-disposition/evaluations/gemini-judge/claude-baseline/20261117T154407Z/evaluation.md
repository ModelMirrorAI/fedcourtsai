# Evaluation of `claude-baseline` — *Jack Rabbit, LLC v. Visa Inc., et al.* (`scotus/9026000420`, `evt-petition-disposition`)

## Quantitative Summary

- **Stage:** `cert` (`moment: distribution`)
- **Predicted / Actual Disposition:** `denied` / `denied` (`correct = 1`)
- **Predicted Grant Probability:** `0.012` vs. `actual_granted = 0` (`brier_score = 0.000144`), improving substantially over the stamped segment base rate.
- **Semantic Grades:** Omitted (`cert` stage declares no semantic claim set).

## Reasoning Quality (`reasoning.md`) — `0.86`

`claude-baseline` delivered a concise, accurate, and well-calibrated rationale with zero factual errors on the docket or statistical record:

1. **Base-rate discipline (verified against placement statpack build `dedb32b153e6`, digest `sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`, reconstructed via `fedcourts statpack-at`):** Because the committed statpack in this evaluation checkout had advanced to `sal-v8`, `claude-baseline`'s cited numbers were checked against its placement `sal-v6` statpack build (`dedb32b153e6`). Every figure `claude-baseline` cited matches that build to the decimal: the frozen `baseline` risk-set `cert_anchor.rate` (`0.0519`), the `relist_bucket = 0` terminal slice (`1.3%` granted + `0.5%` GVR = `1.8%`, `n=10,204`), and the `sal-v6` per-Term terminal baseline rates (`0.7%–2.0%`). Crucially, `claude-baseline` explained *why* a petition distributed on bilateral respondent waivers sits well below its risk-set anchor without mechanically equating the ex-ante hazard to a terminal cut: reaching a grant from `distribution_count = 1` with waivers requires first drawing a call for a response (CFR), relist, or hold.
2. **Procedural posture and vehicle diagnosis:** `claude-baseline` accurately read the docket (`Visa` and `Mastercard` both waived response; solo petitioner counsel vs. experienced Supreme Court counsel on the waivers; zero amicus briefs) and cleanly identified the dispositive vehicle problems: the decision below is a non-precedential Second Circuit summary order resting on the companion published opinion in *Old Jericho Enterprise, Inc. v. Visa Inc.*, 175 F.4th 172 (2d Cir. 2026), construing who "accepted" payment cards as a matter of settlement-contract intent, and declining to decide any Clayton Act § 4 standing question—leaving petitioner's borrowed *Tyson Foods* / *Labcorp* circuit split unpresented.
3. **Companion-case verification:** Using `fedcourts query`, `claude-baseline` checked both pending petitions cited in the petition's companion pitch, verifying that *Sunoco v. Cline* (`No. 26-1`) had already been denied on October 5, 2026 (eliminating the primary grant-or-hold hook) while *City of Cleveland v. Pickett* (`No. 25-677`) remained pending after four distributions in a certification (not post-judgment settlement-allocation) posture.
4. **Minor gaps keeping the score below `1.0`:** The doctrinal treatment in `reasoning.md` is relatively compact—it does not unpack the finality/res judicata posture after *Fikes Wholesale, Inc. v. Visa U.S.A., Inc.*, 62 F.4th 704 (2d Cir. 2023), the *Lexmark* distinction between statutory direct-purchaser merits (*Illinois Brick*) and Article III standing, or the fact that the Second Circuit summary order did not pass on petitioner's constitutional/Rule 23 objection at all. (It also did not note Justice Alito's routine recusal on Visa/Mastercard dockets, though `reasoning.md` did not lean on that point.)

## Predicted reasoning (`predicted_reasoning.md`) — `0.88`

`predicted_reasoning.md` led with four concrete, unconditional claims about what the Court would do, alongside one conditional grant-scope block:

1. **Immediate denial at the November 13, 2026 conference on the November 16 order list without a CFR** (`borne-out`): Exact match to `outcome.json` (`denied`, `resolved_at: "2026-11-16"`) and `2026-11-16.json`.
2. **Zero further distributions/relists (`~8%`) and no hold for *Pickett*** (`borne-out`): Exact match to `signals.distribution_count = 1`.
3. **No CVSG (`~0.3%`)** (`borne-out`): Exact match to `signals.cvsg_date = null`.
4. **No noted dissent from denial (`~1.5%`)** (`borne-out`): Exact match to `noted_dissent_from_denial = false` and the summary order entry.
5. **Conditional grant scope (narrowed QP 1, ~25% hold/GVR share, drop QP 2)** (`unresolved`): Untested given the denial, earning neither credit nor penalty under the rubric.

The document earned a high grade (`0.88`) because it committed crisply and unhedgedly to the exact conference, order-list date, absence of a CFR, rejection of a *Pickett* hold, and silent summary denial. It stops short of `1.0` because a silent first-conference waiver denial tests procedural trajectory rather than merits reasoning and because the document did not anticipate the one distinctive notation on the November 16, 2026 order line—that Justice Alito took no part in the consideration or decision of the petition.

## Big-Case Read & Leakage Check

- **Evaluator `big_case` read (`0.15`):** While the underlying MDL settlement totals $5.6 billion, this petition was a solo objector's post-judgment challenge to an unpublished contract-interpretation summary order that drew bilateral waivers, zero amici, no CFR, and a routine first-conference summary denial without noted dissent. (`claude-baseline`'s `0.30` appropriately discounted the $5.6B headline for the narrow contract-interpretation posture.)
- **Leakage (`not_applicable`, `leakage_suspected = false`):** Forward prediction (`run_id: 20261031T173439Z`) completed 16 days before the November 16, 2026 order, with full result capture (`1.0`) across 14 clean calls and zero post-event material.
