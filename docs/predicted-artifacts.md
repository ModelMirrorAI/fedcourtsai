# Predicted artifacts: what one prediction actually consists of

A predict cell is one predictor's answer about one event of one case, and the
answer is not a single number in a single file. This doc walks the files a cell
writes, says what each is for, and shows an example of every structured one, so
that "a prediction" is legible without reading the pydantic models. The models
(`fedcourtsai.schemas`, exported to `schemas/*.schema.json`) stay the contract,
and the instructions a cell actually follows are `.github/prompts/predict.md`;
this is the reader's-eye view of what they produce.

Every example below is invented — the case ids, the case names, the votes, and
the numbers. None of them is a real docket, a real vote, or a real outcome.

**The stage colours the answer, not the file set.** Every predict cell writes
the same files. What varies is `prediction.json`: `granted`, `probability`, and
`predicted_disposition` change *meaning* with the event's stage (`event.yaml`'s
`stage` — `cert`, `interim`, or `merits`), `judgment` is mandatory at one stage
and null at the others, and the declared claim set changes *shape*. All three
stages fan out: the merits admission is `store._merits_forecastable` (an open
merits event on a granted, undecided docket, every one bypassing the salience
gate), with the prompt's merits section carrying the cell contract. See
[decision-model.md](decision-model.md).

## Where the files land

```
data/cases/<court_id>/<docket_id>/events/<event_id>/predictions/<predictor_id>/<run_id>/
  prediction.json          # the quantitative judgment
  predicted_reasoning.md   # what the Court will do
  reasoning.md             # why this number
  retrieval.md             # what was consulted beyond the provisioned inputs
  flags.json               # optional: a durable note for a maintainer
  tooling.json             # a short self-report on the tooling the cell had
```

Paths come from `fedcourtsai.paths`, never hand-built. `run_id` is a UTC
timestamp, so a rerun writes a new directory beside the old rather than over
it, and a predictor writes only under its own `<predictor_id>/<run_id>/` path.

## `prediction.json`

The quantitative judgment, validating against the `Prediction` model. The
fields that mean the same thing at every stage:

- **Identity** — `case_id` (`<court_id>/<docket_id>`), `event_id`,
  `predictor_id`, `run_id`, `created_at`, and `engine` / `model`: which engine
  ran and which resolved model produced the answer.
- **`input_snapshot`** — the path of the provisioned snapshot the cell read.
  The agent's own string, so nothing scored conditions on it; the
  harness-written `context` block carries the conditioning state instead.
- **`granted` / `probability`** — the stage's declared binary and the
  probability of it. The stage names the binary, and the outcome's
  `actual_granted` is defined on the same axis, so `(probability -
  actual_granted)^2` is the Brier score at every stage.
- **`predicted_disposition`** — the realized-outcome label, from the
  `Disposition` vocabulary. Which members are reachable is stage-specific.
- **`votes`** — per-Justice `{justice, vote, writing}`. `vote` takes the *vote*
  vocabulary (`grant`, `deny`, `majority`, `dissent`, …), never a disposition:
  a disposition is what the Court did, not how one Justice voted. Omitting
  `writing` says the cell did not forecast it; `writing: "none"` is the
  affirmative claim that the Justice writes nothing.
- **`judgment`** — the merits axis (see below), null everywhere else. A
  prediction carrying it must carry a non-empty `votes` block; the schema
  enforces that on every artifact.
- **`confidence`** — optional, 0–1.
- **`big_case_score` / `big_case_rationale`** — an optional pre-registered read
  of the case's stakes *if decided*, explicitly not grant likelihood. Graded
  later by rank-agreement with the evaluators' own independent reads, never
  against a ground truth ([salience.md](salience.md)).
- **`reasoning_doc` / `predicted_reasoning_doc`** — the filenames of the two
  prose documents, beside this file. `validate` resolves both pointers, so a
  named document that is not there fails the cell, as does a name carrying a
  path separator.
- **`claims`** — the harness-declared claim set for this event, one `{claim_id,
  probability}` per declared claim. The set is the harness's
  (`fedcourtsai.pipeline.claims`) and is fixed and mandatory: a cell answers
  every declared claim, adds none, and declines none. A block that skips a
  declared claim, states one twice, or whose headline claim diverges from
  `probability` scores nothing at all — a partial answer is malformed, not a
  choice. Where an event declares no set the cell writes no `claims` field, and
  the stamped record carries it as null; never an empty list.
