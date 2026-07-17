# Utah v. Mullins, No. 25-1115 — cert disposition prediction

**Prediction: denied. P(grant, GVR included) = 0.07.**

## The case

Utah (through its Solicitor General) petitions from a 3–2 decision of the Utah
Supreme Court (2025 UT 57, amended Nov. 20, 2025; rehearing denied Dec. 5,
2025) vacating Morris Mullins's juvenile life-without-parole (JLWOP) sentence
for a 2001 aggravated murder committed weeks before his 18th birthday. The
question presented: whether a sentencing court may impose JLWOP even if it
finds (or suggests) the juvenile is not permanently incorrigible — i.e., how to
reconcile *Miller v. Alabama* (2012), *Montgomery v. Louisiana* (2016), and
*Jones v. Mississippi* (2021). The Utah majority read the trilogy to bar JLWOP
for corrigible juveniles and vacated because the sentencing judge's 2002 remark
that Mullins would "have a chance to change" may have been an implicit
corrigibility finding; the dissent read *Jones* to require only a discretionary
proceeding that considers youth. Docketed March 24, 2026; BIO filed June 22,
2026; distributed July 8, 2026 for the September 28, 2026 (long) conference.
Paid petition, Term 2025 (per the snapshot metadata).

## Factors favoring a grant

- **State as petitioner, represented by its SG, from a state high court that
  ruled for a criminal defendant on federal constitutional grounds** — a
  classically grant-friendly configuration; the Court polices state-court
  over-readings of federal constitutional floors.
- **A genuine, acknowledged doctrinal tension.** The petition documents a real
  split-in-description: a minority camp (Utah majority, Maryland in *Malvo*,
  North Carolina in *Kelliher*, Michigan, Alaska Ct. App., pre-*Jones* Second
  Circuit and Wyoming) treats transient immaturity as a substantive Eighth
  Amendment bar, while a larger camp (Third Circuit in *Grant*, Ninth Circuit
  in *Briones*, Arizona, Illinois, Pennsylvania, Mississippi, etc.) reads
  *Jones* as requiring only discretionary consideration of youth. The Seventh
  Circuit (*Walker v. Cromwell*, 2025) said outright the law "simply is not
  clear." Several current justices have signaled interest in cleaning up
  *Montgomery*.
- Petition was drafted to invite either plenary review or outright reversal;
  a 3–2 division below with fully developed dueling opinions is a decent
  percolation vehicle in the abstract.

## Factors against a grant (these dominate)

1. **Finality/jurisdiction under 28 U.S.C. § 1257.** The Utah Supreme Court
   vacated the sentence and remanded for resentencing; under *Berman*, the
   sentence is the judgment, so there is arguably no final judgment to review.
   The BIO leads with this, argues none of the four *Cox Broadcasting*
   exceptions applies (the sentencing court may reimpose LWOP; the State can
   seek review after resentencing), and notes the petition never addresses
   finality. Interlocutory posture alone kills most criminal cert petitions
   (*Florida v. Thomas*).
2. **An unchallenged alternative holding.** On rehearing the Utah court added
   a second ground: the sentencing court "misapprehended its constitutional
   obligation to properly consider Mullins's youth" (appearing to leave youth
   to the parole board). The petition challenges only the corrigibility
   holding, so even a reversal on the QP arguably would not change the
   judgment — an advisory-opinion problem the BIO exploits effectively.
3. **A muddy factual record.** There is no affirmative corrigibility finding —
   only "ambiguous comments" from a pre-*Miller* 2002 sentencing that raised
   "significant concerns." The Court prefers a vehicle with an actual finding
   of corrigibility followed by JLWOP; the BIO plausibly recasts most of the
   claimed 16-jurisdiction contrary camp as cases where no corrigibility
   finding existed, leaving perhaps one square conflict (Maryland's *Malvo*,
   now mooted by statute).
4. **No amicus support — notably, no state coalition brief.** State cert
   petitions the Court grants almost always draw a multistate amicus; zero
   states supported Utah here (per the BIO, unrebutted on the snapshot docket
   through July 16).
5. **Low practical stakes.** Utah banned JLWOP prospectively in 2016; only one
   other Utah prisoner serves JLWOP; Mullins faces a consecutive Arizona life
   sentence regardless; nationally, over 90% of Montgomery-eligible prisoners
   have already been resentenced and 28+ states bar JLWOP. The post-*Jones*
   cleanup issue arises rarely and is shrinking.
6. **Revealed behavior.** The Court has consistently denied post-*Jones*
   cleanup petitions (e.g., cert denied in *Kelliher*-type cases) despite the
   acknowledged confusion.
7. **No relist signal yet.** First distribution, to the long conference. In
   the corpus, petitions resolved with zero relists grant at ~0.8%; the grant
   path here requires at least relists first.

## Calibration

Statpack anchors (live/historical slice, denial-reweighted): modern
discretionary-cert grant rate ~2.5–3.3% per recent Terms; paid petitions run
higher than the blended rate; no CVSG (CVSG cases grant at ~27%, absent here);
relist count currently 0. Starting from a paid-state-petitioner prior well
above the ~3% baseline (the state-petitioner/SG configuration and a colorable
split would ordinarily support ~15%), I discount hard for the finality defect,
the unchallenged alternative holding, the ambiguous record, and zero state
amici — each independently a common denial reason, and here they stack. A GVR
is implausible (no intervening decision to GVR against). There remains a
modest tail in which the Court relists in the fall, some justices push to
summarily reverse or to grant despite the posture, or a dissent from denial
issues instead.

**P(grant incl. GVR) = 0.07; predicted disposition: denied** — most likely
after the September 28, 2026 conference or a short relist, plausibly with a
separate writing.

## Inputs used

Provisioned snapshot `record/snapshots/2026-07-16.json`; provisioned
`questions-presented.txt`, `petition.txt` (truncated at 154 pp. but including
the full argument and the Utah Supreme Court opinion's opening), and
`brief-in-opposition.txt` (complete, 28 pp.); `metrics/statpack.md` base
rates. Mode: `forward` (pending case; conference not yet held). No
outcome-revealing material was encountered; corpus `fedcourts query` calls
returned no rows (see `retrieval.md`).
