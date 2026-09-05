# Freeze record

The append-only record of process-version freezes and their supersessions, of
the **masking-surface** changes that move what reaches an evaluator's
information set under an unchanged digest, of the **scoring-baseline** changes
that move a measured number the same way, of the **provisioning cutoff** that
moves what a predictor is conditioned on, of the **membership rules** that move
which cells a published figure is computed over while moving no value, and of
the boundaries a published figure may not be pooled across.

Each entry is dated evidence rather than description, and two sets of timestamps
carry it. The commit that added an entry is when its assertion was made — that
is what an external evaluator reads to know the claim preceded the outcome. The
commits, promotions, and `prereg/` tags an entry *names* are what it can be
checked against.

This is the one document here that is deliberately **history rather than current
design**. Everywhere else the repository's convention holds — docs and code
describe the design as it stands, and `git blame` finds the rest — but a
pre-registration record whose content is not dated history witnesses nothing, so
the convention does not apply to this file.

**Append-only.** New entries go at the bottom, in the order the changes were
taken, and an entry's substance is fixed once it lands: a fact that later proves
wrong, a boundary that later moves, or a label that is later superseded is
recorded by a **new** entry saying so, never by revising an old one. A record
that can be rewritten proves nothing about when it was written.

The single exception is an entry's **completion**, which the freeze procedure
builds in. An entry authored alongside its freeze commit cannot yet state the
facts that only the carrying promotion produces — the promotion tag, its merge
commit and date, the promotion-time re-run of step 0's stamped-cell grep, and,
where an entry lands in its own freeze commit or executes a de-count, that
commit's hash and the de-counted census — so it carries them as explicit
`<FILL: …>` placeholders, and those placeholders
are filled once, at that promotion. A placeholder is the only editable content
an entry ever has.

What a process version is, which states it passes through, and how the freeze is
performed all belong to
[process-version.md](process-version.md#freezing-the-cutover-procedure); each
freeze commit is recorded here.

## Entries

- Freeze commit: `84b421168` (tagged **`prereg/proc-v1`**) — blesses the six
  proc-v1 digests (three predictors, three evaluators) and sets the freeze
  instant `2026-08-15T00:00:00Z`. Carried to `main` by the promotion tagged
  `promotion/2026-08-12-2` (merged `2026-08-12T14:20:51Z`, before the
  instant — the auditor's check of the cutover procedure above). Zero stamped
  cells existed when the freeze landed on `main`, so nothing is listed as
  pre-registration-excluded; everything earlier is the unstamped
  alpha/shakedown ledger. **Superseded by proc-v2 below with zero cells ever
  stamped under it** (step 0's grep on both branches: 0), so its headline is
  legitimately empty forever; the tag stays as the record that the label was
  registered, then superseded before any cell ran.
- Freeze commit: `04411f166` — the sal-v2 activation commit as amended before
  the tag by the merits-baseline accuracy fix (#1157), which is where the
  blessed set lives, tagged **`prereg/proc-v2`**. Carried to `main` by the
  promotion tagged **`promotion/2026-08-13`** (merge commit `260e8a64a`, merged
  `2026-08-13T19:10:14Z`, before the freeze instant — the auditor's check of
  the cutover procedure). Step 0's stamped-cell grep on both branches at the
  promotion: 0. It re-blesses the
  three predictor digests the predict prompt's third cert moment (the arrival
  cell) moved, and sets the freeze instant `2026-08-16T00:00:00Z`. The
  activation commit flips
  the active salience scorer to `sal-v2`; its caption-census freeze record
  (caption-v1, pooled federal 0.708 vs private 0.054 over OT2017–24, 8/8
  complete Terms) is quoted in the activation PR with the corpus sha it ran
  over. The scored window opens at the first post-promotion metrics refresh,
  not at the flip — a sal-v2 cell minted before the refreshed statpack has no
  published baseline (`docs/salience.md`). The evaluator digests carried by
  the freeze are proc-v1's grading process plus one pre-tag accuracy fix in
  the evaluate prompt's merits note (the harness merits baseline's third pool
  guard — the null-provenance refusal in `merits_base_rate` — a
  scoring-baseline change with no boundary of its own; the prompt edit
  beside it gives it one, the discipline `docs/process-version.md`
  prescribes); zero cells were ever stamped
  under any interim digest set.

- **`sal-v3` registered and activated (caption-v2 carve-in), 2026-08-15.** No
  freeze commit belongs to this entry: the salience version sits outside the
  process digest (`pipeline_sha` is not an input), carries its own
  data-visible boundary (`context.salience_version`), and the flip re-blesses
  nothing. The registration commit (`be774099c`) adds the `caption-v2` rule
  and the `sal-v3` scorer with `sal-v2` still active; the activation commit
  flips the one constant. Its caption-census freeze record, quoted here
  because the census artifact is deliberately uncommitted: `caption-v2` over
  corpus `e665971350fbc5d2729e424c6fd6d0f2b927b59253922cccb60f6dd1fe276469`,
  scored segment OT2017–24, pooled federal 133/181 (0.7348) against
  `caption-v1`'s 114/161 (0.7081), private 0.0524 against 0.0540, per-Term
  federal `n` 17/23/26/41/11/19/29/15 (OT2017–24; right-censored OT2025 21)
  against v1's 16/20/22/39/9/17/22/15, per-Term lift 9.1×–17.7×, 20 rows
  across 16 distinct captions migrating `private`→`federal` in the complete
  Terms (plus 2 in OT2025), one-directional by construction — and because the
  recovered captions were surfaced partly by a grant-ranked residual scan
  (19 of the 20 migrated rows are grants), the pooled-rate rise and the lift
  rise are **not** evidence for the widening; the evidence of record is the
  migrated captions' outcome-free precision (no false positive among the 20
  migrated complete-Term rows) and the pre-registered per-Term replication
  shape, with the incremental class's forward rate estimable only by an
  out-of-sample re-census once frozen-window Terms accrue. The scored window
  opens at the first post-promotion metrics refresh, as it did for `sal-v2`.

- Freeze commit: `8d256a32f`, tagged **`prereg/proc-v3`**. Carried to
  `main` by the promotion tagged `promotion/2026-08-15` (merge commit
  `596740de4`, merged `2026-08-15T16:13:46Z`) — the auditor's comparison of the
  cutover procedure is that date against the freeze instant, and it was a **hard
  gate before the tag was minted**, not a note: the `prereg/` namespace blocks
  update and deletion, so a tag over a bad instant burns the label. The merge
  precedes the instant by under eight hours — inside the gate, with the
  tight margin the entry below anticipated. It blesses
  the six proc-v3 digests (three predictors, three evaluators) and keeps the
  freeze instant at `2026-08-16T00:00:00Z`, deliberately unmoved from proc-v2's.
  Holding it is safe in the direction that matters — proc-v2 has zero stamped
  *predictions* and the enforced filter is prediction-side, so re-using the
  instant blesses nothing retroactively — but it is the **tight** direction
  rather than the generous one the procedure asks for, which is why the gate
  above is stated as a gate. If the promotion merges after the instant, bump the
  constant in a follow-up promotion before tagging, and confirm no stamped cell
  carries a `stamped_at` in the gap.

  **Step 0's stamped-cell grep against `origin/main`: 27, all
  pre-registration-excluded.** Every one is an **evaluation** — no prediction
  carries a stamp at all — over three cert events
  (`scotus/73129750`, `scotus/73275185`, `scotus/73275187`, each
  `evt-petition-disposition`), three evaluators (`claude-judge`, `codex-judge`,
  `gemini-judge`) × three predictors, all labelled `proc-v2` and all stamped
  between `2026-08-14T03:41:05Z` and `2026-08-14T03:47:47Z`. Every stamp
  precedes the freeze instant, so `is_frozen`'s time cutoff excludes them
  mechanically, and **zero cells were ever counted under proc-v2**: its headline
  is legitimately empty forever, and its tag stays as the record that the label
  was registered and then superseded. The grep was re-run against `main` at
  promotion time, as the procedure requires — the count held at 27.

  What moved every digest is the prompt pair: `.github/prompts/predict.md`
  elicits `cert-v2`'s five claims (the two additions in the conditional forms
  their resolvers score), `interim-v1`'s four, and `semantic-v1`'s two
  propositions on a merits cell, and anchors an interim cell on the registered
  scored base rate; `.github/prompts/evaluate.md` keys the base-rate basis on
  the frozen `salience_version`, reads the merits and interim rate/skill pair as
  harness-stamped, scopes `vote_accuracy` to merits cells, and carries the
  semantic grading protocol.

  Riding the same promotion, and named here because each changes what is
  measured **without moving a digest** — the discipline
  [process-version.md](process-version.md) prescribes for exactly this class:

  - the **vote-scoring stage gate** (`pipeline.moments.scores_votes`), which
    changes what is scored under an unchanged digest by denying vote scoring off
    the merits stage by default;
  - the **blinding masking surface**, widened by the new `MODEL_RATES` keys that
    `blinding.identity_terms` reads — a change to every evaluator's information
    set with no digest of its own;
  - the **claim-set declarations** `cert-v2`, `interim-v1` and `semantic-v1`,
    which are tables rather than prompt bytes or actor config;
  - the **harness skill stamp**, which moves `brier_score`,
    `segment_base_rate`, and `brier_skill_score` off the evaluator and onto
    `stamp-cell` on the merits and interim stages — a change to *who computes a
    scored number*, which the scoring-baseline rule puts in this list;
  - the **harness `correct` stamp**, which moves the accuracy column's per-cell
    bit off the evaluator and onto `stamp-cell` on **every** stage, cert
    included: the comparison needs no pooled baseline and so no salience band,
    which is the whole of the skill stamp's cert exemption. No digest moves —
    no prompt byte changed, and `stamp-cell` calls `pipeline.evaluate.is_correct`,
    the same function the evaluate prompt already names as the definition — so
    the quantity is unchanged and only its author moves, which is precisely what
    puts it in this list. The leaderboard's **first rank key** is the affected
    figure. Zero frozen-scope cells were ever stamped under the prior
    ownership: the committed board reads `evaluations_total: 0` at
    `process_scope: frozen`, so no published standing rests on an
    evaluator-authored `correct`;
  - the **retrieval-log capture marker** — `result_capture` on every call and
    the log-level `result_capture_coverage` — which passes `mask_retrieval_log`
    unmasked and so reaches the grader on the leakage grading's own required
    reading path: a change to every evaluator's information set with no digest
    of its own, the masking-surface case
    [process-version.md](process-version.md) names. The promotion carrying it
    lands some hours *before* the freeze instant, so the frozen partition is
    homogeneous: no cell stamps as frozen before the instant, and the frozen
    information set carries the marker from its first cell. No label
    bump;
  - the **retrieval-log condition marker** — `result_status` on every call and
    the log-level `throttled_calls` — which is the capture marker's case
    exactly: it passes `mask_retrieval_log` unmasked and so reaches the grader
    on the leakage grading's own required reading path, a change to every
    evaluator's information set with no digest of its own. It is the same
    class of change and gets the same treatment rather than a quieter one,
    because what makes it a masking surface is that it survives the mask, not
    how interesting the field is. Two things bound it: the evaluate prompt's
    instruction to read both fields rides the proc-v4 evaluator digest (the
    freeze entry below), so instruction and information-set change are
    partitioned together from that label forward — the cells graded before it
    saw the fields unmasked with nothing instructing the read — and a
    committed call's marker is `null` on every log written before capture
    minted it — the frozen partition's cells carry the field from their first
    cell or not at all. No label bump;
  - the **code-mode calls** a code-mode engine makes from inside a
    freeform builtin call, lifted out of that call's source into
    `RetrievalCall` rows of their own — the manifest tools, and the engine's
    own builtins beside them, which is where such a program does most of its
    work. It is the largest of these entries and
    the same class: a candidate whose staged log previously showed builtin rows
    alone now shows the call classes reached from inside a program and their
    query slices. So one
    candidate's information set on the grader's required reading path changes,
    with no digest of its own, which is what puts it here. Four things bound
    it. A lifted row carries no result — no digest, no `retrieved_doc_date`,
    the leakage grading's own timing signal — because a freeform call's one
    combined output is not attributable to an individual call inside it; what
    the grader gains is which tools were asked for, not what came back. The
    rows are *what the engine already did*;
    only their visibility to capture changes, so no cell retrieves differently.
    And `call_source`, the marker naming a lifted row, is the one field
    `mask_retrieval_log` **drops** rather than passing through, because it
    identifies the engine as directly as the raw tool vocabulary the
    respelling removes.
    Unlike the two markers above, this one does **not** leave its partition
    homogeneous, and the difference is worth stating rather than inheriting
    their reasoning: the stamped code-mode cells already committed carry no
    lifted rows and never can — their rollouts are gone — while later
    cells under the same blessed digest carry them, so that partition holds
    three capture regimes — no lifted rows, the manifest idiom alone, both
    idioms — and nothing in a committed artifact names which one a cell was
    minted under. `call_source` separates a lifted row from an item, which the
    capture tripwire reads and the mask drops; what separates the two lifted
    regimes is only whether builtin-named rows are there at all, a presence
    rather than a marker. It still takes no label
    bump,
    because what the split can reach is bounded: a lifted row carries no
    result, so the leakage assessment it feeds gains which tools a program
    asked for and nothing about what came back, and that assessment moves no
    quantitative field. No scored number differs across the regimes. The
    summary fields that do move — a log's `result_capture_coverage`, and the
    call total and observability rate built over its rows — are capture
    statistics the scoring path does not read, and the coverage rate moves
    toward the truth: a cell stamped under the manifest-only lift carries a
    rate asserting that capture had seen retrieval it had not. Two standing
    consequences belong on the record rather than only in the code. The
    builtin names are enumerated, so a rename on that side mints no rows and
    shows up as a code-mode cell's capture rate climbing back toward 1.0 —
    a silent regime change with no tripwire, since the capture tripwire
    deliberately watches the manifest idiom. And a lifted builtin row stages
    under the neutral class `other` unless the tool-class map names it, so a
    staged code-mode log carries rows whose query is plainly a shell command
    under a class that is not `shell`; mapping those names is a change to what
    the grader reads and belongs here when it happens. No
    label bump;
  - the **`sal-v3` activation**, whose own entry is above; it carries a
    data-visible boundary of its own (`context.salience_version`), so it is
    listed here for completeness rather than because it is invisible.

