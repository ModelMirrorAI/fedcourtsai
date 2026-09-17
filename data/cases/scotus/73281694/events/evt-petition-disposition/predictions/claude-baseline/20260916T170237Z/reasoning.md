# Why P(grant) = 0.25 and not another number

## What I read

Provisioned inputs: `record/snapshots/2026-09-15.json` (the baseline named by
`context.json`, read in full), `record/context.json` (mode `forward`, band `elevated` under
`sal-v4`, `distribution_count` 2, no CVSG, term 2025, `signals_observable` true),
`event.yaml` (kind `petition`, no `stage` field, so the cert path governs; moment is the
ordinary distribution moment), and all three provisioned documents: `petition.txt` (29 pp.),
`brief-in-opposition.txt` (32 pp.) and `questions-presented.txt`. None was `empty_text`. I also
retrieved, in forward mode, the petitioner's July 14 reply brief from supremecourt.gov, the
docket of the sibling petition Lynn v. BNSF (No. 25-1046), and the 2023 Mallory opinion via
the CourtListener MCP server (footnote 3 and the Alito concurrence). Retrieval is itemized in
`retrieval.md`.

## Anchor

The context carries a frozen band, so the yardstick is the sal-v4 segment table's bracketed
`reached` rate for `elevated`, pooled over the Terms strictly before this case's Term (2025),
which is every rendered row 2017 through 2024. Pooling grants over n across those eight rows
(17.9% of 336, 17.5% of 354, 19.0% of 300, 20.5% of 342, 16.1% of 397, 13.8% of 334, 15.9% of
347, 17.5% of 400) gives about **17%** (roughly 484 of 2,810 weighted). The table's version
matches `salience_version`, so no mismatch flag is owed. For context only: the modern
discretionary-cert grant family (granted plus gvr) is about 2.8% of resolved petitions; the
paid-segment relist-1 bucket is 8.2% granted plus 5.1% gvr; the CVSG-none bucket is 4.0%
plus 2.3%.

## Adjustments up from 17%

- **The Court called for a response after respondents waived.** That is an affirmative act by
  at least one chambers within a day of the first distribution. The statpack has no cut for it;
  from general experience a paid petition that draws a call for a response grants at a rate
  several times the docket's, and I treat it as at least as strong as one genuine relist. This
  is the main reason I sit above the band anchor even though the band already reflects two
  distribution entries.
- **The question is one the Court itself reserved in this case.** Footnote 3 of the 2023
  opinion says the dormant Commerce Clause argument "remains for consideration on remand," and
  Justice Alito's concurrence said there is "a good prospect" the assertion of jurisdiction
  violates the Commerce Clause. Four Justices dissented on due process. Five plausible votes
  for petitioner's theory exist on the record of the Court's own opinions, which is rare.
- **Quality signals.** Sidley (Carter Phillips, counsel of record Tobias Loss-Eaton), two
  cert-stage amici (Atlantic Legal Foundation, Washington Legal Foundation), a paid petition,
  a clean factual record the Court has already analyzed once, and a QP phrased in a Justice's
  own words.
- **Stakes.** The petition and amici make an uncontested importance case: post-Mallory
  registration-jurisdiction schemes in Illinois, Minnesota, North Carolina and elsewhere, and
  the reply notes respondents never answer the importance point.

## Adjustments down

- **The vehicle is dirty, and this is the crux.** The BIO shows what the petition's statement
  glosses: the trial court denied leave to amend preliminary objections in April 2024 on
  waiver grounds, restated in a January 2025 order footnote that the Commerce Clause argument
  "has waived," and then denied the objections to the amended complaint in April 2025 with no
  reasons. The Superior Court denied permission for an interlocutory appeal citing Hunt
  Refining (a Commerce Clause merits authority, which is petitioner's best fact), and the
  Pennsylvania Supreme Court denied allowance of appeal. The reply's answers (amendment wipes
  the slate under Pa. R. Civ. P. 1028(f); Michigan v. Long presumes no state ground absent a
  plain statement; the Superior Court cited merits authority) are respectable, but the Court
  would be granting to review an unexplained trial-court order in a case where the adequate
  and independent state ground question is live and the § 1257 finality question (Langdeau
  versus the ordinary interlocutory rule) must also be won. The pool memo will lead with this.
  The Court routinely denies strong questions in weak vehicles and waits.
- **No split, and a fresh denial on the same question.** Lynn v. BNSF (No. 25-1046), a
  registration-jurisdiction Commerce Clause petition by a railroad with three amici including
  the Association of American Railroads, was distributed once and denied on May 4, 2026 with
  no call for a response and no writing. The Court was not straining to reach the question
  four months ago. This case differs in that a response was called for, which is why I do not
  discount further.
- **Percolation is available.** The Tenth Circuit appeal in American Food & Vending v.
  Goodyear (BIO at 11) and the stayed North Carolina proceeding (PDII) will produce reasoned
  appellate merits decisions; a Court that wants the question can take it later on a record
  with an opinion below. Norfolk Southern also retains the argument for appeal after final
  judgment.
- **The band's trajectory signal is partly an artifact.** The two distribution entries include
  no true relist (see `flags.json`): the first was superseded by the call for a response. So
  the relist-1 bucket overstates this docket's demonstrated momentum, even as the call for a
  response, which the buckets do not see, restores much of it.

Net: the substantive pull is unusually strong, the procedural drag is unusually strong, and I
land at **0.25**, about eight points above the band anchor. I would put a symmetric band of
roughly 0.15 to 0.35 around it; the direction I would most expect to be wrong is upward, if
the five Justices decide the Michigan v. Long presumption and Langdeau are enough and simply
want to finish what footnote 3 started.

## Other claims

- **relist-increment 0.40.** Stated from the harness count of two distributions; the claim
  resolves if a third appears. From a first real conference on the long-conference list, a
  petition that drew a call for a response and that a Justice may write on is relisted more
  often than the paid median, but most such petitions still resolve at the first conference.
- **cvsg-increment 0.07.** Above the roughly 1% share of paid scored petitions that draw a
  CVSG, because an interstate carrier and a FELA suit implicate federal interests, but well
  below even odds: private parties, a constitutional question the SG has no program stake in,
  and no CVSG on the first Mallory petition.
- **summary-disposition-route 0.03 (conditional on grant).** No intervening decision; the
  merits are unresolved; a GVR or per curiam has nothing to ride on.
- **dissent-from-denial 0.30 (conditional on denial).** A statement respecting denial from the
  author of the 2023 concurrence is the live possibility. The silent denial in Lynn pulls the
  number down; the call for a response here pulls it up.
- **big_case_score 0.7.** Stakes, not odds: a decision would set a constitutional limit on
  where national businesses can be sued and is the sequel to a 5-4 case the business and
  plaintiffs' bars both tracked closely. Not a blockbuster in the public sense.

## Uncertainties and where to discount me

- I cannot see the Court's internal handling of the call for a response (which chambers asked).
- The call-for-response signal has no statpack cut; that adjustment rests on memory of the
  general pattern, not on a committed figure.
- I read the reply and BIO closely but did not read the two amicus briefs beyond the reply's
  summary of them, nor the Pennsylvania Superior Court's Hunt Refining opinion.
- The two `fedcourts query` calls added nothing case-specific: the citation lookup returned
  the coverage note (no match), and the granted-2020s list was unrelated cases.
- I know the 2023 Mallory decision from training, which is the prior proceeding in this case
  and legitimate context, not this event's outcome. The September 28, 2026 conference has not
  yet occurred as of today (September 16, 2026), so no outcome exists to leak.
