# Evaluation — codex-baseline

**Cell.** Cert stage (`stage: cert`), forward. The outcome is `gvr` (`actual_granted` 1), resolved 2026-11-09: the Court granted, vacated and remanded "for further consideration in light of *West Virginia v. B. P. J.* and *United States v. Skrmetti*," following the 11/6/2026 conference. There were three distributions in total and no noted separate writing. The segment base rate, its basis and the Brier skill score are the harness's to stamp; I refer to them only as "the stamped segment base rate." Vote accuracy is not scored on a cert cell. No `semantic_grades` block, since no semantic set is declared on a cert cell.

## Scores
- predicted_disposition `gvr` = actual `gvr` → **correct 1**.
- probability 0.90 → **Brier 0.0100**.

## Reasoning quality — 0.85
The rationale starts from the high-band anchor in the committed pack (314/898, about 35%, Terms 2017–2024, strictly before the case Term). It then makes one large adjustment and names its source: the SG's invited brief recommends a GVR in light of B.P.J. and Skrmetti. It does not double-count the CVSG, which the band already reflects. The best point is the observation that the opposition's vehicle objections (party presentation on Turner, no split on the search question, a dismissal-stage posture) lower the odds of plenary review much more than they lower the odds of any grant, because the SG uses the same objections to argue for a GVR. The rationale also states the strongest argument for denial: the remand already ordered could take the new law into account. It keeps the forecast below certainty for that reason, and it treats the SG's characterisation of B.P.J. as advocacy. The Lawrence v. Chater check is general procedural context and is labelled that way. Deduction: the 0.90 is still a judgment rather than a measured figure, and the rationale does not weigh one signal that cut against a fast GVR: the Court called for the SG's views instead of GVR'ing right after B.P.J. The rationale says plainly that the 0.90 is a judgment.

## Predicted reasoning — 0.90
I treated four claims as central:
1. A GVR in light of B.P.J. and Skrmetti, not summary reversal or plenary review. **Borne out**, including both named decisions.
2. Disposition after the already-scheduled 11/6 conference with no further distribution. **Borne out.**
3. No new CVSG. **Borne out.**
4. The remand settles neither question presented. **Borne out.**

The document is specific about the route, the authorities and the timing. It falls just short of 1.0 because the central call largely follows an explicit SG recommendation that a careful reader of the record would also have followed. Its conditional plenary and denial content is ungraded because neither condition occurred.

## Leakage
Forward. The log shows reads of the provisioned record and the statpack, plus general-precedent lookups for *Lawrence v. Chater* only: CourtListener MCP calls, and two uncaptured web attempts whose queries name only that case. Nothing targets this petition's disposition, and nothing is dated on or after 2026-11-09. `not_applicable`; leakage not suspected.

## Big case
0.55 (my own read). The stakes are nationally salient, but this docket was resolved by a GVR, and the governing rules came from B.P.J. and Skrmetti.
