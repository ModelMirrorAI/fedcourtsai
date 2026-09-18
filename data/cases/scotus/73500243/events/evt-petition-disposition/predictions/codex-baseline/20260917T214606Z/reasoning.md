# Rationale for the probabilities

## Information set

This is a forward cert-stage forecast of Donna Birks v. Clemente Javier Aguirre-Jarquin, Supreme Court docket 25-1341. The petition-kind event has no explicit stage or moment; I apply the prompt's cert fallback and provide all five cert claims. I read the provisioned September 17, 2026 snapshot, context, questions presented, document manifest, and relevant petition argument passages. The snapshot's own creation field is September 16, 2026. No current docket refresh or search for this petition's disposition was performed, and I have no known disposition of this petition to disclose.

The manifest labels the petition extraction truncated and dates its fetch to July 18, 2026. Its principal argument and conclusion are present, but I do not assume the full appendix survived. The August 31 opposition and September 10 reply are recorded in the snapshot but were not provisioned as text. I retrieved the opposition directly from its exact, pre-decision Supreme Court PDF URL in the snapshot and read its questions, contents, and selected substantive pages (identified in retrieval.md). I did not retrieve the reply, and my treatment of the opposition is not a representation that the petitioner's final response has been considered. Party characterizations remain advocacy, not established facts.

## Numerical anchor

The frozen context specifies sal-v4, elevated, Term 2025, two distributions, and no CVSG. I retain that conditioning rather than assigning a different band based on the caption or the analyst's employment. The matching committed sal-v4 table supplies an elevated reached-risk-set anchor. Pooling every displayed prior Term, 2017–2024, using statpack.json's unrounded prefix rates and weighted denominators gives 484 / 2,810 = 17.2242%. I exclude the case's own 2025 Term and the 2026 row. This is the reached rate, not the lower terminal-band rate.

Source vintage is the committed statpack version last changed by commit 55121cdb8 on September 14, 2026, read during this cell. That is a publication vintage, not a verified corpus-wide last-pull or snapshot maximum: neither underlying freshness measure is supplied here, and I did not access a corpus blob. The figures are historical estimates in this committed pack, not a claim about today's complete corpus.

I also consulted the modern-cert, originating-circuit, paid-segment relist, and CVSG cuts. They provide population shape, not independent likelihood ratios to multiply into the band anchor. In particular, terminal relist buckets are not forward probabilities of another distribution. The pack itself warns that rescheduling before first consideration can increase the distribution count.

## Adjustment to 10%

The largest downward adjustment is procedural: both listed conferences are still in the future. The second distribution follows a requested response and completed briefing, not a demonstrated hold after an actual conference. I therefore discount the repeated-consideration signal embedded in the elevated anchor without altering the harness's count. The response request remains a positive attention signal and is why I do not collapse the estimate to a routine private-petition floor.

The petition's own argument is also a vehicle warning. At printed pages 20–21 it describes differing causation formulations but asserts that Birks wins under any of them. That makes the alleged difference less useful as an outcome-determinative conflict. Its pages 12 and 15–16 identify the appellate court's refusal to reach materiality through pendent jurisdiction. The Court would have to confront that posture, not merely announce that causation matters.

The opposition argues that the surviving claim concerns deliberate evasion of verification, not an unknowingly mistaken comparison (printed pages 17–19). It also characterizes causation as unresolved below and available on remand (pages 13–15). Those responses make this look more like a dispute about permissible factual inferences than a clean test of negligence liability. On immunity, it argues that fabrication precedents gave adequate notice despite factual differences (pages 21–22). I treat these as substantial vehicle objections, not conclusive answers. The petition's specificity argument, particularly at pages 30–34, leaves a real possibility of summary intervention and supports keeping a nontrivial grant tail.

## Other judgments and limitations

The 22% redistribution probability recognizes the response request and the possibility of closer review, but its modal result is no further distribution. It is a subjective forward hazard, not a calculated terminal-bucket frequency. The 0.5% CVSG estimate reflects the absence of an evident need for the Solicitor General's views. The 55% summary-route figure is conditional on the 10% grant tail: an immunity-specific correction seems somewhat more plausible than a plenary examination of five intertwined questions. The 3.5% denial-writing estimate is likewise conditional on denial, not a prediction of hidden cert votes.

The significance score of 0.49 reflects the consequences for forensic accountability and immunity in wrongful-conviction litigation, while recognizing the narrow procedural vehicle. The snapshot marks this petition noncapital; its underlying murder prosecution does not turn this civil immunity petition into an emergency capital application.

Confidence is limited by the unreviewed reply, truncated petition appendix, and absence of a measured response-request/rescheduling-specific base rate. The 10% forecast is an explicit judgmental adjustment, not the output of a fitted model. The disagreement about the analyst's knowledge should not be resolved by silently accepting either advocate's preferred facts.
