# Rationale for the numbers

**P(grant) = 0.005.**

*Anchor.* `record/context.json` freezes `band: baseline` under `sal-v4`, `distribution_count: 1`, no CVSG, `mode: forward`, Term 2026. The statpack's "Segment base rate by salience band (sal-v4)" table is the matching version. Pooling the baseline band's bracketed `reached` figure over every rendered Term strictly before OT2026 (OT2017 through OT2025; the OT2026 row is empty) gives roughly 637 grants over a weighted risk-set denominator of 12,720, about 5.0 percent. That is the yardstick this cell is scored against.

*Adjustments down, and why they are large.* The anchor describes every paid petition that ever reached the baseline band, most of them counseled. This petition sits in the weakest part of that population on every dimension the Court visibly cares about:

- **Pro se, paid.** The petitioner signs the petition herself. Counseled paid petitions carry nearly all of the band's grants; pro se paid petitions are granted at a rate far below the band's.
- **No split, no legal question.** All three questions presented are error-correction claims: that the record contained genuine disputes, that McDonnell Douglas was misapplied, and that forfeiture was applied too strictly to a pro se appellant. The petition cites five Supreme Court cases and no circuit authority and alleges no conflict among the courts of appeals.
- **Forfeiture as the ground below.** I read the Fifth Circuit opinion through the CourtListener MCP server (cluster 10705997, published, filed October 17, 2025). The per curiam majority (Judges Smith and Richman) affirmed because the pro se appellate brief cited no relevant authority and did not point to record evidence of pretext, and it noted that four of the ten cases the brief cited appear to be fabricated. A forfeiture holding is an adequate independent ground the Court will not reach past, and the fabricated citations make the case a vehicle the Court would avoid even if it wanted to police summary-judgment standards.
- **Respondent waived.** The City filed a waiver on August 6, 2026 and the Court distributed the petition without calling for a response. The Court calls for a response before granting; a grant from this posture would require a call for response first, which the snapshot does not show.
- **Timing within the snapshot.** The petition was distributed for the September 28, 2026 long conference. The snapshot is dated October 4, 2026 and shows no further entry. The Court customarily releases its long-conference grants a few days before the first October order list, so the absence of any grant entry by October 4 is mildly additional evidence of denial. The Court's order list itself has not issued, so this is a forward cell and the outcome did not exist when I wrote this.

*Adjustments up.* Only one: Judge Dennis's dissent, which is substantive, walks through the record evidence of pretext in detail, and notes that the City never invoked forfeiture. A dissent below is the sort of signal that occasionally draws a Justice to a pro se petition, and Tolan v. Cotton (2014) shows the Court will summarily reverse the Fifth Circuit on the summary-judgment standard. It keeps my number above zero but not above one percent, because Tolan involved a counseled petition on a constitutional claim with no forfeiture ground.

*Net.* I put P(any grant, including GVR) at 0.5 percent, roughly one-tenth of the band anchor.

**Relist increment = 0.07.** The record shows one distribution. The statpack's relist cut (paid scored segment) shows about a quarter of petitions carrying at least one further distribution, but that figure mixes reschedules and the petitions that Justices are seriously considering. For a pro se petition the Court distributed without calling for a response, the realistic relist path is a single hold while a Justice decides whether to write about the dissent below. I weight that at about 7 percent.

**CVSG increment = 0.005.** No federal party, no federal statutory question of first impression, no government interest. Near zero.

**Summary-disposition route (conditional on grant) = 0.7.** The statpack's modern-cert disposition table shows GVRs at roughly 47 percent of the grant family overall. For this case the conditional is much higher than that share, because the only plausible grant is a Tolan-style per curiam or a GVR; a plenary grant on a fact-bound Title VII summary-judgment record with a forfeiture holding is not a realistic outcome. I leave 30 percent on plenary review only because conditioning on an event this improbable means conditioning on something I have not foreseen.

**Dissent from denial (conditional on denial) = 0.03.** Statements respecting denial in pro se employment cases are rare. Judge Dennis's dissent raises the probability somewhat, but the fabricated-citation finding and the forfeiture ground lower it, and the petition itself does not engage either problem.

**Big case score = 0.03.** One plaintiff, one fire department, no legal rule in play.

**What I used.** The snapshot `2026-10-04.json`, `context.json`, the petition text and questions-presented file under `record/documents/` (the petition is a four-page pro se filing with a nine-page appendix; `documents.json` shows no brief in opposition because none was filed), the committed `metrics/statpack.md`, one `fedcourts query` for recent granted priors (little diagnostic value here; recorded in `retrieval.md`), and two CourtListener MCP calls to locate and read the Fifth Circuit opinion.

**Where to discount me.** The number rests heavily on the forfeiture ground and the fabricated citations, both of which I take from the Fifth Circuit majority's description rather than the appellate briefs themselves. I did not read the district court's memorandum ruling or the appendix. A docket oddity: the petition's filing entry is dated March 23, 2026 while the petition is signed "June 2026" and docketed July 17, 2026; I treat this as a clerk-side date quirk with no bearing on the forecast. The petition was filed within 90 days of the January 6, 2026 rehearing denial under either reading, so timeliness is not a problem.
