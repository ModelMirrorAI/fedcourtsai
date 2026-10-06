# Why P(grant) = 0.09

## Inputs I read

- `record/snapshots/2026-10-05.json` — the provisioned baseline (13 docket
  entries, March 24 through October 5, 2026).
- `record/context.json` — mode `forward`, stage `cert`, moment
  `distribution`, band `elevated` under `sal-v4`, `distribution_count` 2,
  no CVSG, Term 2025, `signals_observable` true, no cutoff.
- `record/documents/`: the questions presented, the full petition (46 pp.,
  text extracted cleanly) and the full brief in opposition (24 pp., clean
  text). `documents.json` shows none with `empty_text` or truncation.
- `metrics/statpack.md`: the modern-cert disposition table, the circuit,
  relist, CVSG and capital cuts, and the sal-v4 per-Term salience-band
  table.

## Anchor

`context.json` freezes the band at `elevated` under `sal-v4`, which matches
the statpack table's version, so the anchor is the **bracketed `reached`
rate for `elevated`, pooled over the Term rows strictly before OT2025**
(OT2017–OT2024, all eight rendered). Pooling the eight rows by their `n`
gives roughly **17%** (about 484 weighted grants over 2,810 weighted
petitions that reached the band; the per-Term figures run 13.8%–20.5%).
That number includes GVRs as grants, as the binary does.

Cross-checks from the other cuts, read as shape rather than adopted: the
D.C. Circuit is the best-performing originating circuit (granted 5.5% + GVR
2.3% of resolved modern cert petitions, against about 3–4% for the large
circuits); the petition is paid and not a capital case under the Court's
own marking (the death penalty is at stake in the commission, but
`bCapitalCase` is false); and the no-CVSG population grants at about 4% +
2.3% GVR.

One cut I deliberately did **not** lean on: the relist-count table's
`2` bucket (granted 27.8%, GVR 13.1%). `distribution_count` is 2 here, but
the docket shows both distributions were **rescheduled before the
conference met**, so the petition has never been considered and the count
reflects two reschedules, not two relists. The statpack itself warns the
stored count is an upper bound on relists for exactly this reason. Reading
the bucket's rate onto this petition would import the classic pre-grant
signal where none exists. The reschedules are most naturally explained by
the Court aligning this petition with the companion No. 26-13 (docketed
later, BIO filed the same day as this one), which is neutral as to outcome.

## Adjustments down from 17%

1. **No live or recurring split.** The petition's only conflict is with the
   Court of Appeals for the Armed Forces in *Dean* (2009) on a then-identical
   court-martial rule. The BIO's strongest point is structural and I think
   decisive for a split-driven Court: the court-martial rule was repealed in
   2018, the only rule still carrying the "begins performance" language is
   R.M.C. 705(d)(4)(B), and the D.C. Circuit has exclusive appellate
   jurisdiction over military commissions. The conflict therefore cannot
   recur anywhere else and will not percolate. The government also offers a
   respectable reconciliation (*Dean*'s result survives on its post-agreement
   witness-list act, with the stipulation point an unexplained half-sentence
   that the *Dean* dissent itself flagged).
2. **Interlocutory mandamus posture and a fact-bound framing.** The question
   presented is whether a specific sequence of acts (stipulation signed two
   days before countersignature; silence at a suppression hearing) was
   "clearly and indisputably" not performance. The Court seldom grants to
   review a court of appeals' application of the mandamus standard, and the
   petitioner can still litigate the plea-agreement issue after any final
   judgment of the commission. The D.C. Circuit's framing of the death-penalty
   decision as one requiring "political accountability" by the Secretary is
   the kind of deference argument this Court's majority tends to find
   congenial in national-security matters.
3. **Subject-matter base rate.** Since *Boumediene* (2008) the Court has
   denied every Guantanamo detention and commission petition I am aware of
   (*Al-Bihani*, *Latif*, *Al Bahlul* twice, *al-Nashiri*, *Al-Alwi*, *Khadr*,
   *Ali*), many of them with elevated salience and strong counsel. That is a
   sustained, outcome-relevant pattern, and I weight it.
