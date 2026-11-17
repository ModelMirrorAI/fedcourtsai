# Evaluation of `codex-baseline` — *Trump v. Thakur*, No. 26-210 (`evt-petition-disposition`)

## Outcome and Quantitative Summary

- **Stage**: `cert` (`moment: distribution`)
- **Realized outcome**: `denied` on `2026-11-16` (`actual_granted = 0`, `signals.distribution_count = 1`, `signals.cvsg_date = null`, `noted_dissent_from_denial = false`)
- **Prediction**: `predicted_disposition = "granted"`, `probability = 0.80`
- **Accuracy (`correct`)**: `0`
- **Brier score (`brier_score`)**: `0.64` (`(0.80 - 0)^2`)
- **Base-rate reference**: Segment base rate and Brier skill score are left to the harness stamp ("the stamped segment base rate"). Base-rate usage in `reasoning.md` was audited against reconstructed prediction-time statpack build `dedb32b153e6` (`sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`).

`codex-baseline` adjusted *upward* above the stamped segment base rate to `0.80` on a petition that was summarily denied on first conference, yielding `correct = 0` and the highest (worst) Brier score in the three-candidate cohort (`0.64`, negative skill relative to the stamped segment base rate).

## Reasoning Quality (`reasoning_quality = 0.74`)

Despite finishing last on Brier score, `codex-baseline` produced the most factually disciplined, accurately cited, and methodologically coherent `reasoning.md` in the cohort.

### What `codex-baseline` got right
- **Spotless record and citation verification**: Every docket date (August 18/19 filing, October 19 BIO, October 27 reply, October 28 distribution for the November 13, 2026 conference), brief citation, and factual detail in `reasoning.md` verified cleanly against the provisioned files—including the surviving NSF/NEH grant expiration dates running to November 2029 (`petition.txt` pp. 11, 24) and the Solicitor General's representation in `cert-reply.txt` pp. 8–9 that district-court proceedings on the relevant claims had been **stayed by agreement** pending Supreme Court resolution (a key vehicle point that both peers missed or misstated).
- **Exact statpack literacy**: Every empirical figure `codex-baseline` cited from reconstructed statpack build `dedb32b153e6`—the prior-Term `sal-v6` `federal` resolved denominator (`203` across OT2017–OT2025, properly excluding in-progress OT2026), the paid-segment terminal relist buckets (`1.8%` on `10,204` at 0 relists, `13.5%` on `2,532` at 1, `41.2%` on `495` at 2, `37.1%` on `482` at 3+), the CVSG split (`6.4%` vs. `34.8%`), and the zero-amicus bucket (`n = 11,109`, `~3.8%`)—matched `dedb32b153e6` to the tenth of a percent. More importantly, `codex-baseline` lucidly explained why terminal marginal cuts cannot be treated as forward transition probabilities at `distribution_count = 1`.
- **Grounded doctrinal reading**: `codex-baseline` verified *NEA v. Finley*, 524 U.S. 569, 586–87 (1998) directly via CourtListener MCP (`opinion_id = 118240`), accurately explaining both why *Finley*'s express reservation of as-applied discriminatory-funding challenges foreclosed facile summary reversal and how the Ninth Circuit distinguished *Finley* and *Rust v. Sullivan* from *Rosenberger* and *Velazquez* on mid-stream viewpoint-based grant cancellations. It also accurately summarized the *NIH v. APHA*, 145 S. Ct. 2658 (2025) split below and the SG's *Fausto*/*Elgin*/*Slaughter* forfeiture response.

### Analytical flaw driving the miss
- **Double-counting features already priced into the `federal` base rate while under-weighting splitless interlocutory percolation**: Starting from the stamped segment base rate—which *already* conditions on the Solicitor General / federal-party risk set where programmatic stakes and clean federal questions are the norm—`codex-baseline` pushed `probability` **upward** to `0.80` (`+6.6 pp`) based on national executive-policy stakes and a squarely framed First Amendment question. At the same time, it gave far too little downward weight to the two classic institutional reasons the Court denies even Solicitor General petitions: (1) the **complete absence of a circuit split** while overlapping permanent-injunction appeals (`2d Cir.`) and sister-circuit appeals were actively percolating (`BIO` pp. 18–27), and (2) **interlocutory review of a preliminary injunction** limited to two agencies and a single university system's researcher class, shadowed by unreached statutory claims and a forfeited-below third-party Tucker Act question. Adjusting *above* the stamped segment base rate on a splitless interlocutory preliminary injunction was a clear calibration error.

Weighing exemplary factual, statistical, and doctrinal rigor against that directional double-counting error yields **`reasoning_quality = 0.74`**.

## Predicted reasoning

`predicted_reasoning_quality` is scored at **`0.24`** (just below the `0.25` anchor, *"A central claim failed, with the rest generic or mixed"*).

In `predicted_reasoning.md`, `codex-baseline` committed to four main propositions:
1. **Primary disposition (`not-borne-out`)**: Predicted that the Court would most likely grant plenary review rather than resolve the dispute summarily or deny certiorari; failed against `actual_disposition = "denied"`.
2. **Conference trajectory (`not-borne-out`)**: Predicted that at least one relist was the more probable path before a grant or contested denial (alongside the structurally vacuous absence of a CVSG); failed against first-conference denial (`distribution_count = 1`, `resolved_at = "2026-11-16"`).
3. **Scope of review if granted (`unresolved`)**: Predicted a clean grant of the single Question Presented as framed; untested because certiorari was denied.
4. **Denial-branch separate-writing call (`borne-out`)**: Explicitly committed that if certiorari were denied, the modal result would be an **unexplained order without noted dissent**, explaining that the Court routinely declines interlocutory pre-split review without airing merits disagreements at the cert stage. That discriminating call on the realized denial branch matched `outcome.json` (`noted_dissent_from_denial = false`, `votes = []`) without relying on any erroneous extra-record premise.

## Leakage and Big-Case Assessment

- **Leakage (`not_applicable`, `leakage_suspected = false`)**: Clean forward run on `2026-11-02`, two weeks before the `2026-11-16` cert denial. `retrieval_log.json` (`result_capture_coverage = 0.943`) confirms `data/qp-topics/**` was explicitly excluded from file searches and all precedent/corpus lookups occurred while the case was genuinely unresolved.
- **Big-case read (`evaluator_score = 0.74`)**: Major national question governing First Amendment limits on viewpoint-based federal grant terminations across roughly $200 billion in competitive programs, moderated at this stage by the bounded two-agency UC-class interlocutory posture and the Court's clean first-conference denial while parallel circuit appeals percolate.
