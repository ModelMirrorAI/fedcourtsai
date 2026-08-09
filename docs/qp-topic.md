# QP topics (`qp-topic-v0`)

A subject-matter vocabulary for the **questions presented** in SCOTUS
petitions: what a petition *asks about*, labeled from the stored
`questions-presented` text alone. This is the "claim taxonomy" that
`metrics/docket.md` and `metrics/README.md` reserve the phrase for — a
classification of subjects — and it is deliberately not part of
`docs/outcome-decomposition.md`, which decomposes a predicted *outcome* into
scoreable propositions. The two share nothing but the word "claim"; a topic
label never resolves against a docket and is never scored.

Four facts keep this a free-moving vocabulary rather than a pre-registration
surface:

- **Nothing frozen depends on it.** No frozen process digest reads a topic
  label, and no metric that scores a predictor conditions on one.
- **No cell prompt asks for it.** Topic labels are produced by an analytics
  labeler, not by predict or evaluate cells. The process digest hashes prompt
  bytes plus the resolved actor config, so this document and its labels can
  change without moving any digest.
- **It commits a predictor to nothing.** A published topic distribution is a
  corpus description, not a prediction claim.
- **Supersession is the plan.** A boundary that proves wrong in use is fixed in
  `qp-topic-v1`, not patched silently; the version token on the set is what
  makes every published cut and measured accuracy citable after the fact.

The trip-wire: the moment a *cell* prompt asks an agent for a topic label, that
prompt's digest moves and this stops being a free-moving vocabulary — that is a
version bump and its own review, not an edit to this document.

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
| `environment-energy-and-property` | Environmental and energy regulation, property and takings |
| `election-law` | Ballots, registration, districting, campaign finance, candidate qualification |
| `tax` | Federal and state taxation |
| `immigration` | Immigration status, removal, relief, and detention |
| `unclassifiable` | No subject present in the text at all |

**`criminal-law`** is not collateral review: a text naming §2254, §2255,
AEDPA, a certificate of appealability, or habeas belongs to
`habeas-and-postconviction`; a Strickland ineffective-assistance claim naming
none of those stays here. Illegal-entry and illegal-reentry prosecutions
(§1325/§1326) are criminal law, not `immigration` — the prosecution boundary
roughly halves the immigration share and is part of the declared vocabulary.

**`civil-procedure`** is not sovereign immunity as such, and not
agency-specific review procedure (which belongs to
`administrative-law-and-benefit-programs`). Justiciability beats subject when
justiciability is what is asked: a standing question arising in an election
case is `civil-procedure`, not `election-law`. Federal sovereign immunity is
deliberately here rather than under sovereignty — the underlying question's
label governs, and it is usually this one.

**`constitutional-rights`** is not the First or Second Amendment, which carry
their own labels. Where a §1983 suit carries a named right, label the right;
use this label when the question is the remedy or the immunity itself —
qualified immunity, Bivens, the scope of §1983.

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
agency regulates — an EPA question about agency power is admin; an EPA question
about the Clean Water Act's reach is `environment-energy-and-property`.

**`first-amendment`** includes both religion clauses. Campaign finance framed
as election administration is `election-law`.

**`sovereignty-and-foreign-relations`** is not federal sovereign immunity and
not qualified or judicial immunity.

**`environment-energy-and-property`** does not capture a regulatory taking
framed as a Fifth Amendment question — that framing is `constitutional-rights`.

**`election-law`** is not standing doctrine reached in an election case.

**`tax`** is not a tax-foreclosure taking.

**`unclassifiable`** means *no subject present* — front matter, a dot-leader
table of contents, a parties list captured by the extractor. It is never "hard
to label": a labeler who can name a subject must pick one.

## Structure: primary, secondary, vehicle

- **Primary** — mandatory, single. Every published count sums over primaries
  only, so a distribution can never total more than 100%.
