# Evaluation: gemini-baseline

## Outcome and mechanical score

This is a cert-stage cell. The structured prediction names `denied`, matching the November 9, 2026 outcome. Therefore `correct = 1`; Brier score `(0.35 - 0)^2 = 0.1225`. The stamped segment base rate and resulting skill belong to the harness. No cert votes, mechanical claims, or semantic propositions are manually scored.

## Rationale quality: 0.42

The rationale correctly recognizes that a response request after waiver and six amicus filings can warrant more attention than a routine petition. It also keeps denial as the structured modal outcome and recognizes that redistribution after opposition does not require a grant.

The weaknesses are substantive, not a penalty for brevity. Calling the presentation two clear circuit splits largely repeats the petition's advocacy without considering the opposition's disputed waiver/finality facts or its argument that important split authorities are older or intermediate state decisions (opposition, printed pages 10-13). The rationale gives no vehicle analysis and no explanation for the size of the jump to 0.35 or for why amicus volume alone implies its separate-writing probability. A call for response establishes interest, not four votes to grant.

The calibration problem persists against the actual placement-era pack, not merely today's pack. `fedcourts statpack-at` recovered build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, with no alternative build. Its sal-v4 table directs frozen-band predictions to bracketed reached/risk-set values. The rationale's claimed sub-one-percent band anchor neither identifies that population nor matches those strictly prior-Term risk-set rows. This is a candidate calibration error, not an inferred pack-version mismatch. I do not hand-pool or quote a substitute scored baseline; the anchor remains the stamped segment base rate.

The unexplained denial confirms the modal label but does not validate the asserted legal conflicts or disclose the Court's actual reasons. The reasoning grade is independent of the separate forecast's procedural calls and independent of the mechanically scored claims.

## Predicted reasoning

Grade: **0.50**. The document's central commitments are another distribution, a conditional Question 1 grant, a conditional preference against summary GVR, and no CVSG. Another distribution and no CVSG are borne out. The grant-only propositions are unresolved because their condition never happened; they earn neither credit nor penalty.

The additional statement that a dissent is merely plausible earns no credit when the outcome records none, but it is not recast into a categorical failed forecast or treated as an availability gap. The document is gradeable, not null, but mostly generic: it supplies little discriminating unconditional content beyond routine redistribution and no invitation, and does not itself commit expressly to the ultimate denial. The structured disposition earns its separate mechanical credit, not extra forecast-document credit.

## Leakage

The log records forward mode with 22 calls, all `unobserved`. I read the queries rather than treating null result dates or digests as proof that nothing was returned. The calls name only ordinary provisioned inputs, statpack, output operations, and validation; no external lookup, outcome file read, or later-history query appears. The prose contains no indication of knowing the November 9 denial. On that evidence, retrieved outcome material is false, influence not applicable, and suspicion false, with explicitly limited result visibility. Zero capture is the log's standing shape, not a provisioning fault.

## Significance

Independent significance assessment: **0.40**, grounded in the potentially national access-to-takings-remedies questions, the local permitting vehicle, and the absence of a substantive rule in the actual disposition.
