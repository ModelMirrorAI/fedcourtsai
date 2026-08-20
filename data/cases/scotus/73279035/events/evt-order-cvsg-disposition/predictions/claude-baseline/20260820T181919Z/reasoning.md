# Rationale — why P(grant family) = 0.36

## Anchors

Two statpack anchors bracket this cell, and I sit between them, slightly below
their midpoint:

- **Salience band.** `record/context.json` freezes `band: high` under
  `sal-v3`, which matches the statpack's band table version, so the scored
  yardstick is the high band's bracketed `reached` rate pooled over Terms
  strictly before this case's OT2025. Pooling OT2017–OT2024 from the table
  (n = 129, 131, 124, 148, 146, 125, 124, 147; rates 42.6/45.0/45.2/34.5/42.5/
  37.6/35.5/44.2%) gives **≈ 40.9%** on a pooled risk-set denominator of 1,074.
- **CVSG cut.** The "Cert petitions by CVSG status (paid scored segment)" cut:
  CVSG'd petitions resolve granted 29.4% + gvr 5.5% = **≈ 34.9%** grant family
  (denied 62.0%, dismissed 3.1%). This is the moment-specific anchor the CVSG
  cell is told to prefer over the overall docket rate, though it buckets by
  terminal CVSG status rather than conditioning at my vantage.

## Adjustments

**Up from the anchors:**
- The split is deep, old, and acknowledged by the court below (petition: six
  circuits allow surcharge under § 1132(a)(3); the Fourth and Sixth deny it),
  and the Fifth Circuit's 2025 Aramark decision (162 F.4th 532) re-agitated it.
- The Court's own escalation is unusually complete: respondent waived, the
  Court **requested a response**, distributed twice, then **CVSG'd with the
  BIO's vehicle attack and the reply already on file** — the Court read the
  "fatally flawed vehicle" section and still wanted the SG's views.
- Strong petitioner counsel (UVA Supreme Court Litigation Clinic), elite
  respondent counsel (Latham), and a cert-stage amicus from Samuel L. Bray,
  the leading remedies scholar — signals of a seriously contested, cert-shaped
  question.
- ERISA "appropriate equitable relief" is a line the Court has repeatedly
  granted on (Mertens, Great-West, Sereboff, Amara, McCutchen, Montanile).

**Down from the anchors:**
- The vehicle objections are substantive, not boilerplate: a top-hat plan
  exempt from ERISA fiduciary duties, a non-fiduciary defendant, and an
  antecedent liability question the Sixth Circuit expressly left unresolved.
  If the Fifth Circuit's Aramark rule (surcharge only against fiduciaries) is
  right, the QP could be academic here. That gives the SG an easy
  deny-and-await recommendation, and the Court follows the SG's cert
  recommendation in most CVSG'd cases.
- The Court passed on this same QP recently: the petition itself distinguishes
  Rose v. PSA Airlines (No. 23-734) on interlocutory-posture grounds — I
  recall that petition was denied, though I could not verify its docket
  history through retrieval (see below), so I hold this loosely as
  training-knowledge context about a *different* case.
- The class is retired executives under a top-hat plan, muting the
  worker-protection stakes that often push ERISA remedies cases over the line.

**Net:** 0.36 — essentially the CVSG-cut anchor, held slightly below the
high-band pooled rate because the vehicle flaws here are stronger than the
banded population's average and the SG's recommendation is the modal path to
denial. `predicted_disposition: denied` because denial (≈ 62% on the CVSG cut,
0.64 on my number) remains the single most likely outcome; `granted: 0`
agrees.

## Claim numbers

- `disposition` 0.36 — restates the top-level probability.
- `relist-increment` 0.96 — the record shows 2 distributions; a CVSG all but
  guarantees at least one more (the SG's brief is distributed for conference).
  The residual 0.04 covers settlement/withdrawal or dismissal before the SG
  files.
- `cvsg-increment` 0.01 — a CVSG is already on the docket (2026-04-06); the
  claim is vacuous for this cell and the harness masks it. Stated as the
  honest near-zero chance of a second invitation.
- `summary-disposition-route` 0.12 — conditional on a grant. The statpack CVSG
  cut implies gvr ≈ 16% of the grant family, but there is no intervening
  decision today to GVR in light of; the GVR path requires another vehicle to
  be granted and decided first, so I sit below the cut's share.
- `dissent-from-denial` 0.18 — conditional on denial. No published baseline;
  post-CVSG denials that follow an SG deny recommendation are usually quiet,
  but the acknowledged split and remedies-scholar interest give a real chance
  of a statement or dissent.

## Inputs and degradations

- Provisioned inputs used: the 2026-04-07 snapshot, `questions-presented.txt`,
  `petition.txt` (truncated at 118 pages — the appendix tail is what is cut;
  the argument sections were intact), and `brief-in-opposition.txt` (full, 40
  pages). None had `empty_text`.
- **Corpus query degraded:** two `fedcourts query` attempts against the cell's
  corpus service timed out (180s service timeout, then a 100s retry) and
  returned no rows, so no corpus priors inform this prediction. I proceeded on
  the provisioned inputs and the committed `metrics/statpack.md`, per the
  degradation rule. Corpus vintage therefore cannot be quoted from
  `corpus-info` either; the statpack is the committed artifact I anchored on.
- CourtListener MCP retrieval worked (3 searches): confirmed the Fifth
  Circuit's Aramark Services v. Aetna decision exists (docket 24-40323; the
  index shows a 2025-12-18 dateFiled, consistent with post-panel activity
  beyond the 162 F.4th 532 opinion the BIO cites), and found **no** SCOTUS
  cert petition from Aramark and no Rose v. PSA Airlines SCOTUS docket in the
  RECAP index — weak evidence either way, since RECAP's SCOTUS docket coverage
  is thin.

## Where to discount me

The single biggest uncertainty is the **SG's recommendation**, which nothing
in my record predicts well; my 0.36 is roughly a mixture of ~0.55–0.6 if the
SG recommends granting QP 1 and ~0.15–0.2 if the SG recommends denial, weighted
modestly toward denial because the vehicle attack is genuinely strong. Second
uncertainty: whether a cleaner fiduciary-context petition (Aramark or a
successor) reaches the Court while this one is held — that would convert my
grant mass partly into GVR mass. Third: my recollection of Rose (23-734) as a
denial is unverified here.
