# Rationale — why 0.72 and the other numbers

## The cell

Forward-mode interim cell at `moment: response-filed`: application 26A203, the
federal government's application (Solicitor General as counsel of record) for
a stay of a modified preliminary injunction in the White House
ballroom-construction litigation, D.C. Circuit No. 26-5123, respondent
National Trust for Historic Preservation. Snapshot dated 2026-08-18, cutoff
2026-08-19. Frozen conditioning: `band: null` (normal for interim — I do not
anchor on any cert band), `response_requested: true`,
`referred_to_court: false`, `amicus_briefs: 0`, term 2026.

## The anchor

The committed `metrics/statpack.md` carries "The interim docket
(applications)". Pooling the resolved substantive slice over application-Terms
strictly before 2026: Term 2025 contributes 178 resolved / 16 granted and Term
2024 contributes 47 / 14, for a pool of **225 resolved, 30 granted — 13.3%**,
which clears the pre-registered floor of 50, so a published baseline exists
for this cell and that is what I anchored on. The section's caption states the
scored-baseline terms directly (no descriptive-only caveat), so I read it as
the scored rate. The caveats travel with it: raw counts, denial-first collapse
of mixed orders, uneven parse coverage across Terms (2024's 47 resolved sit
beside 1008 unparsed), and the registered selection gap — the predicted
population is picked by escalation-ladder order, so it sits above this
cohort's rungs by construction.

## Adjustments from 13.3% up to 0.72

1. **The applicant is the United States.** The pooled rate is dominated by
   prisoner and private applications, which fail at very high rates. The
   government's contested substantive applications in the 2024 and 2025 Terms
   were granted in the substantial majority of cases — the Court repeatedly
   stayed lower-court injunctions against executive action across personnel,
   spending, and immigration disputes. That class difference alone moves the
   number several-fold.
2. **Maximum escalation short of referral.** The Chief Justice called for a
   response within a day of filing, on a four-day fuse keyed to the D.C.
   Circuit's own 14-day window (its August 7 judgment stayed itself to August
   21 and the mandate issues that day). The court below explicitly built the
   window "to allow the Defendants, if they choose, to seek Supreme Court
   review" — everyone involved treats this as live full-Court business.
3. **The merits map onto this Court's revealed preferences.** The injunction
   runs against the President, the Executive Office of the President, NPS,
   DOI, and GSA over alterations to the White House complex itself. The
   separation-of-powers objection to judicial supervision of the President's
   own residence is the kind of argument this Court has consistently credited
   at the stay posture, and Judge Rao's 35-page dissent from the 2-1 panel
   affirmance supplies a ready-made merits roadmap.
4. **Pulling the other way:** two courts have now ruled against the
   government, the second after full briefing and argument in a 101-page
   opinion; the respondent's irreparable-harm story (irreversible construction
   on a historic site) is unusually concrete while the government's is mostly
   delay; and the denial-first collapse means a stay granted only in part
   scores as a denial, which shaves the number below where "some relief" would
   sit. A withdrawal or mooting also scores as ungranted, though nothing on
   this record suggests either.

Balancing: I put P(unqualified grant) at **0.72** — near the government's
recent contested-application grant rate, trimmed for the partial-grant
collapse and the strength of the equities below. `interim-disposition`
restates this number, as required.

## The increment claims

- **response-requested-increment 0.02** — the rung already fired (request on
  the docket August 14), so the claim is vacuous for this cell and will be
  masked; the nominal figure prices only a superseding second request.
- **referral-increment 0.90** — referral is near-certain for a contested
  government application of this profile, and the pipeline's referral signal
  matches the standard disposing recital ("…and by him referred to the
  Court…"), so it fires when the full Court disposes. The residue covers
  pre-order mooting/withdrawal, a single-Justice disposition, and
  non-standard order phrasing.
- **amicus-increment 0.10** — this is mostly a measurement call, and a reader
  should discount it accordingly. Six amicus briefs are visibly on the
  snapshot, but the frozen context reads `amicus_briefs: 0` because the
  counter (`interim_signals._AMICUS_RE`) matches the literal phrase "amicus
  curiae", which the application docket's "Amicus brief of X submitted."
  entries never contain. The resolver compares the same counter's
  resolution-time value against the frozen 0, so unless a future entry
  happens to carry the phrase (a motion for leave, a differently-worded
  entry), the count stays 0 and the claim resolves false — despite real
  amicus activity being obviously present and possibly still growing. Flagged
  as data-quality in `flags.json`.

## Uncertainty and candor

- My largest uncertainty on the disposition is not the applicant class but the
  equities: unlike the personnel/spending stays, the claimed harm here is
  physical and irreversible, and I cannot read the modified injunction's exact
  scope from the entries (whether it halts all work or only some). If the
  injunction is narrower than I assume, the government's urgency case weakens
  and a denial or partial grant becomes more likely; 0.72 could reasonably be
  0.60–0.80.
- Corpus retrieval added little: `fedcourts query` ranks by recency and
  returned only routine time-extension grants, which are excluded from the
  interim rate; no useful substantive-application priors surfaced. Base rates
  came from the committed statpack (the vintage the anchor rests on is the
  committed pack itself; `fedcourts corpus-info` is not served in this cell —
  the service backend refuses the client-side connection it needs).
- CourtListener retrieval (D.C. Circuit docket 26-5123) established the
  posture: the August 7 per curiam judgment affirming the modified
  preliminary injunction, the panel split, the 14-day self-stay, and the
  August 21 mandate date. I did not query for this application's own
  disposition, news coverage of it, or the SCOTUS docket's current state; the
  forecast rests on the pre-decision record.
- The statpack's Term-2026 row (0/22 granted) contains my own Term and is
  excluded from the anchor per the pooling rule.
