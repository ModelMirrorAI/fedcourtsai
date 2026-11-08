# Reasoning — Venkatraman v. Bank of America, N.A., No. 26-367

**P(grant) = 0.004; predicted disposition: denied.**

## What I read
- Snapshot `record/snapshots/2026-11-08.json`: paid petition, docketed Sept. 17, 2026, from the Fifth Circuit (No. 25-10969, decided Apr. 14, 2026). Petitioner is self-represented (he is listed as his own counsel of record). Two docket entries: petition filed (response due Oct. 19, 2026) and "DISTRIBUTED for Conference of 12/4/2026" (Nov. 4). No response, waiver, or brief in opposition shows on the docket, and no amicus filings.
- `record/context.json`: forward mode, band `baseline` (sal-v8), `distribution_count` 1, no CVSG, `cert_anchor.rate` = 0.0515 (10-Term pooled baseline-band reached rate).
- `record/documents/`: `questions-presented.txt`, `petition.txt` and `appendix.txt` (all with text, none OCR-derived). No BIO was filed, so none was provisioned.

## Anchor and adjustments
- The anchor is the frozen `cert_anchor` rate of about 5.2%. It covers the whole paid baseline band, which includes counseled petitions that go on to relist. The statpack's relist-0 bucket shows a grant rate of about 1.3% (plus 0.5% GVR) for petitions that are never relisted. This case's own Term 2026 baseline row reads 0.6% terminal and 1.2% reached.
- **Large downward adjustments:**
  - The question is one of Texas tort law: whether a bank owes a duty to a non-customer, in a diversity case. The Court does not take review to correct a federal court's reading of state law.
  - The petition claims no circuit split. Its own framing is that the Fifth Circuit applied Texas cases (*Owens v. Comerica*, *Midwestern Cattle*, *Taya*).
  - The decision below is an unpublished summary-calendar opinion.
  - The petitioner is pro se. The petition is 14 pages and argues mainly that fraud is a national policy problem, citing FTC and FinCEN figures.
  - The bank has not filed a response, and the Court has not called for one. In practice the Court almost never grants a petition without first calling for a response.
- Nothing in the record points upward. There are no amici, no federal party, and no intervening decision that would support a GVR.
- That leaves the grant probability well below 1%. I settled on 0.4%, which leaves a small allowance for a response call or an unforeseen event.

## Claims
- relist-increment 0.03: the most likely path is denial at the Dec. 4 conference. Another distribution would mostly come through the Court calling for a response, which I put at about 1–2% for a pro se state-law petition, or through a reschedule.
- cvsg-increment 0.002: there is no federal interest and no federal-law question.
- summary-disposition-route 0.3 (conditional on a grant): any grant here would be anomalous. If one happened, a GVR or summary action is roughly as plausible as plenary review.
- dissent-from-denial 0.005.

## Uncertainty
- The snapshot shows no waiver entry, so either the bank has not yet answered or the entry was not captured. Either way, the Court distributed the petition without a response, which is the ordinary path to denial.
- I did no retrieval beyond the provisioned inputs and one corpus query, which gave only generic priors and did not move the number.
