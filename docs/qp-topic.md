# QP topics (`qp-topic-v0`)

A subject-matter vocabulary for the **questions presented** in SCOTUS
petitions: what a petition *asks about*, labeled from the stored
`questions-presented` text alone. This is the "claim taxonomy" that
`metrics/docket.md` and `metrics/README.md` reserve the phrase for — a
classification of subjects — and it is deliberately not part of
`docs/outcome-decomposition.md`, which decomposes a predicted *outcome* into
scoreable propositions. The two share nothing but the word "claim"; a topic
label never resolves against a docket and is never scored. Nor is a topic the
corpus's `topic` column (`fedcourts query --topic`), which carries an upstream
nature-of-suit string on circuit rows only — SCOTUS rows have none, which is
why this vocabulary exists.

Four facts keep this a free-moving vocabulary rather than a pre-registration
surface:

- **Nothing frozen depends on it.** No frozen process digest reads a topic
  label, and no metric that scores a predictor conditions on one.
- **No cell prompt asks for it.** Topic labels are the business of an
  analytics labeler, not of predict or evaluate cells — the cell prompts
  forbid cells from reading `data/qp-topics/` at all (see the reference-set
  section). The process digest hashes prompt bytes plus the resolved actor
  config, so this document and its labels can change without moving any
  digest.
- **It commits a predictor to nothing.** A published topic distribution is a
  corpus description, not a prediction claim.
- **Supersession is the plan.** A boundary that proves wrong in use is fixed in
  `qp-topic-v1`, not patched silently; the version token on the set is what
  makes every published cut and measured agreement citable after the fact.

The trip-wire: the moment a *cell* prompt asks an agent for a topic label, that
prompt's digest moves and this stops being a free-moving vocabulary — that is a
version bump and its own review, not an edit to this document.

Of the machinery this document contracts for, everything up to the labels
artifact exists: the vocabulary, the reference set (both blocks), the labeling
prompt (`.github/prompts/qp-topic-label.md`), the extract and measurement
commands (`fedcourts qp-corpus` / `fedcourts qp-topics`), the shadow rules
(`fedcourtsai.pipeline.qp_topics`), the run mode that dispatches the labeler
(`run-analytics`'s `qp-topic-label`, which lands `data/qp-topics/qp-topics.json`
as a reviewed PR — see `docs/pipeline.md`), and the court-facing docket pack's
topic section, which renders — always with the inline scope string below, and
only from a gate-passing labels artifact — in place of the gap bullet that
names the missing distribution until then. No labels artifact has been
produced, so no distribution is published. The publication bar the reference
section sets is **not** enforced by the cut's code and cannot be: whether a
labeler has been measured against the supplement block is a property of the
labeling run's review, which the labels artifact does not record — so
producing and merging the first artifact is the decision that publishes the
first cut.

## The register

Sixteen labels: fifteen subjects plus `unclassifiable`. Every question
presented takes **exactly one primary label**. Boundaries are stated as what a
label is *not*, because in practice the errors live on the boundaries, not in
the centers.

| Label | Covers |
| --- | --- |
| `criminal-law` | Substantive criminal law, sentencing, criminal procedure at trial and direct appeal |
| `civil-procedure` | Jurisdiction, justiciability, standing, preclusion, remedies procedure, federal-courts doctrine |
| `constitutional-rights` | Constitutional rights and their remedies outside the First and Second Amendments |
| `business-and-financial-regulation` | Bankruptcy, arbitration/FAA, securities, antitrust, RICO, commercial regulation |
| `firearms` | Second Amendment challenges **and** firearms regulation |
| `habeas-and-postconviction` | §2254/§2255, AEDPA, certificates of appealability, collateral review |
| `administrative-law-and-benefit-programs` | Agency power, review procedure, deference, public benefit programs |
| `first-amendment` | Speech, press, assembly, and both religion clauses |
| `employment-and-antidiscrimination` | Title VII/IX, ADA, FHA, FLSA, NLRA, ERISA, FELA, public employment |
| `intellectual-property` | Patent, copyright, trademark, trade secret |
| `sovereignty-and-foreign-relations` | Foreign, state, and tribal sovereignty; Indian law |
| `environment-energy-and-property` | Environmental and energy regulation, land use, property schemes |
| `election-law` | Ballots, registration, districting, campaign finance, candidate qualification |
| `tax` | Federal and state taxation |
| `immigration` | Immigration status, removal, relief, and detention |
| `unclassifiable` | No subject or no cognizable question present in the text |

