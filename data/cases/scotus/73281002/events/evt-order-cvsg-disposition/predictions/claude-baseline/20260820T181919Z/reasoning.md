# Rationale for the numbers

**P(grant family) = 0.55.**

## Anchors (committed statpack, `metrics/statpack.md`)

- My cell's frozen context carries `band: high` under `sal-v3`
  (`salience_version` matches the statpack's band-table heading), so the scored
  yardstick is the high band's bracketed **`reached`** rate pooled over Terms
  strictly before this petition's OT2025: pooling the eight rendered rows
  (2017–2024, n = 1,074 weighted resolved) gives **≈ 41%**.
- The CVSG cut (paid scored segment): petitions with a CVSG resolve granted
  29.4% + gvr 5.5% ≈ **35% grant family**, versus ~6% for the no-CVSG bucket —
  an order of magnitude above the modern-cert docket rate of a few percent.
- The relist cut is by *terminal* count and a CVSG'd petition mechanically
  accrues more distributions, so I read it only for shape (the hazard climbs
  steeply past two distributions) and did not anchor on my current
  distribution_count = 2 row.

## Adjustments from ~0.41 up to 0.55

Signals that put this petition well above the typical high-band/CVSG member:

1. **The Commonwealth itself is a petitioner** on the vided companion
   (Pennsylvania v. Eakin, 25-967, confirmed live via CourtListener) — a state
   seeking review of a federal invalidation of its own election statute, the
   classic profile the Court takes.
2. **En banc denied 7–6** below — six appellate judges signaled the panel was
   wrong or the issue certworthy.
3. **Three alleged circuit splits** on Anderson-Burdick's operation
   (rational-basis threshold, burden measurement, McDonald's application to
   mail voting) — a recurring framework question that controls election
   litigation nationally.
4. **The Court's own escalation ladder**: response requested sua sponte on
   4/1/2026 after every respondent waived, then a CVSG after two conferences.
5. **The likely SG posture**: the current administration is aligned with
   petitioners; a grant recommendation (which the Court usually follows) is the
   modal outcome. My mixture is roughly P(SG favors grant) ≈ 0.65–0.7 with
   P(grant | SG grant) ≈ 0.7 and P(grant | SG deny) ≈ 0.2, landing near 0.55.

## Adjustments holding it down

- **Vehicle problems the BIO presses**: the Eakin respondents' BIO leans on
  record stipulations that Pennsylvania election officials concede the date
  requirement serves no current fraud-detection or timeliness purpose — that
  makes this a strange vehicle for petitioners' broad "usual burdens of
  voting" rule, since the state-interest side of Anderson-Burdick was
  effectively conceded below.
- **Parallel state litigation** (Black Political Empowerment Project v.
  Schmidt, cited in the BIO): if the Pennsylvania courts independently bar
  enforcement of the date requirement under the state constitution, the
  federal question's practical stakes shrink and mootness/redressability
  clouds gather — a reason for the SG or the Court to wait for another
  circuit's case.
- The date requirement is arguably an idiosyncratic relic with "few modern
  analogues" (BIO), cutting against national importance.
- CVSG'd petitions still resolve **denied 62%** of the time in the statpack's
  cut; a CVSG is attention, not a commitment.

## Other claims

- **relist-increment 0.96**: mechanical. A CVSG'd petition is redistributed
  once the SG files; the residual 4% covers dismissal/withdrawal/mooting
  before any further distribution.
- **cvsg-increment 0.01**: the CVSG is already on the docket (2026-06-29,
  frozen in my context), so the claim is vacuous for this cell and the harness
  masks it; stated pro forma.
- **summary-disposition-route 0.06** (conditional on grant): no intervening
  decision exists to GVR in light of; a CVSG signals plenary interest. Small
  residual for an unforeseen intervening decision or a grant-and-hold
  resolution behind the companion.
- **dissent-from-denial 0.40** (conditional on denial): well above the docket
  base rate because this is precisely the profile that draws separate writings
  — a politically salient election case, a 7–6 en banc split, a CVSG, and
  Justices who have written on Pennsylvania mail-ballot disputes before. No
  published baseline exists for this claim; the number is banked.

## Uncertainty and where to discount me

- The largest uncertainty is the **SG's recommendation**, which is a year of
  political and doctrinal contingency away; my 0.55 is a mixture over it.
- I could not verify the status of the Pennsylvania state-constitutional
  litigation as of prediction time; if enforcement is already enjoined on
  state grounds, my number is too high by perhaps 10 points.
- Corpus vintage: `fedcourts corpus-info` errored in this cell (no local blob;
  traceback recorded in tooling notes), so I cannot quote the blob's pull
  stamp. The one corpus fact I used beyond the committed statpack — the
  RiseandShine CVSG-to-grant timing prior — came from a live `fedcourts query`
  via the cell's corpus service (row's `last_live_polled` 2026-08-16).
- Provisioned documents were complete (petition, QP, and a six-brief BIO
  concatenation, none `empty_text`); I read the QP, the petition's opening,
  and the Luzerne and Eakin BIOs' argument summaries, not every respondent
  brief in full.