- **`semantic_claims`** — the *semantic* claim set's propositions, and **null on
  every cell**: no event declares a semantic set, so no prompt asks for one and
  no cell writes one. The field is the wired-but-inert seam of the alpha
  `semantic-v0` methodology ([outcome-decomposition.md](outcome-decomposition.md),
  *The semantic family, alpha*); a cell that invents a block for it is writing
  a claim the harness never declared.
- **`process_version` / `context`** — harness-written, never the agent's; see
  *What the cell does not write*.

### Cert stage: a petition for certiorari

The event is `evt-petition-disposition` (kind `petition`, stage `cert`); a
petition- or appeal-kind event recording no stage reads as cert, since those
kinds resolve on the cert standard by construction.

- `probability` is P(any grant), and `granted` its 1/0 form.
- `predicted_disposition` may take any label in the vocabulary. `gvr`,
  `summary-reversal`, and `granted-in-part` all count as grants on the binary
  axis, so they travel with `granted: 1`.
- The declared set is **`cert-v1`**, three claims: `disposition` — which must
  equal the top-level `probability` exactly, being the same belief restated so
  the set is self-describing — plus `relist-increment` and `cvsg-increment`.
  Both increments are forecasts *from* the state the snapshot showed, never
  levels: they resolve the count and CVSG date at resolution against the ones
  frozen in the cell's `context`.
- `votes` is optional and `judgment` is null: no majority opinion accompanies a
  denial, so there is usually no vote to forecast.

A cert prediction, with the two harness-written blocks the stamp adds. Key
order here is reading order; a stamped file is key-sorted and spells every
absent optional field as null.

```json
{
  "schema_version": "1.0",
  "case_id": "scotus/99000001",
  "event_id": "evt-petition-disposition",
  "predictor_id": "claude-baseline",
  "engine": "claude-code",
  "model": "claude-fable-5",
  "run_id": "20260412T101500Z",
  "created_at": "2026-04-12T10:21:07Z",
  "input_snapshot": "data/cases/scotus/99000001/record/snapshots/2026-04-10.json",
  "granted": 0,
  "probability": 0.05,
  "predicted_disposition": "denied",
  "votes": [],
  "judgment": null,
  "confidence": 0.55,
  "big_case_score": 0.35,
  "big_case_rationale": "A narrow preemption question; the split is real but shallow.",
  "reasoning_doc": "reasoning.md",
  "predicted_reasoning_doc": "predicted_reasoning.md",
  "claims": [
    {"claim_id": "disposition", "probability": 0.05},
    {"claim_id": "relist-increment", "probability": 0.35},
    {"claim_id": "cvsg-increment", "probability": 0.08}
  ],
  "context": {
    "schema_version": "1.0",
    "mode": "forward",
    "snapshot_date": "2026-04-10",
    "snapshot_provenance": "as-stored",
    "cutoff": null,
    "decided_before": null,
    "signals_observable": true,
    "distribution_count": 1,
    "cvsg_date": null,
    "band": "baseline",
    "salience_version": "sal-v2",
    "term": 2025
  },
  "process_version": {
    "label": "proc-v2",
    "digest": "sha256:1f0a9c7e5b3d2648a0c1e4f78b95d2360a7c4e18b5d9f0632a1c8e7d40b6f925",
    "algo": "sha256",
    "pipeline_sha": "9f2c1ab7d40e5836c2b90f14a7de3c58b1042ef6",
    "stamped_at": "2026-04-12T10:24:02Z"
  }
}
```

### Interim stage: a stay or injunction application