**`criminal-law`** is not collateral review: a question whose own ask or
posture names §2254, §2255, AEDPA, a certificate of appealability, or habeas
belongs to `habeas-and-postconviction` — the collateral vehicle in the
question's posture governs even when the underlying claim is a trial right. A
marker that appears only inside a *discussed precedent* does not count (a
question about the *Heck* bar quoting "habeas relief" from case law is not a
habeas question), and a Strickland ineffective-assistance claim naming no
collateral marker stays here. Illegal-entry and illegal-reentry prosecutions
(§1325/§1326) are criminal law, not `immigration`; the boundary shifts real
mass, and one agreed reference text — a §1326 reentry prosecution — exercises
it.

**`civil-procedure`** is not sovereign immunity as such, and not
agency-specific review procedure (which belongs to
`administrative-law-and-benefit-programs`). Justiciability beats subject when
justiciability is what is asked: a standing question arising in an election
case is `civil-procedure`, not `election-law`. Federal sovereign immunity is
deliberately excluded from `sovereignty-and-foreign-relations`; a federal
sovereign-immunity question is almost always an ask about jurisdiction or
remedies, so it lands here unless its underlying subject is what the question
turns on.

**`constitutional-rights`** is not the First or Second Amendment, which carry
their own labels. Where a §1983 suit carries a named right, label the right;
use this label when the question is the remedy or the immunity itself —
qualified immunity, Bivens, the scope of §1983. A takings question framed on
the Fifth Amendment lands here too, tax-foreclosure takings included.

**`business-and-financial-regulation`** is not tax. A preemption question goes
to the regulated subject, not to preemption doctrine.

**`firearms`** includes firearms *regulation* — licensing, dealer rules,
manufacture and classification — not only Second Amendment challenges. It is
not the sentencing consequence of a firearms conviction, which is
`criminal-law`.

**`habeas-and-postconviction`** is not a prisoner conditions-of-confinement
suit, which is `constitutional-rights` (or `civil-procedure` when the question
is procedural).

**`administrative-law-and-benefit-programs`** is not the substance of what the
agency regulates — an EPA question about agency power is administrative law; an
EPA question about the Clean Water Act's reach is
`environment-energy-and-property`.

**`first-amendment`** includes both religion clauses. Campaign finance framed
as election administration is `election-law`.

**`sovereignty-and-foreign-relations`** is not federal sovereign immunity and
not qualified or judicial immunity.

**`environment-energy-and-property`** keeps the takings questions embedded in
a land-use or regulatory scheme, where the scheme's reach is what is asked;
the Fifth-Amendment-framed remainder goes to `constitutional-rights` (see
above).

**`election-law`** is not standing doctrine reached in an election case.

**`tax`** is not a tax-foreclosure taking, which follows the takings routing.

**`unclassifiable`** covers two cases and only these: *no subject present*
(front matter, a table of contents in either alignment, a parties list captured
by the extractor — a failure mode the current extractor guards against, so its
main source is stored texts that predate a guard and stay as they are until
`fedcourts backfill-questions-presented` re-derives them) and *no cognizable
question present* — coherent text, typically pro se, in which no doctrinal question can
be made out even though subject-flavored words appear. It is never "hard to
label": a labeler who can name the subject of an actual question must pick one.

## Structure: primary, secondary, vehicle

- **Primary** — mandatory, single. Every published count sums over primaries
  only, so a distribution can never total more than 100%.
- **Secondary** — optional, single, advisory. It never enters a published
  count. A *facet chain* — several questions elaborating one subject — gets no
  secondary (three nondelegation questions are one administrative-law
  question; "are contract rights property" as an element of a fraud theory is
  one `criminal-law` question). A *smuggled question* under a different label
  gets one: two §922(g) questions bracketing a Guidelines-commentary question
  is `firearms` with a `criminal-law` secondary.
