# Reasoning: why P(grant) = 0.08

## What I read

Provisioned inputs, in the contract's order: `AGENTS.md`, the predict prompt
and `schemas/prediction.schema.json`; then `event.yaml` (stage cert, moment
distribution, opened 2026-04-16), the snapshot
`record/snapshots/2026-09-15.json`, `record/context.json`, and all three
provisioned documents: `questions-presented.txt`, `petition.txt` (172 pages,
truncated; I read the Reasons for Granting, the good-faith section, and the
appended Wisconsin Supreme Court opinion including its treatment of the
circuit conflict), and `brief-in-opposition.txt` (34 pages, read in full).
`documents.json` shows none of the three as `empty_text`.

## Anchor

`context.json` freezes `band: elevated` under `sal-v4`, `distribution_count: 2`,
no CVSG, Term 2025, mode `forward`. The statpack's "Segment base rate by
salience band (sal-v4)" table matches the version, so I anchor on the
`elevated` band's bracketed `reached` rate pooled over Terms strictly before
2025, which is all eight rendered prior Terms (2017–2024):

| pool | grants (weighted) | n | rate |
| --- | --: | --: | --- |
| OT2017–OT2024 | 484.4 | 2810 | 17.2% |
| OT2020–OT2024 | 313.1 | 1729 | 18.1% |

So roughly one in six petitions that reach this band is granted (GVRs
included). The relist cut is not directly applicable: the two distributions
here are a first distribution superseded by a call for a response and a
re-distribution, not a relist after conference, and the cut buckets on
terminal count anyway. The CVSG cut does not apply (none on the docket).

## Adjustments from the anchor

**Down, hard, for jurisdiction.** The Wisconsin Supreme Court affirmed the
reversal of a pretrial suppression order and remanded for further proceedings;
Gasper has not been tried or convicted, and the BIO identifies unresolved
suppression theories still pending in the trial court. Under 28 U.S.C. §
1257(a) and Florida v. Thomas, 532 U.S. 774 (2001), which dismissed a
state-court interlocutory suppression ruling in almost this posture, the Court
lacks jurisdiction unless a Cox Broadcasting exception applies, and none fits
comfortably (the federal issue is not conclusive of the prosecution, later
review remains available after a conviction, and there is no distinct erosion
of federal policy). This is the single largest driver of my number. The Court
treats state-court finality strictly in criminal cases, and a defect visible on
the face of the record is exactly what a call for a response tends to surface.

**Down for lack of practical effect and an alternative ground.** Even the two
Wisconsin justices who rejected the private-search holding would not have
suppressed the ten files found on the phone: one applied good faith, the other
found the CyberTip alone supplied probable cause for the warrant. The petition
does not answer this. The Wisconsin Court of Appeals had also found no proven
subjective expectation of privacy (the affidavit was excluded and abandoned);
that decision was vacated, but the record problem remains an alternative
ground for affirmance. The Court avoids vehicles where a win changes nothing.

**Down for petition quality and question framing.** Two of the three
questions were not decided below. The Reasons for Granting open with rhetoric
about Communist-era and Prohibition-era contraband, and the petition did not
cite United States v. Lowers, 170 F.4th 134 (4th Cir. 2026), the most
favorable recent authority, which the BIO points out. Counsel is a solo
practitioner without Supreme Court experience visible on the docket. The
Court, faced with a genuine split, generally waits for a clean federal vehicle
with experienced counsel, and this question is arriving in federal courts
continuously.

**Up for a real, acknowledged, deepening split, and for the Court's own
signal.** The BIO concedes the conflict. The state waived, the Court called
for a response anyway (May 8), and a privacy organization represented by an
experienced Supreme Court advocate filed an amicus brief. Retrieval confirmed
the split has widened since the petition was filed: the Seventh Circuit's
August 20, 2026 decision in United States v. Braun (No. 25-2740) records the
Eleventh Circuit (United States v. Brillhart, 181 F.4th 1181 (11th Cir. 2026))
joining the Fifth and Sixth, and the Fourth (Lowers) joining the Second and
Ninth. Braun itself did not decide the question because the government did
not contest the district court's search ruling on appeal; the panel reversed
on independent probable cause, and Chief Judge Brennan wrote separately to say
he would side with Reddick and Miller. That is a forward signal predating my
snapshot, and it cuts both ways: the split is now six circuits deep, but Braun
also illustrates the "CyberTip alone gives probable cause" workaround that
makes this petitioner's private-search win unlikely to matter.

**Net.** Starting from ~17%, the finality defect alone would take me to the
low single digits for a private criminal petitioner; the strength and maturity
of the split and the CFR pull back up. I settle at 0.08. I would be more
worried about under-predicting if the jurisdictional argument were contested,
but the petition was filed before the BIO and there is no reply on the docket
answering it.

## Claim-by-claim

- `disposition` 0.08 (equals `probability`).
- `relist-increment` 0.30: a CFR petition with an amicus at the long
  conference is relisted more often than the docket average, and a hold for a
  possible SG petition in Lowers is a live minority path; the finality defect
  makes a first-conference denial the modal outcome.
- `cvsg-increment` 0.05: strong federal interest in the question but a state
  criminal petition with a facial jurisdictional problem is not where the Court
  asks the SG.
- `summary-disposition-route` 0.25 (conditional on grant): the band's GVR
  share of the grant family is roughly a third; the only intervening decision
  (Chatrie, 2026) is a poor fit for the private-search ground, and a GVR needs
  the same finality a plenary grant does, so I sit somewhat below the share.
- `dissent-from-denial` 0.12 (conditional on denial): salient issue, Justices
  with a record of writing on it, but jurisdictional denials rarely draw a
  statement.

## Big case score

0.55. If decided, the case would fix the constitutional rules for the
CyberTipline pipeline, which processes tens of millions of provider reports a
year and underlies a large share of child-exploitation prosecutions; that is
significant and would be widely covered, but it is a doctrinal application of
Jacobsen rather than a new framework, so it sits below a Carpenter-class case.

## Uncertainty and where to discount me

- The largest uncertainty is how the Court weighs the finality problem. If a
  Justice is eager to take the hash-match question this Term, the Cox
  exceptions can be read generously; I think that is unlikely for a private
  petitioner in a CSAM prosecution, but it is where an upside surprise would
  come from.
- I could not find, through CourtListener's docket search, whether any other
  petition on the same question is pending at the Court (SCOTUS docket text
  searches returned no results for topical queries). If a cleaner companion is
  pending, the relist and hold probabilities should be higher and the grant
  probability somewhat lower.
- The amicus brief was not provisioned and I did not retrieve it; my read of
  the amicus support is from the docket entry and counsel listing only.
- I did not read the prior prediction runs on this docket (mine or others')
  and this forecast is formed from the current record alone.
- Chatrie v. United States (2026) postdates my training knowledge in detail; I
  know of it only through the Seventh Circuit's citation, so my judgment that
  it is a poor GVR fit rests on the ground the Wisconsin court used, not on
  Chatrie's reasoning.
- Corpus freshness: the snapshot is dated 2026-09-15 and the docket's next
  event is the September 28, 2026 conference, so the cell is genuinely forward
  and nothing about the disposition exists to leak.
