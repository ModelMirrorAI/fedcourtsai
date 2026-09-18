# Rationale for the numbers

**P(grant) = 0.12; predicted disposition: denied.**

## Inputs read

- Snapshot `record/snapshots/2026-09-17.json` (the file `context.json` names).
  Paid docket 25-1341, Term 2025, Eleventh Circuit (No. 23-10811, decided
  November 4, 2025, rehearing denied January 22, 2026). Entries: extension
  application granted by Justice Thomas; petition filed May 22, 2026; waiver
  June 15; distributed June 17 for the September 28 conference; **Response
  Requested July 31** (due August 31); brief in opposition August 31; reply
  September 10; redistributed September 16 for the October 9 conference.
- `record/context.json`: mode `forward`, `band: elevated` under `sal-v4`,
  `distribution_count: 2`, `cvsg_date: null`, `term: 2025`, `cutoff: null`.
- `record/documents/`: `questions-presented.txt` and `petition.txt` (171 pages,
  truncated, fetched 2026-07-18). No BIO was provisioned because it was filed
  after the fetch; in forward mode I retrieved the brief in opposition and the
  reply from supremecourt.gov and read both (see `retrieval.md`).
- `metrics/statpack.md`: the sal-v4 segment table, the relist and CVSG cuts,
  and the circuit cut.

## Anchor

The context carries `band: elevated` under `sal-v4`, and the statpack's segment
table is computed under the same version, so the anchor is the band's
bracketed `reached` rate pooled over Terms strictly before OT2025. Pooling the
eight rendered prior Terms (OT2017 through OT2024, weighted by their `n`) gives
a reached grant-family rate of about **17%** (n = 2,810). The relist-1 bucket
of the paid scored segment (granted 8.2% + gvr 5.1%, about 13%) describes a
similar state, but this docket's second distribution entry is the
post-response redistribution rather than a relist, so I treat that cut as
shape only. The Eleventh Circuit's grant-family rate (about 3.6%) and the
no-CVSG rate (about 6.3%) are the unconditioned background and sit far below
the band anchor.

## Adjustments from the anchor (net: down, from ~17% to 12%)

**Up.** The Court called for a response after respondent waived. That is the
Court's own signal, and it is the main reason this petition is in the
`elevated` band at all. It tells me at least one chambers saw a qualified-
immunity issue worth reading a response on. The Court has kept policing
"clearly established law" defined at a high level of generality by per curiam
reversal, most recently in Zorn v. Linton (March 2026), which postdates the
decision below and so is a conceivable GVR hook. The Eleventh Circuit's theory
(that intentionally routing verification to an examiner one believes
incapable is itself a fabrication of the forensic result) has no on-point
precedent, and the panel said as much ("even assuming our case law is not
directly on point"). Those are the conditions under which the current majority
sometimes summarily reverses a QI denial.

**Down, and further.**
1. *Vehicle.* The posture is interlocutory summary judgment with inferences
   drawn for respondent. The lead question (causation/materiality) was not
   decided below: the panel declined pendent jurisdiction over it, so there is
   no ruling to review, and petitioner's fallback ask (grant and remand to
   consider causation) is not a form of relief the Court gives on a cert
   petition absent an intervening decision.
2. *No split that matters.* Petitioner concedes in the petition that the
   circuits' differing causation formulations make no difference to this
   case, and the BIO quotes that concession back. The "knowing falsity"
   consensus petitioner invokes is not contradicted by the decision below,
   which inferred knowledge from the sham-verification pattern.
3. *The BIO's answer is strong.* It reframes the fabrication as attesting to
   a "confirmed" identification when no genuine verification occurred, cites
   the 2007 investigation's pattern evidence (verifier shopping, skipped
   verifications, an admitted practice of "exceptions"), and invokes Taylor
   v. Riojas obviousness. The reply's best point is factual (McQuay had not
   yet retired in June 2004), which is the kind of record dispute the Court
   does not resolve on certiorari.
4. *Optics.* Respondent spent fourteen years on death row, the conviction was
   vacated after another person's confessions and DNA testing, and the
   charges were dropped. Summary reversals protecting officers cluster in
   split-second excessive-force cases; a per curiam shielding a forensic
   examiner in an exoneration case would be an unusual choice even for
   Justices skeptical of the panel's generality.
5. *Presentation.* Five overlapping, fact-laden questions presented and a
   local firm rather than Supreme Court specialists, which correlates with
   lower grant rates within the called-for-response population.

On balance I land below the band anchor: the CFR is real interest, but the
response answers it well and the petition's own framing undercuts its split.
I would not go below about 8% given the CFR, nor above about 18%.

## Claims

- `disposition` 0.12: same belief as `probability`.
- `relist-increment` 0.38: P(at least one more distribution entry after the
  two shown). Both a per curiam and a dissent from denial require relists;
  a reschedule also adds an entry under the stored count. Modal outcome is
  still a first-conference denial.
- `cvsg-increment` 0.02: no federal interest.
- `summary-disposition-route` 0.55 (conditional on grant): a QI-generality
  per curiam or a Zorn GVR is the natural grant form for this petition;
  plenary review on these questions is the less likely half.
- `dissent-from-denial` 0.10 (conditional on denial): a short conservative
  writing is possible given the CFR; a bare denial is the strong mode.

## Uncertainty and where to discount me

- I do not know which Justice called for the response or why; a CFR driven by
  vehicle-checking reads very differently from one driven by a desire to
  summarily reverse. This is the largest source of variance.
- The petition text was truncated at 171 pages; I read the petition body,
  the questions, and the Count I portion of the appended opinion, not the
  district-court order.
- The corpus `query` I ran returned recent granted SCOTUS priors but the CLI
  has no topic or originating-court filter for SCOTUS rows, so it gave me no
  qualified-immunity comparables; the CourtListener search I ran returned
  zero results on a strict phrase query. Neither informed the number.
- I have no knowledge of this petition's outcome; my training data does not
  reach the October 2026 conference.

## Big-case score

0.35. The human story is prominent (a death-row exoneree suing the forensic
examiner) and a merits ruling on the mens rea for fabrication claims would
matter across wrongful-conviction litigation, but the realistic grant form is
a narrow per curiam and a denial changes nothing beyond this case.