- **Vehicle** — boolean. A petition asking for a GVR in light of a named
  decision is labeled by the *underlying subject* and flagged as a vehicle;
  without the flag, the GVR stratum manufactures a phantom procedure topic.

The reference set records **primaries only**: secondary and vehicle stay out
of every published cut. The GVR reference block now exercises the vehicle
flag and found it structurally near-empty under the text-only contract (see
the reference-set section), so the bar stands on evidence rather than
absence: nothing a v0 cut publishes may lean on secondary or vehicle.

The adjacent-pair tie-break is the **remedy-versus-right rule**: label what the
question *asks*, not what the case is about. A question about the *Heck* bar's
application to a First Amendment §1983 suit asks about the remedy →
`constitutional-rights` with a `first-amendment` secondary. A question about
the ripeness of a donor-disclosure challenge asks about justiciability →
`civil-procedure` with a `first-amendment` secondary.

## The labeler contract

A `qp-topic-v0` labeler is **text-only**: it reads the stored
`questions-presented` text and nothing else — no docket context, no case name
lookup, no outcome. That is what keeps labels reproducible and replay-safe at
the label level (a topic assigned from text that predates the decision can
never encode the decision).

**Labeling authority is the agent labeler alone.** Deterministic
statute/keyword rules are the wrong instrument for this vocabulary's hardest
labels: the labels are defined by what a question *asks*, the two largest
error sinks (`constitutional-rights`, `civil-procedure`) have no distinctive
citation to key on, and keywords actively mislead — background prose fires
rules, cited statutes belong to different subjects than the question, and
case-name mentions contaminate ("habeas relief" inside a *Heck* discussion).

Measured once at declaration time, against the reference set *as first
labeled* — two entries have since been relabeled under the collateral-marker
rule, and the landed shadow rules record their own measurement in the labels
artifact, which supersedes these declaration figures: a rule set tuned **on
that same set** fired on 145 of 189 texts and was right on 117 —
80.7% (117/145) where it fired, 61.9% (117/189) end to end. The four most
precise rules, **selected post hoc from the same data** (`firearms`,
`intellectual-property`, `tax`, `employment-and-antidiscrimination`), jointly
fired on 39 with 36 correct (92.3%). All of these are in-sample,
post-selection figures — bounds on out-of-sample behaviour, not estimates of
it — and three of the four precise rules rest on ≤7 reference positives
(`tax`: 2), where a single error moves the rate by tens of points. The landed
shadow rules are a re-derivation, not the originals: against the founding
block they fire on 36 of 189, all in agreement, and
`fedcourtsai.pipeline.qp_topics` carries their per-rule table.

**The out-of-sample check exists, and it is sobering.** The reference
supplement (164 texts the rules were never tuned on) is a true out-of-sample
set for them: there the four rules fire on 32 and agree with the reference on
23 — **71.9%**, against the 100% their tuning set shows. Per rule: `firearms`
12/13 (holds), `employment-and-antidiscrimination` 9/13,
`intellectual-property` 1/3, `tax` 1/3 — the module docstring's predicted
failure modes (`taxpayer` firing on standing questions, trademark vocabulary
on speech challenges) are exactly what realized. This does not change the
rules' role — a trip-wire needs stability, not precision — but it retires any
reading of the in-sample table as a precision claim.

Those four rules' declared role is a **shadow check only**: they publish
nothing and pre-empt nothing; their disagreement rate with the agent labeler
lands in the run summary as a standing regression trip-wire, so a drifting
labeler shows up as a moving disagreement rate before it shows up anywhere
else.

## The reference set

`data/qp-topics/qp-topic-reference.json` — labels for 353 cases, assigned by
reading the stored `questions-presented` texts under this document's rules
(text-only, primaries only), recorded against the Court's docket numbers and
joined to canonical case ids. The labels are therefore keyed to the text as
stored when they were assigned: a run of `fedcourts
backfill-questions-presented --apply` rewrites some of those texts, so the
entries whose text it changes are re-read before the set backs another
measurement — an entry labeled off a fragment is not evidence about a labeler
that now sees the question. The set is two blocks with different rater
processes, both disclosed: the **founding block** (189 cases, a single agent
session, no second pass) and the **stratified supplement** (164 cases,
labeled by **two independent blind agent raters**, whose 13 primary
disagreements were adjudicated case by case under this document's rules,
with the rationale recorded in the introducing change).

