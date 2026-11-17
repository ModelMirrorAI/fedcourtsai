# Evaluation of `codex-baseline` — *Jack Rabbit, LLC v. Visa Inc., et al.* (`scotus/9026000420`, `evt-petition-disposition`)

## Quantitative Summary

- **Stage:** `cert` (`moment: distribution`)
- **Predicted / Actual Disposition:** `denied` / `denied` (`correct = 1`)
- **Predicted Grant Probability:** `0.03` vs. `actual_granted = 0` (`brier_score = 0.0009`), improving over the stamped segment base rate, though less sharply than `claude-baseline` (`0.012`) and `gemini-baseline` (`0.01`).
- **Semantic Grades:** Omitted (`cert` stage declares no semantic claim set).

## Reasoning Quality (`reasoning.md`) — `0.88`

`codex-baseline` produced a thorough, factually accurate, and methodologically careful analysis in `reasoning.md`:

1. **Statistical accuracy and methodological discipline (verified against placement statpack build `dedb32b153e6`, digest `sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`, reconstructed via `fedcourts statpack-at`):** Checked against the `sal-v6` statpack build in force when `codex-baseline` ran (`dedb32b153e6`), every figure in `reasoning.md` is exact: the frozen `sal-v6` `baseline` reached anchor (`0.0518752467429925`), the overall modern discretionary-cert grant+GVR rate (`(671 + 603) / 44,770 = 2.85%`), the relist buckets (`1.8%` at 0 over `n=10,204`; `13.5%` at 1 over `n=2,532`; `41.2%` at 2 over `n=495`; `37.1%` at 3+ over `n=482`), the CVSG split (`6.4%` over `n=13,549` without CVSG vs. `34.8%` over `n=164` with CVSG), and the zero-amicus slice (`3.8%` over `n=11,109`). `codex-baseline` also rightly cautioned against multiplying overlapping ex-post terminal cuts as if they were independent forward likelihood ratios.
2. **Doctrinal and procedural command:** `codex-baseline` accurately read the docket (both Visa and Mastercard waived response; zero amici; single distribution on Oct. 28 for the Nov. 13 conference; Justice Sotomayor's September time-extension grant properly set aside as non-substantive; 118-page petition truncation bound explicitly verified). Substantively, `codex-baseline` pinpointed why the case is a poor vehicle for the *TransUnion* / *Labcorp* class-standing debate: (a) certification and settlement approval were already final, so the order under review merely enforced an existing settlement release and construed who "accepted" cards under the contract; (b) as the Second Circuit noted in *Old Jericho* (App. 6a–9a), the settling parties compromised the disputed indirect-purchaser defense specifically to avoid litigating it, and a disputed statutory direct-purchaser defense under *Illinois Brick* is not equivalent to lack of concrete Article III injury; and (c) the Second Circuit summary order did not separately address this objector's legal argument at all. It also verified via `fedcourts query` that *Sunoco v. Cline* (`No. 26-1`) was denied on October 5, 2026 while *City of Cleveland v. Pickett* (`No. 25-677`) remained pending after four distributions.
3. **Minor limitation keeping the score below `1.0`:** While its directional reasoning is sound, `codex-baseline`'s downward adjustment from the `5.19%` risk-set anchor to `P(grant) = 0.030` (and `P(relist-increment) = 0.16`) is noticeably conservative for an unpublished summary order that did not pass upon petitioner's question and drew bilateral waivers with zero amicus support. Retaining nearly three-fifths of the baseline risk-set grant rate—a pool dominated as to grants by contested briefs in opposition, multi-amicus filings, and cleaner circuit-split vehicles—gave excessive tail weight to a *Pickett* hold or CFR after `codex-baseline`'s own analysis established how ill-suited this post-judgment contract-interpretation dispute was even for a hold. (Like the other candidates, it also did not anticipate Justice Alito's recusal in Visa/Mastercard matters.)

## Predicted reasoning (`predicted_reasoning.md`) — `0.84`

`predicted_reasoning.md` organized its forecast around five central claims (four unconditional, one conditional on grant):

1. **Denial of certiorari without explanatory opinion, most likely in the ordinary orders following the November 13, 2026 conference** (`borne-out`): Confirmed by `outcome.json` (`denied`, `resolved_at: "2026-11-16"`) and `2026-11-16.json`.
2. **Modal path of no further distribution beyond `distribution_count = 1` (16% chance of additional distribution via CFR, relist, or hold)** (`borne-out`): Confirmed by `signals.distribution_count = 1` and immediate Nov. 16 denial.
3. **No CVSG (0.5% probability)** (`borne-out`): Confirmed by `signals.cvsg_date = null`.
4. **If granted, review limited to a narrowed Question 1 with plenary review favored 65% to 35% over a summary cert-order disposition** (`unresolved`): Untested given the denial; neither credited nor penalized.
5. **No noted dissent or statement respecting denial (3% conditional probability, naming Kavanaugh as most plausible separate writer)** (`borne-out`): Confirmed by `noted_dissent_from_denial = false` and the silent summary denial entry.

All testable central claims held up cleanly, and identifying Justice Kavanaugh (author of the *Labcorp* DIG dissent) as the most plausible separate writer if one occurred was grounded in the record. The grade (`0.84`) sits slightly below `claude-baseline`'s (`0.88`) because `codex-baseline` hedged the timing/relist call somewhat more (`"most likely in the ordinary orders following the November 13, 2026 conference"`, `16%` further-distribution tail) and likewise missed Justice Alito's recusal on the November 16 order line.

## Big-Case Read & Leakage Check

- **Evaluator `big_case` read (`0.15`):** Despite the $5.6 billion MDL settlement backdrop, this solo-objector petition seeking review of an unpublished contract-interpretation summary order drew bilateral waivers, zero amici, no CFR, and a first-conference summary denial without dissent. (`codex-baseline`'s `0.62` weighted the hypothetical national class-action stakes heavily relative to the petition's severe vehicle flaws and non-engagement at the Court.)
- **Leakage (`not_applicable`, `leakage_suspected = false`):** Forward prediction (`run_id: 20261031T173439Z`) executed 16 days before the November 16, 2026 denial. Its 34 logged calls (`result_capture_coverage: 0.853`; 5 `unobserved` web-search calls queried prior SCOTUS opinions in *Labcorp* `24-304` and *TransUnion* `594 U.S. 413`) were strictly pre-outcome.
