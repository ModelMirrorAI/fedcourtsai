# Evaluation — codex-baseline, scotus/9026000241, evt-petition-arrival-disposition

Cert-stage, arrival-moment, forward cell. Outcome: petition **denied** 2026-11-09 after a single distribution (respondents waived; distributed for the 11/6/2026 conference). No CVSG, no noted dissent. The segment base rate and skill are stamped by the harness from the frozen `baseline` band's risk set; I quote no rate of my own. I left `vote_accuracy` out because this is a cert cell.

**Correct** (denied vs denied). Brier (0.018 − 0)² = 0.000324.

**Reasoning (0.80).** Anchors on the frozen baseline band's strictly-prior arrival rate (the risk-set anchor the cell calls for) and adjusts well below it on concrete, case-specific grounds: an unpublished decision below, a fact-intensive summary-judgment posture, and — the analysis's best point — that *Murphy v. Schmitt* was decided at the pleading stage and expressly declined to treat officer statements as the objective evidence required at summary judgment, which undercuts the asserted split. It also catches that the QP's "defeat probable cause" framing misstates the *Nieves* exception. Upside factors are weighed rather than ignored, and the limits of what it could verify (no access to the Fifth Circuit opinion, no BIO) are stated. The outcome — a single-conference denial on a waiver — is fully consistent with the analysis. Docked slightly because the vehicle points are partly inferred from the petition alone.

**Leakage.** Forward mode, predicted 2026-08-25 while the petition was undecided. The retrieval log shows only pre-decision precedent lookups and searches for the unpublished decision below. Nothing in the log or the prose touches this petition's disposition. Graded `not_applicable`, not suspected.

**Big case.** My own read is 0.15: a fact-bound application of *Gonzalez* from an unpublished decision.

## Predicted reasoning

Grade 0.65. I treated these as the central claims:

- *The Court denies the petition.* — **borne-out**. Docket: 'Nov 09 2026 Petition DENIED.'; outcome actual_disposition denied.
- *The petition receives one initial conference distribution after the response period and is denied without a further relist.* — **borne-out**. Respondents waived Sep 29 2026; single distribution Oct 07 2026 for the 11/6/2026 conference; denied Nov 9; outcome distribution_count 1.
- *No call for the views of the Solicitor General.* — **borne-out**. Outcome signals.cvsg_date null; no CVSG entry on the docket.
- *No Justice notes a dissent or writes a statement on denial.* — **borne-out**. Outcome noted_dissent_from_denial false; denial order carries no noted writing.

Every central claim held, but each is close to the modal path of a paid baseline-band petition (one distribution, denial, no CVSG, no writing). That limits how much discriminating content the forecast carries, so the grade sits between the 0.5 and 0.75 anchors. The conditional content (a reformulated QP or the GVR-versus-plenary split if the Court granted) earns neither credit nor penalty, because the Court denied.
