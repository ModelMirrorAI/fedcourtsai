# Reasoning — P(stay granted) = 0.02

**Inputs read:** snapshot `2026-11-09.json` (a single entry: the application, submitted to Justice Gorsuch, marked CAPITAL CASE, linked with 26-6095), `record/context.json` (forward mode, arrival-position cut, band null as expected for an interim cell, no response requested, no referral, 0 amicus), and `record/documents/application.txt` (10 pages, not truncated, not OCR-derived). No cert petition, response or decision below was staged. My read of the underlying claim therefore comes only from the application's summary of it.

**Anchor:** the statpack's interim section, table "Substantive applications by applicant class". It pools the ten application-Terms before OT2026 on the finer reading. The whole pool is 11.7% (156/1337), which clears the floor of 50 and is the yardstick. The cell that matches this application is `private` × `capital`: **3.5% (10/288)**. I leaned on that cell, not on the pool. A private capital stay is a very different population from the federal and state applications that drive the pooled rate. The 3.5% probably overstates the rate for a last-minute stay pending a novel cert petition. Some capital "grants" in that cell are likely stays tied to a pending merits case, or cases where the State conceded.

**Adjusting down from 3.5%:**
- The question is an extension of *Peña-Rodriguez v. Colorado*, which the Court framed as limited to racial bias. Its cases on the no-impeachment rule (*Tanner*, *Warger*) point the other way. No split is alleged, and four votes for cert are improbable.
- The case comes up through a successive state post-conviction proceeding. The OCCA likely relied on state procedural bars (waiver/successive-petition rules), and that independent and adequate state ground is a serious vehicle problem. I cannot confirm this because the decision below was not staged.
- The application is filed three days before the execution. The Court's equitable doctrine on last-minute stays (*Bucklew*, *Hill v. McDonough*) weighs against it, though the application blames the late discovery on the State.
- The Court's recent practice in Oklahoma executions has been to deny such stays, and Oklahoma's AG is not confessing error here (contrast *Glossip*).

**Why not lower:** the application does allege knowing falsity by prosecutors (a *Napue* theme), and it has a sworn juror declaration. That at least gives the liberal Justices a basis to note dissents. Still, three votes don't make five. I settle at 2%.

**Ladder claims:** capital stay applications are routinely referred to the full Court, so referral is 0.9. The State usually responds uninvited, so a formal call is unlikely (0.08). Amicus filings on a three-day capital stay are rare (0.04).

**Uncertainty:** I have not seen the OCCA opinion or the cert petition. If the OCCA reached the merits without a procedural bar, the vehicle would be cleaner, but the grant probability would still be low. Retrieval was limited to two corpus queries (no row for 26-6095, and an uninformative listing of recent "granted" applications that are mostly extensions). I did not use web or CourtListener lookups.
