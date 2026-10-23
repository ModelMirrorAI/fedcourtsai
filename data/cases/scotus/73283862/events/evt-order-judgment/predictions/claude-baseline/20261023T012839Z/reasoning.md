# Reasoning — P(disturbed) = 0.80

**Inputs.** Snapshot `2026-10-13.json` (forward cell; date cut at 2026-10-14). Provisioned
documents read: questions-presented, brief in opposition (United States, May 2026), cert
reply (June 2026, first ~14k characters). The petition and appendix were not read directly; I took the posture from the BIO and reply. No
merits briefs were provisioned or consulted — correct for a `moment: grant` cell, so this is
a forecast from cert-stage papers and the docket skeleton. The petitioner's 2026-08-05
supplemental brief is on the docket but its text was not provisioned; I do not know what it
said. The CourtListener MCP returned HTTP 429 on my first call, so I made no further live
retrieval (flagged).

**Anchor.** `metrics/statpack.md`, *The merits docket (granted cases)*, which publishes an
`excluded` count, so it is quotable. Grant date 2026-10-13 → grant Term 2026; pool grant
Terms 2016–2025. The table renders no 2016 row (no parsed judgment), so the pool is
2017–2025: 377 disturbed / 540 parsed = **69.8%**, well above the 30-judgment floor.
Coverage: 540 parsed of 596 granted overall; the 2025 Term is the most censored (24 parsed of
51 granted), so its 70.8% skews to quick dispositions.

**Adjustments up (to 0.80).**
- The government's BIO does not defend the Eleventh Circuit's Hamilton rule on the merits;
  it argues the split is shallow, has little practical effect, and that the vehicle is poor
  (procedural default, untimeliness). The reply notes this pointedly. When the respondent
  has effectively not defended the rule below, reversal/vacatur rates run well above base.
- The Court granted an IFP federal prisoner's petition over the SG's opposition after five
  distributions — a deliberate grant of a pure procedural question, which the Court usually
  takes to correct the rule, not to bless it.
- Precedent (Miller-El, Buck, Slack) frames the COA as a threshold debatability screen; an
  out-of-circuit holding the other way is hard to call undebatable.

**Discounts (why not 0.9).** A conservative majority could accept the futility argument
(a COA only leads to a panel bound by the same precedent) and the strict-AEDPA reading; the
vehicle defenses give a route to affirm on alternative grounds if a majority thinks the
claim is non-debatable regardless; and I lack the supplemental brief and all merits
briefing. DIG risk is small but real given the government's vehicle objections.

**Judgment label.** I chose `vacated` over `reversed` because the natural remedy is to send
the case back for a COA determination under the correct standard with the government's
alternative defenses open; "reversed and remanded" is nearly as likely (Slack, Jimenez,
Buck used reversal language). Both count as disturbed, so the probability is unaffected.

**Votes.** Low confidence (0.55). Thomas and Alito are the likeliest dissenters on habeas
gatekeeping; Gorsuch has sided with criminal defendants on textual procedural questions and
Kavanaugh/Barrett/Roberts tend to favor uniform national rules resolving splits.

**Big-case score 0.3.** Recurring, affects every COA application nationwide, but procedural
and low-profile.
