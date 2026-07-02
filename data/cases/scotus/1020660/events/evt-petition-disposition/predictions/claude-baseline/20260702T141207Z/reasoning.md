# Willie Frazier v. Ward Lane — petition disposition (scotus/1020660)

## The question

Will the Supreme Court grant this petition? The event is
`evt-petition-disposition` with `decision_target: disposition`, so the call is
the realized disposition of the petition itself.

## What the snapshot shows

The snapshot (`data/cases/scotus/1020660/record/snapshots/2026-07-02.json`) is
sparse but structurally informative:

- **Docket number `33, Misc`** — the Supreme Court's *miscellaneous docket*,
  which historically carried in forma pauperis petitions, overwhelmingly pro se
  prisoner filings. This is the single most predictive fact available.
- **Caption `Willie Frazier v. Ward Lane`** — an individual petitioner against
  an individual respondent, consistent with a prisoner petition against a
  custodian (habeas or similar collateral attack). No United States, state, or
  institutional party posture suggesting a government-side petition.
- **No counsel, no attorneys, no docket entries** — no indication of
  represented status, a call for the views of the Solicitor General, a response
  requested, relisting, or any other positive grant signal.
- **`date_cert_granted` and `date_cert_denied` are both null**, and
  `date_terminated` is null — the outcome is not leaked in the snapshot; the
  event is genuinely open as presented.
- The docket's `source` and cluster linkage indicate the record was digitized
  from published reports, consistent with an older case whose disposition would
  appear as a one-line memorandum order.

## Governing standard

Certiorari is discretionary (Sup. Ct. R. 10): the Court grants to resolve
circuit or state-court splits, or for questions of exceptional national
importance — not for error correction. A pro se in forma pauperis petition
carries none of the usual grant signals (able counsel framing a split, a CVSG,
amicus support, a published circuit conflict).

## Base rates

- Corpus-wide (`fedcourts stats --court scotus`): among resolved SCOTUS events
  in the corpus, **granted ≈ 1.4%** (4/296), denied ≈ 4.4%, dismissed ≈ 15.9%,
  with "other" (78%) dominated by old appellate-jurisdiction cases that are not
  comparable to a discretionary petition.
- Historically, the miscellaneous (IFP) docket's grant rate has always been far
  below the paid docket's — low single digits at its most generous (the era of
  routine GVRs of prisoner cases), well under 1% in the modern era. Either way,
  denial is the overwhelming outcome.

## Weighing

Every structural signal points the same direction: an unrepresented prisoner
petition on the miscellaneous docket with no visible response, relist, or CVSG.
The only probability mass on the grant side comes from the historical practice
of summary grant-vacate-remand orders for IFP prisoner petitions in older
Terms, which is why I do not push the probability to the floor. There is no
basis in the snapshot for `dismissed`, `withdrawn`, or a partial grant.

**Prediction: denied.** P(granted) = **0.03**, `granted = 0`, confidence 0.85.
No per-judge votes: the snapshot gives no Term-composition or panel
information, so predicting nine named votes would be invention rather than
inference.

## Caveats

The snapshot has no docket entries, no filing/decision dates, and no
originating-court information, so this prediction rests on the docket-number
class, the caption posture, and base rates rather than on the petition's
merits. Flagged in `flags.json` as a data-quality note.
