# Why P(grant) = 0.18

**Anchor.** `record/context.json` puts this case in band `baseline` under sal-v4, with distribution_count 1 and no CVSG. The statpack's sal-v4 band table gives a bracketed `reached` rate of about 4–6% per Term for `baseline` over 2017–2025, roughly 5% pooled. The 2026 row (1.4%, n=146) is this case's own Term and very thin, so I set it aside. The band's version matches the table's.

**Upward adjustments, from the provisioned petition and the snapshot:**
- **The split is real and acknowledged.** The petition (`record/documents/petition.txt`; the QP is in `questions-presented.txt`) says the South Carolina Supreme Court expressly declined to follow *In re Whittaker Clark & Daniels*, 176 F.4th 241 (3d Cir. 2026). That case involved the same receiver, appointed by the same South Carolina trial court. A corpus lookup shows the receiver himself (Protopapas) has petitioned from Whittaker in No. 26-159, with a second petition, No. 26-263 (Official Committee of Talc Claimants), from the same judgment. So both sides of the conflict are before the Court in separate vehicles. That is an unusually strong signal that the question will be resolved somewhere.
- **The question recurs.** The petition says the same trial court has set up more than a dozen extraterritorial receiverships. It also cites a U.K. injunction against this receiver, which gives the case foreign-relations friction.
- **Signals of quality.** Gibson Dunn is counsel of record. Three amici filed at the petition stage, jointly with the companion petition 26-350 from the same judgment.

**Downward adjustments:**
- **Finality under § 1257.** A trial on the merits remains on remand, so jurisdiction depends on the *Cox*/*Langdeau* exception. The Court often avoids interlocutory state-court vehicles.
- **The Court may prefer the federal vehicle.** In that case this petition is held, and the grant probability then depends on how the merits come out (a GVR only if the receiver loses).
- **Respondents waived.** I expect a response request to neutralize this, but it is still mildly negative.
- I have not read the Whittaker petitions themselves. 26-263 looks like it may turn mainly on bankruptcy questions rather than the receivership question, which weakens the "both sides want review" reading.

**Rough decomposition.** P(the Court takes the receivership question in some vehicle this Term or next) ≈ 0.3. Given that, P(this case gets a grant or GVR) ≈ 0.6. Adding a small residual gives about 0.18. That is roughly 3–4 times the band anchor, which I think the corroborated split and the companion federal petitions justify. I would not go higher, because of the finality problem and the fact that the federal vehicle would usually be preferred.

**Increments.** I put relist-increment at 0.85 because of the very likely response request and the pending related petitions. I put CVSG at 0.08 because the foreign-relations angle makes a CVSG possible but not likely. Summary route given a grant is 0.4, driven by hold-and-GVR. Dissent from denial is 0.05.

**Inputs and discounts.** I read the snapshot `2026-10-23.json`, the QP file, and the petition (skimmed, focusing on the split, the U.K. injunction, and the jurisdiction section). I did not read the appendix (`appendix.txt`, truncated) in depth. There is no BIO because both respondents waived. The vintage of the corpus rows for 26-159 and 26-263 is their last live poll on 2026-10-17. Their status may have changed since then; I did not check CourtListener.