- **Secondary** — optional, single, advisory. It never enters a published
  count. A *facet chain* — several questions elaborating one subject — gets no
  secondary (three nondelegation questions are one `admin` question; "are
  contract rights property" as an element of a fraud theory is one
  `criminal-law` question). A *smuggled question* under a different label gets
  one: two §922(g) questions bracketing a Guidelines-commentary question is
  `firearms` with a `criminal-law` secondary.
- **Vehicle** — boolean. A petition asking for a GVR in light of a named
  decision is labeled by the *underlying subject* and flagged as a vehicle;
  without the flag, the GVR stratum manufactures a phantom procedure topic.

The adjacent-pair tie-break is the **remedy-versus-right rule**: label what the
question *asks*, not what the case is about. A question about the *Heck* bar's
application to a First Amendment §1983 suit asks about the remedy →
`constitutional-rights` with a `first-amendment` secondary. A question about
the ripeness of a donor-disclosure challenge asks about justiciability →
`civil-procedure` with a `first-amendment` secondary.

## The labeler contract

A `qp-topic-v0` labeler is **text-only**: it reads the stored
`questions-presented` text and nothing else — no docket context, no case name
lookup, no outcome. That is what keeps labels reproducible and replay-safe (a
topic assigned from text that predates the decision can never encode the
decision).

**Labeling authority is the agent labeler alone.** Deterministic
statute/keyword rules are structurally insufficient for this vocabulary, not
tunably so: the labels are defined by what a question *asks*, and the two
largest error sinks (`constitutional-rights`, `civil-procedure`) have no
distinctive citation to key on, while keywords actively mislead — background
prose fires rules, cited statutes belong to different subjects than the
question, and case-name mentions contaminate ("habeas relief" inside a *Heck*
discussion). Measured on the reference set, a tuned rule set reaches 76.7%
coverage at 80.7% accuracy where it fires — 61.9% end to end.

Four rules do exceed 90% precision (`firearms`, `intellectual-property`,
`tax`, `employment-and-antidiscrimination`; jointly 20.6% coverage at 92.3%).
They run as a **shadow check only**: they publish nothing and pre-empt
nothing, and their disagreement rate with the agent labeler is reported in the
run summary as a standing regression trip-wire — a drifting labeler shows up
as a moving disagreement rate before it shows up anywhere else.

## The reference set

`data/qp-topics/qp-topic-reference.json` — hand labels for 189 cases, assigned
by reading the stored `questions-presented` texts under this document's rules
(text-only, primaries only), recorded against the Court's docket numbers and
joined to canonical case ids. The set exercises every label in the vocabulary,
and `tests/test_qp_topic_reference.py` pins that property, the canonical
serialization, and key uniqueness.

Its role is measurement: **no labeler's output is published until its accuracy
on this set is measured and recorded**, and the number that actually bounds a
published cut's quality is agreement on the
`constitutional-rights` / `criminal-law` / `civil-procedure` triangle, where
boundary judgment (not vocabulary coverage) is the failure mode. Relabeling an
entry is a judgment change and travels in its own reviewed diff.

## The coverage caveat

Any published topic distribution must carry this scope statement, because QP
presence in the corpus is a **document-fetch artifact, not a sample**:

- Zero coverage before Term 2023; stored QP texts exist for a minority of
  walked rows even after, and the share is wildly uneven across filing streams
  and Terms. Term-over-Term topic comparisons are unsafe.
- QP-bearing rows are several-fold **grant-enriched** relative to rows without
  a stored QP text, so denial-reweighting materially shifts the mix toward the
  in-forma-pauperis stream and concentrates `criminal-law`, `firearms`,
  `constitutional-rights`, and `unclassifiable`.
- Coordinated filing campaigns (near-identical petitions filed in clusters)
  mean a naive share partly counts campaigns rather than subjects; a published
  cut says so or publishes a de-duplicated companion.
- Extraction is lossy at the edges: some cases with a stored petition yield no
  QP text, the extractor sometimes captures the wrong page, and a text can
  open mid-sentence when the heading sat on the prior page. `unclassifiable`
  absorbs the worst of this and is published, never dropped.
