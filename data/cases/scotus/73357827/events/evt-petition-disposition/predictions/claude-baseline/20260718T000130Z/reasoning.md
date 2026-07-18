# Wisconsin Voter Alliance, et al. v. Don M. Millis, et al. — No. 25-1288

**Event:** cert petition disposition (forward mode). **Prediction: denied, P(grant) = 0.03.**

## The case

Petitioners (Wisconsin Voter Alliance, its president Ron Heuer, and member
Kenneth Brown) filed HAVA administrative complaints with the Wisconsin
Elections Commission alleging that WEC itself was violating HAVA; WEC returned
the complaints without adjudication, reasoning it could not decide complaints
against itself. Petitioners sued under 42 U.S.C. § 1983 to compel the
HAVA-mandated complaint process. The Eastern District of Wisconsin dismissed
for lack of Article III standing, and the Seventh Circuit affirmed in a
published opinion (166 F.4th 627, Feb. 10, 2026), holding the denial of the
administrative process a "bare procedural violation" without a concrete-harm
analog under *TransUnion*, rejecting a First Amendment Petition Clause theory,
and — notably — announcing a restrictive "core business activities" test for
organizational standing that declares its own *Common Cause Indiana v. Lawson*
precedent obsolete in light of *FDA v. Alliance for Hippocratic Medicine*.

The questions presented ask (1) whether HAVA creates privately enforceable
rights under § 1983 (an asserted 1st/6th vs. 3rd/9th/11th circuit split), and
(2) whether total deprivation of HAVA-mandated administrative procedures is a
concrete Article III injury.

## Base rates

From the committed statpack (modern discretionary-cert slice,
denial-reweighted): overall grant rate ~2.5–3.3% per recent Term; **paid**
petitions (this is a paid case, Term 2025) grant at ~5.4% (Term 2025 paid
class, statpack.json). Originating-circuit cut for CA7: granted ~2.0%. No
CVSG (none-bucket: 3.0% grant). The petition has not yet been to conference
(distributed June 17 for the September 28, 2026 long conference), so the
relist signal is not yet observable; granted priors pulled from the corpus
(e.g. the June 30, 2026 grants) typically show 3+ conference distributions.

Starting anchor: ~4–5% for a paid, counseled petition from a published
circuit opinion.

## Case-specific adjustments

**Down:**

- **Respondents waived the right to respond (June 11, 2026), and as of the
  snapshot the Court has not called for a response.** The Court virtually
  never grants without a response on file; a grant path here requires a CFR
  first, which is itself a low-probability branch. This is the strongest
  single denial signal in the record.
- **Vehicle problems on QP1.** The Seventh Circuit resolved the case on
  Article III standing and never reached whether HAVA creates § 1983 rights,
  so the lead "circuit split" question is not cleanly presented by the
  decision below — the Court would have to resolve standing before it could
  reach the split. The asserted HAVA-enforceability split is also old
  (*Sandusky* is 2004, *Colon-Marrero* 2016) and the Court has let it
  percolate for two decades without intervening.
- **Petitioner profile.** WVA is a small election-integrity advocacy group
  whose prior election litigation (e.g. the 2020 *Wisconsin Voters Alliance v.
  City of Racine* injunction applications, cited in the petition itself) has
  uniformly failed at the Court. The lone amicus brief is from aligned
  election-integrity groups sharing the movement's counsel network, not from
  states, chambers, or cross-ideological voices.
- **The alternative-remedy story cuts against urgency.** The petition leans on
  the DOJ's June 2025 warning letter to WEC, but that letter shows the § 21111
  Attorney General enforcement pillar actively engaging with the exact
  grievance — reducing the practical need for a private right.

**Up (modestly):**

- The Seventh Circuit's published opinion openly narrows *Havens Realty*
  organizational standing post-*Hippocratic Medicine* and declares circuit
  precedent obsolete; the scope of organizational standing is a live question
  the Court may eventually take, and QP2 (procedural deprivation as concrete
  injury) sits near *TransUnion*'s fault line.
- Paid, counseled, published-opinion posture; election-administration subject
  matter ahead of the 2026 midterms.

The up-signals are the kind that produce an eventual grant in a better
vehicle (a case with adversarial briefing, broader amicus support, and a
cleanly presented question), not this one. Netting the waived response,
the standing-first posture, and the petitioner profile against the paid-class
anchor, I put P(grant, including GVR) at **0.03** — near the CA7 cut and
below the paid-class base rate. No plausible GVR predicate (no intervening
decision pending that would resolve this), and dismissal/withdrawal is
unlikely for a group that litigates to finality, so denied is the residual
disposition with ~95% of the mass.

## Timing note

Distribution for the long conference means no disposition before late
September 2026; the modal outcome is a denial on the first order list of
OT2026 (early October), with a smaller branch where the Court requests a
response and the case slips later.

## Inputs used

- Snapshot `record/snapshots/2026-07-17.json` (docket entries through the
  June 17, 2026 distribution).
- `record/documents/questions-presented.txt` and `petition.txt` (full 56-page
  petition text; no brief in opposition exists — respondents waived).
- `metrics/statpack.md` and `statpack.json` (base rates, per-fee-class and
  per-circuit cuts).
- Corpus priors and CourtListener lookups per `retrieval.md`.