The arrival event is `evt-motion-disposition` (kind `motion`, stage `interim`
— the first of the stage's three declared moments), and it resolves as the
grant or denial of the requested relief.

- `probability` is P(the disposing entry reads as an **unqualified** grant),
  not P(any relief): the interim resolver matches denial language first, so a
  "granted in part and denied in part" order resolves as denied. The collapse
  is pre-registered ([salience.md](salience.md), *The interim docket*), and
  scoring partial relief as a grant would over-state the number on exactly the
  mixed shadow-docket shape.
- `predicted_disposition` draws from four labels only — `granted`, `denied`,
  `withdrawn`, `dismissed`. `gvr`, `summary-reversal`, and `granted-in-part`
  are cert-stage routes the interim vocabulary never records.
- **No `claims` field.** No interim moment declares a set, whatever the
  event's kind, so the cell writes none and the stamped record carries a null.
- `votes` is optional and `judgment` is null. None of the cert signals exists
  here either: an application is not distributed for conference and a CVSG is a
  cert-stage act, so the cell reads the escalation ladder — response requested,
  referral to the full Court, amicus count — instead.

The harness blocks are omitted from this and the next example for brevity;
every committed prediction carries them.

```json
{
  "schema_version": "1.0",
  "case_id": "scotus/99000002",
  "event_id": "evt-motion-disposition",
  "predictor_id": "claude-baseline",
  "engine": "claude-code",
  "model": "claude-fable-5",
  "run_id": "20260412T101500Z",
  "created_at": "2026-04-12T10:33:41Z",
  "input_snapshot": "data/cases/scotus/99000002/record/snapshots/2026-04-11.json",
  "granted": 0,
  "probability": 0.28,
  "predicted_disposition": "denied",
  "votes": [],
  "judgment": null,
  "confidence": 0.4,
  "big_case_score": 0.7,
  "big_case_rationale": "A statewide election rule, weeks before the ballot deadline.",
  "reasoning_doc": "reasoning.md",
  "predicted_reasoning_doc": "predicted_reasoning.md"
}
```

### Merits stage: what the Court does to the judgment below

The event is `evt-order-judgment` (kind `order`, stage `merits` — the first
of the stage's two declared moments) — the grant order is the filing that
opened it, and the thing to predict is the judgment.
It is minted by a cert grant that actually opens a merits proceeding, so a GVR
and a summary reversal, which terminate at the cert order, mint nothing.

- `probability` is **P(disturbed)**: that the judgment below is reversed,
  vacated, or reversed in part. A dismissal as improvidently granted and an
  affirmance by an equally divided Court both count as *undisturbed*, since
  each leaves the judgment below standing. `granted` carries the same binary.
- `judgment` is **mandatory** and takes the full `Judgment` vocabulary
  (`affirmed`, `reversed`, `vacated`, `affirmed-in-part-reversed-in-part`,
  `dismissed-as-improvidently-granted`,
  `affirmed-by-an-equally-divided-court`). `validate` holds each predictor's
  latest prediction on a merits-stage event to carrying one, and the schema
  holds any prediction carrying one to a non-empty `votes` block — a merits
  forecast is over per-Justice votes, so a judgment call with no vote block is
  malformed.
- `predicted_disposition` is `other`. The cert/interim vocabulary has no merits
  member by design, so the label carries nothing here and `judgment` carries
  the forecast — mirroring how the outcome is written.
- The declared set is **`merits-v1`**, one claim: `judgment-disturbed`, which
  restates `probability` exactly, under the same rule as the cert `disposition`
  claim.

```json
{
  "schema_version": "1.0",
  "case_id": "scotus/99000003",
  "event_id": "evt-order-judgment",
  "predictor_id": "claude-baseline",
  "engine": "claude-code",
  "model": "claude-fable-5",
  "run_id": "20260412T101500Z",
  "created_at": "2026-04-12T10:47:12Z",
  "input_snapshot": "data/cases/scotus/99000003/record/snapshots/2026-04-09.json",
  "granted": 1,
  "probability": 0.68,
  "predicted_disposition": "other",
  "judgment": "reversed",
  "votes": [
    {"justice": "Justice A", "vote": "majority", "writing": "majority"},
    {"justice": "Justice B", "vote": "majority"},
    {"justice": "Justice C", "vote": "majority"},
    {"justice": "Justice D", "vote": "majority"},
    {"justice": "Justice E", "vote": "concur-in-judgment", "writing": "concurrence-in-judgment"},
    {"justice": "Justice F", "vote": "dissent", "writing": "dissent"},
    {"justice": "Justice G", "vote": "dissent"},
    {"justice": "Justice H", "vote": "dissent"},
    {"justice": "Justice I", "vote": "recused"}
  ],
  "confidence": 0.5,
  "reasoning_doc": "reasoning.md",
  "predicted_reasoning_doc": "predicted_reasoning.md",
  "claims": [
    {"claim_id": "judgment-disturbed", "probability": 0.68}
  ]
}
```

## `predicted_reasoning.md`

Free-form markdown: the forecast of what the **Court** will do with this event
and why. Claims about the future that the docket will later confirm or refute —
so, at the cert stage, procedural rather than doctrinal: whether the petition
is relisted further and roughly how often, whether a CVSG issues, which
question presented the Court would take, whether a summary disposition is the
likelier route, and any dissent from denial expected and from whom. An interim
cell forecasts the procedural facts its own event resolves to — whether a
response is called for, whether the application is referred to the full Court,
and roughly when it is disposed of. Merits-shaped content belongs here only
conditionally ("if granted, the likely ground is …"), never as an unconditional
claim about an opinion a denial will never produce.

Written on every live cell. `predicted_reasoning_doc` is nullable only so
records written before the field existed still validate — not so a cell can
skip the document, and `validate` enforces exactly that split: a
process-stamped cell provably post-dates the field, so a null pointer on one
fails validation, while unstamped shakedown records stay valid.

## `reasoning.md`

Free-form markdown: the predictor's rationale for **its own numbers**. Why this
probability and not another, what in the provisioned snapshot and the filed
documents drove it, which base rates it anchored on and what it adjusted from
them, what it is uncertain about, and where a reader should discount it. This
is also where a degraded input, a missing snapshot, or an outcome the cell
already knew gets recorded.

The two documents are deliberately separate, because they have different
epistemic status: `predicted_reasoning.md` resolves against the docket, while
`reasoning.md` resolves against nothing and is self-justification. Merged,
neither can be read for what it is, and the forecast cannot be scored because
it cannot be separated from the rationale. The evaluator's `reasoning_quality`
grades `reasoning.md` and that document only.

## `retrieval.md`

Free-form markdown, not schema-validated: what the cell consulted beyond the
provisioned inputs — each corpus lookup (the `fedcourts` command line and the
`ranged corpus reads: …` line it printed), each CourtListener MCP lookup, and
any web searches the engine surfaced. What a cell consults is logged, not
limited. A cell that consulted nothing writes the single line "No retrieval
beyond the provisioned inputs."

It is the cell's own account, and it sits beside the harness's independent
capture in `retrieval_log.json`.

## `flags.json`

Written **only** when the cell has something durable to surface — a
data-quality problem, a scope question, an ambiguous event, or the reason it
was blocked. It validates against the `AgentFlags` model, and the `collect` job
rolls every cell's flags into the run PR body, the Actions summary, and one
long-lived agent-feedback tracking issue, so the note survives the trigger
issue's closure and a maintainer sees it without reading every `reasoning.md`.
`category` is one of `data-quality` / `scope` / `ambiguous-event` / `blocked` /
`other`, and `severity` one of `info` / `warning` / `blocker`.

```json
{
  "schema_version": "1.0",
  "case_id": "scotus/99000001",
  "run_id": "20260412T101500Z",
  "role": "predictor",
  "actor_id": "claude-baseline",
  "flags": [
    {
      "category": "data-quality",
      "severity": "warning",
      "message": "The provisioned brief in opposition has empty_text: true, so the opposition is read from the docket entries rather than its text.",
      "event_id": "evt-petition-disposition"
    }
  ]
}
```

## `tooling.json`

Written briefly on **every** run, unlike `flags.json`: a short structured
self-report on the *environment* the cell was given rather than on the data.
Whether it used the corpus-query CLI and base-rate context, which abilities
helped, and what was missing. Rolled up across runs so maintainers can see
whether the corpus tooling earns its keep and where to invest next. It is the
agent's own account — subjective, advisory, and never a gate.

```json
{
  "schema_version": "1.0",
  "case_id": "scotus/99000001",
  "run_id": "20260412T101500Z",
  "role": "predictor",
  "actor_id": "claude-baseline",
  "used_corpus_query": true,
  "used_base_rates": true,
  "tools_used": ["fedcourts query", "courtlistener MCP search"],
  "helpful": ["the per-Term salience-band table", "the questions presented"],
  "gaps": ["a per-Term relist hazard cut conditioned on the current count"],
  "notes": "Two MCP citation lookups timed out; the cell proceeded on the snapshot.",
  "tool_manifest": ["courtlistener"]
}
```

## What the cell does not write

Part of what a prediction consists of is not the agent's word, and reading the
directory without knowing which part is which invites trusting the wrong half.

- **`usage.json`** — measured token counts and the estimated cost for the cell,
  written by a post-run harness step from the engine log.
- **`retrieval_log.json`** — the tool-call transcript, captured harness-side
  from the engine's own log: tool names, query slices, and document dates where
  legible. It is the cross-evaluator's leakage evidence precisely because the
  agent does not write it; credential-shaped runs are redacted at capture.
- **`attempt.json`** — the durable fact that a cell ran and produced no usable
  prediction, written by the `collect` job, which is the only observer of that.
- **`process_version`** on `prediction.json` — stamped by `fedcourts
  stamp-cell` from the prompt-template bytes and the resolved configuration in
  force at run time. Anything an agent puts there is overwritten. The `digest`
  is the identity that the frozen partition keys on; the `label` beside it is
  human-readable sugar and never a partition key. See
  [process-version.md](process-version.md).
- **`context`** on `prediction.json` — the `PredictionContext` block: the
  cell's mode and replay cutoff, and the conditioning state frozen at
  provisioning (the salience band, the distribution count and CVSG date as at
  prediction, the Term). Written by provisioning and copied on by the stamp. It
  matters that it is harness-owned more than most: the band a cell is scored
  against only ever strengthens, so a band re-derived at evaluation would
  condition a forecast's baseline on its own future — and the `mode` is a
  scoring input in its own right, since a forward claim the record contradicts
  voids the cell (the forward-claim exclusion, `metrics/README.md`).

## What the prediction is then scored against

An evaluate cell runs once the event resolves and writes one pair of files per
predictor it scores, under
`events/<event_id>/evaluations/<evaluator_id>/<predictor_id>/<run_id>/`, plus
one `retrieval.md`, one `tooling.json`, and an optional `flags.json` for the
cell as a whole, a level above at `evaluations/<evaluator_id>/<run_id>/`. This
is the short version; `metrics/README.md` is the authority on what any of these
numbers may be claimed to show.

The evaluator never sees that layout while it works. It grades **blind**: the
harness stages each predictor's latest prediction under an opaque alias with its
identity masked (`fedcourtsai.blinding`), the evaluator reads those and keys its
output on the alias, and a post-run step renames the directories onto the real
predictor ids before the stamp. The committed layout above is what un-aliasing
produces. What a blinded grade may be read as is in
[outcome-decomposition.md](outcome-decomposition.md); which files are staged and
which are dropped is in [cli.md](cli.md), under
`provision-blinded-predictions`. Briefly: a candidate's
`usage.json`, `tooling.json`, and `flags.json` are not staged at all, so a
predictor's own leakage disclosure reaches the grader only where it also made it
in prose.

- **`evaluation.json`** (the `Evaluation` model) — `correct` (did the
  prediction name the right label on the stage's own axis: the disposition at
  cert and interim, the judgment at merits), `brier_score` on the stage's
  binary, `judgment_correct` on a merits cell only, `vote_accuracy` over the
  Justices both sides name, `reasoning_quality`, a structured `leakage`
  assessment over the harness-captured retrieval log, and the evaluator's own
  independent `big_case` read. `claim_scores`, `base_rate_salience_version`,
  and `process_version` are the harness's, never the evaluator's word.
  `semantic_grades` is null on every cell — the counterpart of the prediction's
  `semantic_claims` above, and inert for the same reason: nothing declares a
  semantic set, so nothing is graded. It is the one *claim-family* block that
  could never be the harness's word, unlike `claim_scores`, since resolving a
  semantic claim needs a reader; that is why inter-grader agreement is what a
  published grade would have to travel with.
- **`evaluation.md`** — free-form: what the prediction got right or wrong and
  why, and what drove the `reasoning_quality` score.

Three per-stage differences are worth knowing when reading a scored cell:

- **A cert cell** carries `segment_base_rate` where one is derivable: its
  frozen salience band's grant rate, pooled over Terms strictly before the
  case's and bounded by `salience.base_rate_lookback_terms` (shipped at ten,
  matched to what the statpack's Term table renders). `base_rate_basis` records
  which population it was taken over — `risk_set` for every petition that ever
  *reached* the frozen band, which is the population a live cell was in, or
  `terminal` for those that *ended* in a band re-derived now, the fallback
  where no band was frozen. The two run several-fold apart in the weak bands,
  so a skill number means something only within one basis, and both it and
  `brier_skill_score` are omitted where no band, no prior-Term rate, or no
  matching salience version exists.
- **An interim cell omits both**, by rule and not by accident: no interim
  segment base rate is published, so there is nothing to score skill against.
  The omission is keyed on the stage, not on whether a band happens to be
  frozen.
- **A merits cell's baseline is registered and scored** — the statpack's
  pooled strictly-prior disturbed rate (its cohort guarded label-independently
  against cert-order-dated judgments), keyed on the grant Term and returning
  nothing below a stated minimum of parsed judgments — feeding both the
  evaluator's `brier_skill_score` and the claim block's difference form.

An evaluation of the cert prediction above, had that petition been denied
without a further relist. Its `process_version` stamp is omitted for brevity,
as on the predictions above:

```json
{
  "schema_version": "1.0",
  "case_id": "scotus/99000001",
  "event_id": "evt-petition-disposition",
  "predictor_id": "claude-baseline",
  "evaluator_id": "claude-judge",
  "engine": "claude-code",
  "model": "claude-fable-5",
  "run_id": "20260620T090200Z",
  "created_at": "2026-06-20T09:11:33Z",
  "correct": 1,
  "brier_score": 0.0025,
  "reasoning_quality": 0.7,
  "leakage_suspected": false,
  "leakage": {
    "mode": "forward",
    "retrieved_outcome_material": false,
    "influenced_prediction": "not_applicable",
    "notes": "Predicted while the petition was pending; no post-event material in the log."
  },
  "big_case": {
    "evaluator_score": 0.3,
    "notes": "Fact-bound preemption question with no federal party."
  },
  "segment_base_rate": 0.067,
  "base_rate_basis": "risk_set",
  "base_rate_salience_version": "sal-v2",
  "brier_skill_score": 0.443,
  "claim_scores": {
    "declared_set_version": "cert-v1",
    "claims": [
      {"claim_id": "disposition", "probability": 0.05, "baseline": 0.067,
       "outcome": 0, "score": 0.001989},
      {"claim_id": "relist-increment", "probability": 0.35, "baseline": null,
       "outcome": 0, "score": null},
      {"claim_id": "cvsg-increment", "probability": 0.08, "baseline": null,
       "outcome": 0, "score": null}
    ],
    "total": 0.001989,
    "floor": 0.0,
    "lift": 0.001989
  },
  "notes_doc": "evaluation.md"
}
```

Read that block with four things in view. The cell priced the petition below
its band's prior-Term rate and the petition was denied, so the skill score and
the scored claim both come out positive. The skill score is violently unstable
at a rate this low, because its denominator is the baseline's own Brier: this
same cell reads about −7 scored against the terminal basis instead of the
risk-set one, and about −4 had the forecast been 0.15 rather than 0.05. A
single cell's skill figure is illustrative only — never a rank signal, and
never comparable across bases. The `floor` of 0.0 beside the total prices
*baseline-restating and nothing else*: base-rate drift and
baseline estimation error stay unpriced, so a positive total is not by itself
skill. The total covers **one of the three declared claims**; the other two
carry a null baseline, because the committed statpack publishes no cut that
supports a strictly-prior, properly-conditioned rate for them, and they go
unscored rather than scored against an invented number — which makes this total
incomparable with a block where all three scored. And a claim's `outcome` can
itself be null, masked because the *record* discloses nothing: a property of
the record, never of the predictor.

Nothing about a single cell is a performance claim. What may be said from a set
of these numbers, and over which strata, is `metrics/README.md`'s subject; how
a claim total may be published is
[outcome-decomposition.md](outcome-decomposition.md)'s.