4. **The Solicitor General opposes** at full length and with no concession
   on the merits or vehicle. The elevated-band base rate already contains
   many petitions where the government was petitioner or acquiesced; this is
   the harder configuration.

## Adjustments up (why not lower than 0.09)

- The stakes are genuinely national: the 9/11 prosecutions, the death
  penalty, and whether the government must honor a signed plea agreement.
  Importance alone occasionally carries a grant, and the petition's
  *Hamdan*/*Boumediene* framing is pitched at exactly that.
- The panel was sharply divided, Judge Wilkins' partial dissent is long and
  pointed, and three military tribunals (the military judge, the Court of
  Military Commission Review, and the CAAF in *Dean*) read the rule the
  petitioner's way. The "cannot be clear and indisputable when another
  federal appellate court disagrees" argument is a clean, non-fact-bound
  hook the Court could take if it wanted the case.
- The D.C. Circuit origin, experienced Supreme Court clinic counsel, and a
  paired companion petition (two petitions on the same question make a
  consolidated grant more attractive than a lone one).
- The SG asked for two extensions and filed a full BIO rather than waiving,
  though in a case of this profile that is not informative.

Net: the structural "no prospective significance" point and the Court's
Guantanamo record together outweigh the importance and division points. I
land about half the band anchor, at **0.09**.

## The other claims

- **relist-increment 0.96.** The petition was distributed for October 9 and
  then rescheduled on October 5; a rescheduled petition is redistributed for
  a later conference, which adds a distribution entry. The residual is the
  rare docket where a disposition issues without a new entry or the
  petition is withdrawn.
- **cvsg-increment 0.01.** The United States is the respondent and has
  filed its brief; a CVSG is not a coherent possibility.
- **summary-disposition-route 0.08** (conditional on a grant). No
  intervening decision bears on the question, so a GVR has no anchor, and
  summary reversal of a published, divided mandamus opinion is improbable.
  The residual covers an unusual grant-and-vacate paired with No. 26-13.
- **dissent-from-denial 0.15** (conditional on a denial). Material for a
  statement exists (the stakes, the Wilkins dissent, the three-tribunals
  point), but the Court's Guantanamo denials have been almost uniformly
  silent and the political cost of a separate writing here is high.
- **big_case_score 0.78.** Stakes, not odds: if decided, this would be the
  Court's first merits engagement with the military commissions in nearly
  two decades and would determine whether the 9/11 accused face capital
  trials or plead under the 2024 agreements.

## Retrieval and its limits

- Forward cell: retrieval unrestricted, no leakage clock. I did not look up
  this docket's current state or disposition; the snapshot shows it pending
  with a conference set for October 9, 2026, and no disposition exists.
- `fedcourts query --court scotus --era 2020s --disposition granted` returned
  eight recent grants (several are applications and government petitions,
  none on point). It served as a sanity check on how the corpus records
  distributions and grants, not as a prior for this question; no corpus
  filter can surface military-commission or mandamus priors.
- Two CourtListener MCP searches for the companion docket No. 26-13 (by
  docket number and by case name) returned nothing, so I could not confirm
  the companion's distribution schedule and my reading of the reschedules
  as alignment with it rests on the BIO's footnote and the pattern alone.
- The corpus-wide vintage of the base rates is the committed statpack; the
  Term tables were read for OT2017–OT2024 only.

## Where to discount me

- The reschedule reading. If the two reschedules instead reflect a Justice
  wanting more time with this petition specifically, the pre-grant signal is
  stronger than I credit, and a number nearer the 17% anchor would be right.
- The Guantanamo base rate is from memory of the Court's denial pattern, not
  a corpus cut; it is directionally solid but I cannot quote a denominator.
- Importance-driven grants are the hardest class to price, and this case is
  about as important as a narrow procedural question gets.
