# D.A. v. Tri County Area Schools, No. 25-1143 — cert disposition

**Prediction: denied, P(grant) = 0.15.**

## The legal question

Whether *Bethel School District No. 403 v. Fraser*, 478 U.S. 675 (1986), permits
public schools to censor nondisruptive political speech that is not plainly
profane or lewd. Petitioners — two middle-school brothers represented by FIRE —
were made to remove "Let's Go Brandon" sweatshirts under the district's
dress-code profanity ban. A divided Sixth Circuit panel (Nalbandian, J., over a
Bush, J., dissent) affirmed summary judgment for the school, holding that
administrators could reasonably classify the euphemism as vulgar because of its
conceded origin in the "F*** Joe Biden" chant. 156 F.4th 782. En banc rehearing
was denied December 26, 2025, with only Judge Bush noting dissent.

## Governing standard for the prediction

Cert is discretionary and rare. From the committed statpack: the modern
discretionary-cert base rate is ~3.1% overall; Term-2025 **paid** petitions
grant at an estimated **5.4%** (IFP 1.1%); CA6-originating petitions ~3.5%.
This is a paid petition from CA6, so the fee-class anchor of ~5% is the
starting point before case-specific signals.

## Grant-positive signals (from the snapshot and filed documents)

1. **Call for response.** Respondents waived (May 1, 2026); the Court requested
   a response on May 18 after the petition had already been distributed for the
   May 28 conference. A CFR means at least one chamber is engaged; empirically
   it is one of the strongest pre-conference grant correlates, lifting a paid
   petition's odds several-fold above the ~5% anchor.
2. **Four cert-stage amicus briefs** (First Amendment Scholars, Buckeye
   Institute, Defending Education, NCAC) — cert-stage amicus support is a
   well-documented grant correlate.
3. **A colorable, expressly acknowledged split.** The petition rests on the en
   banc Third Circuit's *B.H. v. Easton Area* ("plainly lewd" limit on
   *Fraser*) and the Ninth Circuit's *Chandler* ("per se vulgar"), and the
   panel majority itself acknowledged it was declining to follow the Third
   Circuit's approach. Judge Bush's dissent says outright that the decision
   "creates at least two circuit splits" and that "the Supreme Court itself
   must ultimately clarify, and ideally limit, Fraser's reach." The Court has
   itself said *Fraser*'s "mode of analysis ... is not entirely clear"
   (*Morse*).
4. **Clean merits posture on the doctrinal question.** It is uncontested that
   the speech was political and caused no disruption, so the case isolates
   *Fraser*'s scope from *Tinker*'s disruption test.
5. **Signal from the opposition.** Respondents retained Lisa Blatt / Williams &
   Connolly for the BIO after initially waiving — defense-side behavior
   consistent with a perceived real grant risk.
6. **Ideological salience.** Censorship of a conservative political slogan is
   the fact pattern most likely to engage the Justices who dissented from
   denial in *L.M. v. Town of Middleborough* (2024 Term; Alito, J., joined by
   Thomas, J.) — I carry that denial from training knowledge; it predates this
   petition and is forward context, not leakage.

## Grant-negative signals

1. **The base rate.** Even strong CFR-plus-amici petitions die at conference
   far more often than not; the relist table shows petitions that never get
   relisted grant at under 1%, and this case has not yet produced a
   post-BIO conference vote (first substantive look comes at the September 28,
   2026 long conference).
2. **The split is contested, and plausibly so.** The BIO argues the Third
   Circuit has never held that coded speech with a conceded vulgar meaning is
   not "plainly" lewd (*B.H.* itself called Fraser's innuendo-laden speech
   "plainly lewd"), and that *Chandler*'s "per se" language was
   motion-to-dismiss posture. That reading makes the split shallower than the
   petition suggests and gives a denial vote an easy rationale.
3. **A bad fact.** Both students admitted in depositions that they understood
   and intended the sweatshirts to convey "F*** Joe Biden." That lets the
   Court view the Sixth Circuit's ruling as a fact-bound application
   ("plainly vulgar meaning") rather than a rule in conflict with other
   circuits.
4. **Vehicle objection.** The BIO presses a pending qualified-immunity
   alternative ground. It is only a partial objection — the claims for
   prospective relief against the district (the ban still applies at the high
   school the brothers now attend) would survive QI — but it adds friction.
5. **Recent behavior in adjacent cases.** The Court denied *L.M. v.
   Middleborough* (nondisruptive political T-shirt, First Circuit) over a
   two-Justice dissent, suggesting the Court is not eager to re-enter
   school-speech doctrine absent a crisper split.

## Weighing

The paid-petition anchor is ~5%. The CFR alone plausibly moves this to the
8–12% range; the amicus support, the published 2-1 decision with a
cert-urging dissent, the acknowledged intra-doctrine confusion, and the
salience of the topic push it further up. Against that, the contested split,
the petitioners' own concessions about the slogan's meaning, the QI vehicle
argument, and the Court's recent denial in *L.M.* keep this well short of a
coin flip. I land at **P(grant) ≈ 0.15** — several times the salient-petition
base rate, but denial remains the clear modal outcome, so
`predicted_disposition = denied`, `granted = 0`.

If granted, the likeliest path is a plenary grant out of the September 28,
2026 long conference or after one or two relists; a GVR is implausible (no
intervening decision to GVR in light of), so `gvr` probability is folded into
the residual and does not change the modal call.

## Inputs used

- Snapshot `data/cases/scotus/73281630/record/snapshots/2026-07-16.json`
  (docket 25-1143: filing dates, waiver, CFR, distributions, paid fee class).
- Provisioned `questions-presented.txt`, `petition.txt` (39 pp., full text),
  and `brief-in-opposition.txt` (31 pp., full text) — the QP, split framing,
  and the BIO's no-split / bad-vehicle / correct-on-merits response.
- Committed `metrics/statpack.md` + `statpack.json` (paid vs. IFP Term-2025
  grant rates, circuit and relist/CVSG cuts).
- `fedcourts query` corpus priors (no on-point student-speech prior surfaced;
  recent-era rows used only as context) — see `retrieval.md`.
