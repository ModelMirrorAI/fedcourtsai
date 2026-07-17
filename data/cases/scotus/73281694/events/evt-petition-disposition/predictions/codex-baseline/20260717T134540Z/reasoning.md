# Prediction: denied

I estimate a **12% probability of any grant** and predict denial of certiorari. The grant probability includes plenary review or a GVR, although the record supplies no plausible intervening authority that makes a GVR the likeliest grant-side disposition.

## Question and governing standard

Norfolk Southern asks whether Pennsylvania may, consistently with the dormant Commerce Clause, exercise general personal jurisdiction over an out-of-state company solely because it registered to do business in Pennsylvania, where the plaintiff, defendant, and underlying conduct are all outside Pennsylvania. Certiorari ordinarily requires four Justices and is most likely when an important federal question is cleanly presented, has generated conflicting authority, and is free of jurisdictional or vehicle defects.

## Grant-side signals

The issue is important and recurring. The petition says Pennsylvania's rule exposes nationally operating companies to all-purpose jurisdiction for claims arising anywhere, encourages forum shopping, and may deter interstate expansion. It is also unusually salient because this is the same litigation in which the Court held the Pennsylvania scheme consistent with due process while expressly leaving the Commerce Clause question open. Justice Alito's concurrence stated that Pennsylvania's assertion of jurisdiction likely violates the Commerce Clause, and the four Mallory dissenters likewise saw no legitimate Pennsylvania interest in this forum-unconnected dispute. That creates a plausible merits coalition of at least five Justices if the Court reaches the question.

The docket adds modest positive signals: the Court requested a response after respondents initially waived one, the petition is supported by two amici, and the case has been distributed for the September 28 conference. The question is concrete, and its application to an interstate railroad strengthens the asserted commerce burden.

## Denial-side signals

The BIO's vehicle objections are substantial and drive the forecast. Its appended January 2025 order expressly says the trial court had already found Norfolk Southern's dormant-Commerce-Clause argument waived under Pennsylvania procedure. On respondents' account, no lower court decided the federal merits, the case remains interlocutory, and the state appellate courts merely denied discretionary review. Those facts raise preservation, independent-state-ground, finality, and advisory-opinion concerns. Even Justices interested in the merits can wait for a case without those obstacles.

The decisional conflict is also immature. The BIO identifies no federal circuit or state-high-court split, notes that certiorari was recently denied in *Lynn v. BNSF Railway*, and describes one relevant federal district-court case as still on appeal. A limited CourtListener search likewise surfaced only sparse post-*Mallory* treatment. In *Tom James Co. v. Zurich American Insurance Co.*, an Indiana intermediate appellate court declined to reach a dormant-Commerce-Clause issue because it had not been preserved, illustrating the procedural-avoidance problem rather than a developed merits split.

## Calibration

The committed statpack reports a 5.36% estimated grant rate for paid petitions in the 2025 Term and a 3.0% rate for petitions without a CVSG. This petition merits an upward adjustment for the requested response, repeat appearance, express reservation, likely merits interest, and significance. I then discount sharply for the unusually serious waiver/finality problems and lack of a mature split, resulting in 12%.

I do not predict individual votes because cert-stage votes are not public and the likely merits alignment does not reliably identify which four Justices would accept this procedurally compromised vehicle.

## Inputs and leakage handling

I relied on the July 17 snapshot, the questions presented, the complete petition, and the complete BIO. During input-path discovery, the workspace listing showed that an `outcome.json` path exists even though `event.yaml` says `resolved: false` and `context.json` says `forward`. I did not open that file, learned no disposition from it, and did not use it in this forecast. I recorded the mismatch in `flags.json`.

The ranged corpus query failed on DNS resolution before any corpus bytes were read, so no retrieved corpus priors informed the forecast. I instead used the committed statpack and the available CourtListener MCP legal-research surface; details are in `retrieval.md`.
