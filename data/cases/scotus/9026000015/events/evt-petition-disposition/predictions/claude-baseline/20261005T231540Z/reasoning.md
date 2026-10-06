# Rationale for my numbers

**P(any grant) = 0.30; predicted disposition `denied`; confidence 0.5.**

## What I read

- `record/snapshots/2026-10-05.json` (the provisioned baseline, read in full).
- `record/context.json`: `mode: forward`, `band: baseline`, `salience_version:
  sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2026`.
- `record/documents/questions-presented.txt` and `petition.txt` (the QP,
  introduction, statement, both split arguments, and the vehicle section;
  the file is truncated in the appendix, not in the petition body). No brief
  in opposition exists yet: the City waived, the Court called for a response,
  and the BIO is now due Oct. 30, 2026.
- `metrics/statpack.md`: the modern discretionary-cert table, the originating
  circuit, relist and CVSG cuts, and the sal-v4 segment table.
- Beyond the provisioned inputs: one corpus `query`, and six CourtListener MCP
  calls, mostly to read the Fifth Circuit's December 12, 2025 opinion
  (details in `retrieval.md`).

## Anchor

Band is `baseline`, so the scored yardstick is the baseline band's bracketed
`reached` rate pooled over Terms strictly before 2026. Weighting each Term's
`reached` rate by its `n` over 2017–2025 gives about 5.0% (roughly 637 grants
over 12,720 petitions). The relist-count cut's bucket 1 (8.2% granted, 5.1%
GVR) describes petitions that *ended* at one distribution, which this one
will not, so I did not anchor on it. CA5's grant-family rate (about 3.7%) is
in line with the docket as a whole and moved nothing.

## Adjustments upward

1. **Call for a response after a waiver.** The single strongest fact on the
   docket. The City waived on Jul 21; the Court distributed on Jul 29 and
   requested a response on Jul 30. A CFR is not in the frozen context and not
   a band feature under sal-v4, so the 5% anchor is blind to it. From what I
   know of paid-docket practice, a CFR raises the grant chance several-fold;
   it is the main reason my number is six times the anchor.
2. **Thirteen cert-stage amicus briefs** from a coalition spanning Native
   nations, Jewish, Sikh, Hindu, Catholic and evangelical organizations, a
   prisoners'-rights group, and religion scholars, filed by national
   appellate firms. That is top-decile amicus attention for a paid petition
   and signals the religious-liberty bar treats this as the vehicle for the
   question.
3. **A six-judge dissent from denial of rehearing en banc** (Oldham, joined by
   Elrod, Smith, Higginson, Willett, Ho), plus Judge Higginson dissenting on
   every panel iteration. The Fifth Circuit disagreement is unusually visible.
4. **The question is live for this Court.** Zubik left the complicity-burden
   version unresolved in 2016; Justice Gorsuch's dissent from the denial of
   certiorari in Apache Stronghold (May 2025, joined by Justice Thomas; this
   is training knowledge, since the CourtListener index returned no hit for
   the order) said the sacred-site substantial-burden question would recur.
   The current Court grants religious-liberty petitions at well above the
   docket rate. Counsel (the UT Law and Religion Clinic with First Liberty)
   are repeat Supreme Court litigators.

## Adjustments downward

1. **Apache Stronghold was denied.** The Court passed last Term on a cleaner
   federal RFRA sacred-site case with a published en banc split, and only two
   Justices noted dissent. That is direct evidence the bench does not yet
   have four votes for this question, even if Justice Alito's recusal there
   complicates the inference.
2. **Vehicle problems the BIO will press.** Reading the December 2025
   opinion: the substantial-burden holding is framed under *Texas* RFRA using
   Barr v. City of Sinton, with federal RFRA/RLUIPA cases as persuasive
   authority; it is a preliminary-injunction appeal reviewed for likelihood of
   success; the panel says petitioners did not brief the burden issue in their
   opening brief; it rests partly on record findings (cormorants do not nest
   there most of the year; deterrence does not target cormorants); and there
   is an alternative holding that strict scrutiny is satisfied, with the City
   disputing the "never studied alternatives" admission the second QP depends
   on. The petition's answer (Espinoza: a state-law judgment that
   misunderstands federal constitutional limits is reviewable) is plausible
   but not easy.
3. **Mootness and project timing.** The project could proceed between now and
   a decision; a BIO arguing that tree removal is complete or that the
   deterrence program is seasonal and has not harmed nesting would weaken the
   case for review.
4. **The City's initial waiver** suggests it thought the petition weak; the
   Court disagreed enough to call for a response, which is already counted
   above.

Netting these, I land at 0.30: the CFR, amici and en banc dissent put this
petition well into the top few percent of the paid docket, but the state-law
framing, the preliminary posture, and the Apache Stronghold denial make a
quiet denial the single most likely outcome.

## The other claims

- **relist-increment 0.95.** The petition was pulled from its only conference
  by the CFR, so a new `DISTRIBUTED for Conference` entry is near-certain
  after the BIO and reply land. The residual is withdrawal, dismissal, or a
  settlement mooting the case before redistribution.
- **cvsg-increment 0.07.** No federal party or federal statute; a municipal
  Free Exercise case. The federal interest in a parallel RFRA/RLUIPA standard
  is real but indirect.
- **summary-disposition-route 0.08.** No intervening decision; a PI
  affirmance on a developed record is not summary-reversal material.
- **dissent-from-denial 0.45.** Gorsuch and Thomas already dissented from the
  denial in the adjacent case; thirteen amici and the en banc dissent make a
  written dissent or statement plausible, but a vehicle-based silent denial is
  equally plausible.
- **big_case_score 0.6.** Significance if decided is high for religious
  liberty doctrine broadly and for Native sacred-site claims specifically;
  the facts are local and the posture preliminary, so not top-tier.

## Where to discount me

- My CFR adjustment is the largest single move and rests on general
  knowledge of paid-docket practice, not on a committed statpack cut; the
  pack carries no CFR cut.
- I have not read the BIO (not yet filed), so the vehicle objections above
  are my inference from the Fifth Circuit opinion, not the City's own words.
- My account of the Apache Stronghold denial is training knowledge, not a
  retrieved document.
- I did not retrieve anything about this petition's current status beyond the
  snapshot; nothing I saw suggests it has been decided.
