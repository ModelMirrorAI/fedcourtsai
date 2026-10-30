# Reasoning — P(grant) = 0.12

**Inputs read.** Snapshot `record/snapshots/2026-07-29.json` (cut at 2026-07-30,
forward mode); `record/documents/questions-presented.txt` and `petition.txt`
(102 pages, not truncated, not OCR). No brief in opposition exists on my record —
the response had only just been called for — so I have not inferred what it will
say. I also read the case's committed plain-language summary
(`summaries/2026-10-25.md`), which reports the response deadline extended to
2 Nov 2026 and no action yet; that is post-cutoff but forward-mode public docket
state, and it did not move the number beyond confirming the petition is pending.

**Anchor.** `context.json` gives band `baseline` under `sal-v4` (the statpack
table is also `sal-v4`). Pooling the baseline column's bracketed `reached` rate
over Terms strictly before OT2025 (2017–2024, weighted n ≈ 11,600) gives ≈ 5.2%.
The relist-count cut (1 relist bucket: granted 8.5% + GVR 5.2%) is a shape check;
no committed table conditions on a called-for response.

**Adjustments up.**
- The Court called for a response after a waiver. That means at least one
  chambers flagged the petition; grant rates conditional on a CFR in the paid
  docket are commonly put in the low-to-mid teens, roughly 2–3x the band rate.
- Paid petition by experienced Supreme Court counsel (Troutman Pepper Locke,
  Misha Tseytlin), with a cert-stage amicus from South Carolina — a sovereign
  supporting the out-of-state-lender petitioners on federalism grounds. The
  amicus-count cut puts 1-amicus petitions at 10.3% granted (n≈1,162 resolved)
  vs 2.0% at zero, though that is marginal and overlaps the other signals.
- The petition asserts a 3–2 split (CA3, CA5, CA7 vs CA4, CA10) on how NOPSI's
  "generic interest" language is applied at Younger's important-interest step,
  and a companion CA5 petition (TMX FCS) from the same Pennsylvania proceeding
  is forthcoming — two vehicles on one enforcement action.

**Adjustments down.**
- The "split" is about the level of generality and weighing of an interest — a
  methodology dispute that Pennsylvania can recast as consistent application of
  NOPSI to different facts; such splits are often deemed illusory.
- Younger abstention questions get granted rarely (Sprint, 2013, is the last
  major one), and the dormant-Commerce-Clause/extraterritoriality merits sit
  behind a threshold abstention issue, making the vehicle less attractive.
- The Court may prefer to wait for the CA5 companion petition or deny both.

Net: ~2.3x the anchor, P(grant) = 0.12. Summary route given grant 0.07 (no
intervening decision). Dissent from denial given denial 0.05 — a Thomas/Gorsuch
statement is conceivable on the extraterritoriality angle but uncommon.
`relist-increment` 0.97: the called-for response essentially guarantees a further
distribution (masked by the harness on this moment). `cvsg-increment` 0.02.

**Uncertainty.** I have not seen the BIO; the main swing factor is whether
Pennsylvania credibly disputes the split or raises vehicle problems (e.g., the
state proceeding's posture or adequacy-of-forum arguments). Treat my CFR uplift as
judgement, not a committed rate. One corpus query was made for general priors and
did not inform the number materially; a `--docket-number` lookup returned only
usage text.
