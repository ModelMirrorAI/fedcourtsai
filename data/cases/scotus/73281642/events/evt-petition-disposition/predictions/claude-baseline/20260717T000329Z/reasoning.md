# Hadley v. City of South Bend, Indiana, et al. — No. 25-1158 (cert petition)

**Prediction: deny is the modal outcome, but this is a far-above-baseline grant
candidate. P(grant, GVR included) = 0.25.**

## The legal question

Amy Hadley's South Bend home was severely damaged (~$16,000; roughly thirty
tear-gas canisters, broken windows and cameras, interior ransacked) by city and
county officers executing a search warrant for a fugitive who was never there —
the warrant rested on a mistaken IP-address trace. She concedes the search was
lawful; her claim is that the Fifth Amendment's Takings Clause requires just
compensation for the deliberate destruction. The Seventh Circuit (154 F.4th
549) affirmed dismissal at 12(b)(6) under its *Johnson v. Manitowoc County*
"police-power exception": no taking when property is damaged under a power
other than eminent domain. Rehearing en banc was denied.

The petition (Institute for Justice) presents two QPs: (1) whether the Takings
Clause has a police-power exception — a split it counts as 7th/10th/Federal
Circuits yes vs. 4th/5th/6th/11th no; and (2) whether the government is exempt
from takings liability when officers intentionally destroy an innocent person's
property while pursuing a fugitive — where even the anti-exception circuits
have fragmented into a "public necessity" exception (CA5 *Baker*, CA9 *Pena*)
and a "search and arrest" exception (CA6 *Slaybaugh*).

## Why this petition is much stronger than the base rate

- **Square, acknowledged split, already flagged inside the Court.** Justice
  Sotomayor, joined by Justice Gorsuch, wrote a statement respecting the denial
  of certiorari in *Baker v. City of McKinney*, 145 S. Ct. 11 (2024), calling
  the question "important" (the petition quotes it). The split has since
  *widened*: CA11 (*Alford*, 2025) and CA9 (*Pena*, 2025) added themselves, and
  percolation has produced fragmentation, not convergence.
- **A vehicle engineered to fix the predecessors' defects.** *Baker* failed as
  a vehicle because the necessity exception fit its hostage-standoff facts;
  *Slaybaugh* failed because the CA6 search-and-arrest privilege covered it.
  Hadley has no emergency: officers believed the fugitive was posting on
  Facebook, her son had exited, the front door stood open, no hot pursuit, no
  hostages — so under CA5/CA9's own necessity test her claim plausibly
  *survives*, meaning the circuit assignment is genuinely outcome-dispositive
  here in a way it was not in *Baker*. Facts are undisputed at the
  motion-to-dismiss stage, and both lower courts rested solely on the
  police-power exception.
- **Coordinated litigation campaign with a companion.** IJ filed this petition
  concurrently with a petition in *Pena v. City of Los Angeles* (25-1163, from
  the other side of the doctrinal patchwork); an amicus brief was filed jointly
  in both. The Court gets a matched pair.
- **Heavy, cross-ideological cert-stage amicus support.** Five briefs: takings
  scholars (Ely, Mahoney, Saxer, via Sullivan & Cromwell), Pacific Legal
  Foundation, the *Lech* petitioners (UChicago/Jenner Block clinic), small
  property-owner groups, and — notably — a former police chief. Multiple
  cert-stage amici are one of the stronger observable grant correlates.
- **The Court's revealed appetite for takings cases** (*Knick*, *Cedar Point*,
  *Tyler*, *Sheetz*, *DeVillier* across recent Terms) and this line's status as
  the most prominent unresolved takings question.
- Paid petition, experienced Supreme Court counsel, sympathetic and vivid facts.

## Why deny is still the modal outcome

- **Base rates are unforgiving.** From the committed statpack: modern paid
  petitions grant at ~5.4% (Term 2025 fee-class detail; 6.9% and 8.0% the two
  prior Terms); CA7-originating petitions run below average; no CVSG, and none
  is likely (municipal respondents, no federal interest); no relist signal yet
  — the case was distributed on June 24, 2026 for the **September 28, 2026 long
  conference**, and essentially all modern grants come only after at least one
  relist (relist buckets 2/3+ grant at 34%/22% vs 0.8% at zero relists).
- **The Court has passed on this exact issue three times in six years** —
  *Lech* (2020), *Baker* (2024, with only two Justices writing), and *Slaybaugh*
  (cert denied in 2025 — I carry this from training knowledge; it is consistent
  with the petition's framing of *Slaybaugh* as a completed lower-court
  decision and was not retrievable via the cell's CourtListener index). Two
  noted Justices short of four is the last observed count.
- **The BIO gives the Court a ready off-ramp**: it argues the split is illusory
  at the outcome level (every circuit to decide one of these cases has denied
  compensation for reasonable law-enforcement damage), that 750 years of
  common-law tradition and *Bennis*/*Mugler*-line precedent support
  non-compensability, and that Hadley's own concessions (lawful warrant,
  reasonable execution) plus her proposed rule's carve-outs (innocence, "no
  connection," de minimis damage — administrability concerns the CA7 panel
  itself voiced) make this a poor vehicle. The outcome-convergence point is
  weaker here than in *Baker* (see above), but it is the kind of argument that
  lets a cert pool memo recommend denial.

## Weighing

Anchor on the paid-class rate (~5–6%), then apply the large observable
uplifts: an acknowledged and recently flagged split, two Justices on record
calling the issue important and effectively inviting a cleaner vehicle, that
cleaner vehicle now presented with a companion, and five cross-ideological
amici. Petitions with this full profile historically clear well into double
digits. Against that, the Court's three straight denials in this precise line
and the BIO's plausible outcome-convergence denial rationale cap my estimate
below a coin flip. I land at **P(grant) = 0.25** — roughly 4–5× the paid
baseline — with **denied** as the single most likely disposition. A GVR is not
plausible (no intervening decision to GVR in light of), so the grant mass is
plenary grant, most likely limited to QP1 if it happens. If denied, a dissent
from or statement respecting denial (Sotomayor, Gorsuch, possibly Thomas) is
likely.

## Salience

`big_case_score` 0.7: an innocent single mother's home destroyed over a
mistaken IP trace is a nationally resonant fact pattern; the police-power
exception question is the highest-profile open takings issue, drawing
cross-ideological attention (IJ, PLF, academics, and a police chief on the same
side). A merits decision would be a landmark; even a denial will draw coverage.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-16.json` (docket through the
  June 24, 2026 distribution for the 9/28/2026 conference).
- Provisioned `questions-presented.txt`, `petition.txt` (43 pp.), and
  `brief-in-opposition.txt` (51 pp.) — all read in full.
- Committed `metrics/statpack.md` + `metrics/statpack.json` (paid/IFP fee-class
  grant rates, relist/CVSG/circuit cuts). The statpack in this cell carries no
  salience-band table, so I anchored on the fee-class and signal-cut rates.
- `fedcourts query` returned no matching corpus priors (see `retrieval.md`);
  CourtListener's search indexes do not cover SCOTUS cert dockets, so the
  predecessor-petition history rests on the petition's own citations (*Baker*,
  145 S. Ct. 11) and training knowledge (*Lech*, *Slaybaugh* denials).

I have no knowledge of this petition's actual disposition; it is pending
(forward mode), first conference 2026-09-28.