The supplement's draw is deterministic and its one defect is disclosed
rather than hidden: an every-k-th systematic sample in `case_id` order per
disposition stratum (inclusion 100/815 denied, 20/83 dismissed), where the
first GVR draw used floor spacing and so truncated the newest 28 of 87 GVR
rows out of eligibility — an exclusion that was IFP-heavy — and a corrective
second draw took every 2nd of that tail (14 rows, 10 IFP), bringing GVR
inclusion to 44/87 with the stratum's streams restored.

**The selection frame, disclosed in full.** The set is not a sample of the
QP-bearing population: it contains **every QP-bearing granted petition (149 of
149)**, 140 of 855 QP-bearing denials, 44 of 87 GVR and 20 of 83 dismissed
rows (13 QP-bearing rows were undisposed at the frame date and outside every
stratum); 248 paid / 105 IFP against a QP-bearing population of 725 / 462.
Founding-block composition measured against corpus pointer `0efacfd9…`
(2026-08-08); the supplement was drawn against the same pointer.
Three consequences bind every use of the set:

- **Agreement is measured per stream, and the bar on publishing stands.** The
  founding block covers the grant stream; the supplement is the denial- and
  GVR-stratified block a published cut's quality was conditioned on. The block
  now **exists**; it is not yet **measured** — no labeler has been scored
  against it — so the publication prerequisite still holds until the first
  labeler run is. The committed artifact records a pooled rate only; the
  per-stream split is derived at measurement review by joining the reference
  to the corpus's dispositions (deliberately not carried in this file, where a
  stratum tag would sharpen the oracle below), and a labeler that fails the
  denial stream fails review regardless of the pooled gate. The dismissed
  stratum is thin (n=20) and the set's IFP share runs below the population's.
  The set carries **no sampling weights** — its strata are disproportionate by
  design — so it measures labeler agreement and must never be reweighted into
  a population topic distribution.
- **Membership is an outcome oracle.** Every QP-bearing grant is in the file,
  so presence still shifts the odds toward grant (149 of 353 members are
  grants, against ~13% of the QP-bearing population) and absence still implies
  non-grant as of the frame date — and the weakening the supplement brings is
  a fact about the *working tree only*, since the two-block history is one
  `git show` away and differencing revisions reconstructs each block's
  disposition mix. The file is committed, so it is in every cell's checkout:
  for that reason **no predict or evaluate cell may read anything under
  `data/qp-topics/`** — the cell prompts state the prohibition, any read of
  the path in a cell's logged tool calls is a flaggable leakage event on
  audit, and the cell workflows delete the directory before an agent starts,
  so in a cell's working tree there is nothing to read. The labeling run does
  the same in the one place a read would be self-defeating rather than
  leaking: it moves the directory out for the duration of its agent step and
  restores it from the commit before measuring, because agreement with a file
  the labeler copied from is agreement with nothing.
