# Evaluation - gemini-baseline

**Cell.** Cert stage, arrival moment, forward mode. Outcome: petition **granted** on 2026-11-13, plenary route, limited to Questions 1 and 2, after two distributions and no CVSG.

**Scores.** Predicted `granted` at 0.98: `correct` = 1, `brier_score` = (0.98 - 1)^2 = 0.0004. The segment base rate, its basis and the skill score are the harness's to stamp; no vote accuracy on a cert cell; claims are scored in code.

**Reasoning quality (0.60).** The direction and the main driver are right: an SG petition from a judgment invalidating a major presidential immigration proclamation is the kind of case the Court takes, and the *Trump v. Hawaii* analogy is apt. The base-rate figures quoted (52.4% for 2025, 60.0% for 2024, range up to 89.5%) match the statpack build the candidate was placed against (`statpack-at`, build 02dd6a20fccc, not the committed pack). But the analysis is thin. It cites two Term rows and not a pooled anchor, and "the weakest bracketed reached rate historically sitting above 50%" is wrong on that same table (2018 reads 43.5%). It moves from there to 0.98 on a single paragraph of salience, with no account of what the residual covers beyond a passing reference to an intervening event, no mention of the D.C. Circuit's stay of its mandate, the absence of a split, the class-relief question's independent pull, or the petitioner-only record at arrival. It describes the relief below loosely as "a nationwide injunction or classwide relief". The number proved well placed, but the document does less to earn it than the outcome suggests.

## Predicted reasoning

Grade **0.60**. The forecast is short and split. Its lead claim - grant on the first or second distribution - held: the petition was distributed for 11/6, relisted once, and granted on 11/13. Plenary review and not a summary disposition also held. But its one discriminating commitment about the shape of the grant, that the Court would likely take all three questions presented, failed: the order limits the grant to Questions 1 and 2. The no-CVSG call is right but nearly entailed by the SG being the petitioner. The dissent-from-denial passage is conditional on a denial that did not happen and is neither credited nor penalised. Right on the disposition, route and timing, wrong on the one specific claim about scope.

**Leakage.** Forward cell; not applicable. The case was genuinely open when predicted. Every call in the log is `unobserved` (coverage 0.0), so I graded on queries: one CourtListener search for the respondent's caption in the D.C. Circuit, aimed at the decision below. Nothing in the log or the prose points at a disposition of this petition, which did not exist yet.

**Big case (0.95).** My own read: the legality of the administration's central border proclamation plus a classwide-relief question under 1252(f)(1), now set for plenary review.
