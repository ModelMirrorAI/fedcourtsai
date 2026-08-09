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
artifact exists: the vocabulary, the reference set, the labeling prompt
(`.github/prompts/qp-topic-label.md`), the extract and measurement commands
(`fedcourts qp-corpus` / `fedcourts qp-topics`), the shadow rules
(`fedcourtsai.pipeline.qp_topics`), and the run mode that dispatches the labeler
(`run-analytics`'s `qp-topic-label`, which lands `data/qp-topics/qp-topics.json`
as a reviewed PR — see `docs/pipeline.md`). The cut is what remains: no topic
distribution is published, and none may be until the denial- and GVR-stratified
supplement block below exists and is measured.

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
mass, and no reference text yet exercises it.

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
(front matter, a dot-leader table of contents, a parties list captured by the
extractor — a failure mode the current extractor guards against, so stored
pre-guard texts are its main source) and *no cognizable question present* —
coherent text, typically pro se, in which no doctrinal question can be made
out even though subject-flavored words appear. It is never "hard to label": a
labeler who can name the subject of an actual question must pick one.

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

The reference set records **primaries only**: secondary and vehicle are
declared but unmeasured in v0 — the GVR stratum whose distortion the vehicle
flag exists to prevent has zero reference examples — so neither may appear in
any published cut until a reference block exercises them.

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
shadow rules are a re-derivation, not the originals: against the committed
set they fire on 36 of 189, all in agreement, and
`fedcourtsai.pipeline.qp_topics` carries their per-rule table.

Those four rules' declared role is a **shadow check only**: they publish
nothing and pre-empt nothing; their disagreement rate with the agent labeler
lands in the run summary as a standing regression trip-wire, so a drifting
labeler shows up as a moving disagreement rate before it shows up anywhere
else.

## The reference set

`data/qp-topics/qp-topic-reference.json` — labels for 189 cases, assigned by
reading the stored `questions-presented` texts under this document's rules
(text-only, primaries only), recorded against the Court's docket numbers and
joined to canonical case ids. The rater was a single agent session; there has
been no blind second pass and no adjudication.

**The selection frame, disclosed in full.** The set is not a sample of the
QP-bearing population: it contains **every QP-bearing granted petition (149 of
149)**, 40 of 855 QP-bearing denials, and none of the 87 GVR or 83 dismissed
QP-bearing rows; 147 paid / 42 IFP against a QP-bearing population of 725 /
462. Composition measured against corpus pointer `0efacfd9…` (2026-08-08).
Three consequences bind every use of the set:

- **Agreement measured on this set certifies the grant stream only.** The
  denial/IFP stream that dominates any denial-reweighted published cut is
  essentially unmeasured until a denial- and GVR-stratified supplement block
  is added — and no topic cut may be published before that block exists and
  is measured.
- **Membership is an outcome oracle.** Because every QP-bearing grant is in
  the file, presence of a case in it predicts grant and absence predicts
  non-grant within the QP-bearing population as of the frame date. The file is
  committed, so it is in every cell's checkout: for that reason **no predict
  or evaluate cell may read anything under `data/qp-topics/`** — the cell
  prompts state the prohibition, and any read of the path in a cell's logged
  tool calls is a flaggable leakage event on audit. The cell workflows also
  delete the directory before an agent starts, so in a cell's working tree
  there is nothing to read. The labeling run does the same in the one place a
  read would be self-defeating rather than leaking: it moves the directory out
  for the duration of its agent step and restores it from the commit before
  measuring, because agreement with a file the labeler copied from is agreement
  with nothing.
