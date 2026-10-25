# Rationale — P(grant) = 0.17

**Inputs used:** snapshot `2026-10-25.json`, `context.json` (band `baseline`
under sal-v4, distribution_count 1, no CVSG, forward mode), and the provisioned
`petition.txt`, `questions-presented.txt` and `appendix.txt` (none empty or
OCR-derived). The appendix includes the Ninth Circuit memorandum. No brief in
opposition exists yet. The response is due Dec 4, 2026.

**Anchor.** I anchored on the statpack's sal-v4 band table, `baseline` column,
using the bracketed `reached` rate pooled over Terms 2017–2025. Those rates run
3.9%–5.9% per Term, so the pooled rate is about 5%. The 2026 row (1.4%,
n=146) belongs to the case's own Term and is mostly unresolved, so I did not
use it.

**Adjustments up:**
- The Court requested a response after the waiver. For a paid petition this is
  a meaningful signal that at least one chambers wanted a look, and that signal
  does not appear to be reflected in the `baseline` band.
- Two business-community amicus briefs were filed at the petition stage.
- The question is one the Court has granted twice (*Tyson Foods*, *LabCorp*)
  without resolving it, and Justice Kavanaugh has publicly signalled he wants
  it decided.
- The petition describes a split that has deepened, citing 2025–2026 circuit
  decisions, including en banc Sixth Circuit rulings. I did not independently
  verify these citations.

**Adjustments down:**
- The Ninth Circuit's disposition is an unpublished memorandum.
- The facts are small-dollar, and the uninjured subset is refund recipients
  who are arguably identifiable.
- An alternative self-inflicted-injury holding adds friction.
- Most importantly, the Court **denied Takeda v. Painters (25-625) on
  Mar. 23, 2026** on essentially this question. I found that through web
  search. It predates the snapshot, so it is forward signal, not leakage.
- A pending petition, *Bayer HealthCare v. Drake* (26-376, filed Sep 2026),
  presents the issue from a published, divided Ninth Circuit opinion. It
  competes as a vehicle. It also creates a route to a "grant" through a hold
  and GVR if *Bayer* is granted and decided for the defendant. That route is
  most of my grant mass, which is why `summary-disposition-route` sits at 0.35
  conditional on a grant.

**Net:** about 17%. That is well above the band anchor because of the response
request and the Court's evident interest in the question, but below an even
chance because of this vehicle's weaknesses and the recent *Takeda* denial.

**Increments:**
- `relist-increment` 0.95: a further distribution after the response is filed
  is nearly mechanical. The residual covers settlement or withdrawal.
- `cvsg-increment` 0.03: there are no federal parties or interests.
- `dissent-from-denial` 0.12: a Kavanaugh writing is possible, but the
  alternative vehicle makes one less likely.

**Uncertainty / discount me:** I have not seen the BIO, which could raise
vehicle problems such as mootness through redefinition or settlement, or it
could concede the split. I also do not know whether *Bayer* will draw a
response request. Timing is uncertain as well, because a hold could keep this
case pending into mid-2027. I did not run `fedcourts query` priors; the
statpack and the docket carried the forecast.

**No outcome seen:** I found nothing about this petition's own disposition.
