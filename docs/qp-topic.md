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

Of the machinery this document contracts for, the vocabulary, the reference set,
and the labeler machinery exist: the labeling prompt
(`.github/prompts/qp-topic-label.md`), the extract and measurement commands
(`fedcourts qp-corpus` / `fedcourts qp-topics`), and the shadow rules
(`fedcourtsai.pipeline.qp_topics`). No run mode dispatches the labeler, no labels
artifact has been produced, and no cut is published: those are declared here and
not yet built.

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

`data/qp-topics/qp-topic-reference.json` — labels for 339 cases, assigned by
reading the stored `questions-presented` texts under this document's rules
(text-only, primaries only), recorded against the Court's docket numbers and
joined to canonical case ids. The set is two blocks with different rater
processes, both disclosed: the **founding block** (189 cases, a single agent
session, no second pass) and the **stratified supplement** (150 cases — 100
denied, 30 GVR, 20 dismissed, drawn as a deterministic every-k-th systematic
sample in `case_id` order from the QP-bearing rows not already in the set —
labeled by **two independent blind agent raters**, whose 12 primary
disagreements were adjudicated case by case under this document's rules, with
the rationale recorded in the introducing change).

**The selection frame, disclosed in full.** The set is not a sample of the
QP-bearing population: it contains **every QP-bearing granted petition (149 of
149)**, 140 of 855 QP-bearing denials, 30 of 87 GVR and 20 of 83 dismissed
rows; 244 paid / 95 IFP against a QP-bearing population of 725 / 462.
Founding-block composition measured against corpus pointer `0efacfd9…`
(2026-08-08); the supplement was drawn against the same pointer.
Three consequences bind every use of the set:

- **Agreement is measured per stream, and both major streams are now
  covered.** The founding block certifies the grant stream; the supplement is
  the denial/GVR-stratified block that a published cut's quality was
  conditioned on, so the publication prerequisite it named is discharged. The
  dismissed stratum is thin (n=20) and the IFP share still runs below the
  population's; per-stream `n=` travels with any quoted rate.
- **Membership is an outcome oracle.** Every QP-bearing grant is in the file,
  so presence still shifts the odds toward grant (149 of 339 members are
  grants, against ~13% of the QP-bearing population) and absence still implies
  non-grant as of the frame date. The file is committed, so it is in every
  cell's checkout: for that reason **no predict or evaluate cell may read
  anything under `data/qp-topics/`** — the cell prompts state the prohibition,
  any read of the path in a cell's logged tool calls is a flaggable leakage
  event on audit, and the cell workflows delete the directory before an agent
  starts, so in a cell's working tree there is nothing to read.
- **The set enumerates ingested-but-unpublished dockets, deliberately.** 338
  of the 339 case ids have no directory under `data/cases`, so this artifact
  is a stated exception to the boundary that committed surfaces do not
  enumerate the ingested corpus (`docs/security.md`). What it discloses is
  identity-level: every QP-bearing grant is a member (a complete enumeration
  of that subpopulation), though with the supplement mixed in, membership
  alone no longer says which members the grants are. That is accepted because
  the dockets named are maximally public (SCOTUS petitions, named on the
  Court's own site) and no QP text is republished; the extent-by-counts the
  coverage caveat also carries is the posture the docket pack already
  publishes. The exception is accepted for exactly this artifact and is not
  precedent for machine-generated ones.

**What a measurement is.** The quantity any labeler run produces against this
set is *agreement with the reference raters*, not accuracy — reference error
and labeler error cannot be separated, least of all on the boundary labels.
Every reference rater was an agent session, so agreement with an agent
labeler of the same model family partly measures shared convention; that
caveat travels with any reported number. The recorded instruments are:
overall agreement with `n=`, per-label agreement with `n=` (floor-gated,
below), and the 3×3 confusion matrix on the
`constitutional-rights` / `criminal-law` / `civil-procedure` triangle (161 of
339 entries), written into the labels artifact alongside the labels
themselves. **The ceiling is measured**: on the 150-case supplement, two
independent blind raters agreed on 138 primaries — 92.0% (91.0% on denied
n=100, 100% on GVR n=30, 85.0% on dismissed n=20) — so a labeler's agreement
number should be read against ~92%, not 100%, and a rate meaningfully above
it is measuring shared convention, not extra correctness. The publication
gate: a labeler whose overall agreement
on the measured stream is below **80%**, which labeled fewer than **90%** of
the reference cases in its extract, or whose triangle confusion matrix is
unpublished, publishes nothing — `fedcourts qp-topics` enforces the first two
mechanically and refuses to write.

**The bounds that matter** are boundary agreements, not the overall rate: the
triangle (n=161), criminal vs habeas (n=83 combined), criminal vs immigration
(n=75 combined), and the `unclassifiable` rate (n=14), which sets the
denominator of every published share.

**Per-label support floor.** Five of sixteen labels have fewer than 10
reference examples (`environment-energy-and-property` 6, `immigration` 5,
`intellectual-property` 5, `election-law` 5, `tax` 3). Per-label agreement
under the floor is **unmeasured in v0**: it is reported as a raw count, never
as a rate.

**The vehicle flag is structurally near-empty under this contract.** Across
the 30 GVR-disposed supplement texts, both raters independently flagged
exactly one vehicle — the same one, a hold-for-a-named-lead-case ask —
because a stored QP text is written before the disposition, so a text-only
labeler can rarely see "vehicle" at all. The GVR-stratum correction the flag
was declared for is therefore bounded near zero in v0; a cut must not lean on
it.

**Contamination.** Three near-duplicate pairs sit inside the founding block
(two in `firearms`, one in `sovereignty-and-foreign-relations`) — the same
coordinated-filing clusters the coverage caveat names, present in the
baseline too.

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