- **The set enumerates ingested-but-unpublished dockets, deliberately.** The
  great majority of the 353 case ids have no directory under `data/cases` — a
  small published minority does, and that share moves with every predict round
  — so this artifact
  is a stated exception to the boundary that committed surfaces do not
  enumerate the ingested corpus (`docs/security.md`). A growing published share
  does not weaken the exception or widen it: a published case already discloses
  its own identity, so what this set adds is the unpublished remainder, and it
  adds the same thing at any share. What it discloses is
  identity-level: every QP-bearing grant is a member (a complete enumeration
  of that subpopulation, recoverable from history even though the supplement
  mixes the working-tree file). That is accepted because the dockets named
  are maximally public (SCOTUS petitions, named on the Court's own site) and
  no QP text is republished; the extent-by-counts the coverage caveat also
  carries is the posture the docket pack already publishes. The exception is
  accepted for **exactly two committed artifacts** — this set, and the
  labeler's per-case labels file `data/qp-topics/qp-topics.json`, which a
  labeling run commits in full so a reviewer can read every label the measured
  block reports over. Neither is precedent for a third: any further committed
  surface that enumerates the ingested corpus is argued here, before it exists.

  **What the second artifact adds, stated plainly.** Its own membership is
  **fetch-conditioned** — a case is in it because a questions-presented
  document is stored for it — which is weaker than this set's
  outcome-conditioned membership but not innocent: QP-bearing rows are
  grant-enriched by roughly an order of magnitude (see the coverage caveat), so
  presence is already a weak grant signal. The sharper effect is **joint**, and
  it is the reason to say so here rather than to argue each file alone. Because
  this set contains *every* QP-bearing grant as of its frame date and the labels
  file enumerates the QP-bearing rows of the labeling frame, the difference
  between the two committed files is, by construction, that frame's QP-bearing
  **non-grants** — the labels file supplies the frame this set's "absence
  predicts non-grant" inference previously had to range over. The extract's
  frame and row ceiling bound what the pair reconstructs; they do not change
  the character of the inference. That is accepted on the same ground as
  the first: cert outcomes are published on the Court's own order lists, so what
  the pair reconstructs is a public fact in a more convenient shape, and no QP
  text is republished by either. What it is *not* is a licence to relax the cell
  boundary — which is why the predict and evaluate prompts prohibit the whole
  `data/qp-topics/` **path** rather than the reference set by name, and why that
  path prohibition is what has to hold as artifacts are added under it.

  **One non-committed channel — carrying two artifacts — is in scope too,
  because the boundary is about disclosure and not about git.** The labeling run's extract (`fedcourts
  qp-corpus`) is both things no committed surface carries — the stored petition
  text and an enumeration of the QP-bearing ingested population, bounded by the
  labeling scope and by the extract ceiling rather than running to the whole of
  it — and the
  run mode passes it between its two jobs as a GitHub Actions artifact. This
  repository is public, so that artifact is downloadable by any logged-in user
  for its retention window, which the workflow sets to the shortest GitHub
  offers (one day) and which fires on every dispatch, including runs whose gate
  fails and which open no PR. It is accepted on two grounds and no others: the
  population it enumerates is the one the committed pair above already
  discloses, and the text is petition PDFs fetched from supremecourt.gov —
  public records of the Court, outside the CC BY-ND term that
  `docs/data-sources.md` applies to CourtListener's own content and that keeps
  the rest of the corpus access-gated. It is *not* accepted as a general route
  for corpus content into Actions artifacts, and it is the reason the extract
  command refuses to write anywhere inside the checkout: the run artifacts are the
  sanctioned copies, and they are meant to be short-lived. Encrypting it under a
  run-scoped key, or collapsing the two jobs behind step-scoped credentials so
  the extract never leaves the runner, would close the channel outright; both
  cost more than the exposure is currently judged to be worth, and that judgment
  is the thing to revisit if the extract ever carries more than this.

  The labeler's **turn-by-turn transcript** (`qp-label-transcript`) rides the
  same channel under the same terms, because it is the same bytes one step
  later: the agent reads the extract, so its transcript necessarily embeds the
  QP text, and what it adds is the agent's own turns — the kickoff prompt, its
  reasoning, and every tool call's input and output, which is exactly why the
  scan below exists. It exists
  because a run that reports success while writing no labels is undiagnosable
  from the summary block alone, and each re-run costs real model spend — so
  the transcript is uploaded on every path the action survives (a
  gate-refusing run is as diagnostic as a no-output one; a hard step-timeout
  kill is the one path that leaves no file to capture), only after a
  secret scan over the
  transcript passes (a hit withholds the artifact and says so — the collect
  job's withhold-and-continue posture, minus its trigger-issue report, since a
  dispatch mode has none; the transcript surface suppresses exactly one rule,
  the generic entropy one, whose conviction of the transcript's own tool ids
  would otherwise withhold every real file — literal containment of the one
  reachable credential, the structured credential shapes, and the
  keyword-assignment rule all stay on), and under the same one-day
  retention as the
  extract, for the
  reasons argued above rather than a second, looser rule for the same
  disclosure class.

  That scan holds the engine API key, so what it *imports* is as much a part of
  the gate as what it reads. `setup-python-env` installs this project editable,
  which would put the labeler's own tree — and its gitignored venv — on the
  scanner's import path, where the tree-pristine assertion cannot follow: that
  assertion compares tracked files, and an untracked module or a `.pth`
  dropped into the venv is invisible to it. So the scanner is built after the
  agent exits, from a second checkout of this run's commit fetched from GitHub
  into a path of its own — cleared first, since a `.git` left there would be
  reused rather than replaced, and then verified to be this commit and nothing
  else, ignored files included — installed into a venv inside that fresh tree,
  resolved through a package cache inside it, and built on a managed
  interpreter downloaded into it. No part of the scanner's source or its
  site-packages comes from the labeler's tree, its venv, its object store, or
  the caches uv keeps in the runner user's home. The import path is not the
  only way into a process, so two more levers close with it: git reads no
  global or system config for that clone (`core.hooksPath` and
  `init.templateDir` are code, and both fire during a checkout), and the
  install and the scan both unset `PYTHONPATH`, `LD_PRELOAD` and their kin —
  and run Python with `-P`, since `-m` would otherwise put the working
  directory first on the import path — because the runner applies every
  earlier step's `$GITHUB_ENV` writes to later ones and the labeling step's
  subprocesses can append there. The toolchain that builds the scanner is held
  the same way: `uv` against a digest recorded before the agent ran, and PATH
  pinned to the root-owned directories so `git` is the image's. A tampered
  tree therefore keeps its transcript — the capture exists to diagnose exactly
  that run, and the scan does not have to trust the tree. The pristine
  assertion gates the measure step instead, because a rigged *number* is a
  different threat from a stolen key. What the isolation still trusts, and why
  that set is the bound rather than the mechanism, is stated as an invariant in
  [SECURITY.md](../SECURITY.md).

  Four steps stand between the transcript and the artifact — clear the scanner
  path, check the scanner out afresh, install it into its own venv, scan — and
  all four are `continue-on-error`, so a scanner that fails to build costs the
  run its transcript rather than its labels. Each step is `if:`-gated on its
  predecessor's outcome, so a failed build **skips** the scan rather than
  running whatever sits at the scanner path; the upload is gated in turn on the
  scan having succeeded, so the artifact is withheld silently, via the skip —
  read the step outcomes on the run, not the summary, to tell a withheld
  transcript from one that was never asked for.

**What a measurement is.** The quantity any labeler run produces against this
set is *agreement with the reference raters*, not accuracy — reference error
and labeler error cannot be separated, least of all on the boundary labels.
Every reference rater was an agent session, so agreement with an agent
labeler of the same model family partly measures shared convention; that
caveat travels with any reported number. The recorded instruments are:
overall agreement with `n=`, per-label agreement with `n=` (floor-gated,
below), and the 3×3 confusion matrix on the
`constitutional-rights` / `criminal-law` / `civil-procedure` triangle (172 of
353 entries), written into the labels artifact alongside the labels
themselves.

**Reliability is measured on the supplement, and only there.** Across both
supplement draws, two independent blind raters agreed on 151 of 164
primaries — **92.1%** (denied 91/100, GVR 43/44, dismissed 17/20), against a
largest-class floor of ~26% and chance agreement of ~13% on that mix. Read
it for what it is: the task's **pairwise reproducibility on the
denial/GVR/dismissed stream**, design-weighted by the sample (population-
weighted it is ~91.3%, and for a denial-dominated extract the applicable
figure is the 91.0% on n=100). It is *not* a ceiling on agreement with the
adjudicated reference: the adjudicated labels coincide with one rater's on
~98% of supplement rows, so an honest third labeler is *expected* to score
above the pairwise figure, and the founding block — 189 of the 353 entries —
has no measured reliability at all. Adjudication is disclosed beside the
number it shaped: 13 disagreements were resolved by the integrating session
that also authored these rules (same model family as both raters), 10 of the
13 to one rater's reading — a split n=13 cannot distinguish from chance and
is disclosed, not defended — and the adjudicator was **not blind to
disposition** (it saw stratum tags for the first 12, and the corrective GVR
draw is single-stratum by construction). The publication gate: a labeler
whose overall agreement
on the measured stream is below **80%**, which labeled fewer than **90%** of
the reference cases in its extract, or whose triangle confusion matrix is
unpublished, publishes nothing — `fedcourts qp-topics` enforces the first two
mechanically and refuses to write.

**The bounds that matter** are boundary agreements, not the overall rate: the
triangle (n=172), criminal vs habeas (n=95 combined), criminal vs immigration
(n=86 combined, the §1325/§1326 boundary exercised by exactly one text), and
the `unclassifiable` rate (n=14), which sets the denominator of every
published share.

**Per-label support floor.** Five of sixteen labels have fewer than 10
reference examples (`environment-energy-and-property` 6, `immigration` 5,
`intellectual-property` 5, `election-law` 5, `tax` 3). Per-label agreement
under the floor is **unmeasured in v0**: it is reported as a raw count, never
as a rate.

**The vehicle flag is structurally sparse under this contract.** Across the
44 GVR-disposed supplement texts, the raters flagged three vehicles — each
time both raters independently, each a hold-for-a-named-lead-case ask —
because a stored QP text is written before the disposition, so a text-only
labeler sees "vehicle" only when the petition itself asks for the hold. The
GVR-stratum correction the flag was declared for is therefore bounded near
7% of that stratum in v0; a cut must not lean on it.

**Contamination.** Six near-duplicate pairs in four clusters sit inside the
set (5-gram Jaccard ≥ 0.5): two founding-block pairs (`firearms`,
`sovereignty-and-foreign-relations`), one GVR supplement pair — so the GVR
agreement cell rests on 43 independent texts — and a `firearms` triple that
spans the two blocks. The same coordinated-filing clusters the coverage
caveat names, present in the baseline too.

Relabeling an entry is a judgment change and travels in its own reviewed
diff. The set exercises every label in the vocabulary, and
`tests/test_qp_topic_reference.py` pins that property, the canonical
serialization, and key uniqueness.

## The coverage caveat

Any published topic distribution must carry this scope, because QP presence in
the corpus is a **document-fetch artifact, not a sample**:

- Coverage is zero before Term 2023 and thin, uneven, and growing after:
  3.3% of walked Term-2023 rows (138/4,222), 10.0% of Term-2024 (384/3,858),
  16.1% of Term-2025 (665/4,135), measured at corpus pointer `0efacfd9…`
  (2026-08-08) — a fetch-state fact a later walk will change. Term-over-Term
  topic comparisons are unsafe.
- QP-bearing rows are **grant-enriched by roughly an order of magnitude**
  (the exact ratio varies by Term and by raw vs reweighted framing, and the
  newest Term's ratio is censored by still-pending petitions), and coverage
  is far higher on paid dockets than IFP. Denial-reweighting therefore shifts
  the observed mix toward the in-forma-pauperis stream and concentrates
  `criminal-law`, `firearms`, `constitutional-rights`, and `unclassifiable`.
- **The labeled rows are the QP-bearing part of one frame, and it is the
  published cut's own frame.** `qp-corpus` selects the live/historical slice's
  modern discretionary-cert petitions — the same frame the docket pack's topic
  section is computed over — so `kept` and `<N>` in the scope string are counts
  over one population rather than two, and no row inside the section's frame is
  unlabelable. The extract does **not** narrow to the predict-scope segment,
  which is the tempting narrowing and the wrong one; the reason is in *What one
  labeling run can hold* below, and it is a measurement-integrity reason rather
  than a statistical one.
- **No reweighting recovers the docket.** Topics exist only for QP-bearing
  rows, and QP presence is itself outcome- and stream-correlated, so a
  denial-reweighted topic share is still a share of *QP-bearing rows only* —
  the missingness is non-ignorable, and nothing in this repository turns the
  figure into a share of the docket.
- Coordinated filing campaigns (near-identical petitions filed in clusters)
  mean a naive share partly counts campaigns rather than subjects; a
  published cut says so, or publishes a companion de-duplicated on
  near-identical normalized QP text, stating the equivalence it used.
- Extraction is lossy at the edges: some cases with a stored petition yield
  no QP text, the extractor sometimes captures the wrong page, and a text can
  open mid-sentence when the heading sat on the prior page. A capture the
  extractor cannot vouch for is stored as an **empty** text, which `qp-corpus`
  skips, so it never reaches a labeler and never enters a denominator — read
  "QP-bearing" as text-bearing throughout. `unclassifiable` absorbs what does
  reach the labeler and is published, never dropped.

The caveat travels **inline**: every published share renders with a one-line
scope string beside it, of the form
`(QP-bearing rows only — <coverage>; grant-enriched; primaries only; not
docket-representative)`, with the numbers of the corpus it was computed from. A
section-level caveat does not survive a quoted number; the scope string does.

`<coverage>` is stated in the frame the cut is computed in, and the two frames
are not interchangeable. A **per-Term** cut states `<pct> of walked Term-<T>
rows` against that Term's serial census, the frame the coverage figures above
are quoted in. A **pooled** cut — the docket pack's, computed over the whole
modern discretionary-cert live slice — states `<n> of <N> ingested rows`:
counts, because a pooled percentage against a census that spans Terms of 0% and
16% coverage reads as a coverage level no Term has, and *ingested* rather than
*walked*, because the denial sampling puts the walked serial count several-fold
above the rows on hand. A pooled cut must also say that coverage is uneven
across Terms, since its own ratio cannot show it.

## What one labeling run can hold

The extract is **bounded by what a dispatch can finish, not by how many texts
exist**. A labeling run is a single headless turn inside one job, and
`qp-topics` writes nothing until the labels file holds exactly one line per
extract row — so a run that outlasts its cap leaves durable slices, full spend,
and no artifact. Partial progress is not partial coverage here; it is nothing.
The cap that bites is the **labeling step's**, set below the surrounding job's
so a runaway trips the step and still leaves a run to read; the ceiling is
derived from that one, since a bound sized against the outer cap would admit
exactly the extracts the inner one kills.

`qp-corpus` therefore enforces a ceiling (`LABEL_ROW_CEILING` in
`fedcourtsai.pipeline.qp_topics`) and refuses to write a larger extract,
printing the count and the scope it would have had to label. Its value is a
**declared budget, not an observed rate**: no labeling dispatch has completed,
so the pace behind it is unmeasured, and the first finished run is what should
re-derive it. That refusal is
the useful outcome, not a failure to route around: it costs the extract job
rather than the labeling one, and its count is what decides between a narrower
scope and a different design. The labeling prompt states its budget as
"whatever the extract holds" for the same reason — one number, in one place,
and no second copy to drift.

**Why the scope stops where it does, and not one clause further.** The obvious
next narrowing is the predict-scope segment — the population the salience gate
actually spends on — and it is barred, on measurement grounds. On a QP-bearing
population the only predict-scope rule that bites is the in-forma-pauperis
exclusion, while the reference set spans both fee streams — its split is in
*The reference set* above, and roughly three in ten of its entries are IFP.
A paid-only extract therefore caps reference coverage near seven tenths, under
the publication gate's floor, so no labeling run could ever publish. Carrying
the reference set back in to restore the floor is worse, not better: an IFP row
*inside* such an extract would be a certain reference-set member, fee class
rides in the `docket_number` every row carries, and reference membership
predicts a cert grant — which hands the labeler a membership probe for the very
set it is measured against, on the one vocabulary whose whole justification is
that it is text-only. The extract frame is wide because a narrower one leaks
the measurement. If a future scope genuinely needs the paid segment, the
reference set has to move into that frame first.

Two consequences worth stating plainly. The ceiling is not a lever: raising it
without raising the labeling step's cap buys a cancelled run rather than a
bigger artifact, and raising that cap means raising the job's too — the step
sits inside it deliberately — for a single agent turn measured in hours, which
is not a shape this repository runs. And if the scoped population outgrows the
ceiling, the
answer is a **deliberately partial cut** — a documented, reproducible subset
with its own selection rule and its own line in the scope string — never a
truncated one, because a prefix of `case_id` order is a selection on docket
number and would make the published mix a function of it.
