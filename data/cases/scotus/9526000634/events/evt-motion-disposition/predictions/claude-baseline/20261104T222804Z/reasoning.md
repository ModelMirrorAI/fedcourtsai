# Reasoning — scotus/26A634 (Guardado v. Comerford), stay of execution

**P(stay granted in whole or in part) = 0.01.**

## Inputs
- Snapshot `record/snapshots/2026-11-04.json`, cut at arrival position: a single entry,
  Nov 3 2026, "Application (26A634) for a stay of execution of sentence of death, submitted
  to Justice Thomas." It is a capital case linked to cert petition 26-6051. Below it is CA11
  No. 26-14027. Context: forward mode, `band: null`, no response requested, not referred,
  0 amicus.
- `record/documents/application.txt` (18 pp., not truncated, not OCR). Summary: the applicant
  brought a § 1983 Eighth Amendment method-of-execution "maladministration" claim against
  Florida's etomidate three-drug protocol on Sept 28, 2026. His death warrant was signed a
  week later, and execution is set for Nov 5, 2026. He relies on drug-log irregularities:
  undocumented etomidate removals, expiration dates corrected with Wite-Out, short vial
  counts of rocuronium and potassium acetate, lidocaine on the cart, and a spread in
  post-mortem etomidate levels. After an expedited evidentiary hearing the district court
  found these were recordkeeping errors and denied a stay. The CA11 majority affirmed and
  added that he had unduly delayed. Judge Jill Pryor concurred and did not join the delay
  analysis. The application attacks the delay holding (he says Florida law made him
  warrant-eligible only after clemency ended in August 2026) and the courts' fact findings.

## Anchor
The statpack's "The interim docket (applications)" section has nonzero `finer_unread` in
every application-Term from 2016 to 2025. The per-Term finer counts in `statpack.json` are
0 resolved, with all rows unread. Under the pooling rule (every pooled Term must carry
finer counts with `finer_unread` zero), the pool does not clear, so **I anchored without a
published baseline**. The older substantive reading, about 8–14% per Term, is no anchor.
It also pools every kind of stay and injunction, and capital stays are a much lower-rate
subset.

## Adjustments, from the record and general knowledge
- The Court has granted essentially no stays of execution in contested capital cases for
  years. That includes the long run of Florida executions in 2025–26 that the application
  itself cites (18 this year, per Judge Pryor). Method-of-execution claims face *Bucklew*
  and *Glossip*. They require a known and available alternative, and the application does
  not discuss one. They also face the Court's equitable presumption against last-minute stays.
- Both lower courts made adverse fact findings after an evidentiary hearing: the prisoners
  did receive etomidate, and the stock was unexpired. The application mostly asks the Court
  to reweigh credibility. That is a poor vehicle for a stay.
- The strongest point is the delay holding. Judge Pryor did not join it, and the district
  court found no undue delay. But the merits findings stand on their own, so fixing the
  delay error would not change the result.
- Residual mass covers an unusual intervention. It cannot be zero, but it is small.

## Ladder claims
- Response requested (0.10): in Florida warrant cases the State usually responds without
  being asked, and the Court rarely enters a formal call.
- Referral (0.85): the Circuit Justice routinely refers capital stay applications to the
  full Court, and the docket usually shows "referred to the Court." The risk is that the
  referral appears only in the disposition text and is never parsed as a separate rung.
- Amicus (0.04): briefs on a 48-hour warrant docket are rare.
- Order writers: a written dissent is uncommon in these Florida denials. Sotomayor and
  Jackson are the likeliest to write, and the more common shape is a noted dissent with no
  opinion.

## Uncertainty
I did not read the CA11 opinion or the State's response. Neither was provisioned, and I did
not retrieve them. I made no CourtListener or web calls.
