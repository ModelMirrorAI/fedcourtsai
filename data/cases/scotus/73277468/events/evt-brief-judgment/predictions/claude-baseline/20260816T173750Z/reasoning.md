# Rationale — why P(disturbed) = 0.78

**Anchor.** The committed `metrics/statpack.md` merits section publishes an
`excluded` count (67), so its rates are quotable. My case's grant date is
March 30, 2026 (docket) → grant Term 2025, so the scored pool is grant Terms
2015–2024; the pack's parsed rows in that window are Terms 2017–2024, pooling
to 359 disturbed over 515 parsed = **69.7%**, comfortably past the 30-parsed
floor. That is the baseline my Brier skill is scored against.

**Adjustments up (+~8 points).**
1. *Textual asymmetry.* Rule 8(c)(1) ("must ... any"), Rule 15(a)(2) ("only"),
   and Rule 16(b)(4) ("only for good cause") all cut for petitioner, and this
   Court's FRCP cases consistently enforce rule text over circuit-crafted
   purpose glosses. The Eleventh Circuit's own framing (*Hassan*: a
   "technicality") is the kind of language the current Court reverses.
2. *Internal anomaly.* The Eleventh Circuit bars the same defense when raised
   by post-deadline motion to amend, but allows it when smuggled in via
   summary-judgment motion — an incentive structure that rewards bypassing
   Rules 15/16, hard to defend as a reading of the Rules.
3. *Vehicle facts.* Defense counsel admitted the personal-staff exemption
   first occurred to him while drafting the summary-judgment motion — a year
   past the scheduling-order deadline — and never sought amendment or argued
   good cause. Even the intermediate diligence rule (three circuits) disturbs
   on these facts, so petitioner wins under two of the three circuit
   positions; only the pure prejudice test affirms.
4. *Multiple disturbance routes.* Strict rule → reverse; diligence rule →
   vacate-and-remand; even a retained prejudice test tightened to credit the
   GERA forum-channeling harm could vacate. Affirmance requires both adopting
   the lenient test *and* blessing its application here.
5. *Counsel and selection.* Petitioner's counsel (Eric Schnapper) has a strong
   record in exactly this genre of procedural-rules employment cases, and the
   Court granted over a BIO in a case where the decision below followed the
   eight-circuit majority rule — a grant pattern that more often presages
   disturbing the rule below than ratifying it.

**Adjustments down (why not higher).** Respondent's structural argument is
substantial, not makeweight: Rule 8(c) prescribes no consequence for
violation, Rule 12(h) expressly waives only four enumerated defenses, *Wood v.
Milyard* calls the failure a correctable forfeiture, Rule 61's harmless-error
default and *Foman*'s anti-formalism give the Court a principled affirmance
path, and eight circuits already live under the prejudice test. Jones Day
represents respondent, and the respondent-side amicus lineup (West Virginia +
16 states, two others) signals a real defense of the majority rule. I hold
~0.22 for affirmance.

**Net: 0.78**, judgment label `reversed` (modal), with `vacated` a close
second — see `predicted_reasoning.md` for the split.

**What I worked from.** The provisioned snapshot (2026-08-16, forward mode,
as-stored), the questions-presented and petition texts, and the provisioned
respondent document — which concatenates the February 13, 2026 brief in
opposition and the August 3, 2026 respondent's merits brief (both sides'
merits arguments were therefore on my desk). I additionally retrieved the
petitioner's June 8, 2026 merits brief from supremecourt.gov (forward-mode
retrieval; see `retrieval.md`). No argument transcript exists yet — argument
is set for November 2, 2026, after this run. This is a briefed-moment
forecast made from the full merits briefing but before argument.

**Discounts a reader should apply.**
- The vote block assumes the current nine Justices sit unchanged through
  OT2026 and leans on the unanimity pattern of recent FRCP cases; a 6–3 or
  7–2 split with a discretion-preserving dissent is entirely plausible and I
  have not tried to name dissenters.
- Two `fedcourts query` calls returned no prior rows (see `retrieval.md`), so
  no corpus-retrieved precedent informed this cell; doctrinal priors come
  from the briefs and general legal knowledge.
- `record/context.json` carries `band: "high"` — a cert construct on this
  cert docket, not anchored on per the stage rule (no flag owed).
- The statpack pool's nearest Term (2024, and thinly 2025) is
  pendency-censored toward quicker dispositions; I read the pooled 69.7% as
  the committed bar without trying to correct for that.
