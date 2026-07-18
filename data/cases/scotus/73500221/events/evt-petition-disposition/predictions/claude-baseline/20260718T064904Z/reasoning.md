# Rogne v. City of Catoosa, Oklahoma — No. 25-1320 (petition disposition)

**Prediction: denied. P(any grant, GVR included) ≈ 0.012.**

## The case

John Rogne, a Catoosa, Oklahoma landowner, was served with cease-and-desist
orders (2009 and 2011) barring him from stockpiling dirt on his vacant lots;
the City also fenced the property for roughly six years. He sued in Oklahoma
state court for inverse condemnation and lost — the state courts held he
failed to exhaust administrative remedies, and a footnote in the Oklahoma
Court of Civil Appeals opinion said that "as a matter of law there was no
taking" because the City rescinded the order once he sought an administrative
remedy. The Oklahoma Supreme Court denied review. Rogne then refiled in
federal court (N.D. Okla.) under § 1983, invoking the Oklahoma savings
statute (12 O.S. § 100), which permits refiling within a year when a prior
action "fail[ed] otherwise than upon the merits." The district court
dismissed, and the Tenth Circuit affirmed on February 17, 2026 (No. 25-5039,
an unpublished order and judgment), holding the state decision *was* on the
merits.

**Question presented:** whether a state-court dismissal resting on a
prudential exhaustion rule and the government's voluntary cessation
(rescission) is a decision "on the merits" of an uncompensated Takings Clause
claim — invoking *Knick v. Township of Scott*, 588 U.S. 180 (2019), and
*First English*, 482 U.S. 304 (1987).

## Governing standard

Certiorari is discretionary under Sup. Ct. R. 10: the Court grants primarily
for genuine conflicts among circuits or state courts of last resort on
important federal questions, or for questions of exceptional national
importance. Error correction — even of a plausibly wrong decision — is
expressly disfavored ("a petition for a writ of certiorari is rarely granted
when the asserted error consists of erroneous factual findings or the
misapplication of a properly stated rule of law").

## Snapshot facts that drive the outcome

Docket signals as of the 2026-07-18 snapshot (case docketed May 28, 2026):

- **Respondent waived its right to respond** (June 8, 2026), and the Court
  has **not called for a response**. The modern Court essentially never
  grants without a response on file; a CFR is a near-prerequisite signal and
  none has issued.
- **Distributed June 24 for the September 28, 2026 conference** — the summer
  "long conference," where the denial rate runs even above the yearly norm.
  Zero relists so far (and none possible before the first conference).
- **No amicus support.** Post-*Knick* takings petitions that get traction
  (e.g., *Pakdel*, *Cedar Point*, *Tyler*, *DeVillier*) typically arrive with
  institutional property-rights amici (Pacific Legal Foundation, Cato, etc.).
  This one has a solo Oklahoma practitioner and no amici.
- **Paid (not IFP)** petition, Term 2025, No. 25-1320.
- **Unpublished, non-precedential decision below** (Tenth Circuit "Order and
  Judgment"), which cuts strongly against review.

## Merits-adjacent assessment of certworthiness

The petition's strongest theme is real: *Knick* and *First English* do say
rescission cannot extinguish a claim to compensation for the period of a
taking, and there is a genuine post-*Knick* undercurrent about state courts
using exhaustion/ripeness rules to defeat takings claims and about the *San
Remo* preclusion trap. If a well-vehicled circuit split on that question
arrived, the Court might take it.

But this petition is a poor vehicle and pleads no split:

- It **alleges no circuit conflict** — the "Reasons for Granting" sections
  argue the Tenth Circuit was simply wrong, i.e., error correction.
- The federal question is **entangled with state law**: whether the state
  dismissal was "on the merits" matters here only through the Oklahoma
  savings statute (12 O.S. § 100) and Oklahoma preclusion doctrine. The Court
  does not sit to police a state savings statute's application.
- The dispute is **fact-bound** — one landowner, one fence, a decade of
  idiosyncratic procedural history spanning two administrative hearings, two
  state courts, and two federal courts.
- Independent state-law grounds (the state courts' alternative "no taking as
  a matter of law" footnote) muddy the vehicle further.

## Base rates and adjustment

From the committed statpack (live/historical slice, denial-reweighted):

- Modern discretionary-cert anchor: granted ≈ 3.1% of resolved petitions
  overall; **Term 2025: denied 95.4%, granted 2.5%**.
- **Paid** fee class, Term 2025: grant ≈ 5.4% (IFP ≈ 1.1%).
- **Tenth Circuit** origin: grant ≈ 5.0%.
- **Zero relists**: grant ≈ 0.8% (relists are the classic pre-grant signal;
  none here, first conference still ten weeks out).
- **No CVSG**: grant ≈ 3.0% (vs. 27.1% with CVSG).

The paid/CA10 cuts (~5%) are ceilings for a petition with any positive
signal; every case-specific signal here points down from them — waiver with
no CFR, no relist, no amici, no alleged split, unpublished decision below,
fact-bound state-law-entangled QP, long-conference distribution. Petitions in
this posture resolve as one-line denials at very high rates. I set P(grant,
including GVR) at **0.012** — slightly above the zero-relist floor to leave
room for a CFR-then-relist path (the Court retains some appetite for takings
cases) and for the small chance of a summary disposition. A GVR is
implausible: no pending merits case on this question that could intervene
before disposition, so the residual grant probability is nearly all plenary.
Expected timing: denial in the October 5, 2026 order list following the
long conference, or shortly after if a response is called for.

## Salience

`big_case_score` = 0.08: a single landowner's compensation claim against a
small municipality, presenting a narrow procedural/preclusion question. Even
if granted it would be a low-profile procedural takings case, far from the
front pages.

## Degradations

The corpus query sidecar (`fedcourts query` via the local corpus service)
was unreachable (connection timeout on two attempts), so no similar-prior
retrieval from the corpus informed this prediction; base rates come from the
committed `metrics/statpack.md`/`statpack.json`. The statpack build in the
repo does not include the "Segment base rate by salience band" table the
prompt points to, so I anchored on the per-Term, fee-class, circuit, relist,
and CVSG cuts instead. CourtListener MCP was available and used lightly
(forward mode); the loss of corpus priors degrades but does not block the
cell.
