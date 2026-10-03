# Rationale for the numbers

**P(grant) = 0.08; predicted disposition: denied.**

## Anchor

Cert-stage cell, `moment: distribution`, `mode: forward`, `band: baseline`
under `sal-v4` (`record/context.json`), docket Term 2025, one distribution,
no CVSG. The statpack's "Segment base rate by salience band (sal-v4)" table
matches the context's salience version, so the band is a valid anchor. The
bracketed `reached` figure for `baseline` over the Term rows strictly before
2025 (2017 through 2024, eight rows, all rendered) runs 4.5% to 5.9%; pooled
on the `n` beside each figure it is about 5.1% over roughly 11,600 weighted
petitions. That is my anchor.

The relist-count cut's `0` bucket (petitions that *ended* at one distribution)
shows a grant family of about 1.7%, but that is a terminal-count figure and
understates the forward chance from a first distribution; I used the band
anchor, not that row. The CVSG cut's `none` row (4.0% granted, 2.3% gvr) is
consistent with the band anchor for a non-CVSG paid petition. The Ninth
Circuit row of the originating-circuit cut (2.1% granted, 1.1% gvr over all
modern cert dockets, IFP included) adds nothing beyond the segment figure.

## Adjustments up (to roughly 0.10 before the vehicle discount)

- **Return trip.** This is *Wilkins II*: the Court granted and reversed in
  *Wilkins v. United States*, 598 U.S. 152 (2023), and the petition's lead
  theory is that the lower courts treated the pre-reversal timeliness findings
  as law of the case. The Court is more attentive to petitions alleging
  non-compliance with its own remand, and the petition cites per curiam
  summary reversals (*Johnson v. Board of Education*, *Dobbs v. Zant*) on
  exactly that theme.
- **Petitioner quality and salience of the issue to some Justices.** Pacific
  Legal Foundation is a repeat player that won the first trip; the property
  owner has sympathetic facts (shooting, trespass, erosion); the Quiet Title
  Act accrual question matters to western landowners.
- **Published Ninth Circuit opinion** (163 F.4th 636), so the panel's
  law-of-the-case and accrual holdings are precedential, not a memorandum
  disposition.

## Adjustments down (back to 0.08)

- **Independent de novo ground.** The brief in opposition's central vehicle
  point is strong: the Ninth Circuit stated it "would still affirm the judgment
  after a de novo review of the motions for summary judgment" and did so on
  the undisputed decades-long public use of the road (Pet. App. 12a-19a as
  described in both filings). The petition itself concedes the panel found most
  of the government's limitations arguments factually disputed and affirmed on
  the public-use ground. That makes Question 1 largely academic on this record,
  and the Court does not grant to decide a question whose answer would not
  change the judgment.
- **The Court reserved the remand question.** *Wilkins I* at 156 n.1 took "no
  position" on the implications of nonjurisdictionality on remand, so the
  Ninth Circuit's handling is not a defiance of anything the Court actually
  said. The "ignored our mandate" framing is weaker than it looks.
- **No real split.** The law-of-the-case authorities the petition cites all
  concern wholly vacated decisions, which the BIO rightly says the panel did
  not contradict; the accrual authorities are mostly non-QTA discovery-rule
  cases, and *Werner* is distinguishable on the direction of the easement. The
  intracircuit tension with *Waibel Ranches* is unpublished and the Court does
  not grant on intracircuit inconsistency.
- **Question 2 is factbound.** Whether public use since the 1960s put a
  landowner on notice of the government's view of the easement is a
  record-specific application of a stated rule (Sup. Ct. R. 10 territory).
- **Preservation.** The BIO says the "other easement holders" theory for
  Question 2 was raised for the first time in the petition.

Net: the return-trip and petitioner-quality signals lift this above the
baseline floor, but the alternative holding caps how far. 0.08 is about 1.6x
the pooled band anchor. I would discount me toward the anchor if a reader
thinks the Court's appetite for mandate-compliance summary reversals in civil
cases is lower than I assume, and discount me upward if a reader credits a
Justice treating the de novo analysis as infected by the law-of-the-case
framing (the district court's "facts presumed true were proven true" reasoning
does lean on the earlier findings).

## Claims

- `disposition` 0.08: equals the top-level probability.
- `relist-increment` 0.30: from one distribution. In the paid scored segment
  about a quarter of petitions carry at least one further distribution beyond
  the first (the non-zero relist buckets sum to roughly 3,500 of about 14,000
  weighted petitions, an upper bound that includes reschedules). I adjust up
  modestly because the summary-reversal request and return-trip posture are
  the shape of case held for a possible per curiam or a statement respecting
  denial; the SG's opposition is the kind the Court usually accepts at first
  conference, which keeps me from going higher.
- `cvsg-increment` 0.005: the United States is the respondent and the SG has
  filed; a CVSG is structurally impossible. Not exactly zero only because the
  harness resolves the claim against a docket entry and I leave room for a
  mis-parse.
- `summary-disposition-route` 0.55 (conditional on a grant): the only question
  with pull is a mandate-compliance question that, if acted on, would be
  handled by per curiam reversal or a vacatur directing fresh consideration,
  not by plenary argument. The grant/gvr split in the modern-cert disposition
  section (655 granted versus 577 gvr) puts the cert-order share of grants near
  half; this case's theory pushes above that. No intervening decision supports
  a GVR in the ordinary sense, so the summary share here is per curiam
  reversal or a directed vacatur, not a GVR.
- `dissent-from-denial` 0.12 (conditional on a denial): separate writings on
  paid denials are uncommon, but this is a property-rights petition with a
  mandate-compliance theme and sympathetic facts, which raises the chance of a
  statement from Justice Gorsuch or Justice Thomas above the ordinary rate.

## big_case_score 0.15

Low stakes: a single landowner's easement dispute, procedural questions, and a
record-specific accrual holding. Some reach to western QTA litigants, but no
broad doctrinal or public consequence either way.

## Inputs used

Snapshot `record/snapshots/2026-10-03.json` (as-stored, forward cell, no
cutoff); `record/context.json`; `event.yaml`; all three provisioned documents
(`questions-presented.txt`, `petition.txt` 35 pages, `brief-in-opposition.txt`
19 pages, none `empty_text`, none truncated). The reply brief filed
September 14 is on the docket but was not provisioned and I did not retrieve
it. The committed `metrics/statpack.md` for all base rates. Corpus `fedcourts
query` for priors returned recent grants only loosely comparable (the tool has
no subject filter that fits), so it informed nothing beyond confirming the
docket's shape; the citation lookup for *Wilkins I* found the citation column
too sparse to serve. One CourtListener search confirmed the Ninth Circuit
opinion (docket 25-37, filed 2025-12-29) is published. I did not read the
opinion text itself; my account of its alternative holding rests on the
petition's and BIO's descriptions, which agree on the point.

## Leakage and freshness

Forward cell: the conference is October 9, 2026, after today's date, so the
petition is undecided and nothing I retrieved could reveal an outcome. I did
not search for this case's disposition. I carry no prior knowledge of how
*Wilkins II* resolves; my knowledge of *Wilkins I* (a 2023 merits decision)
predates the snapshot and is legitimate forward context.
