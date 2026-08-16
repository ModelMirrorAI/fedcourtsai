# Reasoning — why P(disturbed) = 0.65

**Anchor.** The committed statpack's "The merits docket (granted cases)" section
publishes an `excluded` count (67), so its pooled rate is quotable and is the
baseline my skill is scored against. Grant Term for this cell is OT2025 (grant
order 2026-01-16, from the event's `opened_at`). Pooling `disturbed` over
`parsed` across grant Terms strictly before 2025 within the ten-Term window
(the pack renders 2017–2024; the ten-Term window would reach back to 2015, but
2017 is the earliest Term the pack holds, so the pooled window is 2017–2024):
disturbed 50+34+49+46+57+42+50+31 = 359 over parsed 73+55+72+65+69+54+75+52 =
515, a **69.7% baseline** on a pool well above the 30-parsed floor.

**What pushed me below the baseline (to 0.65).**

1. **The United States is on the respondents' side.** The SG's CVSG brief in the
   companion petition, *Parker-Hannifin Corp. v. Johnson* (No. 24-1030, filed
   December 2025), supported the plan-sponsor position; here the US filed a
   merits amicus for respondents (July 9, 2026, in the respondent-side wave)
   and won divided argument. The Department of Labor backs Intel. SG-supported
   merits positions prevail well above 50%, so this is the strongest single
   signal against disturbance.
2. **A real affirmance theory.** Intel's merits brief (provisioned) frames the
   Ninth Circuit's rule not as a categorical element but as ordinary
   *Twombly*/*Iqbal* plausibility for claims resting *solely* on relative
   underperformance, and Judge Berzon's concurrence below narrows the holding
   the same way. If the Court reads the decision below that narrowly, affirmance
   does not even require blessing a "categorical" rule.
3. **DIG risk.** The parties' briefing partly converges on "context-specific
   inquiry, comparators usually matter," leaving a fact-bound dispute about
   these comparators — the shape that produced post-argument DIGs in *NVIDIA*
   and *Facebook*. A DIG counts as undisturbed. I put ~0.07 here.

**What kept me near the baseline rather than well below it.**

1. **The Court's unbroken pattern in this exact genre.** *Hughes v.
   Northwestern* (8–0) vacated a circuit-made categorical ERISA pleading screen;
   *Cunningham v. Cornell* (9–0) reversed another. The QP as granted is written
   in *Hughes*' own anti-categorical vocabulary, and the Court granted that
   framing.
2. **Vehicle choice.** The Court had a defense-side petition presenting the same
   split (*Parker-Hannifin*, which the SG recommended granting) and instead took
   the plaintiffs' petition from a final judgment, holding the other. That is at
   least weakly more consistent with correcting the benchmark-requirement
   circuits than with affirming one of them.
3. The split is real and acknowledged on all sides (CA6 against CA7/CA8/CA9/CA10),
   so an unresolved-split affirmance-by-silence is unavailable; the Court will
   decide the question one way or the other.

Net: 0.60 vacate/reverse + ~0.02 mixed judgment ≈ **0.65 disturbed**, modestly
below the 69.7% pooled baseline, with the SG's opposition and the DIG route as
the discount.

**Salience band.** `record/context.json` carries `band: "elevated"` (sal-v3);
that is the cert petition's grant-likelihood band, spent at the grant, and per
the stage rules I did not anchor on it.

**Votes.** All nine in the majority reflects the modal vacatur scenario
(*Hughes*/*Cunningham* were unanimous or nearly so). It is knowingly
inconsistent with the affirmance branch (where I would expect 6–3 with
Sotomayor, Kagan, and Jackson dissenting); per-Justice, "majority" is the
highest-probability vote for every Justice once the two branches are mixed.
Kagan as author is a low-confidence guess (she wrote *Hughes*) and authorship
is unscored.

**Evidence base.** Forward cell; I worked from the provisioned snapshot (full
docket through 2026-08-16: fully briefed, SG divided argument granted, set for
argument October 6, 2026), the provisioned petition and QP text, and the
provisioned brief-in-opposition file — which usefully concatenates the
cert-stage BIO and Intel's merits response brief, so I did read the merits-stage
defense theory. I did not retrieve petitioners' merits brief or the amicus
texts; my read of the petitioner-side merits case is inferred from the petition
and the docket. Web retrieval established the SG/DOL alignment and the
*Parker-Hannifin* posture (pre-decision material; the judgment here does not
exist yet, so no leakage is possible).

**Where to discount me.** The 0.30 affirmance weight leans heavily on the SG
signal; if this Court discounts the current SG's systematically pro-business
ERISA positioning, 0.70–0.72 would be the better number. Conversely, if
argument reveals appetite for a *Dudenhoeffer*-style engineered screen (that
case *created* categorical pleading rules while preaching context-specificity),
affirmance is likelier than I priced. My comparator-fact detail on the Intel
funds comes from the parties' adversarial characterizations, not the record
itself.
