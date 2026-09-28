# Why 0.22, and not another number

## Inputs I read

- The provisioned snapshot `record/snapshots/2026-09-27.json` (14 docket
  entries, through the 9/16 re-distribution for 10/9), `record/context.json`
  (forward mode, band `elevated` under sal-v4, distribution_count 2, no CVSG,
  Term 2026, paid docket), and the event definition (cert stage, moment
  `distribution`).
- Provisioned documents: `questions-presented.txt`, `petition.txt` (28 pp.,
  Pacific Legal Foundation), `brief-in-opposition.txt` (44 pp., Hogan
  Lovells). Neither had `empty_text`.
- The petitioner's reply (9/10/2026), fetched from the Court's docket PDF
  and text-extracted locally; not provisioned. Retrieval details in
  `retrieval.md`.
- The statpack sections named in the prompt, and the public docket pages of
  the two prior petitions on this question (Nos. 23-170 and 23-1137) for
  their distribution and disposition histories.

## Anchor

The context carries a frozen band, `elevated` (sal-v4), matching the
statpack's band-table version. Pooling the bracketed `reached` figure for
`elevated` over every rendered Term strictly before OT2026 (OT2017–OT2025,
nine rows) gives **16.9% (n = 3,085)**. That is the yardstick I am scored
against and my starting point.

Cross-checks from the paid scored-segment cuts: the relist-count cut reads
13.3% grant family for bucket 1 and 41% for bucket 2, but the stored count of 2
here includes a reschedule-before-first-consideration (the response request
vacated the 9/28 listing), which the cut's own caption warns inflates the
count, so I treat this petition as bucket 0/1 territory, not bucket 2. The
CVSG cut's `none` row is 6.3% grant family. Fourth Circuit origin runs
slightly below the circuit average (2.5% grant family). The whole-Term paid
grant rate is about 3%.

## Adjustments up (from ~0.17)

1. **The Court called for a response after a waiver.** That is an
   affirmative act by at least one chambers and is the single strongest
   docket signal here. It may already be inside the band, so I weight it
   moderately rather than stacking it.
2. **The split is now real and acknowledged.** Sargent (3d Cir. Feb. 2026)
   expressly rejects the First and Fourth Circuits' approach and adopts the
   Second Circuit's; the reply quotes it. When Boston Parent was denied, the
   Second Circuit's CACAGNY decision was weeks old and the Third Circuit had
   not spoken. Justice Gorsuch's Boston Parent statement read as a request
   for percolation; percolation has happened.
3. **Three Justices are on record** as troubled by the Fourth Circuit's rule
   (Alito and Thomas dissenting twice, Gorsuch's statement), and the issue
   — proxy discrimination after SFFA — is a priority for the current
   majority's equal-protection agenda. Counsel is a repeat Supreme Court
   litigant, and five amici (including Students for Fair Admissions) filed.

## Adjustments down

1. **Vehicle defects are serious, and the BIO is well built.** The decision
   below is an unpublished, unargued, three-page per curiam. The case comes
   up on a Rule 12(b)(6) dismissal. The district court dismissed on two
   independent grounds; the Fourth Circuit affirmed on disparate impact
   alone and never reached intent. The reply shows the intent holding *was*
   challenged on appeal (contrary to the BIO), so the alternative ground is
   not forfeited, but the Court still faces a real chance that a reversal on
   the question presented changes nothing on remand.
2. **The facts are weak for petitioner.** The challenged policy is a
   COVID-era lottery adopted by different officials than the "field test,"
   the Asian-American share of admits exceeds the applicant-pool share and
   rose at two of the four schools, and the complaint pleads no statements
   by the Pandemic Plan's decisionmakers. The Court twice declined on records
   with far stronger intent evidence (TJ: summary-judgment record; Boston:
   district-court animus findings). If it wanted this issue on those facts
   it could have had it.
3. **The QP is framed as a "sequencing" rule**, and the BIO argues
   credibly that no circuit has one; the real disagreement is what counts as
   disparate impact. That gives a cautious Justice an easy reason to wait
   for a case where the framing is cleaner.
4. **Better vehicles are foreseeable.** Sargent itself (the losing school
   district could petition), the pending Boston appeal (1st Cir. No.
   26-1285), and further New York litigation are all in the pipeline.
5. **Mullin v. Doe (2026)** is recent Arlington Heights guidance the BIO
   leans on; the Court may feel it has said enough on intent standards for
   now.

Net: the issue pull is strong, the vehicle pull is strongly negative. Four
votes require at least one of the Chief Justice, Kavanaugh, or Barrett to
accept a pleading-stage unpublished vehicle with an unaddressed alternative
ground. I land at **0.22** — above the band anchor because of the response
request and the crystallized split, well short of even odds because of the
vehicle.

## The other claims

- **relist-increment 0.72.** From the 2-distribution frozen state. Roughly:
  P(grant) × ~0.87 (modern relist-before-grant practice) plus P(deny) ×
  [P(writing) × ~0.95 + P(no writing) × ~0.3]. The prior petitions' seven- and
  eight-distribution histories drive the writing branch.
- **cvsg-increment 0.04.** No federal party or statute; no CVSG in either
  prior case.
- **summary-disposition-route 0.06** (conditional on grant). No
  intervening decision favoring petitioner; a pleading-stage record.
- **dissent-from-denial 0.6** (conditional on denial). Two prior dissents
  from the same Justices on the same rule, but a weaker vehicle they may
  choose not to spend a writing on.

## Where to discount me

- I do not know which docket features sal-v4 uses; if the response request
  and amicus count are already fully priced into `elevated`, my upward
  adjustment double-counts and 0.18 would be closer.
- I could not find any pending cert petition in Sargent through
  CourtListener (its SCOTUS docket coverage is sparse); if one exists and is
  being held alongside this case, the relist probability rises and the
  grant probability shifts in ways I have not modeled.
- The distribution_count of 2 is the harness's frozen state and is what the
  relist claim resolves against; my reading of the second entry as a
  reschedule rather than a relist affects the anchor I chose, not the
  resolution rule.
- No corpus prior I retrieved via `fedcourts query` was close enough to
  inform the number; the citation filter is unpopulated for these rows and
  the granted-2020s sweep returned mostly emergency applications. The
  quantitative anchor is the statpack alone.
