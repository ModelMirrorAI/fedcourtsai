# Redding v. Mullin, No. 25-1336 — cert disposition prediction

**Prediction: denied. P(grant, GVR included) ≈ 0.015.**

## The case

Stephanie Redding, a former Federal Air Marshal, sued DHS/TSA under the
Rehabilitation Act for failure to accommodate. TSA found she no longer met FAM
medical standards; she applied for OPM disability retirement, and TSA — without
telling her — filed an SF-3112D certifying to OPM that accommodation and
reassignment were not possible. TSA then ran a reassignment-as-accommodation
process that moved her to FLETC (a different DHS component, $20k pay cut) and
closed the accommodation file four days after her start date, before any
substantive work or required training. TSA later admitted in writing she "was
not counseled about the impact that the transfer would have on her application
for retirement," and the transfer extinguished the retirement track. The
E.D. Va. dismissed under Rule 12(b)(6) for failure to plead she was a
"qualified individual"; a unanimous Fourth Circuit panel (Wilkinson, joined by
King and Gregory) affirmed in a published opinion, 168 F.4th 203 (Mar. 3,
2026), on two grounds: (1) her complaint conceded she could not perform the
essential functions of the Regional Coordinator position she wanted to keep,
and (2) in any event the self-selected FLETC reassignment was a "manifestly
reasonable" accommodation, "and that is where our analysis ends."

The petition (filed May 28, 2026, paid, counseled) presents three questions:
(I) whether concealing the retirement consequences of a proposed reassignment
and closing the process before training/effectiveness review satisfies the
good-faith interactive process under 29 C.F.R. § 1630.2(o)(3); (II) whether
the Fourth Circuit's outcome-only approach conflicts with A.J.T. v. Osseo Area
Schools, 605 U.S. 335 (2025), and a claimed circuit split on whether
interactive-process bad faith is independently actionable (3d/5th/7th
actionable vs. 9th/10th/11th evidence-only); (III) whether "voluntary"
participation procured by concealment can foreclose review, by analogy to
Bumper v. North Carolina's Fourth Amendment consent doctrine.

## Base rate anchor

From the committed statpack (live/historical slice, denial-reweighted): modern
discretionary-cert petitions resolve ~95% denied / ~3% granted overall. This is
a **paid** Term-2025 petition; the per-fee-class detail in `statpack.json` puts
paid Term-2025 grants at ~5.4% (vs ~1.1% IFP). The prompt's "Segment base rate
by salience band" table is not present in the committed statpack, so I anchor
on the paid fee-class rate (~5%) and adjust from the signal cuts. Fourth
Circuit origination is near the average (granted 4.6% among modern cert
petitions from CA4) — no adjustment either way.

## Case-specific adjustment (down, substantially)

1. **The Solicitor General waived the right to respond** (June 17, 2026), and
   the case was distributed for the September 28, 2026 long conference on that
   waiver. The Court essentially never grants without a response on file; the
   realistic best case at conference is a call for a response (CFR), which
   itself is uncommon and would still leave a low conditional grant rate. No
   relist and no CVSG exist as of the snapshot; the statpack's relist cut puts
   zero-relist petitions at ~0.8% granted, and the granted priors I sampled
   from the corpus all carried multiple conference distributions.
2. **Vehicle defects.** The Fourth Circuit affirmed on an independent,
   antecedent ground — that Redding's own complaint conceded she was not a
   "qualified individual" for the position she sought (Cleveland/Stanley
   admission problem) — which the questions presented do not squarely
   challenge. Even a petitioner win on the interactive-process question would
   likely not change the judgment, and the 12(b)(6) posture plus a
   fact-intensive administrative record make this a poor vehicle for the
   claimed split.
3. **The split is old and repeatedly denied.** The
   actionable-vs-evidence-only division on interactive-process failures has
   existed since the late 1990s (Taylor, Beck, Willis) and the Court has
   passed on it many times; most circuits tie the claim to showing a
   reasonable accommodation was ultimately possible, which loops back to the
   qualified-individual defect here. The A.J.T. hook is thin — A.J.T. was an
   education-services case about heightened intent standards, and its holding
   predates the Fourth Circuit's decision, so it supplies no GVR basis either.
4. **Weak petition craft signals.** QP I contains a grammatical error
   ("§ 1630.2(o)(3) engage in"), and QP III imports Fourth Amendment consent
   doctrine (Bumper, Schneckloth) into an employment-discrimination case — an
   idiosyncratic theory no circuit conflict supports. Small-firm counsel, no
   amici on the docket.
5. **Unanimous, ideologically diverse panel.** Wilkinson writing, joined by
   King and Gregory, with no dissent — the absence of any dissent from the
   left-leaning members cuts against the claim that the outcome turned on a
   contested legal rule rather than the pleading concessions.

Modest up-weights — a published (not unpublished) opinion, paid and counseled
status, and a genuinely sympathetic documented-concealment record — do not
offset the waiver, the vehicle problems, and the long-tolerated split.

## Bottom line

Starting from the ~5% paid-petition anchor, the response waiver, zero-relist
posture, independent alternative holding, and fact-bound QPs push this well
below the class average. I estimate **P(grant incl. GVR) ≈ 1.5%** and predict
**denied**, most likely at or shortly after the September 28, 2026 long
conference (statpack median time-to-resolution for Term-2025 petitions is
~62 days from filing; long-conference petitions with waived responses are
typically denied in the first October order list). GVR is implausible because
no intervening Supreme Court decision postdates the Fourth Circuit's judgment.

**Big-case score: 0.10.** A single federal employee's accommodation dispute;
the dual-track OPM-retirement/accommodation conflict is a real structural
issue for federal workers, but any ruling would be narrow and low-salience.

## Inputs used

- Snapshot `record/snapshots/2026-07-18.json` (docket through the 6/24/2026
  distribution entry).
- `record/documents/questions-presented.txt` and `record/documents/petition.txt`
  (full petition text including the appended Fourth Circuit opinion and
  district-court order; no brief in opposition exists — respondent waived).
- Committed `metrics/statpack.md` + per-fee-class detail in
  `metrics/statpack.json`.
- Two `fedcourts query` corpus lookups (see `retrieval.md`).