- **The set enumerates ingested-but-unpublished dockets, deliberately.** 188
  of the 189 case ids have no directory under `data/cases`, so this artifact
  is a stated exception to the boundary that committed surfaces do not
  enumerate the ingested corpus (`docs/security.md`). What it discloses is
  identity-level: because the frame above is disclosed, a reader learns
  exactly which dockets are the QP-bearing grants — a complete enumeration of
  a subpopulation, not a sample. That is accepted because the subpopulation
  is maximally public (granted SCOTUS petitions, named on the Court's own
  site) and no QP text is republished; the extent-by-counts the coverage
  caveat also carries is the posture the docket pack already publishes. The
  exception is accepted for **exactly two committed artifacts** — this set, and
  the labeler's per-case labels file `data/qp-topics/qp-topics.json`, which a
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
  file enumerates the whole QP-bearing population, the difference between the
  two committed files is, by construction, the QP-bearing **non-grants** — the
  labels file supplies the frame this set's "absence predicts non-grant"
  inference previously had to range over. That is accepted on the same ground as
  the first: cert outcomes are published on the Court's own order lists, so what
  the pair reconstructs is a public fact in a more convenient shape, and no QP
  text is republished by either. What it is *not* is a licence to relax the cell
  boundary — which is why the predict and evaluate prompts prohibit the whole
  `data/qp-topics/` **path** rather than the reference set by name, and why that
  path prohibition is what has to hold as artifacts are added under it.

  **One non-committed channel is in scope too, because the boundary is about
  disclosure and not about git.** The labeling run's extract (`fedcourts
  qp-corpus`) is both things no committed surface carries — the stored petition
  text and the full enumeration of the QP-bearing ingested population — and the
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
  command refuses to write anywhere inside the checkout: the run artifact is the
  one sanctioned copy, and it is meant to be short-lived. Encrypting it under a
  run-scoped key, or collapsing the two jobs behind step-scoped credentials so
  the extract never leaves the runner, would close the channel outright; both
  cost more than the exposure is currently judged to be worth, and that judgment
  is the thing to revisit if the extract ever carries more than this.

**What a measurement is.** With one rater, the quantity any labeler run
produces against this set is *agreement with the v0 reference rater*, not
accuracy — reference error and labeler error cannot be separated, least of all
on the boundary labels. The reference rater was itself an agent session, so
agreement with an agent labeler of the same model family partly measures
shared convention; that caveat travels with any reported number. The recorded
instruments are: overall agreement with `n=`, per-label agreement with `n=`
(floor-gated, below), and the 3×3 confusion matrix on the
`constitutional-rights` / `criminal-law` / `civil-procedure` triangle (78 of
189 entries), written into the labels artifact alongside the labels
themselves. The honest ceiling instrument, recommended before the first cut
publishes, is a blind re-label of the triangle cases reported as a
self-agreement rate. The publication gate: a labeler whose overall agreement
on the measured stream is below **80%**, which labeled fewer than **90%** of
the reference cases in its extract, or whose triangle confusion matrix is
unpublished, publishes nothing — `fedcourts qp-topics` enforces the first two
mechanically and refuses to write.

**The bounds that matter** are boundary agreements, not the overall rate: the
triangle (n=78), criminal vs habeas (n=47 combined), criminal vs immigration
(n=44 combined, with the §1325/§1326 rule unexercised), and the
`unclassifiable` rate (n=4), which sets the denominator of every published
share.

**Per-label support floor.** Nine of sixteen labels have fewer than 10
reference examples (`first-amendment` 9, `habeas-and-postconviction` 8,
`employment-and-antidiscrimination` 7, `immigration` 5,
`environment-energy-and-property` 5, `intellectual-property` 4,
`unclassifiable` 4, `election-law` 3, `tax` 2). Per-label agreement under the
floor is **unmeasured in v0**: it is reported as a raw count, never as a rate.

**Contamination.** Three near-duplicate pairs sit inside the set (two in
`firearms`, one in `sovereignty-and-foreign-relations`) — the same
coordinated-filing clusters the coverage caveat names, present in the baseline
too.

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
  open mid-sentence when the heading sat on the prior page. `unclassifiable`
  absorbs the worst of this and is published, never dropped.

The caveat travels **inline**: every published share renders with a one-line
scope string beside it, of the form
`(QP-bearing rows only — <pct> of walked Term-<T> rows; grant-enriched;
primaries only; not docket-representative)`, with the numbers of the corpus
it was computed from. A section-level caveat does not survive a quoted
number; the scope string does.