- **The moment cutoff on forward provisioning, 2026-08-17.** No freeze commit
  belongs to this entry either, on the `sal-v3` pattern: it moves no digest — no
  prompt byte changes, and the prompts are the digest's input — and it carries
  its own data-visible boundary, `context.cutoff`, non-null on a forward cell
  whose event declares a moment **whose opening date is that moment's own
  trigger**. What it changes is what such a cell is **conditioned on**:
  `provision-snapshot` cuts the snapshot's proceedings and the documents at the
  day after the event opened, so a later moment is provisioned at the
  information set it declares rather than at the corpus's latest snapshot.
  Without the cut, a grant-moment merits cell reads the merits calendar — briefs
  filed, amici filed, the case argued — that only the *briefed* moment declares,
  and nothing but agent discipline keeps the two forecasts apart. The registering
  commit is the one this entry lands in; the boundary takes effect for cells
  provisioned after the promotion carrying it.

  The exception is one **moment**, not one stage: only the cert petition
  baseline declares `opened_at_is_the_moment=False`, because its opening date is
  docketing while the moment it declares is the distribution, so a cut there
  would delete the relist history the cell is conditioned on. Every other
  declared moment is placed, the cert stage's own `cvsg` and `arrival` moments
  included, as is the interim application baseline — whose declared moment *is*
  arrival, so its filing date is the trigger.

  What the cut reaches, and what it leaves, are both part of the boundary. It
  removes the post-cutoff proceedings entries, the post-cutoff documents, and
  the top-level fields carrying a date of their own (`date_argued` and its
  siblings, plus the payload's generation stamp). It does **not** reach the
  undated top-level blocks — counsel and amici, which accrue as a case proceeds
  — so a `truncated` cell carries them as at the pull it was reconstructed from.
  That residual rides `truncated` cells only: a `dated` cell is a genuine
  point-in-time payload and has none of it. So the provenance split is not
  merely evidential strength, it is a difference in what survived, and a figure
  over placed cells owes the `dated`/`truncated` counts beside it
  ([metrics/README.md](../metrics/README.md)).

  The pre-cut cohort of record is the 27 merits predictions of run
  `20260816T111104Z` — 9 `evt-order-judgment` events × 3 predictors, the other
  34 of the 43 minted merits event directories carrying no prediction yet —
  each with `"cutoff": null` and `"snapshot_provenance": "as-stored"`. What
  separates them from a placed cell is the **merits calendar**, not the band:
  distributions are a cert-stage signal that stops at the grant, so those cells'
  frozen counts (1, 2, 3, 5) are already pre-grant and their bands are near
  enough invariant across the boundary. Two cautions on top of that. Read
  `context.cutoff` before pooling forward cells of one moment: null and non-null
  are two information sets. And these cells were placed under a **frozen prompt
  that still describes the snapshot as the latest** — the prompt text is the
  digest's input and moves only at a re-bless — so no cross-cohort claim should
  span that re-bless either.

- Freeze commit: `c2a168eea`, carried to `main` by the promotion tagged
  `promotion/2026-08-26` (merge commit `6d92ed81b`, merged
  `2026-08-26T14:46:40Z`). **`prereg/proc-v4` sits on that carrying merge
  itself, not on the freeze commit** — unlike the three entries above,
  whose tags mark their freeze commits. The placement is stated here
  outright because the `prereg/` namespace blocks update and deletion, so
  it is permanent: the pre-registered baseline tree at this tag is the
  promoted batch's rather than the freeze commit's, and the two carry
  byte-identical process inputs (prompts, registry config, the constants) —
  `c2a168eea` is an ancestor of the tagged merge, so the freeze point
  remains findable through it. The audit, run against the merge tree
  before the tag was minted: the predictor digests are **byte-identical**
  to `prereg/proc-v3`'s (the byte comparison this label substitutes for
  step 4's date comparison — the held-instant paragraph later in this
  entry), and the step-0 re-run held exactly at the authoring counts —
  zero cells under any newly blessed digest, 226 stamped predictions,
  105 retiring-digest evaluations. proc-v4 revises the
  **evaluator half only**. What moved the three evaluator digests is
  `.github/prompts/evaluate.md`: the judge-workspace prune (the committed
  `predictions/` and `evaluations/` trees are hidden from a judge cell's
  working tree for the run and restored after, landing with the prompt
  passages that describe it, per the masking-surface rule) plus the folded
  amendment batch — the `correct`/`brier_score` stamped-over provenance
  note, the `result_capture` reading rule, the terminal-basis
  machine-refusal mirror sentence, the moment-cutoff twin in the forward
  leakage branch, and `retrieved_outcome_material` stated as a boolean. The
  three predictor digests are **byte-identical** to the ones
  `prereg/proc-v3` blessed and carry forward unchanged, so the frozen
  prediction population is continuous across the labels: 226 stamped
  predictions at authoring, every one under a carried-forward digest and at
  or after the instant.

  The freeze instant stays `2026-08-16T00:00:00Z`, deliberately unmoved
  again — and this time the step-4 comparison reads the other way around:
  the instant *precedes* the promotion that carries this commit, which for
  an ordinary freeze would be the botched direction. It is sound here
  because the instant does no work for anything this commit newly blesses.
  The digests entering the set are evaluator-side, which the partition
  records but never gates on (`graded_post_freeze` enforces timing alone),
  and no cell can carry them before the promotion lands their bytes on
  `main` — step 0 at authoring found zero stamped cells with any of the
  three. The enforced half — the predictor digests — is byte-identical to
  what `prereg/proc-v3` blessed, and its instant-versus-promotion audit is
  that entry's, already passed. Moving the instant forward instead would
  drop all 226 stamped predictions from the headline for a change that
  touched no predictor byte. The auditor's check for this label is
  therefore not the date comparison but the byte comparison: the predictor
  digests under `prereg/proc-v4` must equal `prereg/proc-v3`'s. The rule
  this instantiates — hold the instant where the enforced half is
  byte-identical to the prior tag's, audit by the byte comparison — is the
  evaluator-half supersession note in
  [process-version.md](process-version.md#freezing-the-cutover-procedure).

  **The retiring evaluator digests and what ran under them.** proc-v3's
  evaluator digests (`sha256:3aeddcede…` claude-judge, `sha256:8771a0c85…`
  codex-judge, `sha256:b2ed9c208…` gemini-judge) leave the set superseded,
  and 105 committed evaluations carry them at authoring (36/36/33 by
  judge), every one stamped at or after the instant. They stay counted: an
  evaluation's digest is recorded but only its timing is enforced, so the
  supersession changes no headline — this entry is where the blessed
  grading process behind those cells stays recorded now that the constant
  no longer names it. Membership, though, is not the numbers: because the
  evaluator digest records but never partitions, the leakage and
  reasoning-quality series pool across the rubric boundary with no artifact
  marking it. The measured exposure at authoring is degenerate — all 105
  are forward cells graded `not_applicable` and unsuspected, 96 recording a
  boolean `retrieved_outcome_material` and 9 a null the boolean amendment
  closes — so the amendments raise coverage rather than break observed
  variation, and a cross-boundary coverage comparison is a coverage change,
  not a behavior change. One authoring-time fact completes the record: the
  boards' `frozen_process.digests` provenance will name three evaluator
  digests no counted evaluation carries until the first proc-v4 grading
  run — for that interval the partition's evaluator half is answered by
  this entry, not the artifact. The step-0 re-run at the promotion
  confirmed the counts here unmoved.

- **The band risk set's reachable-ladder construction, 2026-08-28.** No freeze
  commit belongs to this entry, and no data-visible boundary comes with it
  either: it is the **scoring baseline**, the member
  of [process-version.md](process-version.md)'s list with no boundary at all.
  It re-bases `prediction_base_rate` under unchanged digests, an unchanged
  `base_rate_basis` (`risk_set`) and an unchanged
  `base_rate_salience_version` — the scorer version does not move, only the
  population one of its bands is pooled over. The statpack built each band's
  risk set as a prefix over the band *order*, which under a caption-banded
  scorer puts every `federal` petition in the risk set of bands its caption
  made unreachable; it is now pooled over each petition's own reachable ladder
  (`SalienceScorer.reachable`, [salience.md](salience.md)). Measured on packs
  built either way from one corpus blob (latest pull `2026-08-27`, latest
  snapshot `2026-07-13`), pooled at an OT2026 anchor over the full `sal-v3`
  lookback: `federal` unmoved at 0.7114 (n=201), `high` 0.4117 → 0.3490
  (1161 → 960), `state` 0.3642 → 0.2156 (1425 → 371), `elevated`
  0.1991 → 0.1646 (3737 → 3165), `baseline` 0.0652 → 0.0504
  (13163 → 12591); every *terminal* rate and every `sal-v1` segment is
  byte-identical across the pair.

  **No published number is re-based.** At this commit the ledger's 144
  committed evaluations record 24 `terminal` bases and 120 nulls and **zero**
  `risk_set` bases, and both `metrics/leaderboard.json` and
  `metrics/claim-scores.json` are empty boards (`evaluations_total: 0`). So the
  boundary this entry stands in for separates no two scored cells, which is what
  makes this the moment to take the change rather than a later one. The
  corrected rates reach cells at the first metrics refresh after the promotion,
  as a salience flip's do.

  One inconsistency stays on the record until the next re-bless: three passages
  of `.github/prompts/predict.md` — the band-null cert fallback, the
  version-mismatch fallback, and the arrival anchor — name the weakest band's
  bracketed `reached` rate as the scored segment's unconditional rate. Under the
  reachable ladder that figure is the *private* class's rate, and no single cell
  of the rendered table carries the segment-wide one. The correction is a prompt
  byte, so it moves all three predictor digests and belongs with the next freeze
  label rather than beside the construction.

- **The interim amicus reading, 2026-08-28.** The counter behind
  `amicus_briefs` admits the plural (`amic(?:us|i)\s+curiae`) — a change to a
  number both ends of the `amicus-increment` claim are computed from, under an
  unmoved digest and with no data-visible boundary: it is a scoring-baseline
  member of [process-version.md](process-version.md)'s list, like the entry
  above. The old reading missed roughly half of all amicus-naming docket
  entries (measured 49.5% → 4.1% on the 2026-08-27 blob), and the corpus
  column max-latches, so the corrected counts reach open applications on their
  next poll while every frozen context keeps the count it was provisioned
  with. **Nine pending cells** — `scotus/73279700`, `scotus/9526000163`, and
  `scotus/9526000245`, one `evt-motion-disposition` event each across three
  predictors — are frozen at `amicus_briefs = 0` with the column also 0 at
  this commit: after the first post-promotion poll their `amicus-increment`
  compares an old-reading context against a new-reading outcome, so a
  resolution of 1 on those cells is the measurement widening, not a docket
  movement, and **their increment is not claimable as a forecast hit**. The
  three `scotus/9526000203` events are unaffected — their column already read
  2 under the old counter, so both ends move together.

- **`sal-v4` registered, inactive (the `dist-v2` distribution parse),
  2026-08-28.** No freeze commit belongs to this entry, on the `sal-v3` pattern:
  the salience version sits outside the process digest (`pipeline_sha` is not an
  input), carries its own data-visible boundary
  (`context.salience_version`), and a registration re-blesses nothing. This
  commit adds the `sal-v4` scorer with `sal-v3` still active — the scorer reuses
  `sal-v3`'s score, band, carve-out and reachable **callables** and its band
  **tuple**, and changes one field, `distribution_parse`, from `dist-v1` to
  `dist-v2`. Nothing the live pass selects, latches, or stamps moves at this
  commit; what changes is that `statpack.json` and `salience-replay.json` now
  carry a fourth version's bands. Carried to `main` by the promotion tagged
  `promotion/2026-08-28-2` (merge commit `01c85e2c8`, merged
  `2026-08-28T22:50:08Z`). No freeze procedure fills those three: the freeze
  step that fills placeholders fires at a `prereg/` tag and this entry has no
  freeze commit, so they are the carrying promotion's author's to complete, and
  the promotion PR carries the instruction.

  **The statistical review of record**, quoted verbatim because the census
  artifact carries a one-day retention and is deliberately uncommitted. Two of
  its sentences lean on the issue that proposed the parse, glossed here so the
  record stands alone: that issue's premise was that `dist-v1` inflates the
  relist trajectory by counting ancillary paper, and it named three example
  cells whose counts it said sealing-motion lines had lifted. The review
  confirms those three and qualifies the premise — the inflation sits on decided
  rather than live pending dockets.

  > The dist-v1 → dist-v2 distribution census produced by run-analytics run
  > 33196262688 (main @ 737696ff7c, 2026-08-28, corpus_sha256 =
  > b16b856fcc8a247f0e5df5bc0f22fca207c011c85ea1fa870a6f2be2f9abb9e3) is
  > accepted as the statistical review of record for registering sal-v4, scoped
  > to a sal-v4 that is sal-v3 with the pinned distribution parse changed and
  > nothing else. The artifact was reproduced byte-identically against the named
  > corpus blob by re-running fedcourts distribution-census, and every field was
  > re-derived a second time by an independent implementation. Coverage is 13,839
  > of the 13,840-row frame (99.993%); the single unobservable row is an OT2025
  > pending case and reconciles frame_pending 499 against pending 498 exactly.
  > The delta is 181 changed counts (1.308% of the observable frame) and 159
  > changed bands (1.149%), all downward — count_increased = 0, the full 25-cell
  > zero-filled transition square has every strengthening cell at zero, and a
  > line-level check across all 181 changed cases found no entry matched by
  > dist-v2 that dist-v1 does not also match, so the nesting is observed rather
  > than assumed. An exhaustive audit of every dropped line shows the delta is
  > ancillary paper without exception (176 MOTION, 5 APPLICATION, 2 SUGGESTION, 2
  > MOTIONS, 2 clerk-typo MOTOIN, and one Petition for Rehearing), with no
  > genuine petition distribution dropped and no kept line naming a motion,
  > application, or rehearing; the three cells flagged in #1256 are in the changed
  > set with exactly the sealing-motion lines the issue named. Change rates are
  > homogeneous across the eight complete Terms (pooled 1.424%, χ² = 10.12 on 7
  > df, p ≈ 0.18), and moves concentrate in high (41/1,023) and elevated
  > (118/2,364) as the count-monotone band functions require. One substantive
  > finding qualifies #1256's premise: the inflation is concentrated on decided
  > rather than live pending dockets (pending 0.80% vs decided 1.33% of counts),
  > the maturity confound in its expected direction, so the census figure is an
  > upper bound on what the gate sees at selection time. No anomaly blocks
  > registration. This is the input-level cut only: the corpus distribution_count
  > re-derivation, the statpack rebuild, the relist-tier re-measure, and the
  > salience-replay rank-and-cap remain the activation's own steps, and this
  > review does not license activation.

  **Four findings carried onto this record.** Findings (2) and (3) are the
  quoted review's own numbers; (1) and (4) are not in it — (1) is a further
  observation from the same census artifact, re-derived at this commit against
  the blob quoted above, and (4) is a constraint stated here rather than
  measured. (1) Five cases read never-distributed under `dist-v2` — four falling 1 → 0, and `scotus/68076851`
  3 → 0 on three motion lines. The four are relist-0 under both readings
  (`max(0, count − 1)`), so their bands do not move. The fifth's does, and the
  correction is recorded here rather than carried forward: it crosses both
  cutpoints and bands `high` → `baseline`, so it belongs among finding (3)'s 41
  `high`-leavers and not beside the other four. Checked at this commit against
  the blob quoted above — `scotus/68076851` reads `distribution_count` 3 under
  `dist-v1` and 0 under `dist-v2`, primary rate 0.4197 → 0.0337, no CVSG, and a
  caption `caption-v2` does not read `federal`. What is true of all five is the
  cohort key: `distributed_for_conference` is deliberately unversioned, so they
  sit in the conference cohort an ancillary paper was distributed for while
  carrying a zero count. A declared divergence of the unversioned key, recorded
  here rather than rediscovered later as a defect. (2) `elevated → baseline` is
  118 rows, 5.0% of
  `elevated`, so activation step 2's statpack rebuild is **expected to move that
  band's published rate**, not merely to relabel its members; a rebuild leaving
  the rate unmoved is evidence the rebuild did not happen. (3) 41 cases leave
  `high`, the always-include tier, which is a real selection consequence rather
  than a labelling one — leaving `high` means leaving the carve-out for the rank
  contest — and is `salience-replay`'s question, not the census's. (4) The
  sequencing is an **invariant**: `sal-v4` must never be made active before the
  corpus `distribution_count` column is re-derived under `dist-v2`, or frozen
  contexts would carry `dist-v2` counts against `dist-v1` column counts and the
  relist-increment claim's "the count never falls" premise would break upward.
  Activation step 1 already orders this (*The distribution parse* in
  [salience.md](salience.md)); it is stated here as a constraint rather than an
  accident of ordering. What the test suite pins is only the **label** —
  the active scorer's `distribution_parse` equals the parse registry's
  default — which a commit moving `SALIENCE_VERSION` and that default together
  would satisfy while the stored column still held `dist-v1` counts. The check
  that settles the invariant is therefore a data check, not a test: after the
  writer re-derivation and before the flip, a census of the column's own
  reading against `dist-v2` must report `count_changed = 0`.

  **One artifact reads wrong-by-label until activation step 2, harmlessly.**
  `statpack.json` bands every registered version off the corpus's single
  `distribution_count` column, which holds `dist-v1` counts, so the
  `alt_segments` block labelled `sal-v4` in every pack rendered between this
  commit and the column re-derivation is `sal-v3`'s pool under a `sal-v4` label.
  No number is corrupted by it and nothing consumes it: a version-pinned pool is
  read only by a prediction frozen at that version, and no prediction can freeze
  at an inactive one. It is recorded because the block is committed and dated,
  and a later reader comparing packs across the activation would otherwise read
  the correction as a population shift.

  **The rank-and-cap read, and why it settles nothing.** `fedcourts
  salience-replay --terms 2022,2023,2024` was run at this commit with `sal-v4`
  registered, against the blob the review names (`corpus_sha256` as quoted above;
  latest pull `2026-08-28`, latest stored snapshot `2026-07-13`, and the
  local pointer warning that the blob on disk is not the committed ref's — the
  same blob as the review's, so the comparison holds). What it observed: over the
  four cells that select anything — OT2023 and OT2024 at `distribution-1` and at
  `resolution` — the selected set is identical under `sal-v3` and `sal-v4`. The
  other five cells of the 3 Terms × 3 policies select nothing under either scorer
  (all three OT2022 cells, both `arrival` cells) and carry no evidence either
  way. The parse bites in one cell only, OT2023 at `resolution`, where four
  projected dockets change count — two falling `high` → `elevated`
  (`scotus/72479901`, `scotus/72480027`) and two `elevated` → `baseline`
  (`scotus/72479771`, `scotus/72482969`) — and the selected set is identical at
  149 petitions with only the provenance of two picks moving, 48 → 46 carve-out
  picks against 101 → 103 rank fills, the two `high`-leavers losing their
  guarantee and being re-picked by the fill. Set identity was checked case by
  case with a scratch script; the committed artifact publishes counts only, so it
  cannot be re-derived from the cell.

  That zero is **not** a bound on disruption in the reassuring direction. The
  slice the replay could reconstruct is not a sample of the frame but its granted
  end: measured on this blob, the reconstructable rows carry grant-family rates
  of 0.4207 (OT2023, 69/164) and 0.4000 (OT2024, 90/225) against 0.0318
  (38/1,194) and 0.0009 (1/1,087) on the rows it could not read, over Terms whose
  own rates are 0.0788 and 0.0694; OT2024's read slice holds 90 of that Term's 91
  grants, and OT2022 reconstructs nothing at all. Within it the gate selects 149
  of 164 readable OT2023 rows and 1 of 29 cohorts is capacity-bound, so the rank
  contest has almost no opportunity to exclude a demoted petition. The run
  therefore has close to no power to detect selection disruption, and its zero is
  consistent with any amount of it at full coverage. No rate, band mix, precision
  or recall from it transfers to the frame.

  The cause is data availability, not the replay's method, and `corpus_sha256`
  invites the wrong reading of it: the hash names the SQLite **index**, while the
  snapshot payloads live in the per-case content store this checkout does not
  have wired. Re-running the census itself here, against that same blob, observes
  811 of the 13,840-row frame (5.9%) where the `run-analytics` census reached
  99.993% — so the gap between the two artifacts is the store, not the
  reconstruction. That re-run also corroborates finding (1) independently:
  `scotus/68076851` appears in its `band_changed` ids, and its transition square
  carries the single `high` → `baseline` move.

  **This finding is provisional.** The census's 41 `high`-leavers are not shown
  to keep their funding, and the instrument that would show it is the same replay
  run where the store is wired — `run-backtest`'s salience-gate replay, a
  dispatch rather than a local command. Until that runs, the selection question
  activation turns on is open.

- **`sal-v4` activated (the `dist-v2` distribution parse), 2026-08-28.** A
  distinct entry rather than a completion of the registration entry above: that
  entry is landed, and the only editable content an entry ever has is its
  `<FILL:>` promotion placeholders, which are the carrying promotion's and not
  activation's. This follows `sal-v3`'s precedent, where registration and
  activation are recorded together because they shared one entry's lifetime; here
  they did not. No freeze commit belongs to this entry either, on the same
  argument: the salience version sits outside the process digest (`pipeline_sha`
  is not an input), carries its own data-visible boundary
  (`context.salience_version`), and a flip re-blesses nothing.

  **The flip is one commit moving two constants**, and the pairing is a
  requirement rather than tidiness. `SALIENCE_VERSION` goes `sal-v3` → `sal-v4`
  and `cert_signals.DEFAULT_DISTRIBUTION_PARSE` goes `dist-v1` → `dist-v2`
  together, for two reasons. The active-scorer-parse-equals-registry-default
  alignment is test-pinned, so a split commit fails the suite. And the re-latch
  paths — the live poll, `refresh-dockets`, the Term walker — write the
  **default** parse's count, so a flip that moved only the version would keep
  writing `dist-v1` counts into a column re-derived to `dist-v2` and re-corrupt
  it pull by pull. Neither reason is discretionary.

  **The consumer chase.** Nothing in `src/` branches on either literal — the
  design is registry dispatch throughout — so the statpack's `alt_segments`
  split, `salience-replay`'s per-parse projections, `registered_versions()`'s
  active-first ordering, the cell-context parse hand-off and every
  `salience_version` stamp follow the constants without edit. Three things did
  need a decision. `sal-v1` through `sal-v3` keep `distribution_parse =
  "dist-v1"`, including the `SalienceScorer` field default they take it from,
  which is now deliberately *not* the registry default: re-pointing it would
  re-read three frozen versions. The `distribution-census` command's
  `--candidate-parse` became **required**, because with the incumbent following
  `DEFAULT_DISTRIBUTION_PARSE` a bare post-flip invocation would have been a
  parse-against-itself census reporting no movement on every row. And the
  `run-analytics` census dispatch defaults were left at `dist-v1` → `dist-v2`,
  which now reads the activation backwards rather than arguing a candidate — a
  re-derivable check on what the flip moved, not a review of anything.

  **Activation step 2's decision, taken here: the outgoing version's frozen
  predictions re-baseline, and the block does not record its parse.** The pack
  bands every registered version off the one `distribution_count` column, so once
  that column reads `dist-v2` the `sal-v1` / `sal-v2` / `sal-v3` `alt_segments`
  blocks are measured on populations their declared parse never defined, and a
  prediction frozen at `sal-v3` reads one. Recording the parse on the block was
  the alternative; it is a schema change on a committed artifact, with its own
  drift check and review, and it would label the substitution rather than repair
  it. Stating it does the same work: a `sal-v3` cell's published baseline after
  the rebuild is `sal-v3`'s band rule over `dist-v2` counts — `sal-v4`'s pool
  wearing `sal-v3`'s name — and the substitution is bounded by the census delta,
  159 changed bands on 13,839 observable rows, 1.149% pooled. The bound that
  matters is per band, because the movement concentrates: `elevated` 118 of 2,364
  (5.0%) and `high` 41 of 1,023 (4.0%), four to five times the pooled figure, and
  `high` is the always-include tier — which is also why the registration entry
  expects `elevated`'s published rate to move. Those three figures are the
  registration census's, taken on blob `b16b856f…`, not this entry's
  `c6b43484…`; the frame sizes coincide and the blobs do not.

  **Activation step 3, the relist-tier re-measure.** Basis: a **snapshot-side
  recount**, not a column read — the local blob still held `dist-v1` counts when
  this was taken, so the column-side confirmation lands with the post-apply
  statpack rebuild. Corpus blob
  `c6b43484cab17ac7495d23d1c81f01ad686be098914d88cbe6d9b9cb7085e085` (latest pull
  `2026-08-28`, latest stored snapshot `2026-07-13`), store-served, read over the
  distribution census's own frame (live-slice, paid, modern-cert, parseable Term)
  on the resolved rows, both parses counted off each case's latest live-shaped
  snapshot so the readings are compared on identical rows. Frame 13,840 rows;
  13,839 observable, 1 unobservable, 13,341 resolved. A **fit diagnostic for a
  ranking constant, not a scoring baseline**: it pools the whole walked range with
  no own-Term exclusion and no `base_rate_lookback_terms` cut, so no figure here
  is the per-Term prior-Terms-only band rate an evaluator scores against.

  Reported in **both** granted-side vocabularies, because the mis-fit below lands
  in different tiers under each. `GRANTED_DISPOSITIONS` (the binary target) and
  `GRANT_FAMILY_DISPOSITIONS` (the statpack's published `est_grant_rate`) both
  include GVR and coincide on this frame, whose only resolved dispositions are
  granted, GVR, denied and dismissed; a granted-only cut dropping GVR is a third
  vocabulary the pipeline neither scores nor publishes.

  | relist tier | n (`dist-v1` / `dist-v2`) | granted-only (`dist-v1` / `dist-v2`) | grant family (`dist-v1` / `dist-v2`) | fitted constant |
  | --- | --: | --: | --: | --: |
  | 0 | 9,768 / 9,892 | 0.01188 / 0.01284 | 0.01730 / 0.01820 | 0.008 |
  | 1 | 2,566 / 2,486 | 0.08262 / 0.08407 | 0.13016 / 0.13475 | 0.078 |
  | 2+ | 1,007 / 963 | 0.24926 / 0.25234 | 0.38431 / 0.38941 | 0.394 |

  Pending rows sit outside those denominators, censored unevenly across the tiers:
  449, 42 and 7 under `dist-v2`, being 4.3%, 1.7% and 0.7% of each tier's
  observable rows.

  A corroboration falls out of the same run: over all 13,341 resolved observable
  rows the **stored column's** tier assignment is identical to the snapshot-side
  `dist-v1` recount, tier for tier and disposition for disposition. That is the
  pre-apply state observed rather than assumed — this blob's column holds
  `dist-v1`, which is the premise the merge hold below rests on. The `dist-v1`
  reading also reads close to the committed statpack's relist section (0 → 1.2%,
  1 → 8.0%, 2 → 26.3% and 3+ → 23.3%, pooling to ≈24.8% at 2+). That is a
  sanity check on the frame, not an identity: the statpack cut is
  **denial-reweighted** while this one is raw (the census frame raises on
  `sample_weight != 1` and did not raise, so it carries no weighted rows), and it
  splits 2 from 3+ where this pools them. That the statpack's own frame is
  effectively unweighted too is **inferred** from the two agreeing, not checked —
  its cut carries no parseable-Term filter and a different vintage. The agreement
  to within a few tenths of a point says the reweighting does not bite hard on
  this cut; it does not license quoting one number for the other.

  **What the parse moves, and what it does not.** The tiers move by 0.096, 0.145
  and 0.308 percentage points, all upward — which is a **mixture shift, not a
  uniform improvement**: the overall grant rate is fixed at 579/13,341 = 4.340%
  under either reading, so all three conditional rates can rise only because mass
  moved into the low-rate tier. Two flows are exact rather than inferred, since
  relist-2+ is the ceiling of a count that can only fall (pure outflow) and
  relist-0 its floor (pure inflow): 44 resolved rows carrying 8 grants left 2+
  (0.1818, below 2+'s 0.2493), and 124 resolved rows carrying 11 grants entered 0
  (0.0887, far above 0's 0.0119). So the petitions `dist-v2` demotes grant at
  roughly the relist-1 level rather than the relist-0 level, and demoting them
  costs a little top-to-bottom separation: the 2+-to-0 rate ratio falls from
  20.99× to 19.65×, and on the grant family from 22.21× to 21.40×, so the
  direction does not depend on the vocabulary. Whether that ~4–6% loss is real or
  sampling noise is not settled by 11 grants on 124 rows, and it is not what the parse was argued for —
  `dist-v2` is a correctness claim about what the DISTRIBUTED phrase means, not a
  discrimination improvement. Recorded so a `sal-v5` refit starts from it rather
  than from the assumption that a narrower reading is a cleaner one. Nothing in it
  moves a cutpoint.

  **The mis-fit finding, recorded and not corrected — and which tier mis-fits
  depends on the vocabulary.** Against **granted-only** the 2+ constant is the
  outlier: 0.394 against 0.25234 is 1.56×, +14.2 points, while relist-0 and
  relist-1 sit *below* their measured rates at 0.62× and 0.93×. Against the
  **grant family** — the vocabulary the statpack publishes in, and the one
  `pipeline/salience.py` names as the constants' source — it inverts: 0.394
  against 0.38941 is **1.01×, +0.46 points**, essentially exact, and the mis-fit
  moves to relist-0 (0.44×) and relist-1 (0.58×). One constant is nearly right in
  each reading and never the same one, so the three are not all estimating the
  same quantity on this frame. Which of them is wrong is not answerable from this
  measurement, only from the fitting frame they were taken from, which it cannot
  recover.

  Two things it does establish. The divergence is **invariant to the parse**
  (granted-only 1.56× at `dist-v2` against 1.58× at `dist-v1`; grant family 1.01×
  against 1.03×), so the parse does not cause it. And **corpus drift does not
  cause it either**, at least at 2+: the fresh `dist-v1` reading 0.24926 agrees
  with the committed statpack's own 2+ pooling (≈0.2489) to within four
  hundredths of a point, so a corpus that had drifted 14 points away from the
  constant would have had to drift the published pack with it, and it did not.
  The cause is recorded as unidentified rather than guessed at.

  Two constraints travel with these numbers to whoever refits. They are a fit
  diagnostic, **not** a scoring baseline — no own-Term exclusion, no
  `base_rate_lookback_terms` cut — so none of them is the per-Term
  prior-Terms-only band rate an evaluator scores Brier skill against. And the tier
  is read off each case's **latest** live snapshot, its final count, while the
  score applies these constants to the count **as at prediction**; a refit taking
  them at face value would fit final-count rates for prospective use on
  systematically lower as-at-prediction tiers.

  The cutpoints do **not** move, and the reason is more than the registry's rule
  against editing a frozen constant: the always-include **floor** is entangled
  with the 2+ constant, and entangled *differently* under each vocabulary.
  `salience.floor` is 0.28, set to sit at the relist-2 / CVSG grant-rate band.
  Substituting the **granted-only** 0.25234 for 0.394 leaves the *band* alone
  (every 2+ petition still clears the `high` cutpoint of 0.20) but drops it out of
  the always-include carve-out for every originating circuit except `cadc`, the
  only nudge large enough to reach the floor: 0.29804 against `ca5`'s 0.27804,
  `ca9`'s 0.26914 and an unlinked petition's 0.25734. Substituting the
  **grant-family** 0.38941 instead changes nothing, since it already sits above
  the floor. So one refit silently strips the always-include tier of nearly every
  2+ petition and the other is a no-op, and which it is turns on a vocabulary
  choice no one has taken on the record. All arithmetic checked at this commit
  against the shipped `config/tracking.yaml`. A refit must therefore re-decide the
  floor **and** the vocabulary in the same version — which is the `sal-v5` agenda
  this finding feeds, argued from this re-measure as the census argued `sal-v4`.
  (A 2+ petition carrying a CVSG keeps the carve-out under either substitution:
  its primary signal takes the CVSG rate 0.283, and CVSG is its own carve-out
  predicate besides.)

  **One seam this activation opens and does not close.** A cell frozen under
  `sal-v3` carries the wider reading's count while the re-derived column serves
  the narrower one, so on a docket the readings disagree about, the
  relist-increment claim's strict comparison can read a genuine relist as no
  increment. The direction is the safe one — a **suppressed** increment, never a
  spurious hit. Measured rather than assumed: of the 106 committed prediction
  cells carrying the claim, across 36 cases, exactly **9 cells on 3 cases** sit on
  dockets the parse moves — `scotus/73500263`, `scotus/73500287` and
  `scotus/9026000013`, three predictors each, all frozen at `sal-v3`. Their frozen
  `context.distribution_count` reads 2, 2 and 1 (the `dist-v1` reading), and the
  `dist-v2` recount of the same snapshots reads 1, 1 and 0 — which is why those
  are also the post-apply column targets the spot check below names, and why the
  check is re-derivable from the committed artifacts.
  All three cases are **pending** on this blob, so no such claim has been scored
  and none can be until they resolve. Masking those cells — the frozen version's
  parse against the column's — is a scoring change and is deliberately not made
  in this commit; it is a follow-up with its own review.

  **The pre-flip data check, corrected.** The registration entry above states
  that the invariant is settled by "a census of the column's own reading against
  `dist-v2` reporting `count_changed = 0`". That check is weaker than it reads and
  is recorded here as superseded rather than by revising it: `distribution-census`
  takes **neither** side off the column (both counts come off the latest
  live-shaped snapshot, by design — the column holds one parse's answer,
  max-latched, so it could not supply either side on equal terms), so after the
  re-derivation the named census is `dist-v2` against `dist-v2` and its zero is a
  tautology about the label. What actually settles it is the apply dispatch's own
  reported applied-row count, plus a spot check on the three cases named above:
  their stored `distribution_count` must read 1, 1 and 0. That check is cheap, it
  is a `query` away, and it fails loudly if the writer's latch bypass did not
  bite. It must be taken on the far side of the window named next, not before it.

  **The re-inflation window, and why the hold runs past the merge.** `run-pull`'s
  `live` mode is scheduled (`47 4,10,16,22`), and a scheduled workflow runs from
  the **default branch** — where `DEFAULT_DISTRIBUTION_PARSE` is still `dist-v1`
  until this flip is *promoted*, not merely merged to `staging`. Every live poll
  between the apply dispatch and the promotion therefore recomputes the wide count
  for the rows it touches and writes it through `upsert_rows`, whose
  `distribution_count` latch is `MAX(COALESCE(excluded, cases), COALESCE(cases,
  excluded))` — so the re-inflation is **permanent**, and no later `dist-v2` write
  can lower it. Once `sal-v4` is live those rows are the upward break the whole
  invariant exists to prevent: a narrow frozen count against a stuck-wide column,
  producing spurious relist-increment hits and a band stronger than `sal-v4`
  declares. The exposed set is small and quiet, which is what makes it dangerous —
  the parses disagree on ~0.8% of pending rows, and the three cases named above
  are pending, so they sit squarely in the poll rotation.

  **This commit is MERGE-HELD** until the maintainer's re-derive apply dispatch
  has run, and the re-derivation must be **run again after the promotion lands**
  (or the live writers held across the window above). It is the sequencing
  invariant, not a preference: the flip must not reach `staging` before the column
  it depends on is re-derived, because the test suite pins only the label and
  would pass with the stored column untouched — and it must not sit on `main`
  over a window in which the outgoing parse is still writing. Carried to `main` by
  the promotion tagged `promotion/2026-08-28-2` (merge commit `01c85e2c8`,
  merged `2026-08-28T22:50:08Z`). No freeze procedure fills those three — this
  entry has no freeze commit — so they are the carrying promotion author's to
  complete.

  **The scored window opens at the first post-promotion metrics refresh, not at
  the flip**, as it did for `sal-v2` and `sal-v3`. The committed `statpack.json`
  carries no `sal-v4` block, so until the rebuild every `sal-v4` cell reads the
  version-pinned pool's designed `None` — legitimately empty, supporting no
  claim. The `elevated` band's published rate is **expected to move** at that
  rebuild (finding (2) of the registration entry: 118 rows, 5.0% of the band); a
  rebuild leaving it unmoved is evidence the rebuild did not happen.

  **The selection question stays open.** The registration entry's replay run has
  close to no power and the activation does not add any. The instrument is
  `run-backtest`'s salience-gate replay with the content store wired — a
  dispatch, not a local command — and until it runs, whether the 41 `high`-leavers
  keep their funding is unanswered.

- **The relist-increment parse mask, 2026-08-28.** A masking-surface change to
  the mechanical claim family, closing the seam the `sal-v4` activation entry
  above records as "one seam this activation opens and does not close". Each
  end of the claim's pair now records the distribution parse it froze under —
  the prediction side already did, via the parse its stamped `salience_version`
  pins, and `ResolutionSignals` gains a `distribution_parse` stamp the outcome
  writer fills with the column's declared parse at resolution.
  `relist-increment` resolves **unavailable** (`ClaimScore.outcome` null)
  wherever the two labels differ, wherever the outcome's block carries **no
  parse stamp**, and wherever the frozen count carries no `salience_version`
  stamp — in every case the record does not disclose a comparable pair, the
  same doctrine as the existing `None`-input masks. The mask reads only the
  committed pair, never the parse live at scoring time, so re-scoring any cell
  reproduces its resolution.

  **An unstamped block is never assigned a parse from its vintage.** The
  tempting fallback — read unstamped as `dist-v1`, the column's original
  reading — fails on ordering twice over. The `dist-v2` activation promoted
  **before** this stamp shipped, so `main`'s scheduled writers spend the
  window between the two promotions writing `dist-v2` counts into unstamped
  blocks; and the only date an outcome carries is the docket's **decision**
  date, while a block is written when a poll or backfill reaches the docket —
  days later on live rows, years later on backfills — so not even a date gate
  can separate the eras. A date-blind or date-gated `dist-v1` fallback would
  read an in-window block as the wide parse, agree with every `sal-v3`
  freeze, and resolve exactly the suppressed mis-grade this change refuses —
  silently and permanently. Masking every unstamped block costs nothing the
  record could have paid: a sweep at this commit found 12,666 outcomes, 9,686
  carrying a signals block, **zero stamped, newest resolved 2026-06-30**, and
  none of them beside a claim-carrying prediction — the fallback had no
  legitimate consumer to lose.

  What it reaches: a cell whose freeze and resolution **straddle** the
  `dist-v2` activation, in either direction — a `sal-v3` freeze against a
  `dist-v2`-stamped block reads low and could suppress a genuine increment; an
  active-version freeze against a wider-parse block reads high and could mint
  a spurious one. At this activation that is the **whole committed claim
  cohort: 106 cells across 36 cases, every one frozen at `sal-v3` and every
  one on a still-pending event**, so each will resolve against a stamped
  `dist-v2` block and its relist-increment claim resolves unavailable — the
  claim's first scorable cohort is the post-flip `sal-v4` cells. The mask is
  declared **before any such claim can resolve**, which is the timestamp this
  entry witnesses. The nine cells on three cases the entry above names
  (`scotus/73500263`, `scotus/73500287`, `scotus/9026000013`, three predictors
  each) are the subset whose stored *counts* the two parses actually move; the
  other 97 mask equally, because agreement at freeze time cannot promise
  agreement over the docket's remaining life and the committed pair discloses
  only the labels. The treatment that would have recovered them — stamping the
  count under **both** registered parses on `ResolutionSignals` — is
  deliberately not taken: the outcome writer reads `row.distribution_count`, a
  single max-latched column, so a second reading would need a resolution-time
  payload recount, and the latch means the stored value is not a clean
  single-parse read for polled rows in any case. No committed grade moves
  under any arm of the mask: the same sweep found every one of the 106
  claim-carrying cells on a still-unresolved event — no committed outcome, no
  stamped claim block anywhere in the cert family. No published number moves at
  this commit — the claim's baseline
  is the registered `None` (no strictly-prior relist cut exists), so this is a
  masking-surface declaration, not a scoring-baseline move — and no digest
  moves: claim resolution is harness-side arithmetic outside the process
  digest.

- **The post-freeze proc-v3 predictor cohort declared shakedown; the counted
  record opens at `proc-v5`, 2026-08-29.** A boundary declaration rather than
  a freeze: no digest and no constant moves at this commit, and it is made
  now because its evidentiary value is its date. The declaration: **every
  prediction stamped under the three predictor digests `prereg/proc-v3`
  blessed** — byte-identical under the `proc-v4` label, whose freeze
  re-blessed the evaluator half only — **is shakedown, not the counted
  record, for the long-conference claim window; the counted record opens with
  the predictor-half re-bless labeled `proc-v5`**, and no claim pools across
  that boundary in either direction — nor across the salience boundary the
  cohort's cert cells straddle beside it, their contexts frozen at `sal-v3`
  while the active scorer is `sal-v4` (the activation entry above registers
  that rule). Measured at this commit (the staging
  tree): **231 stamped predictions** carry those digests, 77 per predictor
  (226 labeled `proc-v3`, 5 labeled `proc-v4` with the same bytes — the
  continuity the proc-v4 entry above records is exactly what this declaration
  ends).

  **What the date proves, stated exactly.** For the claim window this
  declaration governs — the cert-stage record the long conference resolves —
  it precedes every outcome: **zero** of the cohort's cert-stage predictions
  sit on an event with a committed outcome at this commit, so the beta is
  declared while every cert outcome is unknown, which is the standard a beta
  claim needs. The cohort's full partition, so no slice reads as chosen:
  **cert 105** cells (57 arrival, 30 cvsg, 18 distribution) — 0 resolved;
  **merits 87** (66 grant, 21 briefed) — 0 resolved; **interim 38** (20
  arrival, 9 response-filed, 9 response-requested) — **21 resolved**; and one
  stage-less cell, unresolved. The interim slice is not clean and is stated
  rather than hidden: those **21 predictions on 7 already-resolved
  application events** (9% of the cohort, 55% of its interim slice) resolved
  before this entry, so for those cells the declaration is *after* the
  outcome and creates no pre-registered boundary. The committed frozen-scope
  board already reads them — 54 gradings across the three interim stage
  blocks, carrying the registered interim base rate
  (`pipeline.base_rates.interim_base_rate`; `segment_base_rate` 0.133 on
  these cells) and a published per-predictor Brier skill against it, at n=2
  events per block, spanning −0.489 to +0.804 across the three predictors.
  What limits the damage is what those figures were already: the interim
  stage is unranked and pools into no cert figure or headline, and the
  metrics contract already registers that an interim skill number is not by
  itself evidence of forecast skill — its base-rate pool is the whole
  substantive slice while the scored cells are reserve-selected on the
  escalation ladder. Those figures are the cohort's, they are visible now,
  and the enforcement paragraph's "claim nothing from them" is what governs
  them. Their grading series will still split at the `proc-v5` boundary, and
  any interim series later published across it must state this paragraph.

  The grounds, all on the record before this entry: the cohort ran under a
  frozen prompt whose amendment debts moved the information set it describes —
  the prompt still calls the provisioned snapshot the latest while the moment
  cutoffs bound it (the moment-cutoff entry's own caveat, 2026-08-17, above),
  the arrival-anchor
  instruction points a state-caption arrival cell at the weakest band's rate
  where the reachable ladder scores it against its own class floor an order
  of magnitude higher, and the first post-freeze rounds surfaced provisioning
  defects (#1296 — later-moment forward cells provisioned with the latest
  snapshot instead of their moment's information set — and #1298 — cells run
  silently against a missing record directory), whose
  affected cells hold heterogeneous information sets. Excluding such cells
  after their outcomes resolved is the move an
  external evaluator would not accept; declaring the cohort a beta before its
  claim window's outcomes exist is the alpha ledger's own boundary, one label
  later.

  **Enforcement follows at the `proc-v5` freeze, not here.** The re-bless
  replaces the predictor digests in `FROZEN_PROCESS_DIGESTS` and moves
  `FROZEN_SINCE` past its carrying promotion (the third supersession shape,
  [process-version.md](process-version.md)), which de-counts the cohort from every
  frozen-scope artifact mechanically. Until that promotion lands, committed
  boards built under the current constants still count the cohort — read
  them, from this entry's date forward, as shakedown figures awaiting their
  de-count, and claim nothing from them. The `proc-v5` freeze entry states
  the final de-counted census and points here as its licence.

- Freeze commit: `0b019da58`, to be tagged **`prereg/proc-v5`**
  per step 4 — on this freeze commit itself, once its carrying promotion
  lands and the instant audit passes (`proc-v4`'s merge-placed tag is the
  recorded anomaly, not the rule). Blesses the six proc-v5 digests — the three
  **predictor** digests moved by the predict-prompt amendment batch below,
  and the three **evaluator** digests carried forward byte-identical from
  `prereg/proc-v4` — and sets the freeze instant **`2026-09-05T00:00:00Z`**,
  moved past the carrying promotion per the ordinary step-4 rule: the
  predictor half moves bytes, so the held-instant exception cannot apply and
  the auditor's check is the date comparison, promotion merge at or before
  the instant, instant before the first counted run. The instant is guessed
  generously late on a one-sided trade: predict is label-triggered, and the
  live channel's transition-queued cells before the instant merely land as
  shakedown, while a promotion slipping past the instant forces the
  proc-v3 remedy — bump the constant in a follow-up promotion **before**
  tagging (the `prereg/` namespace burns a tag minted over a bad instant),
  and confirm no stamped cell carries a `stamped_at` in the gap; the check is
  not vacuous, because `graded_post_freeze` tests timing with no digest test
  at all, so a gap evaluation would read as counted while the constant was
  still editable. Carried to `main` by the
  promotion tagged **`promotion/2026-08-29`** (merge commit `39a3a9565`,
  merged `2026-08-29T16:26:24Z`). Step 0's stamped-cell grep for the newly
  blessed digests at authoring: **zero** on `origin/main` and this tree,
  against 231 predictions and 138 evaluations under the retiring set; re-run
  at the promotion: **zero** for all three newly blessed predictor digests.

  **The amendment batch**, every debt named on the record before this freeze:
  the claims-block count corrected to the five-claim cert-v2 set; the
  `empty_text` parenthetical covering QP-derived rows (an unextractable
  petition leaves the QP file empty the same way); the `query` population
  clause (the non-cert letter forms screened out unless asked for); the
  caption-class-floor anchors replacing all three whole-segment fallback
  anchors — the band-null fallback, the version-mismatch fallback, and the
  arrival anchor, whose state-caption case the reachable-ladder re-base had
  left mis-pointed at the weakest band's figure where its own scored floor
  runs severalfold higher: pooled over the pack's nine rendered Terms, 5.0%
  (n = 12,591) against `state`'s 21.6% (n = 371), and on the single Term 2025
  cells 3.9% (n = 1,132) against 39.1% (n = 23) — and the moment-cutoff passages mirroring the evaluate
  prompt's blessed twins: the snapshot as a moment-bounded baseline
  (`context.cutoff` a cohort marker, non-null even on a forward cell), the
  band as at the snapshot rather than as at now, and the forward-mode
  cutoff-is-not-a-retrieval-clock rule.

  **The de-count this freeze executes.** Replacing the predictor digests
  retires the set `prereg/proc-v3` blessed and `proc-v4` carried, removing
  every prediction stamped under them from every frozen-scope artifact — the
  declared-shakedown cohort, licensed by the declaration entry above (dated
  2026-08-29, before any cert-window outcome existed; its interim exposure
  stated there). Census at the declaration: 231 stamped predictions, 77 per
  predictor, and 138 stamped evaluations — every evaluation predates the new
  instant, so all of them de-count via `graded_post_freeze`, the six carrying
  the still-blessed evaluator digests included: the timing limb tests no
  digest, and the boundary is total in both halves, per the third
  supersession shape. Final census at the carrying promotion, both halves:
  **231 predictions and 138 evaluations** — unchanged from authoring; no stamped cell landed in the window.
  The de-count becomes **visible** at the first post-promotion
  `metrics-refresh`, not at the merge — the committed boards are static
  artifacts, and the refresh that empties their interim stage blocks is the
  promotion's runnable effect check (`fedcourts leaderboard`, then the
  diff showing the blocks empty) — as the scored window opened at the first
  refresh for `sal-v2` and `sal-v3`. The counted record for the
  long-conference claim window opens with the first cells stamped under
  these digests at or after the instant, which is why the carrying promotion
  must land **before the long-conference predict round runs**.

- **The capital-marking strip re-partitions the paid scored segment,
  2026-08-29** (no digest moves, no new process version): the
  cert **scored segment** — the paid modern-cert population
  `analytics._is_scored_segment_row` defines, which the statpack's segment base
  rates, the per-Term `classes` blocks, `cert_backtest`, and
  `salience_replay`'s frame are all conditioned on — gains the SCOTUS
  petitions whose stored `docket_number` carries the Court's
  `*** CAPITAL CASE ***` marking. Recorded here because it moves a measured
  number under unchanged digests, after `prereg/proc-v5` was tagged
  (freeze commit `0b019da58`, instant `2026-09-05T00:00:00Z`), and the
  pre-registered baseline is the whole tree at that tag.

  **What changed and why it is a correction, not a re-definition.** Fee class is
  read from the docket serial, and the marking is appended to the number
  upstream, so a marked number parsed as nothing: `_fee_class` returned `None`,
  the row fell outside the paid segment, and — the same parse, the other
  direction — `corpus.is_ifp_petition` returned `False` on a marked IFP
  petition, admitting it to a scope the registered Tier-0 rule excludes. Both
  readers now strip the marking before parsing. `docs/salience.md`'s statement
  that the scored set is paid-only, and `metrics/README.md`'s rule that an
  anchor match the population it anchors, were **already** the registered
  intent; the implementation did not meet them. No registered rule text moves,
  which is why this is not a `sal-v5`: a salience version is the five things
  `docs/salience.md` enumerates (score function, band function, band names,
  always-include rule, distribution parse), and Tier-0 hard eligibility is none
  of them — it lives upstream of scoring in `corpus.OUT_OF_SCOPE_RULES`.

  **Measured effect.** Read from the corpus blob whose newest `last_pulled` is
  `2026-08-29` (newest stored snapshot `2026-07-13`), 2,152,649 case rows:
  463 stored numbers carry a `*** … ***` string, of which 462 are the Court's
  capital marking on SCOTUS rows and one is a Second Circuit consolidated
  docket string that uses the asterisks as a separator and is deliberately left
  alone. Of the 462: **183 paid** modern-cert rows enter the scored segment
  (dispositions 147 denied, 21 granted, 10 GVR, 5 unresolved — a grant-family
  rate several times the segment's own, so the addition is **not** a random
  slice), and **123 IFP** rows become Tier-0 out of scope, **63 of which
  currently carry `salience_selected = 1`** — the gate has been funding
  petitions the registered rule excludes. Pooled OT2017–OT2025 the resolved
  paid segment moves n = 13,163 → 13,341 (+178), its grant rate 4.163% →
  4.265%, and its grant-family rate 6.450% → 6.596%. The 178 added rows carry
  31 grant-family outcomes — **17.4%**, against the segment's own 6.6% — which
  is the fact that matters: this is a re-partition on a population correlated
  with the outcome, not a random top-up. Per band (directional —
  computed with the active scorer over current row state, unweighted, no
  risk-set prefix), the move concentrates in `state` (+1.16pp on n ≈ 294); the
  always-include `high` band is essentially unmoved (−0.03pp — the 43 joining
  rows carry the band's own rate); per Term the paid grant-family rate moves
  ≤ +0.50pp (largest at OT2021). The raw-count figures above also assume the
  stored weights: the statpack's published rates are denial-reweighted, and 24
  marked rows are grid denials whose stored `sample_weight` is 1 where the
  corrected rule gives 10 (`backfill_live_signals` fills only NULL weights, so
  the strip cannot repair them). Reweighted as stored, the paid segment reads
  n = 13,458 weighted and grant-family **+0.089pp** rather than +0.146pp; the
  weight repair is a writer-lane pass owed separately.

  **The same strip moves the interim stratum harder, registered here too.**
  `corpus.scotus_application_term_year` now parses 156 of the 462 marked rows
  — application-form dockets that previously parsed to no Term at all — into
  the per-Term interim cut (OT2025 +102, OT2024 +36, OT2026 +18; among them
  77 granted / 74 denied / 1 withdrawn). Measured against the committed
  statpack, whose OT2025 interim block this method reproduces exactly: OT2025
  substantive resolved 178 → 226, grant rate 8.99% → 7.52%; OT2024 49 → 70,
  28.57% → 20.00%; and the pooled prior-Terms anchor an OT2026 interim cell
  grades against moves 13.22% → 10.47% — **−2.75pp, −21% relative**, roughly
  twenty times the cert-segment move above. `interim_base_rate` is
  harness-stamped at grade time from the committed pack, which makes this the
  entry's sharpest non-pooling boundary. (The 135 committed interim
  evaluations carrying a `segment_base_rate` are all proc-v3 shakedown, so
  nothing counted is re-priced — an argument about today's ledger, which is
  why the boundary is registered rather than assumed.) A companion data fact:
  every one of the 156 carries a cert-shaped `evt-petition-disposition`
  baseline minted off the unparsed number; the application relabel now reads
  the stripped number, so its next writer-lane run relabels them into the
  application stratum.

  **Nothing counted is re-based.** At this entry's date the frozen cert
  headline is empty (`metrics/leaderboard.json` `entries: []`,
  `events_scored: 0`), and the standing `interim@arrival` forward entries are
  already declared shakedown by the 2026-08-29 declaration above and de-count
  at the proc-v5 freeze. One marked paid docket carries predictions (three) and
  **zero** evaluations, so no graded cell is re-priced. Of the 63 de-selected
  IFP rows, two reached a committed event and neither carries a prediction, so
  `cleanup-out-of-scope-predictions` deletes nothing — a window that closes
  when this lands, and would open only if a predict round ran first.

  **The rule this entry registers.** A figure built from a pre-refresh pack —
  a `segment_base_rate` stamped on a cert or interim cell, a `cert-backtest`
  report, or `metrics/salience-replay.json`'s committed frame (a sal-v1
  vintage outside the weekly refresh set, so its figures simply pre-date this
  re-partition until someone regenerates it) — may not be pooled with, or
  read against, a post-refresh figure under the same labels. The refresh that
  closes the boundary: `5435f0a24` (`metrics: refresh statpack, scope`, run
  `33406805287`, over blob `a9767436f34c`), merged to `main` in `cd6dcdd1a` at
  `2026-08-31T15:20:38Z` — before the 2026-09-05 instant, with no predict
  round in the promotion-to-refresh window. That refresh closes the statpack
  half of the effect check; the docket pack regenerates on demand
  (`fedcourts docket`), so its fee-class `(none)` bucket empties at its next
  regeneration, not on the refresh schedule.

  **The entry is dated before the instant deliberately.** Landing it and
  refreshing metrics before `2026-09-05T00:00:00Z` means no counted number ever
  straddles the change. The committed boards move at the first
  `metrics-refresh` after this promotion, not at the merge, and that refresh is
  this change's runnable effect check: `fedcourts statpack`, then the diff
  showing the paid class counts risen by the per-Term additions above and the
  docket pack's fee-class `(none)` bucket emptied.

- **The owed grid-denial weight repair is withdrawn; the raw `+0.146pp`
  stands as the registered paid-segment delta, 2026-08-31** (no digest
  moves, no committed number moves): the capital-marking entry above names,
  as an owed writer-lane pass, a `sample_weight` repair for the 24 marked
  grid-denial rows stored at weight 1 where its corrected rule gives 10, and
  publishes the projection that under it the paid segment reads n = 13,458
  weighted and grant-family **+0.089pp** rather than +0.146pp (the parent
  phrases this "reweighted as stored"; 13,458 = 13,341 + 13 × 9 is
  arithmetically the corrected-weights figure, the only coherent reading). Building that
  pass falsified its premise, so the repair is withdrawn and the projection
  with it: the raw figures (n = 13,341; **+0.146pp** raw and as-published
  — every paid-segment row carries weight 1, so weighted equals raw and the
  statpack always read it that way) are the registered
  delta, and the committed boards — which never carried the projection — do
  not move.

  **Why the premise is false.** The derivation rule —
  inline in `backfill_live_signals` (`pipeline/ingest.py`) — tests that a denial's serial is on the legacy walker's 1-in-10 grid at or
  below its cursor — which proves the serial was *probed*, not that only one
  in ten was *kept*. The two coincided only during the legacy IFP walk, and
  every genuinely sampled row shows it: the corpus's 2,583 `sample_weight =
  10` rows all sit in eight IFP OT2017–OT2024 (Term, stream) cells with
  live-slice serial coverage 0.127–0.135, and none is capital. The 24 targets — 13 paid
  OT2017–OT2024, 11 IFP OT2025 — sit in cells with live-slice coverage
  0.994–1.000, and each has 7–8 of its 8 nearest live-slice serial
  neighbours individually present at weight 1: their ranges are enumerated, so weight 1 is *correct*.
  Reweighting them would have made one row stand for ten petitions, nine of
  which are already present — 216 phantom weighted denials (117 inside the
  paid scored segment; the projection's own arithmetic, 13,458 − 13,341 =
  13 × 9, is exactly those phantoms), moving per-Term band base rates by up
  to 6.3pp — largest at OT2020 `state`, 32.43% → 26.09% (weighted n 37 →
  46); the largest move in the always-include `high` band is 5.4pp, OT2022
  37.14% → 31.71% (n 105 → 123). Provenance confirms the class: `capital_case` latches from the
  upstream boolean as well as the number parse, so the flag never attributed
  a stored weight to a defeated parse, and the blob — read after the
  normalization pass the parent entry named as owed converged the 462 marked
  spellings into the latched flag — holds no word-marked asterisk spelling
  at all (7 asterisk rows corpus-wide, every one a circuit-court row, none a
  SCOTUS marking). The repo's standing invariants said so independently — the
  budget's paid-census note, and the caption, salience-banding, and
  distribution-census cuts, each of which raises on any scored-segment row
  with `sample_weight != 1`. Evidence read
  from the blob pulled 2026-08-31 (newest stored snapshot 2026-07-13).

  **What this entry changes and what it leaves.** The withdrawal corrects a
  *projection* the capital-marking entry published beside its registered
  figures; the entry's registered raw deltas, its scored-segment
  re-partition, and its pooling rule are untouched. No counted figure moves:
  the stored weights were right all along, and every committed board already
  read them. The rule's latent over-derivation — the probed-vs-kept gap,
  which `backfill_live_signals`'s NULL-only predicate scoped correctly by
  accident — was not small: run unguarded over the whole live slice
  instead of NULL-only, the rule matches 1,567 on-grid stored-weight-1
  denials, 1,224 of them paid scored-segment rows — 11,016 phantom
  weighted denials, nearly doubling the 13,341 segment, against the 117
  the withdrawn repair would have added. The code half of this correction
  landed with it: the rule is extracted as a named function and guarded
  on density — a denial whose eighteen neighbouring serials, nine either
  side, hold seven or more stored live-slice rows is in an enumerated
  range and stays at weight 1 (the walk did not record which side of a
  kept serial its block fell, so the guard looks both ways). The guard
  counts within that window, never cell-wide, and it counts rather than
  testing presence, because the blob separates the two populations by
  count alone: a sampled row's window holds at most six stored
  neighbours — the walk's grant-family keeps, and 1,156 of the 2,583
  genuinely sampled rows hold at least one (distribution 0: 1,427;
  1: 813; 2: 263; 3: 65; 4: 10; 5: 3; 6: 2), so a presence test would
  wrongly strip the sampling weight from 44.8% of them, 40.3% of the
  legacy weight — an enumerated row's window holds ten or more, and the
  range between is empty of both. The 24 targets' windows read 17–18,
  the enumerated side (their eight nearest alone read 7–8, the neighbour
  figures above), and guarded, the same whole-slice run matches 117
  rows, not 1,567: the grid rows genuinely inside sampled ranges yet
  latched at weight 1 — an under-count left open as its own repair, and,
  though identically sized by coincidence, a different population from
  the 117 phantoms the withdrawn repair would have added.

- **The retroactive-blessing tripwire moves to the bless boundary,
  2026-08-31** (no digest added or retired, no instant moved, no new process
  version — the six new literals the constant gains are derived facts about
  git, not pre-registered choices, per the tag paragraph below): the
  enforcement correction the `proc-v5` entry above already traded for. `FROZEN_PROCESS_DIGESTS` now maps each blessed digest to the
  instant it was blessed — the merge time of the promotion that carried its
  freeze commit to `main` — and the ledger tripwire
  (`tests/test_process_version.py`) asserts a committed prediction's
  `stamped_at` is at or after **that** moment rather than at or after
  `FROZEN_SINCE`. Nothing about counting changes: `is_frozen` and
  `graded_post_freeze` still gate on the instant alone, and the map's
  membership semantics are identical to the frozenset's.

  **The `prereg/proc-v5` tag predates this shape, and correctly.** That tag
  sits on freeze commit `0b019da58` (`2026-08-29T14:01:23Z`), whose tree holds
  a bare `frozenset` with no bless moments — it could not have held them, since
  its own carrying merge had not yet happened. The pre-registered baseline is
  unaffected: the six blessed digests and the `2026-09-05T00:00:00Z` instant at
  that tag are exactly the six and the instant in force now, and the bless
  moments are facts about git recorded afterwards, not choices the tag could
  have pre-registered. An auditor reads them here and from the constant on
  `main`, and re-derives them with the two `git log` commands below.

  **Why the instant was the wrong boundary for this test.** The two moments
  answer two questions. A stamp before its digest's **bless moment** ran
  against a commitment still editable on `main` — retroactive blessing, which
  no declaration licenses. A stamp in the window between the bless moment and
  the **counting instant** ran against an immutable commitment and is merely
  uncounted, because the instant is guessed generously late by design. The
  `proc-v5` entry registered exactly that trade in advance — "the live
  channel's transition-queued cells before the instant merely land as
  shakedown" — so a tripwire keyed on the instant contradicted the entry it
  was meant to enforce, and would fail the build on the first honest cell of
  the open `2026-08-29T16:26:24Z` → `2026-09-05T00:00:00Z` window. The licence
  for this correction is that sentence, not a new registration.

  **The bless moments, each verified from git.** The three **predictor**
  digests (`sha256:eba87d4c…` claude-baseline, `sha256:b46b3c6d…`
  codex-baseline, `sha256:8c401008…` gemini-baseline) are blessed at
  **`2026-08-29T16:26:24Z`**: `git log -1 --format=%cI 39a3a9565`, the
  `promotion/2026-08-29` merge this file's `proc-v5` entry already names as
  their carrying promotion, whose tree carries all six literals
  (`git show 39a3a9565:src/fedcourtsai/process_version.py`). The three
  **evaluator** digests (`sha256:11a0afbc…` claude-judge, `sha256:9fb7b6f1…`
  codex-judge, `sha256:b9f548f4…` gemini-judge) carried forward
  byte-identical from `prereg/proc-v4`, so they keep proc-v4's bless moment,
  **`2026-08-26T14:46:40Z`**: `git log -1 --format=%cI 6d92ed81b`, the
  `promotion/2026-08-26` merge, on which `prereg/proc-v4` itself sits (the
  merge-placed tag that entry records as its anomaly) and whose tree carries
  those three literals verbatim. Immutable bytes do not need re-blessing, so
  the carried digests keep the earlier moment rather than inheriting
  proc-v5's.

  **Zero committed cells are reclassified, and zero counted numbers move.**
  Verified against the ledger on `origin/main`, not asserted — the ref step 0's
  doctrine names, and identical to this branch's for the cells counted here
  (`git diff --name-only origin/staging origin/main -- data/cases` touches
  only `attempt.json` and `event.yaml`, no `prediction.json` or
  `evaluation.json`). The
  tripwire is predictions-only, and all **231** stamped committed predictions
  carry the *retired* proc-v3/proc-v4 predictor digests (`sha256:06a854e7…`
  76+1, `sha256:7ca86f57…` 75+2, `sha256:93dfaec3…` 75+2, the second figure of
  each pair the proc-v4-labelled re-stamps) — **zero** carry any of the three
  blessed proc-v5 predictor digests, so the tripwire's loop body executes zero
  times under either boundary and cannot have reclassified anything. The
  evaluation half is outside the test but checked anyway: the **6** committed
  evaluations carrying blessed evaluator digests are two runs of three cells
  each, stamped `2026-08-29T04:29:37Z` (`sha256:b9f548f4…`) and
  `2026-08-29T04:33:12Z` (`sha256:11a0afbc…`) — `sha256:9fb7b6f1…` carries
  none — both after their `2026-08-26T14:46:40Z` bless and before the instant,
  the shakedown window read correctly by both boundaries. On the counted side, the only
  digest-membership site in the tree is `is_frozen`, which was untouched and
  still pairs membership with the timing test; the boards' provenance block
  rebuilds byte-identical to the committed one (`frozen_process.digests`, the
  same six sorted, `since` still `2026-09-05T00:00:00Z`), and
  `metrics/leaderboard.json` and `metrics/claim-scores.json` both still read
  `entries: []` under `process_scope: frozen`. What changes is which cell the
  build refuses, so the runnable effect check is the pair that must both hold
  once this is live and a predict round has landed in the window: `uv run
  pytest tests/test_process_version.py::test_no_committed_cell_predates_the_bless_it_claims`
  green over the ledger on `main`, and `uv run fedcourts leaderboard` still
  reporting an empty frozen scope until `2026-09-05T00:00:00Z`.

- **The evaluation-to-prediction join resolves the stamped graded run,
  2026-08-31** (no digest added or retired, no instant moved, no committed
  number moved): the input-selection rule beneath five harness-owned numbers
  changes under unchanged digests, which is exactly the "who computes a
  scored number sits outside the digest" class `docs/process-version.md`
  routes through this record. An evaluation now carries a harness-stamped
  `prediction_run_id` — resolved once by the ordinary stamp, preserved by
  `--regrade`, never the evaluator's word — and every reader joins it
  **named run first**: `correct`, `brier_score`, `segment_base_rate`,
  `brier_skill_score`, and `claim_scores` at stamp time, the stratified
  boards, the leaderboard's agreement views and realized-Term pairing, and
  `validate`'s basis gate, all through one resolver, so a grading of a
  de-counted prediction can no longer ride a frozen re-run of its cell into
  the counted figures. The **forward/retrospective stratum boundary moves
  with it**: the scored prediction's harness clock now decides the stratum,
  not the latest prediction's — the graded artifact is the one whose timing
  the claim describes — with the latest-prediction rule surviving only as
  the fallback for records stamped before the field existed, where its
  conservative reading (never present a possibly post-resolution prediction
  as forward) is still the right default for an ambiguous join.

  **No committed figure moves, verified rather than asserted.** All 150
  committed evaluations predate the field (`prediction_run_id` null), so
  every one takes the fallback and the build is byte-identical over the
  ledger as committed; only 4 `(event, predictor)` cells in the whole ledger
  hold more than one prediction run (all `evt-petition-disposition`, dockets
  `73281059` / `73281063` / `73281345`), none of them carries any
  evaluation, and every prediction in them is unstamped; the committed
  boards read `entries: []` under `process_scope: frozen` before and after.
  The newest committed evaluation stamp is `2026-08-29T04:33:12Z`, before
  the `2026-09-05T00:00:00Z` instant, so **zero** legacy records are in
  frozen scope and the fallback carries no counted cell today. The one open
  edge is promotion order: an evaluate round stamped in the window between
  the instant and the promotion that carries this change would mint
  null-field records that *are* frozen-scope and read through the fallback,
  with `graded_post_freeze` as their only belt — so this change should
  promote before the first post-instant evaluate round, and the runnable
  effect check is `uv run fedcourts validate data` green (the new
  `check_evaluation_targets` pointer discipline holds over the ledger) with
  `uv run fedcourts leaderboard` still reporting an empty frozen scope until
  the instant.

- **The bless-boundary tripwire arms its evaluation half, 2026-09-01** (no
  digest added or retired, no instant moved, no committed number moved): the
  ledger tripwire that walks committed stamps against their digests' bless
  moments now runs over both halves —
  `test_no_committed_cell_predates_the_bless_it_claims` over predictions and
  `test_no_committed_evaluation_predates_the_bless_it_claims` over
  evaluations — superseding the 2026-08-31 entry's "the tripwire is
  predictions-only" scope and mechanizing the freeze procedure's by-hand
  evaluation gap check (step 4). Enforcement scope, stated precisely: the
  tripwire sees a cell only from its digest's bless moment on; the
  `[held instant, new evaluator bless)` window of a held-instant re-bless
  stays governed by the minted-from-`main` convention while open, with the
  tripwire detecting any violation at the re-bless. Verified at arming, over
  the ledger as committed: 150 evaluations, 138 stamped, **6** under
  currently blessed digests (3 under `sha256:11a0afbc…` stamped
  `2026-08-29T04:33:12Z`, 3 under `sha256:b9f548f4…` stamped
  `2026-08-29T04:29:37Z`, both against the carried-forward
  `2026-08-26T14:46:40Z` bless), zero retroactive; the prediction half
  executes over 19 of 660; `metrics/leaderboard.json` and
  `metrics/claim-scores.json` still read `entries: []` under
  `process_scope: frozen`. The runnable effect check is the pair:
  `uv run pytest tests/test_process_version.py -k predates` green over the
  ledger on `main`, and the boards still empty until the
  `2026-09-05T00:00:00Z` instant.

- **The sampled-frame weight repair is registered, and its durability half
  lands, 2026-09-01** (no digest added or retired, no instant moved; no
  committed number moves *on this change* — the apply half moves the weighted
  statpack and docket-pack cuts and the ops digest's always-deny floor, and is
  registered here in advance of it): a
  deliberate re-weighting of the legacy denial-sampling frame, split into a
  code half that lands now and a writer-lane data half that does not.

  **The population.** **117** live-slice SCOTUS rows that the guarded rule
  `legacy_denial_sample_weight` derives at weight 10 and that are **stored at
  1** — grid denials genuinely inside sampled ranges, min-latched to certainty
  by a channel that asserted it. Every figure below is re-derived at
  registration from the blob pulled `2026-09-01` (newest stored snapshot
  `2026-07-13`) by running the shipped rule, density guard included, over all
  22,748 live-slice SCOTUS rows, and is a fact about *that* vintage.
  Every one is IFP, in the eight `historical-ifp` OT2017–OT2024 cells, and the
  per-Term split is OT2017 27, OT2018 26, OT2019 16, OT2020 13, OT2021 15,
  OT2022 5, OT2023 8, OT2024 7. Those cells' live-slice serial coverage is
  **0.127–0.135** — the sampled regime's own signature — and they are exactly
  the eight cells the corpus's 2,583 stored weight-10 rows sit in. None is
  capital. Each row's eighteen-serial neighbourhood holds 0–3 stored rows
  (0: 60, 1: 38, 2: 17, 3: 2), well inside the sampled regime's observed 0–6
  and far below the enumerated regime's 10-or-more.

  **The provenance is checked, not assumed**, because the guard's own registered
  residual has this exact shape: a poller-resolved denial inside a
  walker-covered sampled range reads as sampled though the poller included it
  with certainty, and coverage and occupancy alone cannot tell that apart from a
  genuine 1-in-10 draw. What tells them apart is the grid. In these eight cells,
  of the serials at or below the walk's cursor, **97.5–99.5% of grid serials are
  stored against 3.0–4.0% of off-grid serials** — a 25–33× ratio, so grid
  membership *is* the legacy walk's systematic keep and not an arrival any
  channel could produce by chance; a poller would land on and off the grid
  alike. All 117 are on the grid (117/117), they sit uniformly across each
  cell's walked range (per-cell mean position 0.40–0.57, spanning 0.00–0.99)
  rather than clustering where one channel worked, and they share the 2,583
  weight-10 rows' poll window exactly (`2026-07-13`–`2026-07-20` on both). They
  are the same draw, differing only in what was later written over them.

  **Explicitly a different population from the 24 the capital-marking repair
  withdrew**, and disjoint from it by the same guard that separates them: those
  24 sat in cells of live-slice coverage 0.994–1.000 with neighbourhoods
  reading 17–18, so weight 1 was correct and reweighting them would have
  fabricated petitions the corpus already held. These 117 are the inverse —
  blocks the corpus does *not* hold, whose nine petitions each are represented
  by nobody. The two populations cannot overlap: one is what the density guard
  reads as enumerated, the other what it reads as sampled. The withdrawn repair
  would have added 216 phantom weighted denials, 117 of them inside the paid
  scored segment; that its scored-segment share equals this population's size is
  a coincidence, noted so the two are not later read as one number.

  **The durability half, landing with this entry.** Every live-channel SCOTUS
  write — frontier discovery, the cert and application rotations, the selection
  sweep, and the historical walker's ingest — reaches the corpus through
  `pipeline.live.ingest_live_payload`, and each of them asserted weight 1. The
  min-latch keeps the smaller of stored and incoming, so any such write erases a
  repaired 10; applying the data half without this would leave a repair the next
  walk undoes. That seam now **derives** an asserted certainty through
  `legacy_denial_sample_weight` rather than taking it, so a grid denial whose
  block is still stored one row in ten keeps its sampling weight however often
  the walk re-serves it alone, and regresses to 1 only once the block around it
  is actually enumerated. A caller asserting any weight other than 1 is claiming
  knowledge the corpus cannot reproduce and is written as given. The invariant
  is that no writer writes weight 1 for a row whose block the guard reads as
  sampled, so a later repair's 10 survives every re-serve; seven tests pin it,
  the repair-then-re-walk case included. One writer reaches the column outside
  that seam and is closed with it: the live-duplicate merge took the pair
  minimum reading a NULL as certainty, so a survivor whose weight the
  CourtListener channel never wrote would have stripped its live twin's sampled
  weight; a NULL now asserts nothing and is skipped.

  **The durability half is much larger than the repair it protects, and that is
  registered here so a later reader attributes a moved number to the right
  half.** The guard does not only keep the 117 repaired; it keeps the **2,583**
  rows already stored at 10 from being latched down as the walk re-serves them.
  At nine weighted petitions each that is up to **23,247** weighted denials the
  code half alone preserves, against the apply half's +1,053. No number moves on
  this change — nothing is re-weighted by it — but the counterfactual it
  forecloses is twenty-two times the repair's size.

  **The apply half is not in this change.** Re-weighting 117 stored rows is a
  direct `UPDATE` — a narrower-to-wider weight routed through the upsert path is
  a silent no-op under the min-latch — so it is a pass on `run-repair`, in the
  writer lane, with its dry-run ledger read by a maintainer before any write.
  Nothing about the corpus moves until that runs.

  **Expected effect, direction registered now and magnitudes owed to the
  dry-run.** Each repaired row gains nine weighted petitions, so on the
  `2026-09-01` blob the apply adds **+1,053** weighted denials, taking the eight
  affected cells' weighted denials from **25,950 to 27,003 — +4.06%**, the ~4%
  IFP denial under-count the shortfall was filed as (per cell: +1.70% OT2022 to
  +5.83% OT2017). Every weighted denominator that admits IFP rows therefore
  moves **up**, every denied share **up**, and every grant, grant-family, GVR
  and dismissed share **down**: the statpack's cert-by-disposition and
  cert-by-circuit sections and its per-Term `base_rates` /
  `est_grant_family_rate`, `fee_class=ifp` classes and weighted `timing`; the
  docket pack's weighted sections and its per-Term `weighted_resolved`,
  `dispositions`, `est_grant_rate` and `est_grant_family_rate`; and one
  committed prose figure, the whole-slice IFP-inclusive denial rate in
  `docs/outcome-decomposition.md` (19%, est. n ≈ 43,300 — the rate falls, the n
  rises), whose paid hazards beside it do not move. The direction is uniform;
  the *magnitude* is not, because the 117's distribution across relist, circuit
  and capital buckets differs from the 2,583's — so no single percentage may be
  carried across buckets. The capital cut moves on one side only: none of the
  117 is capital, so the marked bucket holds and the marked-versus-unmarked gap
  widens. As arithmetic on the committed statpack's weighted denied count of
  40,520, the pack-wide denial total rises about 2.6% — indicative only, since
  the committed pack and the repair-time blob are different vintages. **Exact
  deltas are read from the repair dry-run ledger before apply, not from this
  entry.**

  **What the ledger may not be used to license, registered now so the apply
  cannot be read as post-hoc.** The hedge above is about magnitudes, never
  membership. The pass touches only rows that are, at apply time, IFP, on the
  sampling grid, inside the eight `historical-ifp` OT2017–OT2024 cells, at or
  below their cell's cursor, and read as sampled by the density guard. That
  predicate is the registration; the count is whatever it selects on the blob
  the pass runs against, and may differ from 117 as the corpus moves. **A row
  the ledger proposes that falls outside the predicate is a different
  population and needs its own entry** — it is not covered by this one.

  **No scored number moves, and that is a property of the population rather
  than a hope.** All 117 are IFP, and every scored-segment cut is gated on
  `caption._scored_segment` / `analytics._is_scored_segment_row`, which require
  a paid serial below `IFP_SERIAL_BASE`. So the caption census, the
  distribution-parse band cut, the salience census and `salience-replay`, the
  cert back-test, the leaderboard's realized-band skill, the claim-score
  baselines and `evaluate.segment_base_rate` — all paid-only — cannot see these
  rows, and the three census cuts' refusal to run over a `sample_weight != 1`
  frame is not tripped by the repair. `metrics/leaderboard.json` and
  `metrics/claim-scores.json` do not move, and the withdrawn repair's registered
  paid-segment figures (n = 13,341, +0.146pp) survive untouched.

  **One published number outside the boards does move, and it is a
  calibration anchor.** The ops digest's always-deny floor (`ops._deny_base_rate`)
  matches the statpack's cert-stage disposition section *by shape*, and that is
  the IFP-inclusive weighted section — so `deny_base_rate` rises by about
  0.12pp (0.9501 → 0.9513 on the committed pack) over a larger `base_rate_cases`,
  and `lift_over_always_deny` falls by the same ~0.0012 for any accuracy. The
  ops report is committed, so this re-bases a published comparison, by a bound
  under 0.002. It is named here rather than left to be discovered in a diff.

  The runnable effect check, for the promotion carrying the code half:
  `uv run pytest tests/test_legacy_denial_weight.py` green, and — where the
  corpus is pulled — the population reproduced by the shipped rule under the
  membership predicate above before the writer-lane pass, and empty after it.

- **The interim arrival moment is dated from the docket's own submission entry,
  2026-09-02.** A **provisioning-cutoff** entry on the pattern of *The moment
  cutoff on forward provisioning, 2026-08-17* above, and a second boundary
  inside that one rather than a restatement of it: that entry registered
  *whether* a declared moment is cut, and named the interim application
  baseline among the placed moments; this one moves **where** the interim
  arrival cut falls. No freeze commit and no digest movement — no prompt byte
  changes — and the data-visible marker is the same `context.cutoff`, so an
  auditor reading only the 2026-08-17 entry would pool interim arrival cells
  across a real boundary. They may not be pooled.

  **What changed.** `evt-motion-disposition` opened at the row's docketing date
  — the `cases.date_filed` column, which the live channel fills from the
  payload's `DocketedDate` — where it opened at all. It now opens at the date of
  the entry in which the application was submitted
  (`interim_signals.application_arrival_date`), falling back to `date_filed`
  where no submission entry can be dated. `provision.moment_cutoff` is unchanged
  and still returns `opened_at + 1 day`; what moves is the date it is given.

  **The corpus this entry's figures are read against** is the blob whose newest
  pull stamp is `2026-09-02` (newest stored snapshot `2026-07-13`). Two of the
  three measurements below are re-runnable against it from the index alone; the
  third is a payload read, and its predicate is stated so it can be repeated.

  **Index-only, and the half that needs no payload.** Of the **340** rows with
  `application_kind = 'substantive'`, **85** carry no `date_filed` at all — a
  quarter of the substantive interim population, for which the submission entry
  is not the better stamp but the *only* one. Those are the cells that were
  provisioned `as-stored` with `cutoff: null`, the shape this change closes
  outright.

  **The direction, from a payload read.** Over the **60** substantive
  application dockets whose live `supremecourt.gov` payloads were read for the
  stats review of this change — a sample of that 340, not the whole of it, and
  the figures below are that review's measurement rather than a re-derivation
  here — the submission entry **precedes** docketing on 34, by a median 5 days
  and a maximum of 64, and **follows** it on **none**. So the old stamp ran
  systematically late, and late is the enlarging direction: the cut admits
  filings the arrival moment never saw. Two moment-collapses are what that
  bought, on the same sample: the old cut admitted the **response-request**
  entry on 5 of the 7 dockets that have one — the trigger of a *different*
  declared moment (`evt-order-response-requested-disposition`), so the arrival
  cell was conditioned on the thing that defines the moment after it — and
  admitted the **disposition itself** on 4 of the 55 that had been disposed of.
  A second read, of 150 live application dockets, is what the parser rests on:
  the submission clause matched the head entry of all 150 and matched no
  disposing entry on any of them.

  **The cohort split, on the 12 rows that are `salience_selected` with an
  `application_kind` at this entry's date.** Two (`scotus/9526000256`,
  `scotus/9526000273`) move from `as-stored` — no cutoff at all — to placed;
  six keep a cutoff that moves **earlier**; four are unchanged, their submission
  and docketing dates falling on the same day. Ten of the twelve carry a
  committed prediction. A figure over interim arrival cells may not pool across
  the promotion carrying this, and — the 2026-08-17 entry's rule, which applies
  here unchanged — a figure over the placed ones owes the `dated`/`truncated`
  counts beside it.

  **One residual the boundary cannot remove.** On 2 of the 60 — both capital
  applications — the application is submitted and disposed of on the **same
  day**, so a cutoff of arrival + 1 necessarily keeps the disposing entry. The
  cut is exclusive at day granularity and the docket records no finer time, so
  this is a floor of the reconstruction rather than a defect of the rule; such
  a cell is refused by the forward terminal gate rather than placed, and a
  replay of one is reading a docket that was over before the day ended.

  **The boundary takes effect for cells provisioned after the promotion
  carrying it**, which is the 2026-08-17 entry's rule and matters more here
  because the counting instant is close. `process_version.FROZEN_SINCE` is
  `2026-09-05T00:00:00Z`, and the interim predict trigger is the live channel's
  docket-change queue, which mints arrival cells continuously. So **nothing
  counted re-bases provided this promotes before that instant**, and the
  condition is registered rather than assumed: an interim arrival cell stamped
  in a gap between the instant and the carrying promotion would be counted *and*
  provisioned under the old boundary, and would need its own entry.

  **What the existing cells are, and on what ground they are excluded.** The 30
  committed `evt-motion-disposition` predictions sit on 10 application
  baselines and partition 18 `proc-v3` + 2 `proc-v4` + 10 `proc-v5`. The
  2026-08-29 shakedown declaration above covers the first 20; it does **not**
  reach the 10, which carry the currently blessed `proc-v5` predictor digests.
  Those are excluded on the instant alone — stamped `2026-09-01`, before
  `FROZEN_SINCE` — so the coverage rests on two grounds for 20 cells and one for
  10, not on the declaration for all 30.

  No interim base rate re-prices either: `pipeline.base_rates` keys the interim
  section on `application_term` and carries no provisioning version, so it is a
  function of realized outcomes and is untouched by what a cell was conditioned
  on. This is a **conditioning** change and nothing else.

  **One amendment debt, named here because it cannot be paid in the same
  commit.** The frozen predict prompt tells an interim arrival cell its event
  was "opened when the application was docketed", which this change makes false
  — it is now opened at the submission entry. The prompt bytes are an input to
  the process digest, so correcting that sentence moves all three `proc-v5`
  predictor digests; it is therefore owed to the next re-bless rather than taken
  here, and until then an arrival cell is told a slightly wrong thing about why
  its snapshot ends where it does. This is the same shape as the 2026-08-17
  entry's own caveat, that its cells were placed under a frozen prompt still
  describing the snapshot as the latest.

  **The expected-skill corollary, registered now so a decline cannot be read as
  a regression.** `context.response_requested` flips `True` → `False`/`None` on
  5 of the 7 sampled dockets that have a request, and the frozen escalation trio
  is part of what an interim cell reads. So a post-fix `interim@arrival` cell
  sees **strictly less** than a pre-fix one, against an unchanged realized
  baseline. Expected interim skill should therefore **decline**, and a drop
  across this boundary is the change working. A *rise* would be the surprising
  result and would want explaining.

  The runnable effect check, for the promotion carrying this:
  `uv run pytest tests/test_interim_signals.py` green, and — on the next
  interim arrival cell provisioned after it — `record/context.json` carrying a
  non-null `cutoff` equal to the day after the case's own
  `Application (…) … submitted` entry, with that entry the last one surviving
  in the provisioned snapshot.

- **An amendment debt for the merits pool-guard prompt wording, 2026-09-02**
  (no digest added or retired, no instant moved; a debt recorded, on the
  pattern of the arrival-stamp entry above). The statpack's merits section now
  states that `cert_order_excluded` sits **outside** `granted` — the two
  columns partition the pre-guard population — and corrects the guard's
  description everywhere it was wrong: the guard removes a row whose parsed
  judgment is dated **on or before** its own grant (`merits_decided <=
  date_cert_granted`), and an **undated** parse is *not* removed — it stays in
  `granted` as a coverage gap. Two frozen surfaces still carry the old,
  incorrect description and cannot be corrected here, because their bytes are
  process-digest inputs and the edit would move all six enabled actors'
  digests:

  - `.github/prompts/predict.md`, the merits-section paragraph: claims the
    guard excludes a row with "no date the gap could be tested on". False —
    the undated row goes to `granted`.
  - `.github/prompts/evaluate.md`, the same paragraph shape: the same undated
    arm, plus a parenthetical that mislabels an untestable row as a cert-order
    rider.
  - Neither prompt carries the reading rule that `excluded` sits outside
    `granted` — the omission that produced the misreading this entry's change
    corrects, and the one a cell agent is most likely to reproduce in its own
    prose.

  All three corrections are owed to the next re-bless, together with the
  arrival-stamp entry's debt above; until paid, a cell reads a slightly wrong
  account of the pool guard while every non-frozen surface states the correct
  one.

  The runnable effect check, for the promotion carrying the relabel: after the
  next `metrics-refresh`, `rg -n "excluded \(not in granted\)"
  metrics/statpack.md` matches, and the OT2024 row renders `| 2024 | 75 | 34 |
  73 |` under the qualified header — until that refresh the committed statpack
  keeps the old header, which is the regeneration lag and not a defect.

- **`leakage_suspected` becomes an exclusion: a flagged grading leaves every
  rank key and every scored aggregate, 2026-09-02** (no digest moves, no
  committed number moves, no score value changes anywhere). Registered here
  because it changes **which cells a published figure is computed over**, and
  nothing in any actor's canonical config carries the rule, so no digest moves
  and the change is invisible to the frozen/shakedown partition. It is the
  membership counterpart of the **scoring baseline**
  ([process-version.md](process-version.md#harness-code-is-outside-the-digest-and-one-case-of-that-has-teeth)),
  which is recorded here because it moves a measured number under unchanged
  digests: this moves no number and moves the population instead, and a figure
  is as unreadable across an unrecorded population change as across an
  unrecorded re-basing.

  **The state this replaces.** `Evaluation.leakage_suspected` was recorded as
  advisory and read by no aggregation: `store.stratify` handed every graded
  cell to the boards whatever the bit said. The 18 flagged gradings on
  `scotus/73129750` and `scotus/73275185` (2 cases × 3 predictors × 3
  evaluators, all stamped `proc-v2` on `2026-08-14`), whose recorded
  `brier_skill_score` runs to 0.9988 because the prediction read the
  disposition out of a mis-provisioned snapshot, stayed out of the forward
  stratum only because `integrity.classify_stratum` compares the outcome's
  `resolved_at` to the prediction's harness clock and those outcomes predate
  those runs. That is a property of those cells, not of the rule.

  **The rule this entry registers.** A grading carrying `leakage_suspected:
  true` excludes its cell from **every scored stratum and every rank key** on
  every surface built from the `store.stratify` join — the ranked cert board
  and its `stages` blocks, `claim-scores.json`, the dashboard's substance
  funnel, and the semantic census. It is independent of the timing split and of
  the forward-claim rule, and that independence is the whole of it: a leaked
  cell whose outcome resolves *after* its prediction's harness clock classifies
  **forward** on the clock alone and would be published as claimable
  forecasting performance, and the retrospective pair is itself a rank key, so
  near-perfect leaked numbers could order predictors that have no forward
  cells. `classify_stratum` is unchanged — this is an exclusion, never a
  stratum reassignment. A **null** bit is "not assessed", not "clean", and such
  cells are scored; a cell both this rule and the forward-claim rule catch is
  counted in both ledgers and the two counts are never summed. The boards
  publish `leakage_exclusion` — the count, the `assessed` denominator, and the
  per-predictor split — beside their figures, the board builders name each
  dropped cell on stderr, and the refresh PR body carries the count. The
  reading rules are `metrics/README.md`, *The leakage exclusion*.

  **What is deliberately outside it**, on the same terms as the forward-claim
  exclusion, which these surfaces also do not apply: the board's `big_case` and
  `evaluator_agreement` views, which read the ledger by their own path and
  measure stakes reads and grader latitude rather than scored performance, and
  the tool-usefulness figures, which declare themselves a superset. A figure
  there that differs from a board figure is two populations rather than an error
  in either.

  **One stale contract, deferred on purpose and named here so it is a recorded
  deferral rather than an oversight.** The frozen evaluate prompt still tells
  the grader that the leakage assessment "is advisory and segments scores — it
  never changes `correct`, `brier_score`, or the other quantitative fields",
  which is now false in its first clause: the bit does not segment, it removes
  the cell. The prompt bytes are hashed into the process digest, so correcting
  that sentence retires all three blessed **evaluator** digests and needs a
  re-bless — which this change deliberately does not take three days before the
  counting instant. Until that re-bless, every grading is produced by a grader
  who was told the bit is inert, and the 18 already in the ledger were. That is
  a fact about how `excluded` should be read, not a defect in the count: the
  bit is the grader's assessment either way. Which way the old contract biases
  a grader is **not established** — a costless flag might be set more freely,
  an inert one less carefully, and nothing here can tell those apart on 18
  cells from one unanimous panel — so `excluded` is read as a count taken
  under the old contract rather than as a bound in either direction, and a
  count taken after the re-bless is not poolable with one taken before.
  Correcting the prompt is owed to the next digest-moving
  freeze, on the same terms as the arrival-cutoff prompt amendment the entry
  above defers.

  **Nothing counted moves.** All 18 flagged gradings are stamped before
  `process_version.FROZEN_SINCE` (`2026-09-05T00:00:00Z`), so
  `graded_post_freeze` already keeps every one of them off every frozen board;
  the committed `metrics/leaderboard.json` is empty (`entries: []`,
  `events_scored: 0`) and `metrics/claim-scores.json` fully suppressed at this
  entry's date. The measured effect is therefore confined to the
  `--all-versions` diagnostic view, and there it is total: on the pooled cert
  board the 18 **are** the whole retrospective stratum. Measured over the
  committed ledger at this entry's date, before → after: `evaluations_total`
  36 → 18, `retrospective_evaluations` 18 → 0, `events_scored` 4 → 2,
  `predictors_ranked` 3 → 3, `forward_evaluations` 18 → 18 (unmoved — no
  forward cell carries the bit), and every entry's whole `retrospective` block
  goes from a populated aggregate to `null`: `claude-baseline` n=6, accuracy
  0.5, mean Brier 0.0242, population skill 0.9427; `codex-baseline` n=6, 0.5,
  0.0410, 0.8947; `gemini-baseline` n=6, 0.5, 0.0613, 0.8553. The three
  `interim@*` stage blocks are untouched (24/18/18 evaluations), the flagged
  cells being cert-stage. The published `assessed` denominator reads 96 over
  that scope — stage-blind and taken before either exclusion, like
  `claimed_forward` beside it, so it spans the cert board and every stage block
  at once and must never be netted against the cert-scoped 36. What it
  establishes is that the count is against a real denominator rather than an
  unchecked ledger. Those
  three near-0.9 skill figures were the retrospective rank key's entire input,
  which is the concrete form of the hazard: they are what a leaked snapshot
  scores, not what an engine forecast. Every figure here is a diagnostic, not a
  claim about any engine.

  **The entry is dated before the instant deliberately.** Landing it before
  `2026-09-05T00:00:00Z` means the counting window opens with the rule already
  in force, so no published figure ever straddles the change and no board built
  under the old reading has to be pooled with one built under the new. The
  runnable effect check for the promotion carrying this: `uv run fedcourts
  leaderboard --all-versions --out /tmp/lb.json`, whose stderr names each
  dropped cell and whose artifact carries a `leakage_exclusion` block reading
  `excluded: 18` over `assessed: 96`. Run against this entry's ledger it emits
  18 `::warning::leakage exclusion:` lines and writes
  `by_predictor: {claude-baseline: 6, codex-baseline: 6, gemini-baseline: 6}` —
  the exclusion falls evenly across the three engines, so it is not a
  differential-coverage event, which is the reason the split is published at all.

- **The document selector reaches the whole case-opening filing family and the
  application, 2026-09-02.** A **conditioning** entry with no digest movement —
  no prompt byte and no registry field changes — and, unlike the
  provisioning-cutoff entries above, **no data-visible boundary at all**: which
  documents a cell was provisioned with lives in its gitignored
  `record/documents/`, and `prediction.json` carries no *semantic* field
  separating a cell that read its petition from one that did not. So this
  boundary exists only here, and cells minted on the affected dockets before and
  after it may not be pooled. It is nevertheless **mechanically checkable**
  rather than a matter of trusting this record: every stamped cell carries
  `process_version.pipeline_sha`, so a cell resolves to a side of this boundary
  by asking whether that sha is an ancestor of the carrying promotion's merge
  commit. The population is named below so the check has something to run over.

  **What changed.** `pipeline.documents.select_documents` matched one
  case-opening entry, "petition for a writ of certiorari … filed", and had no
  arm for an application at all. It now matches the seven entry shapes the Court
  actually opens a cert-form docket with — certiorari, certiorari *before
  judgment*, *mandamus*, *prohibition*, *mandamus and/or prohibition*, *habeas
  corpus* (whose entry omits the article), and a
  direct appeal's *statement as to jurisdiction* — all stored under the
  unchanged `petition` kind, and selects a docket's own
  `Application (…) … submitted to Justice …` entry under a new `application`
  kind whenever the ask reads **substantive** to the same predicate that gates
  the interim predict queue. An administrative application — more time, more
  pages, more words — is not selected, and neither is an ask that predicate
  cannot read.

  **The population it moves, and what it has already cost.** The census is
  quoted from the per-case route walk that motivated the change — `fedcourts
  corpus-info --text-coverage` run store-configured against the blob whose
  newest pull stamp is `2026-09-02` (newest stored snapshot `2026-07-13`),
  plus a per-case read of each named docket's live JSON: of 249 cases queued
  for prediction, 33 held no primary document, and 19 of those carry a
  first-filing entry with a live document link — 8 cert-form dockets in the
  filing family this arm now matches, and 11 application dockets. **That 19 is
  a reading of the entries and links, not an executed run of the new
  selector**: the walk probed three of them end to end (25-1290, 26-40,
  26A203 — all HTTP 200 with real extracted text) and read the entry text and
  link label on the rest. The effect check below is what settles it, and it is
  the figure that check will falsify first if the reading is wrong.

  **What the new selector does read, run over the same blob.** The class is
  defined by the filing family rather than by that census, so the arms were
  also run — the real `select_documents`, not a re-implementation — over all
  1,567 stored SCOTUS payloads carrying proceedings. The case-opening arm
  newly reaches **51** of them, none of which it previously did and **none
  lost**: 16 habeas-plus-IFP, 10 mandamus-plus-IFP, 5 certiorari before
  judgment, 5 mandamus, 4 mandamus and/or prohibition, 2 bare habeas, 2
  jurisdictional statements, 1 prohibition, and the remainder further IFP
  pairings. The application arm selects **22**, every one of them substantive
  (a stay, a stay of execution, an injunction). Those two numbers are the
  measured shape of what this entry moves; the queued census above is the
  subset of it that costs cells.

  **The cases, named, because the ledgers that hold them today are the ledgers
  this change drains.** Of the 19, **14** already carry committed prediction
  cells that ran docket-only — **66 cells** in all. Four cert-form dockets, 3
  cells each (12): `scotus/73275185`, `scotus/73299074`, `scotus/73358839`,
  `scotus/73500218`. Ten application dockets (54): `scotus/73279700`,
  `scotus/9526000124`, `scotus/9526000139`, `scotus/9526000163`,
  `scotus/9526000203`, `scotus/9526000245`, `scotus/9526000256`,
  `scotus/9526000273`, `scotus/9526000274`, `scotus/9526000275` — four of them
  at 9 cells and six at 3. Prospectively
  this entry closes the class at the trigger; the committed cells stay as they
  were minted, and a cell minted on one of these cases after this lands read
  strictly **more** than one minted before it.

  **None of the 66 has ever been counted, and the condition is registered
  rather than assumed.** Partitioned by their own stamps: 11 are unstamped (an
  unstamped cell is never frozen), 39 carry digests outside
  `FROZEN_PROCESS_DIGESTS` and are de-counted by the membership filter, and 16
  carry blessed `proc-v5` predictor digests but are stamped before
  `FROZEN_SINCE` = `2026-09-05T00:00:00Z`, so they are de-counted by timing.
  **That holds provided this promotes before that instant.** If it promotes
  after it, a cell minted on this population in the gap would be counted *and*
  provisioned under the old selector, and would need its own entry — and the
  interim lane is the one that mints continuously, since its predict trigger is
  the live channel's docket-change queue rather than a conference calendar.

  **The expected-skill corollary, registered so a rise cannot be read as more
  than it is.** A post-change cell on an affected docket reads its primary
  filing where a pre-change one read the docket entries alone, against an
  unchanged realized baseline. Expected skill on that population should
  therefore **rise** — and a rise across this boundary **may not be read as a
  model improvement**. That is the negative form deliberately: the design
  supports excluding one reading, not asserting a cause, and 14 cell-bearing
  cases support no pooled figure either way. The class is defined by the filing
  family and the docket form, not by that count, so a docket entering the gap
  between now and the carrying promotion joins it.

  **No base rate re-prices.** `pipeline.salience` and `pipeline.base_rates` read
  no document text, so no band assignment and no segment base rate moves. This
  is a conditioning change and a measurement change, and nothing else.

  **The measurements this moves.** `corpus-info --text-coverage`'s queued gap
  becomes **form-keyed**: a cert-form
  row is measured against its `petition`, an application-form row against its
  `application`, each against its own form's denominator. The application-form
  gap therefore stops being a structural floor — "an application is not a cert
  petition, so nothing was ever selected" — and becomes a provisioning gap that
  drains as the documents store; it is reported as `queued_without_application`,
  named for its predicate, while `queued_application_forms` keeps its name for
  the population it is now the denominator over. Three more move at the same
  instant. The `petition` kind's own denominator widens, since four further
  filing types now store under it. `cases_read` and the `text frame:` reach line
  rise because `TEXT_COVERAGE_KINDS` gained a kind, which is the kind list
  widening and not more reach. And `metrics/live-frontier.json`'s
  `documents_provisioned` — the one moved figure with a committed downstream
  surface — counts watchlist cases holding any document over a watchlist keyed
  on `is_modern_cert`, so the mandamus, habeas, certiorari-before-judgment and
  jurisdictional-statement dockets on it start counting.

  The runnable effect check, for the promotion carrying this:
  `uv run pytest tests/test_documents.py` green, and — on the next `run-pull`
  window that provisions one of the named dockets — `fedcourts corpus-info
  --text-coverage` showing a `no application, queued` ledger shorter than the
  11 it starts at, with the recovered case holding an `application` row. This
  entry registers the prospective half only. The retrospective half — a bounded
  corpus pass applying the same selector to the cases already past their trigger
  — is not built, and will carry its own entry when it is: without it the 14
  cases whose cells already ran keep the record they were minted with.

- Freeze commit: `86ab9ace96486b22b147bac7e24244929dc9c1c1`, to be tagged
  **`prereg/proc-v6`** per step 4 — on this freeze commit itself, once its
  carrying promotion lands and the instant audit passes (`proc-v4`'s
  merge-placed tag is the recorded anomaly, not the rule). Blesses the six
  proc-v6 digests, retires all six of `prereg/proc-v5`'s, and **holds** the
  freeze instant at **`2026-09-05T00:00:00Z`**. Carried to `main` by the
  promotion tagged **`promotion/2026-09-03`** (merge commit `9293f70539718b5e5dbbad0c904ae4cbca6e6bac`, merged
  `2026-09-03T23:46:41Z`).

  **Fleet-wide: both halves move, and two different inputs move them.** Every
  enabled actor's digest changes, so both halves of the map are replaced at
  once. The shape this takes is the **first** supersession — re-freezing
  before the prior instant has any cells
  ([process-version.md](process-version.md#freezing-the-cutover-procedure)) —
  and not the third: the predictor half is the enforced filter, but
  `proc-v5`'s instant has not arrived, so no cell it retires was ever counted
  and no de-count declaration is called on (the census and the condition are
  below). `prereg/proc-v5`'s headline is therefore legitimately empty forever
  on the intended timing, and its tag stays as the record that the label was
  registered and then superseded — empty for a different reason than
  `prereg/proc-v1`'s, which is empty because nothing was ever stamped under
  it at all, where proc-v5's is empty because nothing stamped under it ever
  reached the instant. The census below is that stamped cohort.

  **One rule this freeze restates rather than relies on, recorded because the
  restatement travels in the same commit.** The third supersession shape read
  "moving `FROZEN_SINCE` past the carrying promotion, the ordinary step-4
  rule", which describes the move rather than the requirement; step 4's own
  text has always stated a **position** — "the literal in the file must be at
  or after that same date" — which an instant already sitting ahead of the
  merge satisfies without moving. `docs/process-version.md` and the
  `process_version` module docstring now say so, and say that where the prior
  instant has no cells the re-freeze is the plain first-shape supersession.
  That is a correction of wording to match step 4 and the first shape's own
  "(zero, or listed)", not a new licence — but the supersession rules are what
  an auditor checks this entry against, so the amendment is named here rather
  than left to `git blame`.
  Two inputs moved the bytes. The **prompt bytes**: `.github/prompts/predict.md`
  and `.github/prompts/evaluate.md` are shared by all three engines, and
  correcting them moves all six digests — which is the reason the three
  standing amendment
  debts below were owed to a re-bless rather than taken where they arose. Both
  files' `MODEL_ID` row is refreshed to the new id in the same pass: it is an
  illustrative example rather than a contract, but its bytes are hashed like
  every other, so leaving it would have cost a second six-digest re-bless to
  correct. The
  **resolved model**, on the claude pair only: `claude-fable-5` →
  `claude-fable-5-1`. No registered actor pins a `model:` override, so
  `pricing.DEFAULT_MODELS["claude-code"]` *is* what a claude cell runs — the
  predict/evaluate matrix resolves `model or DEFAULT_MODELS[engine]` into
  `MODEL_ID` and into `usage.json`, and `process_version._resolved_model`
  hashes that same resolved value, deliberately, so a default bump cannot ride
  under an unchanged digest. `claude-fable-5` keeps its rate in `MODEL_RATES`
  so the cells already in the ledger still price.

  **The digest table** — every enabled actor, retired → blessed:

  - `claude-baseline`, predictor:
    `sha256:eba87d4c4f66e8d9270d72f5e2809de4cce384d2a16451f6ad1e24bf60115774`
    → `sha256:902b332565be0a00f1180796b6ba1b216567300921416c2c3730cc6bca40e485`
  - `codex-baseline`, predictor:
    `sha256:b46b3c6df26f763bb607b091c283c5e7aa55c9a936ab3486e598f5a0f0de312e`
    → `sha256:5af41a53302ee9349ab3f210903b7f756bf27aa5d2a2392eb3394404bbad730f`
  - `gemini-baseline`, predictor:
    `sha256:8c401008655b9fb13080faeb30bc78a3a0d7e6c598bd149d90386409bada4c4f`
    → `sha256:8438d9682a88a0f972ba18fdcaa64f9587096015c4c99d4ba58e6440b0bde999`
  - `claude-judge`, evaluator:
    `sha256:11a0afbcba271935c8ead785b5c13fc2b1e43a4e18e9450a04fa41df9658a0f2`
    → `sha256:e84e8e5fbf47002aa9ed867db60f3f5eee82dcc3bfdd76e44a0b4aac09d5e631`
  - `codex-judge`, evaluator:
    `sha256:9fb7b6f1683a7bcb363cb19ae2084dfec734a9e1251b7b9fcc41dd2564aaff78`
    → `sha256:e44173fbe316c7dc95412f3b1165f7ac37f6f41ac7d2bb4ef58d86dee7dca7a8`
  - `gemini-judge`, evaluator:
    `sha256:b9f548f4f1e2cb1c07e9ba59f7d352220a2d8ae45d82e00f436dc044bd260b1a`
    → `sha256:64ae1b0c392b62f88c952bbbcc44de2d9ea358f7a7c36dbc10d231f9ed3366c3`

  Read off `fedcourts process-digest --all` against this tree. The blessed six
  are the whole of `FROZEN_PROCESS_DIGESTS`: the map holds one blessed process
  per actor, so the retired six are replaced rather than kept beside them, and
  this table is where they stay on the record now that the constant no longer
  names them.

  **The bless moment.** No digest carries forward byte-identical from an
  earlier label — the evaluate prompt moves for all three judges, the predict
  prompt for all three predictors — so none inherits an earlier bless moment
  and all six take this freeze's. At authoring each carries step 2's forecast,
  `2026-09-03T00:00:00Z`: this commit's day floored to midnight, which sits
  below step 2's own floor of the commit timestamp — the safe direction, forecast
  early because a late forecast fires the ledger tripwire on every honest cell
  minted before step 4's correction. Step 4 replaces all six with the carrying
  merge's real time, `git log -1 --format=%cI 9293f7053` =
  `2026-09-03T19:46:41-04:00` (`2026-09-03T23:46:41Z`).

  **The boundary, stated: no committed cell re-stamps.** A cell stamped before
  the bless moment carries the digest that was blessed when it ran, and this
  freeze changes none of them — the stamp is written once by `stamp-cell` and
  a re-grade preserves it. So the whole committed ledger keeps proc-v2/v3/v4/v5
  digests, all of which are now outside the map. Both ledger tripwires
  (`tests/test_process_version.py`) walk their halves and skip every cell whose
  digest the map does not hold, so both are green over the committed data with
  their loop bodies executing zero times; the **evaluation** half is the one
  that enforces the bless boundary on gradings, and it arms against the first
  proc-v6 grading rather than against anything already committed.

  **Census at authoring**, over this tree, whose `data/cases` is byte-identical
  to `origin/main`'s (`git grep -l '"process_version": {' origin/main --
  data/cases` = 434; 257 stamped predictions + 177 stamped evaluations here =
  434): 667 committed predictions, 257 stamped, of which **26** carry the
  retiring proc-v5 predictor digests (9 `claude-baseline`, 8 `codex-baseline`,
  9 `gemini-baseline`); 189 committed evaluations, 177 stamped, of which **45**
  carry the retiring evaluator digests (15 per judge — the 39 labelled
  `proc-v5` plus the 6 labelled `proc-v4`, whose bytes proc-v5 carried forward
  under the same digests, which is exactly the continuity the proc-v5 entry
  recorded). The rest carry proc-v2/proc-v3 digests already outside the map.
  Step 0's stamped-cell grep for each of the six **newly blessed** digests:
  **zero** on `origin/main` and **zero** in this tree, all six. Re-run at the
  promotion: zero on the promotion merge's own tree (`9293f7053`), all six.

  **The de-count this freeze executes, and why no shakedown declaration is
  called on.** Retiring the predictor half removes every prediction stamped
  under those digests from every frozen-scope artifact — the mechanism the
  third supersession shape names, engaged here over an empty set.
  That set is the 26 above, and **none of them was ever counted**:
  `FROZEN_SINCE` is `2026-09-05T00:00:00Z` and the newest stamp anywhere in the
  ledger is `2026-09-03T01:17:40.190125Z`, so all 26 are already de-counted on timing
  by `is_frozen`, as are all 45 gradings by `graded_post_freeze`. A boundary
  declaration exists to license dropping cells that *were* claimable; here the
  headline is empty on both sides of the move, so there is nothing to license.
  That holds on one condition, registered rather than assumed, and stated in
  full below.

  **The counting window, and which side this lands on.** The instant opens two
  days after this entry's date, so the promotion's timing decides which of two
  boundaries the record gets:

  - **Promotes at or before `2026-09-05T00:00:00Z`** — the intended case. The
    counting window opens on proc-v6 with nothing behind it: no cell is ever
    stamped under a proc-v5 digest at or after the instant, the de-count above
    stays empty, and the counted record for the long-conference claim window
    begins with the first cells stamped under the six blessed digests at or
    after the instant. `FROZEN_SINCE` needs no move, and — this is the ordinary
    step-4 date rule being satisfied, **not** the held-instant evaluator
    exception, which is scoped to a byte-identical predictor half and cannot
    apply to a fleet-wide re-bless — the auditor's check is the date
    comparison: the carrying promotion's merge at or before the instant.
  - **Promotes after it** — the split case. Cells minted from `main` in the gap
    `[2026-09-05T00:00:00Z, carrying merge)` run the proc-v5 bytes, carry a
    then-blessed predictor digest and a stamp at or after the instant, and are
    therefore **counted**; landing proc-v6 retires those digests and de-counts
    them, splitting the early counted cohort across two labels at the bless
    moment. Two things follow, both registered here in advance rather than
    improvised then. First, **this entry is the declaration** the third
    supersession shape requires for that cohort: dated `2026-09-03`, before any
    gap cell exists and so necessarily before its claim window's outcomes, it
    declares any cell stamped under a proc-v5 digest at or after the instant a
    **shakedown** cell, with proc-v6 the counted record; no claim pools across
    that boundary in either direction, and the gap cohort's census is filled at
    the promotion below. That census must carry the shape's
    resolved-outcome clause, not just a head count: the declaration predates
    the gap cells themselves, which settles the *forward* slice outright, but a
    gap cell can be a replay over an event that had already resolved, and for
    those the declaration creates no pre-registered boundary. What bounds them
    instead is that a retrospective cell is never claimable performance in the
    first place — so the census names the split rather than resting on the
    date alone. Second, `FROZEN_SINCE` must then be **bumped past the
    carrying merge in a follow-up promotion before the `prereg/proc-v6` tag is
    minted** — the `prereg/` namespace blocks update and deletion, so a tag
    over a bad instant burns the label — which independently drops every
    evaluation stamped before the new instant via `graded_post_freeze`, blessed
    evaluator digests or not, so the boundary is total in both halves.

  Which case obtained: promoted before the instant; the gap is empty
  (merge `2026-09-03T23:46:41Z` against `FROZEN_SINCE = 2026-09-05T00:00:00Z`,
  the clean first-supersession timing this entry intended).

  **The evaluator half's pooling exposure, and the surfaces it actually
  reaches.** An evaluation's digest is recorded but never partitions the
  headline, so the 45 gradings under the retiring
  digests stay exactly as counted (or, here, as uncounted) as they were, and
  grading series pool across the rubric boundary this re-bless introduces with
  nothing partitioning on it. The **frozen board is not one of those
  surfaces**, and only because both halves move together here: a frozen-scope
  cell's prediction digest can only be one of the proc-v6 three, so it was
  minted from `main` after the carrying promotion and its grading necessarily
  carries a proc-v6 evaluator digest. What does pool is the `--all-versions`
  diagnostic view and the deliberately version-blind leakage digest on the ops
  dashboard, which counts every graded cell frozen or not. That exposure is not nominal on this
  label: the leakage bit's contract is one of the three things corrected, and
  the `leakage_suspected` entry of **2026-09-02** already registered that a
  count of flagged gradings taken after the re-bless is **not poolable** with
  one taken before, because the graders before it were told the bit was inert.
  The 18 flagged gradings that entry measures are all on the near side.

  **The three debts paid, each against the entry that registered it.**

  - *The interim arrival moment is dated from the docket's own submission
    entry, 2026-09-02* — its closing "one amendment debt" paragraph. The
    predict prompt told an arrival cell its event was "opened when the
    application was docketed", which that change made false. It now says the
    event opens at the application's own submission entry, with the docketing
    date only where no submission entry can be dated, and says that this is
    where the snapshot ends. An arrival cell is no longer told a wrong thing
    about its own cutoff.
  - *An amendment debt for the merits pool-guard prompt wording, 2026-09-02* —
    all three corrections it names. Both prompts' merits paragraphs drop the
    false undated arm ("no date the gap could be tested on"), state the guard
    as it is — a row whose parsed judgment is **dated on or before its own
    grant** — and say what happens to the undated parse instead: untestable, so
    it stays in `granted` as a coverage gap with only its judgment out of the
    parsed slice. Both now carry the **partition reading rule** neither had:
    an excluded row is counted in `excluded (not in granted)` *instead of* in
    `granted`, so per Term the two partition the pre-guard population, only
    `parsed` nests inside `granted`, and a Term whose `parsed` + `excluded`
    runs past its `granted` is adding across two populations rather than
    showing a defect. The evaluate prompt's parenthetical mislabelling an
    untestable row as a cert-order rider goes with it. Every non-frozen surface
    has said this since that entry; the prompts now agree with them.
  - *`leakage_suspected` becomes an exclusion: a flagged grading leaves every
    rank key and every scored aggregate, 2026-09-02* — its "one stale
    contract" paragraph. The evaluate prompt said the assessment "is advisory
    and segments scores". It now states the rule that entry registered: the bit
    is an **exclusion**, taking its cell out of every rank key and every scored
    aggregate on every board, forward stratum included; the boards publish the
    count with its `assessed` denominator and per-predictor split; the unit is
    the grading, not the prediction; a **null** bit is "not assessed", not
    "clean"; and it still changes **no score value** — `correct`,
    `brier_score`, and the rest stand exactly as computed. From the first
    proc-v6 grading on, a flagged bit is set by a grader who was told what it
    does.

  **One prompt sentence deliberately not touched**, so its survival is a
  recorded judgment rather than an oversight: both prompts tell a cell that a
  `flags.json` note "survives the trigger issue's closure". The phase-2 trigger
  redesign that retires the `run:*` labels is **not** on `staging` at this
  entry's date — `run-predict.yml` still enters on `issues: labeled` — so the
  sentence describes the pipeline as it stands and is true where a cell reads
  it. Correcting it early would state a mechanism that does not yet exist. It
  moves all six digests when it is corrected, so it is owed to the re-bless
  that carries the label retirement, on the same terms these three debts were
  owed to this one.

  **The committed boards keep the old provenance until the next refresh.**
  `metrics/leaderboard.json` and `metrics/claim-scores.json` embed
  `frozen_process.digests`, which still names the proc-v5 six; those artifacts
  are regenerated by the run-analytics `metrics-refresh` job and never by hand,
  so the lag is regeneration and not a defect — the same shape the statpack
  relabel's entry records. Both boards are empty of scored entries at this
  entry's date, so no published figure carries the stale provenance.

  **The runnable effect check, for the promotion carrying this.** Two halves,
  because two different things moved. That the engine accepts the new model —
  an `engine-actions-smoke` dispatch on the claude leg, which resolves its
  model from `DEFAULT_MODELS` and so probes `claude-fable-5-1` exactly:
  `gh workflow run integration-test.yml --repo ModelMirrorAI/fedcourtsai --ref
  main -f scenario=engine-actions-smoke -f engine=claude-code -f
  deploy-environment=prod`, green, with the resolve step's output naming
  `claude-fable-5-1`. And that the fleet stamps the new process — on the first
  predict and evaluate cells minted after the promotion, `prediction.json` /
  `evaluation.json` carrying `process_version.label` `proc-v6` and a digest
  from the table above, with the claude cells' `usage.json` recording
  `"model": "claude-fable-5-1"`.

- *The interim arrival repair moves a provisioning boundary a second time, and
  its instant is a dispatch rather than a promotion, 2026-09-03.* Registered
  **ahead of** the repair that carries it, because the thing that needs
  registering is a rule about when the boundary moves, and the rule has to be on
  the record before the move rather than after.

  **What moves.** The `arrival-backfill` maintenance pass re-derives
  `events.opened_at` on SCOTUS interim baseline events (`evt-motion-disposition`,
  not entry-pinned) whose stamp shows either shape of the pre-arrival-read
  defect: no stamp at all, or the docketing date. `provision.moment_cutoff`
  takes that stamp, so a repaired event's cells are cut at a different — always
  earlier, or newly bounded — instant than the same event's cells were before,
  and `provision.documents_before` takes the same cutoff, so which filed
  documents an interim cell reads moves with it.

  **No digest moves, and the reason is already registered.** The provisioning
  cutoff is on the list in `docs/process-version.md` of things that change what
  a predictor is conditioned on without touching a prompt byte. Corpus data is
  not a digest input; the pass adds no capability and opens no retrieval
  channel — it re-parses stored payloads with the parsers ingest already uses —
  so no `ENGINE_RETRIEVAL` entry is owed and no canonical-config field changes.

  **What this entry registers instead, in three parts.**

  *The instant is the apply dispatch, not the promotion.* The boundary rule
  registered for the arrival read takes effect for cells provisioned after the
  promotion carrying it. For the population this pass exists for — rows the live
  rotation never re-polls — that is false in fact: the promotion moves no stamp,
  the apply does. So a figure over interim arrival cells may not pool across the
  apply dispatch, and the dispatch's own date is the boundary instant to quote.
  It matters more here than at the read's own boundary, and differently on each
  arm. For the **moved** rows `context.cutoff` is non-null on both sides, so the
  two conditionings are not separable from the artifact alone and only the
  dispatch date tells them apart. For the **stamped** rows it moves from null to
  non-null — a pre-repair cell took no cut at all and carries `as-stored`
  provenance — so there the boundary *is* visible in the artifact, as the
  as-stored → placed transition this entry's provenance paragraph describes.

  *It may straddle the counting instant.* `FROZEN_SINCE` is `2026-09-05`. If the
  apply lands on or after it, frozen-counted interim arrival cells exist on both
  sides of the boundary and a figure over them may not pool across it. If it
  lands before, nothing counted re-bases.

  *The pre-repair stamps survive only if they are written down.* After the apply
  the corpus holds the new stamp and each event's committed `event.yaml` is
  rewritten with it the next time any cell runs over that event, so the pass's
  own `filled` list is the sole record of what a committed interim cell's cutoff
  had been derived from. The apply owes an entry here carrying it, along with
  the dispatch date and the ledger's `corpus_vintage` — which every exposure
  figure below is a counterfactual over, so a figure quoted without it states a
  bound whose basis is unrecoverable — plus the `events_seen` /
  `baseline_candidates_seen` / `events_all_slices` / `candidates` /
  `candidates_resolved` / `stamped` / `moved` / move histogram /
  `over_admitted_entries` / `admitted_the_disposition` /
  `admitted_the_disposition_committed` / `residue_admits_disposition` /
  `unrepaired` / `unrepaired_resolved` counts. Only **resolved** rows can appear
  in `admitted_the_disposition` or `residue_admits_disposition` — both are keyed
  on `date_decided` — so neither list discloses anything about a pending case.

  **What the repair can and cannot be said to remove.** The defect is that
  resolution status decides which stamp a row carries — the poller re-polls only
  unresolved applications — which is an outcome-correlated conditioning rule on
  any retrospective interim cohort. The pass removes that correlation on the
  slice carrying a readable live-shaped snapshot with a parseable arrival, and
  no further: a candidate with no stored snapshot, no proceedings list, no dated
  submission entry, or a reading the direction guard refused keeps its
  pre-repair stamp. Late is the safe direction for *leakage* and is the defect
  itself for *conditioning*, so those rows are the still-conditioned remainder
  rather than a safe fallback — and the residue has a structural reason to
  concentrate on the decided side, since a stored live snapshot exists because a
  channel polled the case. The ledger therefore splits the class, the repairs
  and the residue by resolution, and the apply's entry states that split.

  The residue is **measured, not merely counted**, and it has to be: the
  exposure readings below are taken over the rows the pass repaired, and
  conditioning persists exactly where the stamp did not move. So the ledger also
  reports `residue_admits_disposition` — the unrepaired rows whose *surviving*
  stamp still admits their own disposition, answerable from the stored stamp and
  `date_decided` with no arrival needed, so every arm is covered including the
  rows whose snapshot could not be read. A boundary claim scoped to the repaired
  rows describes the half of the class that was fixed and says nothing about the
  half that was not; both halves are stated.

  Two denominators go with that, because one number cannot carry it.
  `baseline_candidates_seen` is matched to the predicate, so the prevalence is
  taken against the population the predicate could actually select rather than
  against the looser `events_seen` (which counts entry-pinned rows this route
  never acts on, and exists only as the wrong-blob refusal). `events_all_slices`
  drops the live-slice limb: this pass needs a stored live-shaped snapshot, so
  rows outside that slice are never candidates and keep their defective stamps
  through every dispatch — the gap between the two is the arm no run of this
  pass reaches, and it is invisible without the count.

  **The reading rule for the move sizes.** The day-delta histogram is the
  *window* the pre-repair cut spanned — an upper bound on what could have been
  admitted, not a measure of what was. A one-day move on a docket disposed of
  that day admits the outcome; a month over a quiet docket admits nothing. The
  claimable figures are the entries-admitted counts beside it and the named rows
  whose own disposition falls inside the band, which is the form the arrival
  read's own boundary measurement took.

  **Those figures are counterfactuals, and must be quoted as such.** They are
  computed against each row's newest stored snapshot with **no date bound**, so
  they state what a cell provisioned *today*, over the corpus at
  `corpus_vintage`, would admit under the pre-repair stamp — a bound on the
  rule's remaining forward exposure, not a measurement of what any committed
  cell was shown. The error runs both ways and neither direction is
  conservative: they **over**-count against a cell provisioned when that docket
  was shorter, and **under**-count wherever the stored snapshot itself predates
  filings the docket has since gained. What turns the bound into something
  checkable is `admitted_the_disposition_committed`, the intersection with the
  events carrying committed predict output — still not proof a cell saw the
  disposition, but the population where that question is worth asking one
  grading at a time.

  **The provenance mix moves with it.** The repair takes rows from `as-stored`
  to placed (the unstamped arm, whose cells took no cut at all and read the
  latest snapshot) and shifts placed rows from `dated` toward `truncated`, since
  an earlier cutoff is less likely to find a stored pre-cutoff snapshot. Any
  figure pooling cells on these events states the mix under the reading rules
  already registered for it.

  **The runnable effect check, for the promotion carrying this.** The promotion
  moves no stamp — this pass is dispatch-gated — so the check is that the pass
  is dispatchable and reports a class:
  `gh workflow run run-repair.yml --repo ModelMirrorAI/fedcourtsai --ref main -f
  repair=arrival-backfill -f repair_mode=dry-run`, green, with the run summary
  carrying a ledger whose `events_seen` is non-zero. The apply is a separate
  decision taken against that ledger, and it is the event this entry's
  successor records.

- *The interim arrival repair applied: 1956 interim stamps repaired — 1847
  moved earlier, 109 newly bounded — and the boundary now sits on the far side
  of the freeze instant, 2026-09-05.* The event the previous entry's successor
  clause owes: the `arrival-backfill` apply, dispatched by the maintainer
  against the same-day dry-run ledger (Actions run 33967007763) and executed
  at 2026-09-05T13:22Z (Actions run 33967774006), corroborated by committed
  state: data commit `89f3b1f5b` ("repair: converge corpus (interim arrival
  stamps)", authored 2026-09-05T13:22:21Z) moved the corpus pointer from
  sha256 `2ee65d00821216e4f5559d251290f0989ea0e02b44556e84f36f821db0efa60b`
  (pre-apply) to
  `2646d8db95597006bb658b2497ffd7325d41ee194ba303295d1df20d92c503f7`
  (post-apply). The apply's figures match the dry run's line for line, and
  both run ids are named above so the equality is checkable.

  **The membership record.** Post-apply, the `filled` (1956) and `unchanged`
  (113) arms are indistinguishable in the corpus — both now carry a
  non-docketing-date arrival — so the set the rule below binds on lives in
  the pass ledger, which is deterministic over a fixed blob: a dry-run
  dispatch against the pre-apply pointer named above regenerates `filled`,
  the candidate class, and the named `admitted_the_disposition` list
  verbatim. That pointer is an `index/sha256/` object on the 30-day
  lifecycle, so the reconstruction path closes around 2026-10-05; a permanent
  copy of the `filled` list must be committed before then or the membership
  set survives only as the counts recorded here.

  **The figures, in the registered form.** Stamped **1956 of 2070**
  candidates, and the class closes exactly: 1956 filled + 113 already
  carrying their arrival (submitted and docketed the same day — matched the
  predicate, found correct) + 1 naming no dated submission entry. The other
  residue arms were empty as an observation, not an inference: 0 with no
  stored snapshot, 0 whose snapshot discloses no proceedings, and
  `later_refused` empty. Denominators as registered: `events_seen` 2096,
  `baseline_candidates_seen` 2095 — prevalence 2070 of 2095 (98.8%), in the
  only population where the defect was measured — and `events_all_slices`
  27631: the 25536 rows outside the live slice hold no re-readable snapshot
  and are unreachable by every dispatch of this pass, and the defect's
  prevalence there is unmeasured. The stamped arm splits 109 with no prior
  stamp at all (those cells took no cut; an unbounded window closed rather
  than a late one tightened) and 1847 moved earlier — worst move 473 days;
  moved-arm histogram 1d: 25, 2–3d: 407, 4–7d: 798, 8–14d: 350, 15–30d: 156,
  31+d: 111, read under the window-not-admission rule the previous entry
  registers. Resolution split: 2067 of 2070 candidates decided; 1955 of 1956
  repairs.

  **The counterfactual exposure, quoted as such** (corpus vintage 2026-09-05,
  the apply's own blob): a cell provisioned at that vintage under the
  pre-repair stamps would admit 936 docket entries across 778 of the 1956
  repaired rows that the repaired stamps do not; for 701 of the 1956 the band
  includes the case's own disposition, and for 15 the response request. Each
  count's denominator is the repaired class — 701 is not a subset of 778 by
  construction, since the disposition read comes from the case row and the
  entry count from dated proceedings entries. The disposition rows are named
  in the ledger, re-derivable from the pre-apply pointer above. The
  `admitted_the_disposition_committed` intersection is exactly one event —
  `scotus/9526000256` `evt-motion-disposition` — whose committed cells carry
  nine leakage gradings from three judges. They split: seven `none`; two
  `possible` with the leakage bit set, on two different cells, from two
  different judges, each contradicted by the other two panel members; one
  `retrieved_outcome_material` null (not assessed). All nine were taken
  against the forward-mis-provisioning shape, not the arrival band. The
  intersection's question is therefore locatable rather than answered: the
  gradings to re-read are named on that event, the partial-flag rule in
  `metrics/README.md` says no aggregate resolves the disagreement, and all
  three cells are shakedown (proc-v4/proc-v5, harness clocks 2026-08-29
  through 2026-08-31), so no frozen figure rests on any of them.

  **The residue.** 1 of 1 unrepaired rows is decided and its surviving stamp
  still admits its own disposition (`residue_admits_disposition` = 1). At
  n = 1 the resolution split is unreadable — the class is 99.9% decided, so
  one decided residue row is what the base rate alone predicts — and the
  claimable statement is the count. The defective class of 1957 (the 2070
  candidates less the 113 found correct) shrank to this one row on the
  reachable slice; the residue's all-decided character was shrunk, not
  removed.

  **The straddle resolved the strict way, and the rule it triggers.** The
  apply landed after the proc-v6 freeze instant (2026-09-05T00:00:00Z), so
  the conditional both predecessor entries carried resolves against the
  relief clause. The standing rule: a figure over interim arrival cells may
  not pool across the apply instant. The split is read from harness
  observables, never a clock the agent controls: a cell whose `run_id` is at
  or after `20260905T132200Z` was planned after the apply and carries
  post-repair conditioning; a cell whose `process_version.stamped_at` is
  before 2026-09-05T13:22:21Z finished before it and carries pre-repair
  conditioning; a run in flight across the instant is the ambiguity band,
  and that band is empty at this entry's date — the latest committed interim
  cell's clock is 2026-09-01T03:00:24Z. On the unstamped arm the boundary is
  additionally artifact-visible, as the previous entry registers:
  `context.cutoff` null → non-null, `snapshot_provenance` `as-stored` →
  placed. In practice both arms of the *frozen* partition start empty: the
  pre-apply frozen arm could only ever be populated from the
  00:00:00Z–13:22:21Z window, which closed with no cell committed inside it,
  and the 30 committed interim cells — all shakedown — sit entirely on the
  pre-apply side. The rule binds the cells the next predict tick mints
  onward.

  **The provenance-mix consequence now applies.** From the next provisioning
  onward the repair takes the unstamped arm from `as-stored` to placed and
  shifts placed rows from `dated` toward `truncated`; any figure pooling
  cells on these events states the mix under the reading rules already
  registered.
