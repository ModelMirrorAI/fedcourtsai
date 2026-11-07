# Reasoning — Rydberg v. United States, No. 26-441 (P(grant) = 0.025)

**Inputs read.** Snapshot `record/snapshots/2026-11-07.json`, `record/context.json`, `record/same-question.json`, `record/documents/questions-presented.txt` and `petition.txt` (62 pp., not truncated, not OCR). No brief in opposition exists: the United States **waived** its response (Oct 29, 2026). No decision-below or lower-court-docket file was staged, so I relied on the petition's description of the Fifth Circuit's ruling.

**Posture.** This is a paid petition from an unpublished per curiam Fifth Circuit opinion (No. 25-10365) affirming health-care-fraud conspiracy and money-laundering convictions. Rehearing en banc was denied without noted dissent. The snapshot shows one distribution, for the conference of Dec 4, 2026, with no relist and no CVSG. The amicus count is zero.

**Anchor.** `context.json` freezes band `baseline` (sal-v7), and its `cert_anchor.rate` is **0.0515** (10-Term lookback). That matches the baseline column's bracketed `reached` figures in the statpack (roughly 4–6% across OT2017–OT2025).

**Adjustments, all downward:**
- **No circuit split is claimed.** The petition relies on Rule 10(c), arguing that the decision conflicts with this Court's precedent, and asks the Court to "disapprove" a Fifth Circuit precedent (*United States v. Anderson*). That is an error-correction pitch.
- **The decision below is unpublished**, and it rests on an **alternative harmless-error holding**: the jury also found a conspiracy to defraud BCBS. The petition disputes that holding (general-verdict problem; the money-laundering counts rest on FECA funds), but it makes the case a worse vehicle.
- **The SG waived a response.** The Court sometimes calls for one anyway, but a waiver with no amici is the typical profile of a denial.
- QP 3 (how the rule of lenity applies, citing the Kavanaugh and Gorsuch concurrences in *Wooden*) is a request for general guidance. The Court rarely grants that, especially when the vehicle depends on a statutory question it has not shown divides the circuits.
- The FECA/§ 24(b) question is a genuine, recurring textual issue in DOL-OWCP fraud prosecutions, and counsel is an experienced cert practitioner. These points keep the number from falling to the private-IFP floor.
- `same-question.json` lists no similar petitions above threshold, so I see no hold or split signal.

The net is about half the band anchor: **0.025**. The relist-0 bucket of the relist cut (about 1.8% grant family) is the cut this petition will most likely end in.

**Increments.**
- **Relist:** about 10%. The main route is the Court calling for a response from the SG, which would push the case to a later conference, plus the chance of a reschedule.
- **CVSG:** essentially zero. The United States is the respondent, so the Court would call for a response rather than invite the SG's views.
- **Summary route given a grant:** 0.15. A grant would most likely be plenary, but a GVR is possible if some pending § 24(b) or lenity decision intervened. I know of none.
- **Dissent from denial:** 3%. Justice Gorsuch's interest in lenity is the most plausible source, but this is a weak vehicle for it.

**Uncertainty.** I did not verify whether other circuits have addressed FECA under § 24(b). If a published decision elsewhere conflicts, my number is too low. The petition does not claim one, which suggests there is none. No CourtListener or web retrieval was done; this rests on the provisioned record and the statpack.
