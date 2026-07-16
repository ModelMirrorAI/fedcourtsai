# Saadeh v. New Jersey State Bar Association, No. 25-1002 — cert disposition

**Prediction: P(grant, GVR included) = 0.42; most likely single disposition: denied.**

## The case

Rajeh Saadeh, a Palestinian and Muslim New Jersey attorney and former NJSBA
board member, sued the (private, voluntary) New Jersey State Bar Association
under the New Jersey Law Against Discrimination over board set-aside seats
reserved for specific demographic groups (Black, Hispanic, Asian Pacific
American, women, LGBTQ+, plus "diverse" categories). The trial court granted
him summary judgment on liability, rejecting the Association's First Amendment
defense. The Appellate Division reversed on the First Amendment alone —
without deciding the state-law question — holding under *Boy Scouts of America
v. Dale* that forcing the Association to abandon its diversity set-asides
would significantly burden its expressive association. The opinion is
unpublished and nonprecedential; the New Jersey Supreme Court denied
certification on September 19, 2025.

The question presented (petition): whether the First Amendment overrides
antidiscrimination laws when the discrimination furthers the defendant's views
about "diversity," "equity," or "inclusion."

## Procedural signals on the docket (snapshot of 2026-07-16)

The signal chain here is unusually strong for a state-court petition:

1. **Paid petition, elite counsel** — Consovoy McCarthy (counsel in *SFFA v.
   Harvard*) took over for the Supreme Court stage.
2. **Four cert-stage amicus briefs**: Students for Fair Admissions et al.,
   America First Legal, Manhattan Institute, and West Virginia + 17 states.
3. **Call for response** (Mar 23, 2026) after the respondent waived — the
   Court affirmatively wanted the case briefed.
4. Distributed for the June 18, 2026 conference, and then, on **June 22, 2026,
   a CVSG**: "The Solicitor General is invited to file a brief in this case
   expressing the views of the United States."

The CVSG is the dominant datum. In the corpus statpack, modern discretionary
cert petitions with a CVSG resolve **27.1% granted / 71.2% denied** (n=59
resolved), against 3.0% granted without one; the paid-petition base rate is
~5–8% per recent Terms. A CVSG means at least several Justices consider the
question serious; it is also not a grant, and most CVSG'd petitions are still
denied.

## Merits posture (why several Justices are interested)

The decision below is a genuine outlier. It extends *Dale* to hold that the
act of demographic set-asides is itself protected expression because it
"expresses" a commitment to diversity — in tension with *Runyon*, *Hishon*,
*Roberts*, and the status/message line drawn in *303 Creative* (600 U.S. at
595 n.3), and in practical conflict with the Eleventh Circuit's *Fearless
Fund* (First Amendment "does not protect the very act of discriminating on
the basis of race") and the Fourth Circuit's *NADOHE v. Trump*. The petition
documents that the decision is being cited nationally (including by the ABA)
as a First Amendment roadmap for insulating DEI programs from
antidiscrimination law after *SFFA*. This Court's recent appetite in exactly
this space (*SFFA*, *303 Creative*, *Ames*) and the near-certain alignment of
the current Solicitor General with the petitioner's position (the
administration's anti-DEI enforcement posture is on the public record, e.g.
E.O. 14151/14173 and DOJ's litigating positions) both push toward a grant
recommendation and a grant.

## Vehicle defects (why the BIO may still win)

The brief in opposition (Gibbons/Lustberg, 36 pp.) is a strong
vehicle-focused opposition:

1. **Article III standing.** Saadeh never applied — or said he would apply —
   for any challenged seat, including during 2022–2025 when the program was
   suspended and every seat was open to him; below he affirmatively argued he
   "d[id] not need to … desire or express interest in any of the … seats."
   Under *Carney v. Adams* ("able and ready") and *ASARCO* (petitioner must
   establish federal standing on review of a state judgment litigated without
   it), this is a serious threshold problem on an undeveloped record — the
   same shape that produced the *Lab Corp v. Davis* DIG.
2. **The program changed.** In November 2025 the Association restructured the
   at-large seats so that all eight are reachable via membership in
   open-to-all affinity bar associations (Saadeh himself belongs to one). A
   merits ruling about the litigated set-asides would speak to a policy no
   longer in effect; only the damages claim for the past period keeps the
   dispute alive.
3. **Open state-law ground.** The Appellate Division never decided whether the
   program violates the NJ LAD. On reversal, the state court could hold there
   was no state-law violation — an adequate and independent ground making this
   Court's ruling effectively advisory.
4. **Posture.** Unpublished, nonprecedential intermediate state decision; no
   published appellate authority anywhere actually adopts the position (the
   BIO plausibly reframes *Fearless Fund* as a threshold expressiveness
   holding on different facts), and the same issue is percolating in multiple
   federal suits (e.g. *AAER v. ABA*, N.D. Ill.) that could present cleaner
   federal vehicles within a Term or two.

## Weighing

I model the disposition through the SG's likely recommendation, which now
controls the timeline (a June CVSG typically returns a brief around
Nov–Dec 2026, disposition in winter–spring 2027):

- P(SG recommends grant) ≈ 0.55–0.6. The ideological alignment is strong, but
  the standing and adequate-state-ground problems give a careful SG office a
  principled basis to recommend denial in favor of a cleaner federal vehicle —
  a common outcome even for administrations sympathetic on the merits.
- P(grant | SG recommends grant) ≈ 0.7 (historical rate ~0.7–0.8, shaded down
  for the vehicle defects, which respondent will re-press).
- P(grant | SG recommends denial) ≈ 0.15 (the Court sometimes grants anyway
  when the recommendation is vehicle-driven and the merits interest is high).

That yields ≈ 0.55×0.7 + 0.45×0.15 ≈ **0.45**, which I shade slightly down to
**0.42** because the corpus's own CVSG base rate (27%) is materially lower
than my conditional structure and because the standing record here is
unusually bad (the petitioner disclaimed the very showing *Carney* requires).
GVR is not a live path — there is no pending merits case whose decision would
be intervening authority — so essentially all grant probability is plenary
grant (or grant limited/reformulated); I therefore predict `denied` as the
single most likely disposition while carrying a high 0.42 grant probability.

No per-Justice votes are predicted: a cert disposition is unsigned, and
individual conference votes are not observable enough to forecast responsibly.

## Big-case score

0.78. If granted and decided, this becomes the leading case on whether the
First Amendment shields private DEI programs from antidiscrimination law —
the direct successor to *SFFA* and *303 Creative*, with immediate consequences
for universities, bar associations, scholarship programs, and corporate DEI.
The pre-decision engagement (18 states, SFFA, AFL, Manhattan Institute, a
CVSG) confirms the stakes independent of the grant odds.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-16.json` (full docket through
  the June 22, 2026 CVSG).
- Provisioned documents: `questions-presented.txt`, `petition.txt` (95 pp.),
  `brief-in-opposition.txt` (36 pp.) — all with extracted text; the QP,
  reasons-for-granting, and the BIO's standing/vehicle/merits sections are the
  basis of the analysis above.
- Committed `metrics/statpack.md` / `statpack.json` — CVSG cut, relist cut,
  paid-vs-IFP per-Term grant rates. (This statpack carries no salience-band
  table; the CVSG cut is the anchor used.)
- `fedcourts query` topic retrievals returned no rows (see `retrieval.md`), so
  no corpus priors beyond the statpack informed the estimate.
