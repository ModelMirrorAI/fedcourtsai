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

- *The interim arrival moment's cut becomes positional as well as dated: the
  snapshot stops at the entry that opened the event, and the boundary is
  recorded on the artifact, 2026-09-05.* A **provisioning-cutoff** change, registered here
  on the terms [process-version.md](process-version.md) sets for that member of
  the list, and carrying prompt bytes with it — the predict prompt's cutoff
  sentences and the evaluate prompt's leakage-clock rule are corrected in the
  same commit and ride the **proc-v7** re-bless, so this entry's digests are the
  ones that batch blesses rather than the ones in force when it was written.
  The batch's own entry records them; this one deliberately names none, because
  a digest written here would be superseded before it was ever stamped.

  **What moved.** A date-valued cutoff cannot express this moment. An interim
  event's `opened_at` names the day an application reached a Justice, the cut
  keeps everything filed strictly before the day after it, and a capital stay
  application can be submitted, referred, responded to, drawn amici and denied
  inside that one day — so the cut necessarily admitted the docket's own
  disposition, on the highest-salience interim shape there is. From this change
  the arrival snapshot is bounded twice: by the date rule as before, and by an
  **anchor bound** stopping the entries at the docket's own submission entry.
  Applied in **both modes** and on **both provenances** — including `dated`,
  which was previously used unmodified, because a snapshot the docket served on
  the arrival day itself already carries that day's later entries. The bound is
  never a naive positional slice: payload entry order is unpinned across the two
  upstream shapes, so the kept set is the intersection of the date bound with an
  anchor bound resolved against the list's own observed chronology, failing
  closed to the anchor entry alone where that chronology cannot be read — which
  is exactly the all-one-day docket the change exists for.

  **The artifact carries the boundary, which is what makes this registrable by
  freeze record alone.** `context.cut_kind` (`date` | `arrival-position`) and
  `context.cut_anchor_index` are new on `PredictionContext`. Without them the
  two conditionings would be byte-identical either side of this entry —
  `context.cutoff` non-null on both — and the separability the provisioning
  cutoff is registrable on would be gone. They also tighten the replay leakage
  clock rather than loosening it: the evaluate prompt's rule now reads
  `cut_kind`, so material dated inside the cutoff's day but positionally outside
  the cell's information set is graded as leakage instead of clean. That rule is
  registered **ahead of the cells it binds**: no lane mints a replay interim
  arrival cell today, so the population it governs is currently empty, and it
  takes effect if and when one is provisioned.

  **The membership rule, published rather than assumed.** A row whose opening
  entry cannot be located in its snapshot is **refused and counted** — never a
  silent fall back to the date cut, which is the conditioning being replaced.
  The anchor derives from the stamped opening entry (`events.opened_at`), so a
  stale-stamped row refuses. `fedcourts arrival-cut-ledger` is the surface that
  counts the refusals, split by resolution status, by same-day disposition, and
  by cause.

  **The figures, executed over the provisioning population.** Corpus vintage
  **2026-09-05**, blob sha256
  `597cd2632908d34910b3e3a3fe8ef4f040a2fd916d8f50d4e828b1c8ca81180c` — the
  pointer committed on `main`, which is where data commits land; a blob resolved
  from `staging` is stale by construction and, read here first, predated the
  arrival-backfill apply recorded in the entry above by six hours and reported
  its entire moved arm as a refusal class. The population is every SCOTUS
  interim baseline event in the live slice carrying a stamp at all
  (`opened_at IS NOT NULL`; an unstamped row takes no cut and this bound cannot
  reach it): **2095 rows**, all with a readable live-shaped snapshot.

  **Two denominators, and only one of them describes the pipeline.** The predict
  matrix drops every non-substantive application
  (`corpus.out_of_scope_reason_full` via `is_non_cert_scotus_form`), and the
  population splits **1665 extension / 345 substantive / 85 unknown** — so 83%
  of it can never be provisioned a cell, and that 83% is itself the terse,
  same-day-disposed shape any refusal correlation would run through. Every rate
  below that describes the pipeline is read over the **345 in-scope** rows; the
  whole-population figures are given beside them and marked.

  - **The same-day-after-opening-entry tail** — the separately named quantity
    this change is measured in, and deliberately **not** the arrival-backfill
    pass's `over_admitted` band, which opens the day *after* the arrival by
    construction and is therefore identically zero on this delta: **73 entries
    across 46 in-scope rows**, of which **7** carried the application's own
    disposition. Over the whole stamped population, 100 entries across 68 rows
    (66 disposed of), 15 carrying the disposition.
  - **The refusals: 1 of 2095, and 0 of 345 in scope.** The single refusal names
    no dated submission entry — the same row the arrival-backfill ledger counts
    as `unparsed` — and is a disposed-of, out-of-scope docket. The stale-stamp
    arm is **0** at this vintage, which is what the arrival-backfill apply
    recorded above bought: it is a corpus-convergence quantity, not a standing
    property of the rule, and it will reopen whenever a non-live re-extraction
    writes the docketing date back (`events.opened_at` takes no fill-in latch on
    the upsert path) until the sweep converges it again. So the membership rule
    costs, at this vintage, **no in-scope cell at all**. At n = 1 nothing about
    the refused class is claimable beyond the count; the resolution and same-day
    splits are registered so the question stays measurable as the arm grows, not
    because they answer it now.
  - **The forward lane's denominator**: the pending in-scope slice is **7 rows,
    7 anchored, 0 refused**. (14 rows are pending across the whole stamped
    population, but a non-substantive application never reaches the matrix
    however open it is, so the larger number is not an operational rate.)
  - **The claim-side deltas over interim-v1**, whole stamped population. The
    amicus-increment claim's frozen context count falls on **5 rows** (6
    entries) — an **upper bound** on new positives rather than a count of them,
    since the claim is `outcome.amicus > context.amicus` and a docket that
    gained a later amicus resolved positive under both readings. The
    response-requested increment moves from vacuously masked to resolvable on
    **31 rows** (29 disposed of); the referral increment on **9** (9 disposed
    of). Both of those then resolve **positive by construction**: the tail entry
    that unmasks the claim is the entry that satisfies it, and both flags are
    monotone-latched. So the realized positive rate of those two claims is not
    comparable across this boundary — the non-pooling rule below covers it, and
    covers *claim* rates as well as headline scores. When the conditioned
    baseline hazard for either is finally computed it must be taken at the
    arrival-position posture, or it will estimate a rate over a population from
    which same-day requests were removed while scoring exactly the cells that
    carry them.
  - **Masking is not reported as a measurement**, because it cannot vary: the
    anchor entry always survives the bound and the observability probe tests
    only that the proceedings key is a list, so an anchored row's cut payload
    always discloses proceedings. Recorded as a property of the bound rather
    than published as a zero that would read as empirical.

  Every figure is a **dry-run counterfactual over stored state**: each row's
  newest stored live-shaped snapshot, read with no date bound, so it says what a
  cell provisioned against this blob would carry rather than what any committed
  cell was shown. The reading needs the per-case content store addressed, not
  merely the index pulled — run against an index alone the command exits 0 and
  reports the whole population under `no_snapshot`, which is a wrong-blob
  reading rather than a clean one.

  **What the review confirmed unmoved, and is not re-derived here**: the interim
  base rate (it pools corpus columns, not snapshots), the interim selection
  population (it fills from latched columns), every stratum boundary (keyed on
  resolution against the harness clock), and placement lag (it reads the date
  stamp, which stays).

  **The straddle, registered affirmatively.** The proc-v6 freeze instant
  (2026-09-05T00:00:00Z) has passed, so frozen-counted interim arrival cells now
  exist on both sides of this conditioning change as they do of the arrival
  repair recorded above. The standing rule: **a figure over interim arrival
  cells may not pool across this boundary**, claim-level positive rates
  included. Unlike the repair's instant, this boundary is artifact-visible on
  every cell it touches, and the transition is `absent` → `arrival-position`
  rather than `date` → `arrival-position`: cells provisioned before the field
  existed carry no `cut_kind` at all, and an interim arrival cell will never
  carry `date`, since that moment either takes the anchor bound or refuses. So
  the split is read from the artifact rather than from a clock and no ambiguity
  band exists. The non-pooling reading is the same one the 2026-09-05 apply
  entry above registers, and the two boundaries compose: a figure over these
  cells states both. As at this entry's date the incoming arm is empty: the
  committed interim ledger holds 30 `evt-motion-disposition` predict cells,
  stamped proc-v3 (18), proc-v4 (2) and proc-v5 (10) — every one of them
  pre-proc-v6 and therefore shakedown, and every one of them taken under the
  date rule with no `cut_kind` recorded. So the rule binds the cells the next
  predict tick mints onward.

  **The runnable effect check, for the promotion carrying this.** A promotion
  moves code, not state, so the check is that a provisioned arrival cell records
  the new boundary and that the ledger reports a class:
  `uv run fedcourts arrival-cut-ledger`, green, with `rows_seen` non-zero,
  `scope_rows` non-zero and `scope_pending_anchored` non-zero. **It needs the
  per-case content store addressed, not merely the index pulled** — the reading
  comes from each row's stored live-shaped snapshot, which lives in the content
  store under the split, and `--corpus-backend` cannot select it; run against an
  index alone the command still exits 0 and reports the whole population under
  `no_snapshot` with `anchored` 0, so **read `no_snapshot` first**. Alongside
  it, `uv run pytest -k arrival_cut`, whose same-day-disposed and reversed-order
  fixtures are what fail if either half of the bound is removed.

- Freeze commit: `466951d756a573b2533a71e59376b4cfb7764758`, to be tagged
  **`prereg/proc-v7`** per step 4 — on this freeze commit itself, once its
  carrying promotion lands and the instant audit passes. Blesses the six
  proc-v7 digests, retires all six of `prereg/proc-v6`'s, and moves the
  freeze instant to **`2026-09-07T00:00:00Z`**. The carrying promotion is
  forecast for 2026-09-06/07; its merge time, the step-4 audit, and the gap
  census land as an **appended promotion-time entry** below — never as an
  edit to this one.

  The six digests blessed, read off `fedcourts process-digest --all` at the
  freeze commit:

  - predictors — claude-baseline
    `sha256:930e02ae18fd07192bede9d3e54ad420a66183db927f0b5d5939c2af0a2c93eb`,
    codex-baseline
    `sha256:c57113fae8715f31767475ef80bb2cee885534ea6c0c39c04aee327241bbf890`,
    gemini-baseline
    `sha256:4edc5ac58c718a385e9518a9a1cfc0f17f32eb62ca788ad79c91e7112c11994a`;
  - evaluators — claude-judge
    `sha256:84cf4c8b52a1475c8982a22876f9d01e2f628f4d5e9027709490679d211da868`,
    codex-judge
    `sha256:fa92c82e827ede277677781a11d13f20afc830517c11377cf50be167c8a07d36`,
    gemini-judge
    `sha256:2585c15a6b2c5f3f6cb4aa5393f49ee63592dbfd8ad38fc1a9b9dae0d2ce1bf3`.

  **Fleet-wide: both halves move, and two different inputs move them.** Every
  enabled actor's digest changes. The shared prompt templates' bytes move
  together — the cell contracts anchor on the case-level `record/` path; the
  predict contract loses the escape hatch that let a forward cell
  legitimately run without a provisioned snapshot (the harness refuses all
  unprovisioned paths); and the positional-cutoff contract lands whole, on
  both halves at once: the baseline bound, the replay retrieval boundary
  keyed on `cut_kind` (the opening entry, not the event date, under
  `arrival-position`), and the grading rule that the opening day is kept up
  to the anchor, with an unreadable ordering treated as outside and flagged
  as a stated conservative default. And on the codex pair alone, the
  resolved model moves: `gpt-5.6-sol` → `gpt-6-astra` (2× the input rate,
  5/3 the output rate; the budget re-projection rides the same batch). A
  codex figure therefore differs across this boundary for two confounded
  reasons, prompt and model at once; the digest boundary already forbids
  pooling across it, and this sentence is the record that the model is one
  of the things it separates.

  **The shape is the first supersession — nothing the retirement removes was
  ever counted.** proc-v6's instant (`2026-09-05T00:00:00Z`) has passed, but
  its counted set is empty: no prediction was ever stamped under any of its
  three predictor digests (the scheduled predict runs since the instant were
  plan-and-hold, their spend holds never released), and the only cells ever
  stamped under its evaluator digests are **14 evaluations** — 7 under
  claude-judge `sha256:e84e8e5f…`, 7 under gemini-judge `sha256:64ae1b0c…`,
  none under codex-judge `sha256:e44173fb…` (its three cells wedged on the
  2026-09-04 run and never landed) — every one stamped
  2026-09-04T18:47–18:57Z, before the instant. So no de-count declaration is
  called on, `prereg/proc-v6`'s headline is legitimately empty forever, and
  its tag stays as the record. Census commands, run 2026-09-06 against
  `origin/main`: `git grep -l 'sha256:<digest>' origin/main -- data/cases |
  wc -l` per retired digest (0, 0, 0 predictors; 7, 0, 7 evaluators, stamps
  read off the files), and the wider census `git grep -l
  '"process_version": {' origin/main -- data/cases | wc -l` → **448** stamped
  cells: 27 under proc-v2's digests, 331 under proc-v3's, 11 under
  proc-v4's, 65 under proc-v5's — the ordinary ledger under labels retired
  before this entry — and the 14 under proc-v6's that this entry retires.
  Step 0 for the six digests blessed here: the same per-digest grep, **0 for
  all six**.

  **The gap, declared in advance.** proc-v6's window is open until the
  carrying promotion lands, so a spend hold released before it would mint
  cells stamped under proc-v6 digests at or after its instant — counted on
  minting, de-counted by this supersession. Dated today, while no such cell
  exists and before any such cell's claim window could resolve, **this entry
  is the declaration** the third shape would then require: any cell stamped
  under a proc-v6 digest at or after `2026-09-05T00:00:00Z` is a
  **shakedown** cell, proc-v7 the counted record, no pooling across the
  boundary in either direction; if any exist by the promotion, the
  promotion-time entry carries the census and must name the
  resolved-outcome split, not just a head count. Operationally the gap is
  kept empty the same way proc-v6's was: the scheduled predict/evaluate
  holds stay unreleased until the promotion.

  **The instant's condition.** `2026-09-07T00:00:00Z` sits ahead of the
  promotion forecast; the registered condition is that the carrying promotion
  lands on `main` at or before it. Should it slip past, `FROZEN_SINCE` is
  bumped past the carrying merge in a follow-up promotion **before** the
  `prereg/proc-v7` tag is minted. Cells minted between the carrying merge and
  the instant land as shakedown, honestly stamped and uncounted.

  **The evaluator half's pooling exposure.** The 14 gradings under the
  retiring evaluator digests stay exactly as uncounted as they were; what
  pools across the rubric boundary is the `--all-versions` diagnostic view
  and the version-blind leakage digest, as at proc-v6, with the same reading:
  a flagged-grading count taken after this re-bless is not poolable with one
  taken before — the more so here, where the grading rule for the
  positional cut's ambiguous same-day citations is *flag as a stated
  conservative default*, a policy that raises the flagged rate by
  construction. The frozen board is again not exposed, because both halves
  move together: a frozen-scope cell's prediction digest can only be one of
  the proc-v7 three, minted from `main` after the carrying promotion, so its
  grading necessarily carries a proc-v7 evaluator digest.

  **The runnable effect check, for the promotion carrying this.**
  `uv run fedcourts process-digest --all` on the promoted `main` prints
  `proc-v7` and exactly the six digests this entry blesses; the promotion
  gate on the next staging PR goes green with no unblessed-digest failure;
  and the first spend-released run at or after `2026-09-07T00:00:00Z` stamps
  its cells `proc-v7` (read off any new cell's `process_version`). The codex
  half of that run is additionally the availability check for `gpt-6-astra`:
  its cells' `usage.json` must record that model, at the registered rates.

- **The proc-v7 carrying promotion lands — the step-4 audit and the gap
  census, 2026-09-06.** The freeze registered at
  `466951d756a573b2533a71e59376b4cfb7764758` promoted: PR #1707 merged to
  `main` as merge commit `4792b4754e69ba2df9c7edd1820fc7eab6a94d0a`
  (parents `5bf3e78d3` / `65400bd93`), committed **2026-09-06T21:18:48Z**.

  **The instant audit.** `2026-09-07T00:00:00Z` sits 2h41m12s after the
  carrying merge, so the registered condition — the promotion lands at or
  before the instant — is met and no `FROZEN_SINCE` bump is called on. The
  true bless moment for all six digests is the carrying merge's committed
  instant, read off `git log -1 --format=%cI 4792b4754`, which prints
  `2026-09-06T17:18:48-04:00` = **2026-09-06T21:18:48Z**; the constant's
  step-2 forecast (`2026-09-06T11:55:00Z`) sits below it, on the registered
  early side, and its correction to the true moment rides the next ordinary
  promotion — together with a comment correction the census below makes
  owed: the constant's first-shape rationale still says nothing was ever
  stamped at or after proc-v6's instant ("the fourteen evaluations"), which
  the census below supersedes. The first-shape *conclusion* survives on
  other grounds stated there — what is wrong in that comment is the stated
  reason, not the shape's outcome. Both tags are minted on this audit:
  `prereg/proc-v7` on the freeze commit, `promotion/2026-09-06` on the
  carrying merge — minted after the audit's checks passed but before this
  entry landed, a step-4 ordering deviation recorded here as the deviations
  before it are; and `prereg/proc-v7` is a lightweight tag where the
  procedure wants an annotated one carrying the record in its message — the
  same lapse `prereg/proc-v6` carries, and since the namespace blocks update
  and deletion, this sentence is its permanent record: for both tags the
  pre-registration record lives in this file, not the tag message.

  **Step 0, re-run at the merge.** Per-digest grep over `data/cases` at
  `4792b4754`: **0 stamped cells for all six blessed digests** — nothing
  claims a proc-v7 digest from before its bless. The frozen map in the
  constant carries exactly the six and none of proc-v6's.

  **The effect check, executed.** `uv run fedcourts process-digest --all` at
  the merge prints `proc-v7` and exactly the six blessed digests, matching
  the freeze entry byte for byte. Of this freeze's registered checks, two
  remain observations to come: the promotion gate on the next staging PR, and
  the first spend-released run at or after the instant stamping `proc-v7` —
  whose codex cells' `usage.json` is also the `gpt-6-astra` availability
  check. (The same carrying promotion also carries the arrival-cut membership
  entry's own effect check, registered with that entry; it is not restated
  here.)

  **The gap census the advance declaration called for — not empty, and not
  the declaration's to license.** The 2026-09-06 evaluate hold was released
  before the promotion (run `20260906T174126Z`), so cells were stamped under
  proc-v6 evaluator digests at or after proc-v6's instant: **15 evaluation
  artifacts**, collectively covering the three interim events on
  `scotus/9526000274`. The run's matrix spanned two cases — every judge on
  the three `scotus/9526000274` events, plus a codex-judge-only retry of the
  three `scotus/9526000275` events — and the cut by judge: claude-judge 3/3
  cells → 9 gradings under `sha256:e84e8e5f…` (stamped
  2026-09-06T17:49:00–17:49:26Z); gemini-judge 2/3 cells → 6 gradings under
  `sha256:64ae1b0c…` (18:50:47Z and 18:52:27Z), the third cell recording
  `attempt.json` with `error_class: no_output`; codex-judge 0/6 cells across
  both cases, each recording `attempt.json` with `error_class: died`
  (queued, uploaded nothing — the run's own logs, which expire, showed all
  six force-killed at the job cap; issue #1668, occurrence 6). The grid is
  therefore judge-unbalanced, and even the version-blind `--all-versions`
  and leakage-digest views over these 15 are not a judge comparison. Two of
  codex-judge's five attempts per cell (`max_attempts_per_cell`, which a
  newer process version does **not** reset) are now burned on each
  `scotus/9526000275` event across the 2026-09-04 and 2026-09-06 runs — if
  those cells cap out, codex leaves their graded population by attrition,
  not design, and a later evaluator-agreement figure must not read the
  absence as a choice.

  The resolved-outcome split the declaration requires, read off each event's
  committed `outcome.json` at the merge: all three graded events are
  **interim-stage** moments that had already resolved **granted** on
  2026-09-04 (`disposition_basis` standard) — an interim grant, not a cert
  grant, poolable with neither cert band — 3/3 events granted, 15/15
  gradings of granted-resolved events. That homogeneity decides the licence:
  every one of the 15 grades an event resolved two days *before* the
  declaration was dated, so the whole cohort is the already-resolved slice
  for which a declaration creates no pre-registered boundary, and **the
  advance declaration licenses nothing here**. What bounds these 15 instead
  is prior unclaimability: all 15 grade predictions stamped **proc-v5**
  (predictor digests `sha256:eba87d4c…` / `sha256:b46b3c6d…` /
  `sha256:8c401008…`, run `20260901T014205Z`), which were never in the
  frozen map — and since the predictor digest is the enforced membership
  filter, no frozen-scope artifact ever contained these gradings and
  retiring the evaluator digests de-counts nothing. The 15 are uncounted on
  those grounds, proc-v7 the counted record, no pooling across the boundary
  in either direction.

  Census commands, run at `4792b4754`: per-digest `git grep -l
  'sha256:<digest>' -- data/cases | wc -l` puts the final tally under
  proc-v6's evaluator digests at **29** — 16 under claude-judge
  `sha256:e84e8e5f…`, 13 under gemini-judge `sha256:64ae1b0c…`, 0 under
  codex-judge — superseding the **14** the freeze entry recorded from its
  pre-release census, and the wider census (`git grep -l
  '"process_version": {' -- data/cases | wc -l`) at **463**, up from the 448
  recorded there (448 + 15). The predictor half of the gap is empty as
  forecast: no predict hold was released, so proc-v6's predictor digests
  retire with zero predictions ever stamped. As of this entry no cell exists
  in proc-v7's window; any cell minted between the carrying merge and the
  instant lands as shakedown per the freeze entry's registered condition,
  and the next entry that counts anything under proc-v7 closes the question.

- *The real-engine cert back-test becomes a standing fortnightly sample behind
  a strictly manual spend hold — registered before the first scheduled release,
  2026-09-07.* This entry supersedes a registered refusal: "a real-engine
  replay spends tokens, so it never runs on a schedule" stood in the workflow
  header, `metrics/README.md`, and the `CertBacktest` schema docstring, and
  all three are amended in the PR carrying this entry, along with the same
  claim's echoes in `README.md`, the lane tables, and the digest's rendered
  empty-state. The rationale those
  statements protected — no tokens move without a human — survives literally:
  **the schedule asks; the hold spends.** A scheduled run derives its plan and
  parks on the `review` environment's required-reviewer hold with no timer
  that can release it; an unreleased, rejected, or expired hold is a
  first-class skipped fortnight that spent nothing and left the standing
  report at its prior vintage.

  The cadence: one cron, Saturday 06:23 UTC, halved by ISO-week parity —
  **even ISO weeks run** — for at most 26 asks per ISO year, 52- and 53-week
  years alike; a 53-week year yields one three-week gap at the seam (W53 and
  the following W01 both skip — first at the 2026→2027 seam, 2026-12-26 to
  2027-01-16). Effective from the first even-ISO-week Saturday after the
  promotion that carries this entry — 2026-09-19 (2026-W38) if promoted
  before then. The check that settles the arming: on that Saturday,
  `gh run list --workflow=run-backtest.yml` shows a `schedule` run whose
  cadence and plan jobs succeeded and whose approval job sits waiting,
  having spent nothing — and before that Saturday the `review` environment
  must still list required reviewers, since an unprotected environment
  releases instantly.

  The sample and selection, pinned on the scheduled path and free on a
  dispatch: `replay=cert`, `engine=auto` with no engine opted out,
  `--limit 10` petitions × the routable predictors (three today) ≈ 30 predict
  cells per released fortnight. The limit is a ceiling, not the sample — a
  petition without a provisionable snapshot drops out, and the report's
  `events_scored` is the realized n. `--scope paid`, because the paid class
  carries the grant-family mass (5.6–7.9% per Term over OT2017–OT2025,
  complete counts, against 2.3–3.3% per Term over the whole modern-cert
  population, whose IFP half is denial-reweighted; the replay's granted-side
  flag is slightly broader than the published family, granted-in-part
  included) and is the only population the per-band segment breakdown
  scores — ten unfiltered petitions would read lift against a
  near-pure-denial floor with empty bands. `--spread`
  round-robins conference cohorts within a run; the draw moves between
  fortnights as the resolved population underneath it moves — newly decided
  petitions entering, and corpus backfills that make older ones selectable —
  never by per-run randomness. Positional selection at the last distribution before resolution
  is unchanged, and the arrival moment stays out of replay scope until it is
  registered as its own extension.

  The budget bound: ≈$70–88 per released fortnight (formal range $65–88,
  whose upper end rests on the thinnest measured row), ≈$1.8–2.3K/yr at 26
  releases, projected at `gpt-6-astra` codex rates in `docs/budget.md`'s
  driver line. The spend is ledger-invisible to the $2,500/30-day backstop —
  replay cells never reach the committed usage ledger — so what bounds it is
  the cadence and parity rule, the pinned limit, the manual hold, and the
  job's `timeout-minutes`.

  Reading rules for the fortnightly series, registered with it. Consecutive
  released fortnights are comparable **in population** if and only if their
  reports' provenance blocks agree — the dispatch shape, the salience floor
  and version, and the base-rate lookback, each stamped there precisely
  because the cadence pins the dispatch but not the config, which any
  promotion can move; constancy is verified from the blocks, never assumed
  from the schedule. (Under the paid scope the population itself is
  floor-independent — the floor belongs to the band and baseline readings.)
  What the reports genuinely cannot show is a prompt or predictor-config
  change between two releases, since replay cells carry no process digest:
  that is legible only from promotion history. A dispatched campaign's
  report is comparable to neither the series nor another campaign — a
  deliberately stricter rule than provenance equality — and the artifact
  records no trigger, so whether a report belongs to the series or to a
  dispatch that used the same parameters is itself read from the run
  history, not from the report. No single fortnight's ranking is a
  measurement at this size: an ordering turns on the one or two granted
  outcomes a draw holds, a band on fewer, and only the accumulating series
  is read — a fortnight in which nothing was granted (probability at least
  roughly one half: (1−p)^n at p ≈ 5.6–7.9% and the realized
  `events_scored` as n, ≈0.5 at the pinned ceiling of ten and higher on any
  shorter draw) has its top line withheld outright rather than ranked. A
  released fortnight's report is **merged regardless of what it says** — the
  release decision precedes the numbers, and the series is exactly the
  committed history of `metrics/cert-backtest.json`, so an unmerged report
  is overwritten by the next run and selective retention would be visible as
  a gap. `provenance.run_id` identifies which sample is standing; a gap in
  the series says only that no report landed — an unreleased hold, an
  undelivered cron, a run with no replayable petition, and an unmerged
  review PR are indistinguishable from the artifact alone. The stratum is
  unchanged throughout: retrospective by construction, an iteration
  instrument, never claimable performance.

- **The interim amicus reading widens to submissions, and the resolution count
  takes an end-of-day cut, 2026-09-10.** Two changes to the same number,
  registered together because they move it in opposite directions and a reader
  of either alone would mis-attribute the net. Both are **scoring-baseline**
  members of [process-version.md](process-version.md)'s list, under an unmoved
  digest and with no data-visible boundary — an outcome's `interim_signals`
  records a count and not the reading that produced it, which is the shape that
  paragraph refuses to leave in a commit message. No prompt byte moves, so no
  predictor or evaluator digest moves and no re-bless is due — and that is a
  **trade taken deliberately, not an absence of impact**. The predict prompt asks
  an interim cell for the probability that "the amicus count rises past" the
  number its record shows, and it does not say which entries that count reads.
  Under the widened reading it now reads submissions too, and the cell is not
  told. Saying so in the prompt would move all three predictor digests and force
  a re-bless; the digests stay put and the elicitation stays slightly coarser
  than the resolver, which is registered here rather than left silent.

  **The reading.** `interim_signals.amicus_briefs` counted only the accepted
  form, `amic(?:us|i)\s+curiae`. It now also counts each distinct **lead
  filer** whose brief the docket shows as submitted and not yet accepted
  ("Amicus brief of X submitted."), deduped against the filer the acceptance
  entry names, so one brief's submitted → accepted lifecycle counts once. A
  motion for leave and a refused brief stay out. The old exclusion was argued
  from cert dockets alone — the corpus snapshots no application's proceedings —
  and on an application docket the submission form is often the only shape a
  brief is ever seen in before the matter resolves. `scotus/9526000203`'s
  **`evt-brief-response-disposition`** cells, provisioned at `context.cutoff`
  2026-08-19, carried six submissions (one 2026-08-16, five 2026-08-18) and
  froze `amicus_briefs = 0`; the counter over the same entries now reads **6**.
  The case's other two events were provisioned at cutoff 2026-08-15, before the
  first submission, and read 0 under both readings — the correction is those
  three cells, not the case. The widening is latch-compatible by construction:
  the submitted arm is an addition over a set of entries disjoint from the
  accepted one, so the new count is never below the old on any docket. It is
  also not an overcount at the far end — the same docket at resolution, its six
  submissions by then accepted and docketed in the Latin, reads **7** under both
  readings. How large the correction is *across* application dockets stays
  unmeasured, and cannot be measured from the corpus: the two dockets checked
  here were both surfaced by cell flags, which is the most biased sample
  available for the question.

  **Those two docket readings are reconstructions, not corpus reads**, and carry
  no blob vintage because none was taken. Application proceedings live only in
  the content store, docket entry text is never committed, and the corpus was
  unreachable from the checkout this entry was written in. The entry *shapes*
  above are strings the two cases' committed predict and evaluate cells quote
  verbatim; the filer names and dates come from the same cells' prose. Every
  other figure in this entry — the 12,687 / 32 / 667 / 58 counts, the histograms,
  the cutoffs, the pending and re-freeze cell lists — is read from committed
  artifacts and is exact.

  **The cut.** The ingest derivation now bounds counted entries to
  `entry_date <= disposition date` where that date is known
  (`interim_signals.amicus_briefs_through`) — **end of day**, so an entry sharing
  the disposition's date counts however the docket orders it, and one filed after
  that day does not. Undated entries always count. This states a cut the record
  previously left unstated: the freeze copies the corpus column at
  resolution-detection time, so without a bound a poll taken after the
  disposition reads entries the Court filed once the matter was over into a value
  labelled "as at resolution". `scotus/9526000275` is the worked case: its one
  amicus entry is a submission dated the day of the denial and docketed *after*
  the denial entry, so it counts (**0 → 1**), while the same docket plus an entry
  dated two days later still reads 1 rather than 2.

  Two limits on the cut's reach are registered with it. It is
  **date-conditioned**: the derivation takes the disposing entry's own date, and
  a resolved application whose disposing entry carries no readable date leaves
  that date null and keeps the unbounded reading. The size of that arm is
  unmeasured. And the column **max-latches**, so the bound governs derivations
  from here and never a value already stored — a row polled before its
  disposition date was readable keeps whatever the unbounded reading gave, and
  only a corpus re-derivation can bring it down.

  **The two cuts are asymmetric on one arm, and there the asymmetry has a
  direction.** The resolution end stops at the end of the disposition day. The
  prediction end depends on `context.cut_kind`, and the two arms differ in
  exactly the way that matters here:

  - On the **date** arm — `cut_kind` null, which every one of the 667 committed
    `prediction.json` carries — the snapshot keeps every entry filed strictly
    before `context.cutoff`, and the cutoff is the day *after* the moment opened.
    The whole opening day is therefore inside the cell's information set,
    however the docket orders it, and the two ends agree about same-day entries.
    No bias arises on this arm.
  - On the **`arrival-position`** arm the snapshot stops at the entry that opened
    the event, so the opening day's *later* entries are outside the information
    set while the resolution end counts them. There an amicus entry docketed the
    same day as the moment being forecast, after the entry that opened it,
    resolves `amicus-increment` **positive with no docket movement at all**: it
    existed when the forecast was taken and was withheld from the forecaster.
    The widened reading enlarges that arm, because a same-day *submission*
    previously read 0 at both ends and now reads 0 at the prediction end and ≥1
    at the resolution end.

  No committed cell takes the second arm, but cells minted from here do:
  `evt-motion-disposition` is the interim **arrival** moment
  (`pipeline.moments`), which is the moment the positional cut is taken on. The
  effect concentrates on the fastest-moving applications — the ones a whole
  matter can be submitted and decided inside a day or two — which are also the
  ones the interim reserve ladder funds first (`pipeline.salience`). **So on an
  `arrival-position` cell the claim's positive rate is biased upward by a
  mechanism that is not a forecast**, and no such resolution may be read as a hit
  without checking that the entry which moved the count postdates the anchor.

  **The affected set, as at this commit.** Of **12,687** committed
  `outcome.json`, **32** carry a non-null `interim_signals` block, across 20
  cases; their `amicus_briefs` values are {0: 20 rows, 1: 3, 2: 3, 6: 3, 7: 3}.
  Of **667** committed `prediction.json`, **58** carry a non-null
  `context.amicus_briefs`, across 10 cases: {0: 47, 2: 3, 6: 8}. **This change
  re-derives none of them.** A `run-repair` pass that re-derives the column,
  re-freezes the ≤32 committed outcome rows and regrades what moves is
  deliberately outside this change; until it runs, every committed row is the old
  reading, and its own entry carries its own declaration. What that pass would do
  is already computable and is registered here rather than left to it:
  `scotus/9526000275`'s three events would re-freeze from 0 to 1, flipping the
  `amicus-increment` resolution of its **7** committed cells from 0 to 1. Those
  seven **are** claimable, and the check is worth showing because it is the check
  every reader of an increment now has to make. The docket's one amicus entry is
  dated 2026-09-03; the three events' cutoffs are 2026-09-01, 2026-09-02 and
  2026-09-03, and the date rule keeps only entries filed *strictly before* the
  cutoff. The entry therefore postdates all three information sets, its frozen
  context reads 0 under both readings, and the flip is docket movement the
  widened counter can now see rather than measurement drift.
  `scotus/9526000203`'s 9 cells resolve 1 under both
  readings and do not flip. Its brief-response arm is worth one further note,
  and it is about the *reading* rather than about the pass: re-derive both ends
  and that cell's increment becomes 6 → 7 rather than 0 → 7 — the same binary hit
  off a far smaller movement. The pass registered above re-derives only the
  resolution end; a committed `context.amicus_briefs` is never re-derived, so
  that comparison is hypothetical and is recorded here so a later reader does not
  mistake the committed 0 → 7 for a large forecast movement.

  **Two derived surfaces move with the column, and neither carries a boundary.**
  `analytics.with_amicus` — the per-**application-Term** count of substantive
  applications carrying at least one brief, published in `metrics/statpack.json`
  (2024: 24/70, 2025: 24/227, 2026: 4/49 as at the committed pack) — is computed
  from the same column, and only **open** rows re-derive, so from the first
  post-promotion pull the series pools two readings with nothing in the artifact
  to separate them. The 2026 arm is where any movement will appear; the pooled
  total will not show it. And `pipeline.salience`'s interim reserve ladder orders
  on the same column, so the widened reading changes **which** pending
  applications the reserve funds — a selection change on the forward stratum, not
  a value change. `fedcourts arrival-cut-ledger`'s `amicus_tail` /
  `amicus_shift_*` readings also move, and a ledger produced after this change is
  not comparable with one produced before it.

  A fourth surface cannot be re-derived at all, and is recorded so a later reader
  is not surprised by it: **committed cell prose reasons from the retired
  reading**. Predict and evaluate documents on both worked dockets argue
  explicitly that a pre-acceptance entry is not counted — that is what those
  cells believed when they were written, it is an immutable record of the run,
  and no repair pass touches it. After the re-derivation the committed reasoning
  and the committed numbers on those cells will disagree, correctly.

  **The prediction-end hazard.** `pipeline.asof` derives a cell's frozen
  `context.amicus_briefs` through the same function, so the two ends of the
  `amicus-increment` claim move at different times: an outcome frozen after this
  change is a new-reading number, while every context already committed is an
  old-reading one. **Nine pending cells** — `scotus/73279700`,
  `scotus/9526000163`, and `scotus/9526000273`, one `evt-motion-disposition`
  event each across the three baseline predictors — are frozen at
  `amicus_briefs = 0` with no outcome yet written. When their applications
  resolve, their `amicus-increment` compares an old-reading context against a
  new-reading outcome, so a resolution of 1 on those cells is the measurement
  widening rather than a docket movement, and **their increment is not claimable
  as a forecast hit**.

- **The document selector reads the merits stage: per-side merits briefs, and a
  cert-stage bound on the opposition row, 2026-09-10.** A **conditioning**
  entry with no digest movement — no prompt byte and no registry field changes
  — and, like the case-opening-family entry above it, with **no data-visible
  boundary at all**: which documents a cell was provisioned with lives in its
  gitignored `record/documents/`, and `prediction.json` carries no field
  separating a cell that read a merits brief from one that did not. So the
  boundary exists only here, and cells minted on the affected dockets before
  and after it may not be pooled. It stays mechanically checkable the same way:
  a stamped cell resolves to a side of it by asking whether its
  `process_version.pipeline_sha` is an ancestor of the carrying promotion's
  merge commit.

  **What changed, and it moves in two directions.** `select_documents` had no
  upper date bound on its opposition arm, and the Court writes a merits brief
  and a cert-stage response in the same words — "Brief of respondent United
  States filed." either way, with "on the merits" appearing on the *scheduling
  order* and never on the brief entry. So the arm **widened** and **narrowed**
  at once:

  - Two new kinds, `merits-brief-petitioner` and `merits-brief-respondent`, one
    row per side and one URL per row, selected only on entries filed strictly
    after the cert grant that the payload's own first disposition entry dates.
    The petitioner's brief on the merits was never fetched under any kind
    before.
  - The `brief-in-opposition` arm is bounded to filings at or before that grant,
    so the respondent's merits brief stops being selected into the cert slot
    (where it was pipe-joined into the combined row and truncated against the
    cert briefs beside it).

  **The population it moves, run over the stored payloads.** The real
  `select_documents`, not a re-implementation, over every stored SCOTUS payload
  in the blob whose newest pull stamp is `2026-09-09` (newest stored snapshot
  `2026-07-13`). Of **269** cases whose payload dates a cert grant, the merits
  arms reach **105**: 102 a petitioner-side brief, 96 a respondent-side one, 93
  both. On the same population the old arm took a **post-grant** filing into the
  `brief-in-opposition` row on **95** cases; the bounded arm takes none, and the
  cert-stage brief it keeps is the same one in every case (25-735 is the shape
  that makes the bound necessary rather than merely tidy: its cert-stage
  response carries no "in opposition" words at all, so only the grant date tells
  its two identically-worded respondent briefs apart).

  **Nothing already stored changes.** Of the **410** stored
  `brief-in-opposition` rows, **0** carry a `|`-joined URL and **0** are dated
  after their case's grant: documents are fetched at the distribution
  transition, before any grant, so no stored row is a cert/merits concatenation
  today. The bound is therefore prospective in the strict sense — and it also
  *prevents* a retroactive loss, because the combine's idempotency key is the
  selected URL set: under the old arm the next re-provisioning of a granted case
  would have found a selected set larger than the stored one, re-fetched, and
  overwritten that case's cert-stage opposition row with the concatenation.

  **The cells this boundary runs through, named.** Of the 105 cases, **8** carry
  committed prediction cells — **45** in all, every one of them on a merits
  event (`evt-order-judgment`, `evt-brief-judgment`): `scotus/73274859`,
  `scotus/73277468`, `scotus/73278510`, `scotus/73278555`, `scotus/73279024`,
  `scotus/73279865`, `scotus/73281007` at 6 cells each and `scotus/73279026` at
  3. All 45 were stamped on **2026-08-16** and carry three digests (one per
  engine, 15 cells each) that are **not** in `FROZEN_PROCESS_DIGESTS`, so every
  one is de-counted by the membership filter — and, being stamped three weeks
  before `FROZEN_SINCE` = `2026-09-07T00:00:00Z`, de-counted by timing as well.
  **None of the 45 has ever been counted.** The committed cells stay as they
  were minted; a merits cell minted on one of these cases after this lands reads
  strictly more than one minted before it.

  **The expected-skill corollary, registered so a rise cannot be read as more
  than it is.** A post-change briefed-moment cell reads both sides' merits
  advocacy where a pre-change one read the docket entries saying a brief was
  filed. Expected skill on that population should therefore **rise**, and a rise
  across this boundary **may not be read as a model improvement**. The negative
  form is deliberate: the design supports excluding one reading, not asserting a
  cause. The class is the granted docket, not the 8 cases above, so a case
  granted between now and the carrying promotion joins it.

  **The amendment debt this creates, and the ordering it constrains.**
  `.github/prompts/predict.md` tells a merits cell that "any provisioned
  `record/documents/` text is cert-stage … the merits advocacy is not on your
  desk unless you go and get it". That sentence becomes **false** for a
  briefed-moment cell the first time one is provisioned over a case carrying
  these rows, and it points the cell at retrieval for material already on its
  disk. The prompt is frozen bytes, so the correction is a **re-bless**, not a
  drive-by edit, and it is registered here as owed: it must ride the next
  process-version freeze, and that freeze must promote **before** the first
  briefed-moment cell over a case holding provisioned merits briefs. Until then
  the residual is a cell mis-describing its own provenance in `reasoning.md`,
  not a disclosure: the cut is unaffected either way — a grant-moment cell's
  cutoff drops both briefs and a briefed-moment cell's admits them, which
  `provision.documents_before` decides and the selector cannot.

  **No base rate re-prices, and no scored figure moves.** `pipeline.salience`
  and `pipeline.base_rates` read no document text. `TEXT_COVERAGE_KINDS` gains
  two kinds, so `corpus-info --text-coverage` grows from eight `kind` ×
  `segment` cuts to twelve and `cases_read` rises where a granted case holds
  only merits rows — a kind-list widening, not more reach — and
  `metrics/live-frontier.json`'s `documents_provisioned` is untouched, since its
  watchlist is pending petitions and a merits brief is post-grant by
  construction.

  The runnable effect check, for the promotion carrying this: `uv run pytest
  tests/test_documents.py` green, and — on the next `run-pull` window whose
  selection sweep re-provisions a granted case — `fedcourts corpus-info
  --text-coverage` showing non-zero `n` on the `merits-brief-petitioner` and
  `merits-brief-respondent` rows, which start at zero. This entry registers the
  prospective half only: the granted cases already past their trigger are
  reached by a document-gap scan widened to the merits kinds, which is not built
  and will carry its own entry when it is.

- **The interim amicus re-derivation is built, and the two ends of the
  increment part company, 2026-09-14.** The retrospective motion the
  submitted-form widening entry above delegated to — "its own entry carries its
  own declaration" — registered here **before** it runs, because what it
  registers is created by the apply and a declaration written afterwards would
  be a report rather than a pre-registration. This entry covers the pass as
  built; a second entry records what the maintainer's apply actually moved.

  **What the pass does.** `run-repair`'s `amicus-rederive` recounts the corpus
  `amicus_briefs` column on **resolved** interim applications — those whose
  latest live-shaped snapshot carries a readable disposition date — under the
  widened reading with the end-of-day cut, writing through a direct `UPDATE`
  that bypasses the column's max latch (the cut lowers a resolved row, which the
  latch is built to reject). It then re-freezes each committed interim
  `outcome.json`'s `interim_signals.amicus_briefs` from that same recount. An
  open application is left to the live channel, which polls it under the same
  reading.

  **The declaration that matters: the two ends diverge, and no artifact says
  so.** A committed `prediction.json`'s `context.amicus_briefs` is **never**
  re-derived — it is the information set a forecast was made on, frozen by
  design. So from the apply onward the `amicus-increment` claim compares a
  **new-reading resolution end against an old-reading prediction end**, and
  neither `InterimResolutionSignals` nor `PredictionContext` carries a reading
  stamp. This is the same hazard the relist-increment parse mask answered with a
  `distribution_parse` stamp and an `unavailable` resolution wherever the two
  ends disagree; the interim pair has **no such stamp and no such mask**, and
  `pipeline.claims._resolve_amicus_increment` compares the two numbers directly.
  The consequence, stated so no later reader has to infer it: **an
  `amicus-increment` resolution of 1 on any cell whose context predates the
  widening is not a forecast hit on the artifact's own evidence.** It is a hit
  only where the entry that moved the count postdates that cell's own anchor,
  which the record does not disclose and which must be checked by hand — the
  check the entry above performs for `scotus/9526000275`, now owed for every
  flip the apply produces. The `PredictionContext.amicus_briefs` field
  description carries this caveat as of this commit; the stamp-and-mask that
  would make it mechanical is not built and would need its own entry.

  **The affected set, as at this commit, and it is larger than the one
  pre-computed above.** Of **12,690** committed `outcome.json`, **35** carry a
  non-null `interim_signals`, across **22** cases: {0: 22, 1: 4, 2: 3, 6: 3,
  7: 3}. The entry above registered 32 across 20 of 12,687, {0: 20, 1: 3, 2: 3,
  6: 3, 7: 3}. The whole delta is growth after it was written, not a widened
  scope: `scotus/9526000306` (two events, frozen at 0) and `scotus/9526000326`
  (one event, frozen at 1), both resolved 2026-09-10. It will be larger again at
  dispatch, since the writer step fast-forwards to the remote tip first, and
  that is expected rather than a defect.

  **What the entry above pre-computed was the population, not the motion.** Its
  reconstruction of which rows move covers two dockets of twenty, and both were
  surfaced by cell flags — the most biased sample available for the question.
  Twenty-two of the thirty-five rows read 0 and can rise under the widened
  reading; **that arm is unmeasured**. So a ledger moving more than the one
  pre-computed docket is the expected result, and the pass's bound is sized as a
  guard against a catastrophic write rather than as a prediction of the count.

  **A move in the ledger is not by itself the reading's doing.** The recount
  reads the docket's *current* snapshot, so an entry dated at or before the
  disposition that the poll had not yet seen at resolution-detection time raises
  the count legitimately under the cut — late docket-data arrival, not the
  widening — and the ledger cannot separate the two. This is why the per-flip
  anchor check above is owed on the moved set rather than assumed from it.

  **The regrade debt.** The re-freeze moves a scored claim's resolution end, so
  each moved outcome owes a `regrade-stale` dispatch — three judge lines per
  event. On the pre-computed flip alone that is 14 committed `evaluation.json`
  across `scotus/9526000275`'s three events. Those cells' `amicus-increment`
  lines carry a null baseline and a null score, so the re-grade moves the
  recorded `outcome` and **no** aggregate claim score and no leaderboard column;
  the recorded resolution is published either way, which is why it is registered
  rather than waved through. There is no `include-scored` holdback here, unlike
  the disposition relabel: the re-freeze corrects a value the retired reading got
  wrong rather than re-characterizing an order, so holding scored events back
  would leave a known-wrong number standing under a grade.

  **One derived surface moves with the column and carries no boundary.**
  `analytics.with_amicus` — the per-application-Term count of substantive
  applications carrying at least one brief, published in `metrics/statpack.json`
  (2024: 24/70, 2025: 24/227, 2026: 4/49 as at the committed pack) — is computed
  from the same column and re-prices at the first post-apply statpack refresh,
  with nothing in the artifact separating the two readings. A series compared
  across the apply is not a comparison.

  The runnable effect check, for the promotion carrying this: `uv run pytest
  tests/test_amicus_rederive.py` green, and the pass's own `dry-run` dispatch
  printing a ledger whose `outcomes_with_interim` and
  `interim_amicus_distribution` match the population stated above — the reading
  the maintainer takes before any apply.

- **The interim amicus re-derivation ran, and the ledger separates what the
  entry above said it could not, 2026-09-14.** The second of the two entries the
  entry above promised: the record of what the maintainer's apply moved, read
  off the pass's own receipts and off the corpus after the fact. The first entry
  stays as written.

  **What ran.** `run-repair` `amicus-rederive`, three dispatches from `main`
  after the promotion tagged `promotion/2026-09-14`: a dry run (run
  `34865920972`, 16:01 UTC), the apply (run `34867559864`, 16:16 UTC,
  `repair_bound=49`), and the idempotence control (run `34869786188`, 16:37
  UTC), which reported `total_changes = 0`: 0 of 2,116 readable rows would move
  and 0 of 35 outcomes would re-freeze, over a blob three live-channel
  resolutions newer than the apply's (2,116 readable and 12 open against 2,113
  and 15), each of which the live channel had already derived under the current
  reading. The distribution it found is the post-apply shape: `{0: 15, 1: 3, 2:
  5, 3: 1, 4: 2, 5: 3, 7: 3, 13: 3}`. The apply read blob
  `a59f1d1dd031825b3951ea372a399fcea25f112c8b9a5629735f188545b98ae6` and pushed
  `f6cb3c23c0fd40eee8705d1c123f5ec955956475bc46476e0357922723cdc0ac`; its data
  commit is `b822bf06b` (the pointer plus 17 `outcome.json`). Dry run and apply
  agreed field for field, so nothing landed between them.

  **What moved.** Of 2,128 eligible interim applications, 2,113 were readable
  (none unobservable — the pass read a full blob, not an index-only pull), 15
  carry no cut — an open application the live channel maintains, or a resolved
  one whose disposing entry carries no readable date; the pass does not tell the
  two apart — and are left untouched, and **32 corpus rows moved, all upward, by
  157 entries in total**; the end-of-day cut lowered no resolved row, so the
  latch bypass carried nothing on this run. **17 of the 35 committed interim
  outcomes were re-frozen, across 7 cases**; the distribution as found was `{0:
  22, 1: 4, 2: 3, 6: 3, 7: 3}`, exactly the population the entry above stated,
  so the apply moved the set it registered and nothing more. The per-row corpus
  moves and the 17 re-freezes are in the apply's run summary; the ones a
  committed cell reads are listed with the flips below.

  **The ledger's moves are attributable where a committed cell reads them, and
  almost none of them are this reading's.** The entry above said a move "is not
  by itself the reading's doing" and that the ledger "cannot separate" the
  widening from late docket-data arrival. Re-deriving each of the 32 dockets
  under three readings — the singular-only counter retired 2026-08-28, the
  plural counter that replaced it, and the submitted-form reading registered
  2026-09-10 — over the post-apply blob `f6cb3c23…`, pulled 2026-09-14,
  separates them completely:

  - **145 of the 157 entries are the plural widening of 2026-08-28**, not this
    one. On 31 of the 32 rows the stored count equals the singular-only reading
    of the docket's current entries to the digit (the 32nd, `scotus/9526000274`,
    equals the plural). That entry recorded that the corrected counts would
    "reach open applications on their next poll while every frozen context keeps
    the count it was provisioned with"; what it did not say, and this pass now
    shows, is that the max-latched column never re-polled a **resolved** row
    either, so the plural correction had reached none of the resolved slice
    until today. The largest moves in the ledger are this correction:
    `scotus/73288357` 10 → 34 and `scotus/73288461` 9 → 32 are 23 and 22 plural
    entries each plus one submission. - **12 entries are the submitted-form
    reading registered above**, on seven dockets: `scotus/9526000297` (+2),
    `scotus/9526000304` (+4), `scotus/9526000326` (+2), `scotus/9526000274`,
    `scotus/9526000275`, `scotus/73288357` and `scotus/73288461` (+1 each). -
    **Late docket-data arrival is excluded outright on the two dockets whose
    committed cells flip, and only there.** The equality above excludes a
    late-arriving *singular*-form entry on 31 of the 32 rows; a plural-form
    entry that reached a docket after its count froze would raise the plural
    reading without touching the singular one and so sit inside the 145
    indistinguishably — on the other 30 rows the widening and late arrival
    remain as inseparable as the entry above said. For the two dockets whose
    committed cells this matters to, every stored daily snapshot from 2026-08-15
    to 2026-08-24 in the per-case content store, read 2026-09-14, carries the
    same accepted-form entries the current one does — 13 on `scotus/9526000124`
    (dated 2026-07-29 and 2026-08-03), 5 on `scotus/9526000139` (dated
    2026-08-03) — so the entries were on the docket before those cells were
    provisioned. The stored counts of 6 and 2 are the singular reading of those
    same entries: 6 of the 13 say "amicus", 7 say "amici"; 2 of the 5 and 3.

  **The anchor check on every flip.** 34 committed cells read one of the 17
  re-frozen outcomes (five re-frozen events carry no prediction and moved
  silently: `scotus/9526000297` ×2 from 0 to 2, `scotus/9526000304` ×2 from 0 to
  4, `scotus/9526000326` from 1 to 3 — a cell minted on those dockets later
  forecasts over a row that moved under it). Under `_resolve_amicus_increment`'s
  strict `>`, **18 of the 34 flip, all 0 → 1**, and they divide exactly along
  the attribution above:

  - **7 are docket movement and read as hits** — the seven the entry above
    pre-computed, on `scotus/9526000275`'s three events — motion (3 cells,
    cutoff 2026-09-01), order-response-requested (2 cells, cutoff 2026-09-02)
    and brief-response (2 cells, cutoff 2026-09-03); `codex-baseline` did not
    run on the last two — the docket's one amicus entry is a submission dated
    2026-09-03, the date rule keeps only entries filed strictly before the
    cutoff, and the frozen context reads 0 under every reading. The entry
    postdates all three information sets. One caveat travels with the seven: the
    count rose only because the resolver now reads submitted-form entries, and
    the entry above registered that the predict prompt does not say so — these
    are hits on the resolver's quantity, scored against cells asked about a
    slightly narrower one. - **11 are measurement drift and do not read as
    hits** — none of them pre-computed. `scotus/9526000124`, 8 of its 9 cells —
    `claude-baseline`, `codex-baseline` and `gemini-baseline` at
    `20260816T173750Z` on each of its three events, context 6, snapshot
    2026-08-16 as stored, no cutoff — for a cell with no cutoff the stored
    snapshot's date is the anchor; the ninth, `gemini-baseline` at
    `20260820T181919Z` on the order-response event with context 0, already read
    1 — and `scotus/9526000139/evt-brief-response-disposition`, 3 cells
    (`20260820T181919Z` ×2 and `20260821T053402Z`, context 2, cutoff 2026-08-04,
    truncated). Every entry that moved their resolution end is dated 2026-07-29
    or 2026-08-03, was in the stored snapshot each cell was provisioned from,
    and predates every anchor; the frozen context, recomputed under the current
    reading over the cell's own snapshot, would equal the new resolution end (13
    and 5), and the increment would resolve 0. The rise is the plural counter
    seeing entries the singular one did not — the class the 2026-08-28 entry
    declared unclaimable for the nine pending cells it named (three dockets, one
    motion event each, three predictors), now shown to reach eleven resolved
    ones it did not name. - The remaining 16 read 1 under both readings (context
    0 against a resolution end already above 0) and do not move.

  **The regrade.** The `run-repair` `regrade-stale` pass, dispatched three
  times: the apply's ledger named 48 judge lines, and the list was not
  dispatchable as printed. 18 of the 48 were superseded runs:
  `scotus/9526000124` and `scotus/9526000139` each carry two evaluation runs per
  judge (`20260824T231401Z` and `20260825T024608Z`), every scoring surface
  collapses a judge's re-runs of one cell to the newest, and `stamp-cell
  --regrade` refuses a superseded run rather than recompute a grade nothing
  reads — the first `regrade-stale` apply (run `34874220224`) refused at its
  first cell and wrote nothing. One more line, `gemini-judge` on
  `scotus/9526000139/evt-order-response-requested-disposition`, names three
  evaluations that carry no `process_version` and omit the `amicus-increment`
  claim; the re-grade refuses an unstamped cell, and the second apply (run
  `34874615889`) refused there, again writing nothing. The ledger's cell listing
  walks every run directory rather than the surviving stamped one — by its own
  account deliberately, naming a re-grade not owed being cheaper than missing
  one — but the re-grade refuses rather than skips, so the over-inclusion makes
  the printed list undispatchable; that is the defect, filed as its own issue,
  and the list was corrected by hand to **29 cells** under one rule — the newest
  evaluation run per (event, judge) line, minus the one line whose evaluations
  carry no `process_version`: 48 − 18 − 1. The third apply (run `34880756787`,
  18:26 UTC) re-graded all 29 and landed data commit `23f1364d8`: 65
  `evaluation.json` changed, 47 `amicus-increment` outcomes moved — hunk for
  hunk the diff the local check below had produced.

  **What a re-grade moves, stated because it is more than the outcome.** The 29
  cells cover 83 committed `evaluation.json`; a local `stamp-cell --regrade` of
  all 29 against `main` at `158f64b30`, run before the dispatch as the executed
  check behind these counts, changed 65 of them and reproduced 18 — every file
  under `scotus/9526000274`, whose cells do not flip, and nothing else. **47**
  recorded `amicus-increment` `outcome` integers move from 0 to 1 — 24 on
  `scotus/9526000124`, 9 on `scotus/9526000139`'s brief-response event, 14 on
  `scotus/9526000275` — the 18 flips above, once per surviving judge line
  (`scotus/9526000275` carries two judges, not three); that claim's `score` and
  `baseline` are null in every file, so it contributes nothing to any aggregate.
  But the interim stage's skill record is harness-stamped, and a re-stamp pools
  it from the statpack as committed **today**: on 51 of the 65 files
  `segment_base_rate` moves from 0.1333 (the pool the 2026-08-25 grading read)
  to 0.1047 — 31 of 296, the current pack's 2024 and 2025 Term rows (14 of 70
  and 17 of 226) — and `brier_skill_score`, the `interim-disposition` claim's
  `baseline` and `score`, and the claim-score `lift` and `total` move with it —
  a lower pool raises the skill of a cell whose application was granted and
  lowers it where it was denied, so of the 51 files 27 rose and 24 fell, the
  largest single move −14.75 in `brier_skill_score` (at a pool near 0.10 the
  reference Brier on a denied cell is about 0.011, and the ratio is that
  sensitive). The 0.1333 the 2026-08-25 grading read carries no denominator the
  committed record can recover; 14 files (all on `scotus/9526000275`, graded
  2026-09-04 under the current pool) move the outcome alone, and 18 move the
  pool alone — the motion and order events of `scotus/9526000139` (9 and 6),
  which do not flip, and the three `gemini-baseline` evaluations on
  `scotus/9526000124/evt-order-response-requested-disposition`, the one cell of
  that docket's nine that does not. The re-stamp also writes the
  `prediction_run_id` field (null) the evaluation schema has gained since. This
  is the stamp's standing behaviour rather than this pass's: every grading date
  carries its own pool, and the committed record held 105 interim evaluations at
  0.1333 beside 71 at 0.1047; the re-grade moves 51 across, to 54 against 122.
  No published number moves today — the committed leaderboard and claim-score
  boards render the frozen scope's empty state, and none of the re-graded cells'
  process digests is blessed into it — so the move is latent: it surfaces on an
  all-versions board or any later scope that admits these gradings, whose
  interim block would then pool two base rates and is not a like-for-like
  aggregate; this entry is where a reader learns that. The 33 stale
  `amicus-increment` outcomes in the superseded `20260824T231401Z` runs and the
  three unstamped `gemini-judge` files stay as written, unread by any surface.

  **The `analytics.with_amicus` re-pricing.** Pre-apply, the committed
  `metrics/statpack.md` on `main` at `b822bf06b` (the pack the weekly refresh
  had already moved off the 4/49 the entry above quoted): 2024 **24** of 70,
  2025 **24** of 227, 2026 **6** of 55, pooled 54 (a count sum). Post-apply,
  rolled locally and uncommitted from blob `f6cb3c23…` pulled 2026-09-14: 2024
  **25** of 70, 2025 **27** of 227, 2026 **9** of 55, pooled 61 (a count sum
  across Terms of unequal parse coverage, not a rate). The pass's 2,128 eligible
  rows are the pack's whole parsed application slice (1,691 extension, 352
  substantive, 85 unknown), so every row feeding `analytics.with_amicus` except
  the 15 uncut ones was re-read, and the series is single-reading from here
  rather than blended. Every substantive-application denominator is unchanged;
  nine of the 32 moved rows crossed 0, and the seven that are substantive
  applications (the other two are of unknown kind) are the seven the table
  gains. The next Monday refresh commits the second triple.

  **What this changes about reading the record.** The entry above registered the
  two ends of `amicus-increment` parting company at this apply. The attribution
  shows they had already parted, silently, at the 2026-08-28 plural entry for
  every resolved row provisioned under the singular counter — the eleven drift
  flips above are that earlier boundary surfacing, not this one. A reader of any
  `amicus-increment` resolution of 1 now has two boundaries to check a cell's
  context against rather than one — the plural counter of 2026-08-28 and the
  submitted-form reading the entry above registers, each a reading the
  resolution end may carry and the context may not — and this entry is where the
  cells that straddle either are named. The stamp-and-mask that would make the
  check mechanical remains unbuilt and would need its own entry.


- Freeze commit: `0272b1b9d209cb1f9a712c5143cb111627ecc620`, to be tagged
  **`prereg/proc-v8`** per step 4 — on this freeze commit itself, once its
  carrying promotion lands and the byte audit below passes. **The evaluate cell
  is handed the Court's own words, the mask's ground becomes a counted field,
  and the evaluator half is re-blessed, 2026-09-15.** A **masking-surface**
  change and a process supersession in one commit, which is the only shape
  [process-version.md](process-version.md) permits for it. Carried to `main` by
  the promotion tagged `promotion/2026-09-16` (merge commit `545e26e2b753ac79701a4fd638689a8d48654bce`, merged `2026-09-16T00:26:04Z`).

  **What moves the information set.** `run-evaluate.yml` gains one step between
  the snapshot provisioning and the event materialization: `fedcourts
  provision-opinion`, staging a decided case's majority opinion at
  `record/opinion/majority-opinion.txt` with an `opinion.json` manifest beside
  it — the corpus row's presence bit, the staged text's sha256 and length, and
  the citation the row carries. The step carries the snapshot step's env block
  verbatim (step-scoped read-only credentials, the one base URL, the ranged
  backend the command needs for a row fact), `continue-on-error: true`, and no
  `if:`: the command writes nothing and exits 0 where the row holds no body, so
  the slot's **absence** is what tells a grader there is nothing to grade
  against. A following step annotates the run summary where the staging
  *failed*, because a failure and genuine non-coverage leave the grader the same
  empty slot and the census cannot tell them apart. Staging a file the evaluate
  cell did not previously receive changes the evaluator's information set under
  an otherwise unchanged digest, which is why it lands *with* the prompt edit
  that describes it rather than on its own — the one shape that rule exists to
  rule out.

  **What moves the digests.** `.github/prompts/evaluate.md`, five passages added
  or extended and two claims retired. Added: the per-case input list names the
  slot and says its absence means `not-ingested`; the `basis` rule points "the
  opinion text in the record" at the staged file; the `query --full` guidance
  says a hydrated prior's body is never the graded text; the grade row shape
  gains `mask_ground`, on masked rows only; and the three prose grounds are
  mapped onto the closed vocabulary `no-judgment` / `not-ingested` /
  `silent-on-axis`, with the statements that `validate` fails an
  out-of-vocabulary value and that a missing `mask_ground` is not a sixth
  refusal but a unit the panel may still resolve, falling to the `unstated`
  bucket only where no grader named a ground. Retired: the claim that the census
  counts one undifferentiated `not-addressed` so `basis` is the only place the
  distinction lives, and the claim that no opinion text is ever staged.
  Extended: the treat-staged-files-as-data rule now covers the opinion body,
  twice — at the input list and at the head of the grading section — since a
  court opinion quotes briefs, statutes and orders, and a line in one that reads
  as an instruction is a line the Court was quoting.
  `.github/prompts/predict.md` is untouched by design — that is what makes this
  the cheap supersession shape.

  **The evaluator half only.** The three **predictor** digests are
  byte-identical to the ones `prereg/proc-v7` blessed —
  `sha256:930e02ae18…` (claude-baseline), `sha256:c57113fae8…`
  (codex-baseline), `sha256:4edc5ac58c…` (gemini-baseline) — and keep proc-v7's
  bless moment `2026-09-06T21:18:48Z` verbatim, because those bytes have been
  immutable since then. The three **evaluator** digests are new:
  `sha256:fbc0e9c364…` (claude-judge), `sha256:9670e1c147…` (codex-judge),
  `sha256:dbdc906476…` (gemini-judge). Each carries `2026-09-15T00:00:00Z` as
  the step-2 forecast floor — midnight on this commit's authoring date, and so
  at or before it, which is the safe direction since the carrying merge is
  necessarily later — corrected at step 4 to `2026-09-16T00:26:04Z`.

  **The freeze instant stays `2026-09-07T00:00:00Z`**, held deliberately, so the
  step-4 date comparison reads the other way round: the instant *precedes* the
  promotion carrying this commit. Sound here for the reason it was at
  `prereg/proc-v4` — the instant does no work for anything this commit newly
  blesses. The digests entering the set are evaluator-side, which the partition
  records but never gates on (`graded_post_freeze` enforces timing alone), and
  nothing can carry the new evaluator bytes before the promotion lands them on
  `main`. The enforced half is byte-identical to `prereg/proc-v7`'s, whose own
  instant-versus-promotion audit stands. So the auditor's check for this label is
  the **byte comparison**: the predictor digests under `prereg/proc-v8` must
  equal `prereg/proc-v7`'s. One difference from the proc-v4 precedent, recorded
  so the argument is not read as stronger than it is: at proc-v4 holding the
  instant protected 226 stamped predictions, while here **no committed
  prediction carries a proc-v7 predictor digest at all** — step 0's grep returns
  0 for each — so holding drops nothing and moving would drop nothing either.
  The instant is held because the rule keys on the enforced half's
  byte-identity, not on the size of the population behind it.

  **Step 0, at authoring.** `git fetch origin main && git grep -l '<digest>'
  origin/main -- data/cases | wc -l` returns **0** for each of the three newly
  blessed evaluator digests, and 0 for each of the three carried-forward
  predictor digests. The wider census, `git grep -l '"process_version": {'
  origin/main -- data/cases | wc -l`, is **482** stamped cells. Re-run at the
  promotion, against `origin/main` at `545e26e2b`: **0** for each of the three
  newly blessed evaluator digests, and the wider census unmoved at **482**.

  **The retiring evaluator digests, what ran under them, and why the counted
  census is zero.** proc-v7's evaluator digests — `sha256:84cf4c8b52…`
  (claude-judge), `sha256:fa92c82e82…` (codex-judge), `sha256:2585c15a6b…`
  (gemini-judge) — leave the set superseded. **19 committed evaluations carry
  them** at authoring: 0 claude-judge, **16** codex-judge, **3** gemini-judge,
  all on the motion, order-response and brief-response disposition events of
  `scotus/9526000274` and `scotus/9526000275`, and every one stamped at or after
  the instant, so every one passes the evaluation-side gate
  `graded_post_freeze`. **None of them is counted**, and the count of *counted*
  cells graded under the retired digests — the number the second supersession
  shape asks this record to name — is therefore **0**. Counting an evaluation
  takes both limbs of `store.stratify`'s frozen gate, `is_frozen(scored) and
  graded_post_freeze(evaluation)`, and the first fails on all 19: the
  predictions they grade are stamped under proc-v5 predictor digests that no
  longer sit in the map. The committed `metrics/leaderboard.json` settles it
  independently — `evaluations_total: 0`, `events_scored: 0`. So 19 is the
  ledger count and 0 is the counted count, and the supersession moves no
  headline in either reading; this entry is where the blessed grading process
  behind those 19 stays recorded now that the constant no longer names it.

  **The exposure, narrowed to where it is real.** Because an evaluator digest
  records but never partitions, a grading series can pool across the rubric
  boundary this re-bless introduces with no artifact marking it. That cannot
  reach the frozen-scope boards, which hold none of these cells; it reaches the
  `--all-versions` views and the version-blind leakage reporting, which is where
  a reader comparing gradings across the boundary should expect it. It is narrow
  even there. All 19 are **interim** cells, which declare no semantic set, so
  not one carries a `semantic_grades` block; the passages that moved are the
  semantic protocol and the opinion slot, and the interim rules those 19 were
  graded under are unchanged byte for byte.

  **The grader population is empty, and the first grades under this design are
  its debut rather than its confirmation.** Both declared `semantic-v1` claims
  require a majority opinion; no merits cell has been graded against one; and
  the first OT2026 opinions are not expected before December 2026. So the
  protocol registered here — the staged slot as the graded text, the closed
  ground vocabulary, the precedence that resolves a split panel — has never met
  a real opinion, which [outcome-decomposition.md](outcome-decomposition.md)
  states in place under *What remains unbuilt*. A reader meeting the first
  ground split should read it as the design's first outing, not as a validated
  measurement.

  **One reading rule this boundary creates, prospectively.** No committed
  evaluation carries a `semantic_grades` block at all today, so every census
  bucket including `unstated` is empty and no mask total is quotable. The
  boundary bites only on gradings written under the retired evaluator digests
  from now until the carrying promotion lands: those answer a protocol that
  never asked for the ground and so fall to `unstated`, which records *nobody
  was asked* and never *nobody could tell*. Because `semantic-summary`'s scope
  gate filters on the *prediction's* stamp rather than the evaluation's digest,
  a census legitimately pools graders from both sides, making `unstated` a
  mixture the artifact cannot separate — and this entry is what dates the
  boundary a reader has to check against (`metrics/README.md`).

  The runnable effect check, for the promotion carrying this: after the next
  evaluate round on a merits cell whose case carries an opinion, `uv run
  fedcourts semantic-summary --stratum forward --all-versions`. The observable
  proof that the staging step, the prompt amendment and the census split all
  moved together is an **ordinal grade**, or a `masked on …` clause naming
  `silent-on-axis` or `no-judgment` — each of which can only be written by a
  grader that read a body. `not-ingested` on an opinion-bearing case is the
  opposite reading: it says the staging step did not deliver, and the failure
  annotation on that run is where to look. `unstated` there says the cell ran
  under the retired protocol.

- **The predict backlog re-owes a cell on a still-forward event whose whole
  cohort a re-bless retired, 2026-09-15.** Registered **before** any of the
  cells it will mint exist, and before any of their outcomes are observable:
  what this entry pre-registers is a **selection rule over a cohort**, and a
  rule written after its cells had been forecast would be a report rather than
  a pre-registration.

  **What creates the need.** The proc-v7 freeze replaced the predictor half of
  `FROZEN_PROCESS_DIGESTS`, which de-counts every cell stamped under the
  retired digests. proc-v8 is an evaluator-half re-bless and carried those
  three predictor digests forward byte-identical, holding the instant, so the
  enforced membership filter and the counting boundary this entry reasons
  about are proc-v7's and unchanged. The supersession entries above treat that
  over cells whose events have **resolved**, where what moves is a published
  figure. The other half of the retired cohort sits on events that are still
  open, and there the consequence is invisible until it is too late to fix:
  the predict backlog's owed check is version-blind — a committed prediction is
  a committed prediction — so an event holding only retired cells reads as
  covered, derives no work, resolves, is graded, and every result is dropped
  from the frozen board by `store.stratify`. The event is consumed for nothing.
  As at this commit **no committed `prediction.json` in the ledger carries any
  blessed predictor digest**, so on present state the frozen board's predictor
  population is empty and would stay empty however many events resolve.

  **The rule, as a cohort and not a case list.** In
  `pipeline.pull.derive_predict_backlog`, an event is owed a cell **again** for
  a predictor when all of:

  1. It is **genuinely forward**, on the record-side gate the fan-out already
     applies (`store.forward_refusal_reason_from_parts`): no committed
     `outcome.json`, not flagged resolved in the corpus, and — for the event's
     own stage — no disposition, no resolution date, no latched merits
     judgment, no recorded merits termination. The stage limb is what excludes
     a docket the live channel has polled as decided but whose outcome it has
     not yet written; `scotus/9526000326`, decided 2026-09-10, is such a case
     at this commit. A cell minted there would be a replay in forward clothing,
     with unrestricted retrieval over an answer already public.
  2. Its **declared moment is still open** — `pull.REPREDICT_MOMENTS`, a table
     of `(stage, moment)` pairs: cert/distribution, cert/cvsg, and the three
     interim moments. A cert/distribution event is additionally refused unless
     it carries a `distributed_for_conference` still ahead — a past one because
     that cell forecasts the conference the petition is distributed for and
     once the conference is behind us a new cell answers a different question;
     an absent one because the distribution moment has not happened at all,
     which is the information-set precondition the fan-out's own
     premature-cell refusal applies. **The three interim rows carry no
     equivalent bound**, and the asymmetry is registered rather than hidden:
     the distribution limb is self-closing, so a petition decided at its
     conference leaves the rule the next day whether or not a poll has caught
     up, while an interim event's only outcome guard is gate 1. On an
     application docket that guard reads the application's own disposition and
     is exact — it is what refuses `scotus/9526000326`. On a **cert-numbered**
     docket an interim motion's row disposition is the *cert* disposition, not
     the motion's, so the guard there is the corpus event's `resolved` flag
     alone. Exposure at this commit is one event (`scotus/73279700`), which the
     record-freshness hold is currently holding anyway.
  3. **Every** committed prediction that predictor holds on the event is
     outside the frozen process scope —
     `store.predictor_holds_only_retired_predictions`, which asks `is_frozen`,
     so *both* of its limbs count: a digest outside
     `FROZEN_PROCESS_DIGESTS`, and a blessed digest stamped before
     `FROZEN_SINCE`. An unstamped cell is outside on the first. A predictor
     already holding a cell inside the scope is not re-owed one, so a
     partly-blessed cohort re-mints only its retired half — and an event
     carrying both a predictor with no cell at all and predictors whose cells
     are all retired is owed cells on **both** grounds, so a run can never mint
     one blessed cell beside de-counted rivals.

  Every existing gate is untouched, in the two places they sit. **Upstream of
  the rule**, deciding which events it is asked about: `predict_excluded`, the
  predict-scope rules and the per-cell attempt cap. **Downstream of it**,
  deciding what a run actually mints: the record-freshness and
  provisioning-attempted holds, the per-cycle case cap, the per-run cell cap,
  and the ex-post spend backstop. The rule adds an admission ground and loosens
  none of those. It does widen exactly one: the **salience
  funding gate**, whose cohort-completion narrowing governs the never-predicted
  arm alone while this rule is asked over the whole forecastable set, for the
  reason given under the exclusions below. Nothing about the
  salience selection itself moves — no case is latched or unlatched, and the
  round's own capacity is untouched.

  **The exclusions and their grounds.** *cert/arrival* is excluded because its
  contract is "forecast at docketing, before any distribution or
  docket-acquired signal exists" — every such petition has since been
  distributed, so a cell minted now would not be a late forecast of that moment
  but a forecast of a different one, and only the original cell ever observed
  it. *merits/grant* and *merits/briefed* are excluded on funding, not on
  correctness: their moments stay genuinely open, so the rule would apply, but
  they are spend now for a board population a Term away. The exclusion is the
  absence of their two rows from `REPREDICT_MOMENTS`, and adding the pairs
  `(merits, grant)` and `(merits, briefed)` there is the whole change needed to
  take them. *Undeclared events* — entry-pinned motions, legacy
  baseline ids — are excluded because the register cannot place them in a
  cohort. A *salience-deferred case* is **not** excluded, and this is the one
  place the rule widens an existing gate rather than sitting inside it. Such a
  case reaches the deriver only on the cohort-completion ground, whose
  narrowing keeps the events a claimable board already counts — and that
  narrowing governs the **never-predicted arm alone**: this rule is asked over
  the case's whole forecastable set, so a deferred case's wholly retired events
  are re-owed alongside a funded case's. The ground is the comparability
  argument the narrowing itself rests on: what that predicate refuses is a
  *partial* completion — one blessed cell beside siblings that will never be
  counted — and a wholly retired cohort is re-minted for every engine at once,
  which completes a cohort rather than manufacturing a one-engine one.

  The widening is bounded by the rule and stops there. An event no predictor
  has forecast is not re-owed, so no **event** the funding gate declined is
  opened, and the salience selection itself does not move — nothing is latched
  or unlatched by this rule. At the **cell** grain a re-owed event does
  complete: an engine holding no cell on it is minted its first one, because
  the fan-out's already-predicted skip never drops an engine holding nothing.
  That is the completeness the whole ground rests on, and it is registered here
  rather than left as a surprise in the ledger — a deferred case can therefore
  carry a first-ever cell for one engine beside re-mints for the others. It
  buys no priority: such a case is still classified as re-owed work and still
  follows every case owed a never-predicted cell.

  **Old cells are retained, unedited.** A re-predict writes a new run
  directory beside the old one. Nothing edits, moves or deletes the retired
  cell. Provisioning stages the **newest** run per predictor
  (`blinding.latest_prediction_dirs`) and an evaluation records the
  `prediction_run_id` it graded, so the new cell is the one a board reads and
  the old one is history that no figure counts twice. This is not a re-grade:
  no existing `evaluation.json` moves and `superseded_gradings` is untouched.

  **Expected size on the state at this commit** — corpus blob pulled
  **2026-09-14** (newest pull stamp; newest stored snapshot 2026-07-13;
  blob sha256 `5ff9b1b6ed4e9550d646bfe9e514f2fbe9fe99e099b0cd1cace0f90068d2da10`,
  named because the committed corpus ref has moved since and this census is
  reproducible only against that blob), ledger
  at the `main` tip `86ab3dd2b` — the ledger the production lane derives
  against, read before this work moved to its `staging` branch, since data
  commits land on `main` and never ride staging. Of 663 committed
  `(case, event, predictor)` cells, **zero** carry a blessed digest. **223**
  events hold nothing but retired or unstamped cells. Applying the three gates
  above leaves **123** events at an allow-listed open moment — 110
  cert/distribution (every one distributed for the **2026-09-28** long
  conference), 10 cert/cvsg, 3 interim/arrival. **That whole set is the
  cohort.** The salience funding gate does not subtract from it: 52 of the 123
  are on `salience_selected` cases and the other 71 are not, and the rule's
  second admission ground at the cohort-completion narrowing takes both. The
  alternative was to re-predict the funded 52 and leave the 71 holding only
  pre-freeze cells — to be graded on resolution and dropped from the frozen
  board, which is the exact failure this rule exists to prevent, left standing
  on the larger half of the cohort.

  An uncapped read of the deriver itself (`fedcourts predict-plan` with the
  cycle and cell caps lifted, against that blob and that ledger) mints **122
  events on 122 cases = 362 cells** today — **110** cert/distribution, **10**
  cert/cvsg, **2** interim/arrival — at an estimated **$820.86**, priced at the
  per-(seam, engine) rates in [budget.md](budget.md) ($4.27 + $1.88 + $0.64 =
  $6.79 an event across the three engines). That is the **whole-run** rate,
  whose measured fan-out was 11 merits events of 27, and merits runs about
  $1.2 an event above cert; this cohort is 120 cert and 2 interim events and no
  merits at all, so the figure reads **high** — budget.md's cert-first-
  distribution row is $6.66 and its 137-event pre-freeze cert-distribution
  reference $5.57, which bracket the honest range at roughly $670-813 — the top
  of that on the 122-event count (122 x $6.66), the bottom on the 362 cells
  actually priced (120.67 three-engine event-equivalents x $5.57). Read that
  bracket with its own limit: budget.md carries **no CVSG row at all**, so 8%
  of this cohort has no measured rate behind it, and the $6.66 row is n = 3,
  which budget.md's own instruction ("read the row `n`s before the dollars")
  says not to lean on. The wider post-freeze per-stage rows — cert $6.68
  (n = 35) and interim $6.41 (n = 12) — are the better lower anchor. The
  $820.86 is the **re-owed subset** priced at the same per-(seam, engine) rates
  `predict-plan` applies; the plan's own `estimated_spend_usd` covers the
  never-predicted arm too and reads **$909.86 over 402 cells**, and
  `reowed_pre_freeze_cells` is a count with no spend figure beside it. Both are
  priced without conditioning on the forecast moment, which the plan does
  deliberately.

  The two figures are **pre-hold 123** and **post-hold 122**, so they are named
  here: the remaining **1** is held, not excluded — the record-freshness bound
  on `scotus/73279700`, last polled 2026-09-02 — and it clears at that case's
  next poll. A quoted "123 x 3" would be wrong; the cells minted today are
  362, four short of 122 x 3 because four `(event, predictor)` cells on
  re-owed events belong to the never-predicted arm instead. The
  provisioning-attempted bound holds **none** of this cohort: every case in it
  was provisioned when it was first predicted, and the reading above addresses
  the content store, so document presence is answered by the store that holds
  it rather than by the payload-free blob. The same derivation carries **12**
  never-predicted events (40 cells with the four above, $89.00) which are
  ordinary backlog and not this rule's doing; the whole owed set is **131**
  cases.

  **How long it takes, and what it costs upstream.** The drain is paced by
  `salience.sweep_cases_per_cycle` (25 cases a tick) rather than by the cohort's
  size, and `run-predict` ticks twice a day: **about 5 ticks** for the 122
  re-owed cases, 6 for the whole 131-case owed set — roughly three days from
  promotion, and the deadline that matters is the 2026-09-28 conference. A
  tick's cells stay well inside `predict.max_predict_cells_per_run` (240): the
  first tick as read at this commit is 81. That drain is a **floor**: the
  derivation writes no debounce stamp and reads committed state, so a tick whose
  collect PR has not merged re-presents the same head and buys nothing. Thirteen
  days against a five-tick floor is the slack, and it is slack in ticks rather
  than in days. The **CourtListener** budget is
  unaffected by the cohort's size for a structural reason worth stating, since
  the cohort roughly tripled against the funded-only alternative: a tick's
  fan-out runs at most **6 cells in parallel** (`run-predict.yml`'s
  `max-parallel`), and that ceiling is per tick, not per cohort, so a larger
  cohort buys more ticks rather than a larger burst. Each tick's retrieval
  therefore sits under the account's hourly ceiling on its own, exactly as a
  funded-only round would, and the rest of the account budget — the pull lane's
  rotation — is bounded by its own per-window caps and untouched by this rule.

  **The cohort spans bands, and the composition is registered rather than left
  to be rediscovered from the board.** The funding line is a salience-band
  split — that is what makes it a statistical fact and not only a spend one —
  and taking the whole cohort is what keeps it from becoming a **boundary** of
  the frozen population. Over the 110 cert/distribution events that pass the
  forward and moment gates, by `sal-v4` band, with the funding line shown so
  that the split it would have drawn is on the record:

  | | n | high | elevated | baseline | state/federal | mean score (range) |
  | --- | ---: | ---: | ---: | ---: | ---: | ---: |
  | **the cohort** | **110** | **1** | **37** | **70** | 1 federal, 1 state | **0.0504** (0.0130-0.4108) |
  | of which salience-selected | 39 | 1 | 34 | 3 | 1 federal | 0.0983 (0.0334-0.4108) |
  | of which declined | 71 | 0 | 3 | 67 | 1 state | 0.0241 (0.0130-0.0830) |

  The salience score approximates P(grant | relist / CVSG / circuit signals), so
  the two sub-rows differ roughly fourfold in the mean; their ranges overlap on
  4 of the 39 selected cases, which is the whole overlap and is recorded rather
  than rounded to "disjoint". Had the cohort stopped at the funded 39 it would
  have been an **elevated-band** population wearing a cert-stage label. The
  other two arms are not band-spanning: the 10 cert/cvsg events are all
  **high** band, and the 2 interim/arrival events are baseline. That is a fact
  about these 12 rather than a structural guarantee — a federal-caption petition
  carrying a CVSG bands `federal`, not `high` — so a later cohort must
  re-measure rather than assume it.

  **What the cohort is not: the conference.** Taking all 110 improved the
  population; it did not make it representative, and the stronger claim is the
  one to refuse in writing. 557 SCOTUS petitions are distributed for
  2026-09-28; 180 of them are in predict scope; the cohort is **110 of those
  180** — every one of the 37 elevated, the 1 high and the 1 federal, but only
  70 of 138 baseline and 1 of 3 state. It is the previously-predicted residue of
  earlier funded rounds, so it is **selected upward on band**: 63.6% baseline
  against the in-scope conference's 76.7% and the distributed set's 87.8%. Its
  band-mix-implied grant rate is correspondingly about 1.2x the in-scope
  conference's and 1.5x the distributed set's (10.05% against 8.30% and 6.67%,
  on the basis named below). No figure over this cohort is a figure about the
  conference, the docket, or a random sample of either.

  **The reading rules that follow, registered now.** Band mix is not a
  formality here — the always-deny floor a figure is read against is the band's.
  So:

  - A frozen-board figure over this cohort is reported on the **per-band cut**
    (n = 1 high / 37 elevated / 70 baseline / 1 federal / 1 state on the
    cert/distribution arm, with 10 cert/cvsg and 2 interim/arrival beside it)
    and never as a single pooled row.
  - The **high band is n = 1 on cert/distribution and n = 10 on cert/cvsg**,
    n = 11 across the cert stage and never pooled across the two moments. A
    high-band claim on the distribution arm is a claim over one event; the CVSG
    arm is where the cohort's high band actually sits.
  - The anchor is the **registered segment base rate by salience band (sal-v4)**
    — the risk-set (`reached`) rate pooled over `base_rate_lookback_terms`,
    excluding the cell's own Term, which is what the predict prompt anchors on
    and what the evaluator scores skill against
    ([salience.md](salience.md)). On the committed statpack that is baseline
    **5.02%** / elevated **16.89%** / high **35.51%** / federal **70.79%** /
    state **23.63%**, so the always-deny floors are 94.98% / 83.11% / 64.49% /
    29.21% / 76.37%. These count the whole grant family, GVR included, because
    that is what the board scores. The terminal-composition shares in the
    statpack's *Cert petitions by salience band* table are a different
    vocabulary and are not the floor.
  - On that anchor the cohort's band-mix-implied grant rate is **~10.1%** over
    the 110 cert/distribution events (selected subset ~17.8%, declined ~5.8%),
    and **~12.2%** over all 120 cert-stage events once the 10 CVSG are folded
    in. A **whole-docket anchor of 1-3% is wrong for this cohort by 3-10x** and
    may not be used for it. The 2 interim/arrival events carry no salience-band
    base rate at all — an interim cell is scored against `interim_base_rate`
    with `base_rate_basis` null — so they are outside every figure in this
    bullet.

  **The salience overhang is kept and disclosed, not cleared.** 39 of the 110
  cert/distribution events are on cases the current round selected against a
  long-conference capacity of 24. The overhang is deliberate and stays: no
  `unlatch-overselected` pass runs for this, the selected set is not narrowed,
  and the extra cases are re-predicted as forward cells like the rest. Taking
  the whole cohort changes what the overhang bears on rather than removing it.
  A figure over **all 110** is not a selection at all and carries no overhang —
  it is the conference's still-forward retired-cohort set, and its denominator
  is 110. A figure over the **selected subset** is over-capacity by
  construction, which is a fact about the selection round and not about the
  rule registered here — and disclosure alone does not say which way it moves,
  so: the 15 events above capacity are the **rank tail**, the lower-salience end
  of the selected set, so that subset's implied grant rate sits **below** what a
  capacity-24 selection would give. Any such figure carries the denominator
  **n = 39** and may **not** be compared with a capacity-N salience replay,
  which is a different population.

  **The conference date is a one-way door, so the completeness this rule buys
  has a deadline — and a reading rule rather than more code.** The
  distribution limb refuses an event once its conference is past. That is the
  safety property gate 2 exists for, and it has a cost: from 2026-09-29 the rule
  can no longer heal a **partially** re-predicted cohort. Any cert/distribution
  event whose three cells are not all committed by 2026-09-28 is left
  permanently with some blessed and some retired cells — reachable four ways: a
  cell fails on the last tick (its `attempt.json` re-owes it, but no later tick
  can mint it), a provisioning-held case does not clear, the freshness-held case
  is not re-polled, or a scheduled tick does not run. Thirteen days against a
  drain of about five ticks is slack, but the failure is silent and terminal, and it is exactly the
  cross-engine shape a leaderboard cannot show: per-predictor cells resting on
  **different event sets**, with nothing on the board separating "this engine
  was not scored here" from "this engine was structurally excluded here", while
  the ranking is on N-unweighted point estimates.

  Registered now, because it cannot be added afterwards: **a frozen-board figure
  over this cohort is published over events carrying all three blessed engines,
  or it prints the per-engine `n` and the complete-grid `n` beside it.** That is
  the discipline [budget.md](budget.md) already applies to its own reference
  fan-out ("132 events carrying all three" of 137), so it is this repository's
  existing instrument rather than new machinery.

  A second registration for the same deadline, at the **cohort** grain rather
  than the event grain: the drain is ordered stalest-queue-stamp first, not
  randomly, and the live sweep re-polls selected candidates, so poll recency
  correlates with salience. A cohort only partly drained when the conference
  arrives is therefore **not a random 60% of the table above** — it is the head
  of a recency-ordered queue, band-biased in a direction this entry cannot
  predict. So: if any tick of the drain does not run, the surviving cohort's
  band mix is **re-measured at the conference** and the re-measured table is
  what a figure is read against. The table registered here describes the cohort
  the rule derives, not whatever subset of it gets minted.

  **The comparability caveat, and it is the same one the amicus re-derivation
  carries.** A figure that rises across this boundary is **not** a measurement
  of model improvement. The cells on either side were produced by different
  processes — that is what the digest partition means — and the frozen board
  will hold only the post-boundary side, so there is no before-and-after series
  to read at all. The entry *The interim amicus re-derivation is built, and the
  two ends of the increment part company, 2026-09-14* states the same rule for
  its own apply ("a series compared across the apply is not a comparison"), and
  it holds here for the stronger reason that the pre-boundary side is not
  merely differently derived but structurally absent from every frozen-scope
  artifact.

  **What this rule cannot repair, and the loss is concentrated where the signal
  is.** An event whose moment has already closed — a petition whose conference
  has passed, a cert/arrival cell — keeps its retired cohort and will be graded
  out of scope when it resolves. Those events are spent: **100** of the 223,
  attributed **forward-gate-first**: 21 the forward gate refuses and 79 whose
  moment has closed. The deriver itself runs the moment filter first, for cost,
  which attributes the same 100 as 83 moment-closed and 17 forward-refused; the
  split is an attribution choice and only the 100 is a property of the state. The composition
  matters more than the count. Across the whole retired-only cert/distribution
  set (143 events) the bands are 17 high / 40 elevated / 80 baseline / 4 state /
  2 federal, and **only 1 of those 17 high-band events survives into the
  cohort** — the other 16 are moment-closed or already resolved. The 21 the
  forward gate refuses have themselves resolved 12 granted / 8 denied / 1
  dismissed, so the surviving cohort is depleted of resolved grants by
  construction. Registered consequence: **the frozen board's
  cert/distribution arm will carry essentially no high band until new petitions
  reach it**, and a high-band figure over that arm is a figure over n = 1. The
  cohort's high band is the **cert/cvsg** arm's 10 events, which is a different
  moment and does not pool with the distribution arm. The rule bounds the loss to
  what has already happened rather than recovering it, and nothing here claims
  otherwise.

  **The effect check, for the promotion carrying this.** `uv run pytest
  tests/test_predict_backlog.py` green. After promotion, the next scheduled
  `run-predict` ticks derive re-owed cells rather than reporting a drained
  backlog: `uv run fedcourts predict-plan` (run where the corpus is pulled)
  shows a non-zero `counts.cell_ledger.reowed_pre_freeze_cells` with the
  matching records under `reowed_pre_freeze` — 45 over 15 cert/distribution
  events on the first tick as read at this commit, 10 of those 15 cases
  salience-declined and kept by the widening, which is the arm's own executed
  check — and the run's own plan report carries the same figure at the review
  hold. About five such ticks drain the cohort. The lasting check is the one the
  rule exists for: after the 2026-09-28 conference the evaluate round's
  gradings of those events enter the frozen board — `metrics/leaderboard.json`
  built with `process_scope: "frozen"` and a non-zero cell count, where today
  it renders its empty state.

- Freeze commit: `100a911adf3d8c249296dcf0124e025bb7dc8910`, to be tagged
  **`prereg/proc-v8`** per step 4 — on this freeze commit itself, once its
  carrying promotion lands. **The predict contract answers four questions it
  left open, the predictor half is re-blessed, and proc-v8 becomes a full
  freeze, 2026-09-15.** proc-v8's evaluator half is registered two entries
  above; this one registers its predictor half, and because neither half has
  reached `main` yet the two ride **one** carrying promotion, so the
  `prereg/proc-v8` tag covers both. Carried to `main` by the promotion tagged
  `promotion/2026-09-16` (merge commit `545e26e2b753ac79701a4fd638689a8d48654bce`, merged
  `2026-09-16T00:26:04Z`).

  **What moves the digests.** `.github/prompts/predict.md`, four amendments and
  nothing else — every byte of that file is hashed into all three predictor
  digests, so the change is stated as a list a reader can check against the
  diff:

  1. **`input_snapshot` acquires a canonical form, and its consequence.** The
     field asked for an "identifier/path"; it now asks for the provisioned
     file's bare basename `YYYY-MM-DD.json`, or the literal `missing` with the
     reason in `flags.json`, and it states what the harness does with the
     answer — `stamp-cell` compares the cell's string against the provisioned
     snapshot, both reduced to that file's day, and records
     `context.snapshot_uptake` `unread` on disagreement, with a harness note
     beside it. That comparison was built without telling the cell it existed,
     and a cell judged on a field whose contract it was never given is the
     coarseness this closes. Validation stays permissive — the committed
     ledger's several spellings were elicited under the looser ask and are not
     wrong under it — so what tightened is the prompt, and the schema and
     [predicted-artifacts.md](predicted-artifacts.md) now say which is which.
  2. **`big_case_score` becomes required with a null escape.** It was optional,
     and an absent field pooled two different records: a cell that weighed the
     stakes and could not place them, and a cell that never engaged the
     question. The prompt now asks for the number, or an explicit `null`
     carrying a one-line `big_case_rationale`. The field's meaning is unchanged
     — "score the stakes, not the odds" stands byte for byte — and the schema
     stays nullable and optional so the committed ledger validates, which
     leaves the separation the prompt's to hold. Every figure over this field
     counts reads rather than cells, so the pooling moved a denominator; from
     here a declared null is visible in it.
  3. **The merits-stage documents correction**, which the entry *The document
     selector reads the merits stage: per-side merits briefs, and a cert-stage
     bound on the opposition row, 2026-09-10* registered as owed — "that
     sentence becomes **false** for a briefed-moment cell the first time one is
     provisioned over a case carrying these rows, and it points the cell at
     retrieval for material already on its disk". The prompt told a merits cell
     that "any provisioned `record/documents/` text is cert-stage"; it now
     names `merits-brief-petitioner.txt` and `merits-brief-respondent.txt` and
     says which moment sees them: where `context.cutoff` is set, the date bound
     that cuts the snapshot cuts the directory, so a `moment: grant` cell's
     briefs fall outside it and a `moment: briefed` cell's fall inside. It
     states the **rule** rather than that outcome, because `moment_cutoff`
     returns null for an event row carrying no `opened_at` and an uncut
     directory is then the case's latest whatever the moment — so the
     amendment adds a refusal the old sentence had no need of: a merits brief
     on a `moment: grant` cell's disk is a provisioning anomaly, to be
     disclosed in `flags.json` (`data-quality`) and kept out of the forecast,
     or the two merits moments collapse into the one the later of them was
     declared to be. It asks the cell to name the provisioned briefs it read in
     `reasoning.md`, and to **summarize rather than reproduce** them, since that
     prose is committed to a public ledger — a republication constraint
     [data-sources.md](data-sources.md) now carries in the same terms as the
     questions-presented text beside it. That discharges the ordering
     constraint the same entry set: this freeze promotes before the first
     briefed-moment cell over a case holding provisioned merits briefs.
  4. **The amicus elicitation clause**, which the entry *The interim amicus
     reading widens to submissions, and the resolution count takes an
     end-of-day cut, 2026-09-10* registered as deliberately deferred: "the
     predict prompt asks an interim cell for the probability that 'the amicus
     count rises past' the number its record shows, and it does not say which
     entries that count reads. Under the widened reading it now reads
     submissions too, and the cell is not told. Saying so in the prompt would
     move all three predictor digests and force a re-bless; the digests stay
     put and the elicitation stays slightly coarser than the resolver, which is
     registered here rather than left silent." The re-bless is due for other
     reasons now, so the coarseness closes at no extra cost. The
     `amicus-increment` bullet now states the count both ends resolve on, as
     `interim_signals.amicus_briefs` actually computes it: every docket
     **entry** reciting `amic(us|i) curiae`, one per entry and therefore
     including an entry that recites the Latin without being a brief, plus each
     distinct lead filer whose brief the docket shows as submitted in English
     and whom no Latin-form entry names — and the monotonicity that follows
     from the corpus column's max-latch, that a submission the Court later
     refuses stays counted. That last clause is worth naming, because the
     record sentence this amendment is discharging is looser than the resolver
     on exactly that point, and a looser sentence in a *record* becomes a wrong
     contract once a scored claim resolves against it. **Exactly that gap and
     no more.** The other half of that entry — the resolution end's end-of-day
     cut, and the positional-arm asymmetry it creates — is not an elicitation
     coarseness and stays where it is registered.

  Nothing else in the prompt moves: no restructuring and no re-ordering, and
  the cert-stage spine, the claim sets, the retrieval doctrine and the leakage
  rules are byte-identical.

  **What else rides the commit and moves no digest.** `run-predict.yml`'s three
  engine kickoff messages gain the case-level record path
  (`data/cases/<court>/<docket>/record/`, matrix-interpolated so the engine
  reads a resolved literal), and `pipeline.runner`'s local mirror of that
  kickoff gains the same line, so an engine that reads the identifiers and
  never opens the template still lands on the provisioned inputs. A kickoff is
  hashed into no digest — the template file's bytes and the resolved registry
  config are what the digest covers — so this widens what a cell is told
  without moving a process version. It is recorded here because it reaches the
  same cells as the amendments above and is therefore part of what the first
  proc-v8 predictions were produced under, not because it is a boundary of its
  own. [data-sources.md](data-sources.md)'s republication paragraph moves with
  amendment 3 on the same footing: it is the written model catching up to a
  document class the provisioner already staged, and it moves no digest either.

  **The digests, before and after.** The three **predictor** digests move; the
  three **evaluator** digests do not:

  | actor | retired (proc-v7's, carried into proc-v8's evaluator half) | blessed here |
  | --- | --- | --- |
  | claude-baseline | `sha256:930e02ae18…` | `sha256:b89df0c6d7…` |
  | codex-baseline | `sha256:c57113fae8…` | `sha256:bfd8489590…` |
  | gemini-baseline | `sha256:4edc5ac58c…` | `sha256:c28fa7ac37…` |

  The evaluator digests stay `sha256:fbc0e9c364…` (claude-judge),
  `sha256:9670e1c147…` (codex-judge) and `sha256:dbdc906476…` (gemini-judge):
  the entry two above blessed them and this commit does not touch
  `.github/prompts/evaluate.md`. All six therefore carry the **same** step-2
  forecast floor, `2026-09-15T00:00:00Z` — midnight on this commit's authoring
  date, and so at or before it, which is the safe direction because the
  carrying merge is necessarily later — and all six take step 4's correction to
  `2026-09-16T00:26:04Z`. None is carried forward from an earlier
  label, so none keeps an earlier bless moment.

  **The freeze instant moves to `2026-09-17T00:00:00Z`**, from proc-v7's
  `2026-09-07T00:00:00Z`. The held-instant exception is scoped to a predictor
  half byte-identical to the prior `prereg/` tag's, and this commit is exactly
  the case it excludes, so the ordinary rule governs: the literal must be at or
  after the carrying promotion's merge and before the first run intended to
  count. The value is two days past this commit's authoring date, guessed late
  as step 2 asks, and `run-predict`'s review hold is what keeps the window
  between the merge and the instant empty in practice — no cell spends until a
  maintainer releases it, so a run released inside that window is a choice
  rather than an accident. What that choice costs is worth stating plainly,
  because it is not merely a few uncounted cells: a cell minted in the window
  carries a blessed digest and still fails `is_frozen`'s time limb, so the
  pre-freeze re-predict rule registered in the entry immediately above re-owes
  it on its gate-3 second limb and the round is paid for twice — on this cohort
  that is the whole ~$820 of it.

  **Two things the move does that this label's predecessor entry did not
  anticipate, recorded because an append-only record must name the claims it
  falsifies rather than leave two entries disagreeing.** First, the move is
  total in both halves, as [process-version.md](process-version.md) says a
  predictor-half re-bless is: the instant independently drops every evaluation
  stamped before it through `graded_post_freeze`, blessed evaluator digest or
  not. The 19 evaluations the entry two above registered as *"every one stamped
  at or after the instant, so every one passes `graded_post_freeze`"* are
  stamped 2026-09-14 and 2026-09-08, inside `[2026-09-07, 2026-09-17)`, so
  every one of them now fails it. Their counted census stays **0** — the
  predictions they grade carry no blessed digest, and the committed leaderboard
  is 0/0 — so no published figure moves; what moves is the reading, and this is
  where it is dated. Second, that entry registers as `prereg/proc-v8`'s *only*
  auditor's check that "the predictor digests under `prereg/proc-v8` must equal
  `prereg/proc-v7`'s". Under this commit that comparison fails by design, so it
  is **retired**: the audit for the tag is the ordinary step-4 date comparison
  stated above, and an auditor running the byte comparison is running a check
  this entry superseded before the tag was minted.

  **The move costs nothing, and the census says so rather than the argument.**
  A predictor-half re-bless is the third supersession shape — the only one that
  de-counts — but the population it de-counts here is **empty**. No committed
  `prediction.json` carries any of the three retired predictor digests, so
  `is_frozen`'s membership limb was already false for every cell in the ledger,
  and moving the instant takes nothing out of a published figure that was in
  one. This is therefore the plain supersession rather than the
  licensed-by-declaration shape, and no shakedown declaration is owed: there is
  no de-counted claim window, because there are no counted cells. The
  `metrics/leaderboard.json` committed at this commit settles it independently
  — `evaluations_total: 0`, `events_scored: 0`.

  That census is a fact about **this commit**, and the window to the carrying
  promotion is live: a `run-predict` tick released into it mints cells under
  the retired predictor digests, which the promotion then de-counts. So the
  claim above is stated conditionally rather than as a standing one, and this
  entry is dated before any of those cells' outcomes are observable, which is
  what lets it serve as the prospective **shakedown declaration** for whatever
  that window mints: any cell stamped under a retired predictor digest between
  this commit and the carrying merge is declared shakedown here, before its
  event resolves, and the label whose cells are the counted record is proc-v8.
  The promotion-time re-run of step 0 below is what says whether that arm is
  empty or populated; either way no boundary is drawn after an outcome.

  **Step 0, at authoring.** Against `origin/main` at `61e1bfee6`, the per-digest
  grep over `data/cases` returns **0** for each of the three newly blessed
  predictor digests (`sha256:b89df0c6d7…`, `sha256:bfd8489590…`,
  `sha256:c28fa7ac37…`), which is the precondition rather than a note — a
  prediction carrying one would be retroactive blessing by construction and
  would redden the ledger tripwire. The same grep returns **0** for each of the
  three retired proc-v7 predictor digests (`sha256:930e02ae18…`,
  `sha256:c57113fae8…`, `sha256:4edc5ac58c…`), which is the de-counted census
  above, and **0** for the three evaluator digests, unchanged from the entry
  two above. The wider census of stamped cells — the object-form grep for
  `"process_version": {` over the same tree — is **482**. Re-run all of it at
  the promotion, against `origin/main` at `545e26e2b`: **0** for each of the six
  digests the map carries at that merge — the three evaluator digests unchanged,
  and the three predictor digests the entry below re-minted,
  `sha256:1a0b2bef2e…`, `sha256:70fee15852…` and `sha256:a9033e5681…`, which are
  what this promotion actually blesses — **0** for each of the three retired
  proc-v7 predictor digests, and **0** for each of the three superseded digests
  this entry printed, which never reached `main`. The wider census is unmoved at
  **482**.

  **What the retired predictor digests ran, and why the ledger count is zero
  too.** Unlike the evaluator half two entries above — whose retiring digests
  carry 19 committed but uncounted evaluations — the retiring **predictor**
  digests carry no committed cells at all, counted or ledgered. proc-v7 blessed
  them on 2026-09-06 and the predict lane has minted nothing under them since,
  which is the same fact the entry immediately above — *The predict backlog
  re-owes a cell on a still-forward event whose whole cohort a re-bless
  retired, 2026-09-15* — derives its whole cohort from. So this supersession
  retires a blessed process that never produced a record, and that process's
  headline was legitimately empty for the whole of its life.

  **The cohort this freeze is timed for.** The re-predict rule registered in the
  entry immediately above derives **122 events on 122 cases = 362 cells** on the
  state at that commit, every cert/distribution member of it distributed for the
  **2026-09-28** long conference, drained at about 25 cases a tick over roughly
  five ticks. Those cells are the frozen board's first predictor population, and
  they are the reason this amendment lands **now** rather than after them: a
  predictor re-bless taken later would de-count the whole cohort and re-owe it,
  against a conference date that closes the distribution limb on 2026-09-29.
  Minting the cohort under the amended prompt from its first tick costs one
  promotion; the same correction a week later costs the cohort. The band mix,
  the reading rules and the complete-grid discipline that entry registers for
  those cells are untouched by this one — this moves which process produced
  them, not which events they sit on.

  **What is not claimed.** The first cells under the amended prompt will be that
  cohort, on real spend: no committed prediction exists under these bytes, so
  nothing here reports how the four amendments change a forecast. The
  whole-suite freshness run's engine-smoke cells are the rehearsal — a real
  engine over the amended template, one cell per engine — and they smoke the
  contract rather than measuring it. Two expectations are stated so a later
  reading cannot be dressed up as a finding: `big_case_score` coverage should
  **rise** toward every cell carrying either a read or a declared null, and a
  briefed-moment merits cell should cite provisioned merits briefs where its
  case holds them. Neither is a skill claim, and the second inherits the
  expected-skill corollary the 2026-09-10 selector entry registered — a rise
  across that boundary may not be read as a model improvement.

  **Three elicitation boundaries this creates, and the pooling each refuses.**
  The evaluator half two entries above registered its rubric boundary the same
  way, and symmetry asks for it here. (a) `amicus-increment` is elicited
  against a stated count where it was elicited against an unstated one, so
  before and after answer different targets: a Brier or calibration series over
  that claim may not pool across this boundary. (b) `big_case_score` coverage
  moves, which changes **which cases** enter the rank agreement rather than
  changing any score, so a tau-b read across the boundary is a correlation over
  two populations and not a trend. (c) `snapshot_uptake` was elicited from
  cells never told the comparison existed; the harness's definition is
  unchanged either side, but the elicitation is not, so an `unread` rate may
  not be pooled across it. The exposure of all three is bounded to the
  `--all-versions` views and the claim-score boards, because the frozen boards
  hold no predictor cells at all — which is the same reason the de-count above
  costs nothing, read from the other end.

  **The effect check, for the promotion carrying this.** `uv run fedcourts
  process-digest --all` at the merge prints `proc-v8` and exactly the six
  blessed digests, matching the map. Then the first `run-predict` tick released
  at or after the instant mints the re-predict cohort's first cells stamped
  with the new predictor digests — read `process_version.digest` off any new
  `prediction.json` — and `uv run fedcourts predict-plan` (run where the corpus
  is pulled) shows the re-owed bucket those cells come from. The lasting check
  is the one the timing is for: after the 2026-09-28 conference the evaluate
  round's gradings of those events enter the frozen board, with
  `metrics/leaderboard.json` built at `process_scope: "frozen"` carrying a
  non-zero cell count where today it renders its empty state.

- **The selector reaches the merits reply, and the gap scan reaches the granted
  cases already past their trigger, 2026-09-15.** A **conditioning** entry, in
  the same class as *The document selector reads the merits stage* above and
  with the same properties: no prompt byte and no registry field moves, so no
  digest moves; and there is **no data-visible boundary at all**, because which
  documents a cell was provisioned with lives in its gitignored
  `record/documents/` and `prediction.json` carries no field separating a cell
  that read a merits reply from one that did not. The boundary exists only here,
  cells minted on the affected dockets before and after it may not be pooled,
  and a stamped cell resolves to a side of it by asking whether its
  `process_version.pipeline_sha` is an ancestor of the carrying promotion's
  merge commit.

  It is also the entry the one above deferred to — "the granted cases already
  past their trigger are reached by a document-gap scan widened to the merits
  kinds, which is not built and will carry its own entry when it is."

  **Two changes, and only the first one moves what a future cell reads.**

  - **The reply kinds.** `merits-reply-petitioner` and
    `merits-reply-respondent`, one row per side and one URL per row, taken from
    the entry's `Main Document` link and selected only on entries filed strictly
    after the cert grant. The Court files the reply as a distinct entry family
    ("Reply of X filed.", "Reply Brief of X filed.") that the opening-brief
    anchors never reach, so it was fetched under no kind before. The post-grant
    bound carries more weight on this arm than on any other in the selector: the
    **cert**-stage reply to a brief in opposition is spelled word for word the
    same, and **422** of the **1,652** payload-bearing cases read below carry
    one these predicates match — so an unbounded arm would store a reply to the
    BIO as merits advocacy across a quarter of the docket stock.
  - **The gap scan's merits arm.** `document-backfill`'s class gains a second
    arm: a granted row whose respondent has filed on the merits
    (`merits_brief_filed` dated) and which holds neither or one of the two
    per-side merits briefs. Granted-**and**-briefed rather than granted alone is
    what makes it drain — a granted row with no briefing dated on it has nothing
    for a fetch to find, and is either still being briefed, which the selection
    sweep provisions while its merits event is open, or briefed in a shape no
    arm reads. The replies are deliberately **not** gap kinds: not every granted
    case is replied to, so keying the class on one would hold every un-replied
    case in it forever; a reply the docket carries is fetched with the rest.

  **The population, and the route it was read by.** The blob's newest pull stamp
  is `2026-09-14` and its newest stored snapshot `2026-07-13`. The walk runs the
  real `select_documents` rather than a re-implementation, over the case ids the
  blob's own `snapshots` table names, reading each case's latest payload through
  `corpus.latest_snapshot` — which under the split routes to the **content
  store**. That is not the route the entry above took, and the difference is
  named rather than smoothed: read from the blob's `snapshots` table alone, at
  this same vintage, the population is **269** granted with the merits arms
  reaching **105** — that entry's figures exactly, unmoved. Read through the
  store it is **1,652** payload-bearing cases, of which **271** have a payload
  dating a cert grant and the merits-brief arms reach **110** (101 both sides, 6
  petitioner-only, 3 respondent-only). Every figure here is the store reading,
  because that is the route the pipeline itself reads by.
  On the same 271 the reply arms reach **101** cases — **100** a petitioner-side
  reply and **10** a respondent-side one — so the reply is the ordinary shape of
  a briefed merits docket rather than a rarity, and it is the largest single
  addition to what a briefed-moment cell reads since the merits briefs
  themselves. The per-side split is what Rule 25.3 predicts and it is stated
  here so the respondent row's small `n` is not later read as a coverage
  failure. Three of the eight cases the entry above named as carrying committed
  merits cells — `scotus/73278510`, `scotus/73278555`, `scotus/73279865` —
  carry a petitioner reply the arm reaches.

  **Nothing already stored changes, and nothing is fetched by this commit.**
  The corpus holds **0** rows under either merits-brief kind and **0** under
  either reply kind (its `documents` table is 1,480 `petition`, 1,187
  `questions-presented`, 410 `brief-in-opposition`). The merits arm is a
  *scan* widening: it names candidates and writes nothing until a maintainer
  applies the pass. Over the whole predict-relevant live-slice population the
  widened scan reports **1,466** addressable candidates where the primary arm
  alone reported **1,233** — **431** of them merits gaps, **198** of which were
  already in the class for their opening filing too. The class is not reordered
  by arm, and on this corpus it does not need to be: `case_id` order puts the
  older granted dockets near the head, so **176 of the first 200 candidates in
  class order are merits gaps**. That is an observation about this corpus rather
  than a property of the pass, and it is recorded so a later dispatch's
  composition is read against what was expected — in particular, `merits_candidates`
  against `candidates` is a class-level ratio and not the mix a bounded slice
  will take. Separately, and the coincidence of the two counts is arithmetic
  rather than a transcription slip: **176 of the 431 merits gaps are OT2022 or
  later**, inside the upstream link window, and every one of those selects at
  least one merits brief over its stored payload (173 both sides, 3 the
  respondent's alone); of the 255 older ones 91 do and **164** select nothing,
  which an apply reports as floors rather than recoveries.

  **The expected-skill corollary, restated because this widens it.** A
  post-change briefed-moment cell reads both sides' opening advocacy *and* the
  reply that answers it, where a pre-change one read the opening briefs and a
  pre-09-10 one read only the docket entries saying a brief was filed. Expected
  skill on the granted docket should therefore rise again, and a rise across
  this boundary **may not be read as a model improvement**. The negative form is
  deliberate: the design supports excluding one reading, not asserting a cause.

  **The amendment debt is unchanged in kind and larger in size.** The predict
  prompt still tells a merits cell that any provisioned `record/documents/` text
  is cert-stage and that the merits advocacy is not on its desk unless it goes
  and gets it. That sentence was already false for a case holding provisioned
  merits briefs; it is now false about the reply as well. The prompt is frozen
  bytes, so the correction is a re-bless that must promote **before** the first
  briefed-moment cell over a case holding these rows — this entry adds no new
  ordering constraint, it enlarges what the registered one has to describe.

  **One derived surface moves and carries no boundary.**
  `TEXT_COVERAGE_KINDS` gains the two reply kinds, so `corpus-info
  --text-coverage` grows from twelve `kind` × `segment` cuts to sixteen. The two
  reply rows read differently from every row above them and the report says so:
  their `n` is bounded by the granted cases whose docket carries a reply at all,
  and the respondent-side row again by the postures that give a respondent the
  last word, so a low count there is neither a granted-slice size nor a coverage
  gap. No base rate re-prices, no scored figure moves, and
  `metrics/live-frontier.json`'s `documents_provisioned` is untouched, its
  watchlist being pending petitions.

  The runnable effect check, for the promotion carrying this: `uv run pytest
  tests/test_documents.py tests/test_merits_signals.py
  tests/test_document_backfill.py` green, and — run where the corpus is pulled —
  `uv run fedcourts backfill-documents --max-cases 0` reporting a non-zero
  `merits_candidates` beside its `candidates` (431 of 1,466 at this commit's
  blob), which is the walk-only reading that costs no upstream round trip. The
  fetching half is a writer-lane dispatch and its own dry run is what a
  maintainer reads before it: `run-repair` with `repair=document-backfill`,
  dry-run first, then an apply bounded by what that ledger's floors and arm
  split say the slice would actually recover.

- **The proc-v8 instant is set to `2026-09-16T00:00:00Z` ahead of the carrying
  promotion, 2026-09-15.** The entry above forecast `2026-09-17T00:00:00Z`,
  guessed late as the procedure asks, and named what a cell minted inside the
  window between the merge and the instant would cost: it carries a blessed
  digest, fails `is_frozen`'s time limb, and is re-owed by the pre-freeze
  re-predict rule — one event spent twice. The carrying promotion is planned for
  2026-09-15, so the instant is brought forward to the first midnight after it:
  at or after the merge, and before the first scheduled `run-predict` tick that
  could mint a cohort cell (14:12 UTC on 2026-09-16). That closes the window
  without leaning on the review hold to keep it empty. The value is still a
  forecast: if the merge lands on or after 2026-09-16 the step-4 correction
  moves the instant to the merge's own timestamp, never earlier than the merge.
  Nothing counted moves — the population under the proc-v7 predictor digests is
  empty, as the entry above records — and the bless moments are unchanged
  placeholders for step 4.

- **The predict prompt's interim baseline passage is corrected and the three
  predictor digests re-computed, 2026-09-15.**
  `.github/prompts/predict.md` told an interim
  cell that the statpack's interim base-rate section "does not yet reach" its
  pre-registered floor, and that the only strictly-prior Term carrying resolved
  substantive applications "contributes 44" against an OT2025 cell. Both halves
  are false on the committed pack (`metrics/statpack.json`, refreshed
  2026-09-14): OT2024 carries **70** resolved substantive applications of which
  14 were granted, so an OT2025 cell's strictly-prior pool clears
  `INTERIM_BASE_RATE_MIN_RESOLVED = 50` and `interim_base_rate` returns
  14/70 = 0.200, and an OT2026 cell pools 31/296 = 0.105. Both figures carry
  the coverage caveat the estimator's registration attaches to any quoted
  interim rate, and it binds hardest on the thinner one: OT2025's baseline
  rests **entirely** on OT2024, a Term the poller has parsed 325 of 1,297
  applications for, against OT2025 and OT2026 rows with nothing unparsed. So
  0.200 is a subsample rather than a census, and the gap between it and
  OT2025's own 7.5% is not evidence of a change in the Court's behaviour. The
  section reaches; what the prompt
  described as the standing answer — no baseline, anchor without one — is the
  arm the estimator does not take on either application-Term now predictable.
  A prompt is an agent contract, so this is a conditioning defect rather than a
  documentation one: left in place it would govern the whole post-freeze
  interim stream, each cell told to abandon a baseline the harness then scores
  it against. The passage now states the rule and **quotes no Term count** —
  the pooled strictly-prior rate where the pool clears the floor, the
  no-baseline arm where it does not, and the section's own per-Term table as
  the authority on which — so it cannot go stale again as parse coverage
  accrues. No other byte of the prompt moves, and
  `.github/prompts/evaluate.md` is untouched.

  **The digests, before and after.** The three **predictor** digests move; the
  three **evaluator** digests do not:

  | actor | superseded | blessed here |
  | --- | --- | --- |
  | claude-baseline | `sha256:b89df0c6d7…` | `sha256:1a0b2bef2e…` |
  | codex-baseline | `sha256:bfd8489590…` | `sha256:70fee15852…` |
  | gemini-baseline | `sha256:c28fa7ac37…` | `sha256:a9033e5681…` |

  The superseded three are the ones the proc-v8 predictor-half entry above
  blessed. They were never blessed on `main` — they existed only on `staging`,
  under a freeze commit whose carrying promotion has not run — so this is a
  **replacement**, not one of the three supersession shapes: no bless moment is
  retired, no cell is de-counted, and no shakedown declaration is owed. The
  bless-moment placeholders are unchanged, all six still carrying the step-2
  forecast floor `2026-09-15T00:00:00Z` for step 4 to correct at the carrying
  merge, and `FROZEN_SINCE` stays at the value the entry above set. **Read that
  entry's predictor half through the constants rather than through the values
  it printed**: its before-and-after table and its step-0 paragraph name the
  three superseded digests, and what its promotion carries is whatever
  `FROZEN_PROCESS_DIGESTS` holds at the carrying merge — the three blessed
  here. That is the only correction this entry makes to it.

  **Step 0, at authoring.** Against `origin/main` at `0e0a9e38f`, the per-digest
  grep over `data/cases` returns **0** for each of the three newly blessed
  predictor digests, which is the precondition rather than a note: a prediction
  carrying one would be retroactive blessing by construction. The same grep
  returns **0** for each of the three superseded digests, which are absent from
  `origin/main` entirely — the freeze commit naming them has not promoted.
  Nothing counted is affected: no committed `prediction.json` carries any
  predictor digest of this label, and the committed leaderboard is 0/0. Re-run
  at the promotion, against `origin/main` at `545e26e2b`: **0** for each of the
  three blessed predictor digests, **0** for each of the three superseded ones,
  still absent from `main` entirely, and the wider census unmoved at **482**.

  This entry must land **before** the carrying promotion, not after it. Once
  the promotion blesses a predictor half, a later prompt correction is a second
  re-bless that drops whatever the re-predict cohort minted in between; at this
  commit the population under every predictor digest is empty, so the
  correction is free exactly here and nowhere later.

  The runnable effect check, for the promotion carrying this: `uv run fedcourts
  process-digest --all` on the promoted tree printing the three predictor
  digests above, and then the cohort's first interim cell anchoring on the
  pooled strictly-prior rate — visible in its `reasoning.md` — rather than
  reporting that it anchored without a published baseline. An OT2025 cell's
  anchor should be the 0.200 above, read with the coverage caveat beside it.

- **The proc-v8 carrying promotion lands — step 4's correction to the instant
  and to the six bless moments, 2026-09-16.** The label's two freeze commits,
  `0272b1b9d209cb1f9a712c5143cb111627ecc620` (the evaluator half) and
  `100a911adf3d8c249296dcf0124e025bb7dc8910` (the predictor half, whose three
  predictor digests its branch-mate
  `09395d931d42a6779d426989b2fd7299dabf6ba7` re-minted inside the same PR and
  the entry above superseded again), promoted together on one merge as the
  predictor-half entry said they would: merge commit
  `545e26e2b753ac79701a4fd638689a8d48654bce` on `main` (parents `f67bd8e7a` /
  `a5ff08fb5`), tagged `promotion/2026-09-16`, committed
  **2026-09-16T00:26:04Z** — read off `git log -1 --format=%cI 545e26e2b`,
  which prints `2026-09-15T20:26:04-04:00`. The `<FILL:>` placeholders in both
  proc-v8 clusters and in the digest-recompute entry above are filled against
  that merge in the same commit as this entry. This is a new entry rather than
  a completion because it moves a constant, which a completion may not do.

  **The instant moves forward, from `2026-09-16T00:00:00Z` to
  `2026-09-16T00:26:04Z`.** The forecast midnight was chosen against a
  promotion planned for 2026-09-15; the merge landed 26 minutes and 4 seconds
  the far side of it, so the forecast sits **before** the moment the
  commitment became immutable on `main` and does not satisfy the ordinary
  step-4 rule. The entry that set it registered exactly this contingency — "if
  the merge lands on or after 2026-09-16 the step-4 correction moves the
  instant to the merge's own timestamp, never earlier than the merge" — and
  this is that correction, taken at the merge's own committed instant rather
  than at a later round number. That is the earliest value the rule allows,
  and choosing the earliest is deliberate on the reasoning the predictor-half
  entry gave for bringing the forecast forward in the first place: a cell
  minted between the merge and a later instant carries a blessed digest, still
  fails `is_frozen`'s time limb, and is re-owed by the pre-freeze re-predict
  rule, so its event is paid for twice. At equality that window has zero width
  and no such cell can be minted at all, which is a stronger guarantee than
  the review hold keeping it empty by decision.

  **The six bless moments move from the placeholder floor
  `2026-09-15T00:00:00Z` to that same `2026-09-16T00:26:04Z`.** proc-v8 is a
  **full** freeze — both halves blessed at one carrying promotion, with
  nothing carried forward from proc-v7 — so every entry in
  `FROZEN_PROCESS_DIGESTS` takes that one merge's time and the map holds a
  single distinct moment, which is the shape the constants-only ordering check
  reads. The two corrections land in one commit but are not the same kind of
  thing: a bless moment is a fact about git that the constant merely restates,
  and it could not have been in either freeze commit's tree because the merge
  establishing it had not happened; the instant is the pre-registered choice,
  which is why the `prereg/proc-v8` tag waits for the promotion that carries
  this commit rather than being minted at the one above.

  **No cell was minted in the window, so the forward move de-counts nothing.**
  The window is `[2026-09-16T00:00:00Z, 2026-09-16T00:26:04Z)`, and it is
  empty on three independent readings. No `run-predict` run started between
  the carrying merge and this entry: the newest is `35018975003`, scheduled
  2026-09-15T20:20:04Z — four hours before the merge, and a 1m14s
  plan-and-hold that mints nothing — and the newest `run-evaluate` is
  `35012098344` at 2026-09-15T19:11:11Z, likewise before it. `main` carries no
  commit at all after the carrying merge, so no data PR could have landed a
  cell there. And the ledger itself holds no cell stamped on the day: over
  `data/cases` at `545e26e2b`, the grep for `"stamped_at": "2026-09-16`
  returns **0** files. Nothing counted moves in either direction and no
  published figure changes — the committed `metrics/leaderboard.json` is still
  `evaluations_total: 0`, `events_scored: 0`, and still carries proc-v7's
  constants, not yet having been rebuilt since the freeze promoted.

  **Step 0, re-run at the promotion.** Against `origin/main` at `545e26e2b`,
  the per-digest grep over `data/cases` returns **0** for each of the six
  digests the map carries — predictors `sha256:1a0b2bef2e…`,
  `sha256:70fee15852…`, `sha256:a9033e5681…`, evaluators
  `sha256:fbc0e9c364…`, `sha256:9670e1c147…`, `sha256:dbdc906476…` — so
  nothing claims a proc-v8 digest from before its bless and both ledger
  tripwires have nothing to fire on. The same grep returns **0** for each of
  the three retired proc-v7 predictor digests and **0** for each of the three
  superseded predictor digests the predictor-half entry printed, which never
  reached `main`. The wider census, the object-form grep for
  `"process_version": {` over the same tree, is **482** stamped cells,
  unmoved from the authoring-time reading.

  **The tag, and where it goes.** `prereg/proc-v8` is **not** minted at the
  carrying merge. The procedure is explicit that an instant which came in
  early is bumped in a follow-up promotion landed *before* tagging — the
  `prereg/` namespace blocks update and deletion, so a tag minted over a bad
  instant burns the label — so the tag waits for the promotion carrying this
  correction, which is the whole content of that batch. Where it goes departs
  from the two clusters above, each of which said "on this freeze commit
  itself", and the reason is that this label has **two** freeze commits and
  neither one's tree states the quantities the tag pre-registers: the
  evaluator half's tree holds proc-v7's predictor digests and the instant
  `2026-09-07T00:00:00Z`, and the predictor half's holds three predictor
  digests a later commit re-minted and the instant `2026-09-17T00:00:00Z`.
  What a `prereg/` tag pre-registers is the blessed digests and the instant,
  so it goes on the **step-4 correction commit** — the commit this entry lands
  in — which is the first commit whose tree states both in the audited form,
  and which reaches `main` through its own carrying promotion. The placement
  and its consequence are recorded here as [pipeline.md](pipeline.md)'s *Tags*
  section asks of any deviation, and the auditor's check is unchanged by it:
  the literal in `src/fedcourtsai/process_version.py` at `prereg/proc-v8` must
  be at or after `git log -1 --format=%cI promotion/2026-09-16`, which it is,
  at equality. The byte comparison the evaluator-half entry once named as this
  label's audit stays retired, as the predictor-half entry retired it.

  **The runnable effect check, for the promotion carrying this.** On the
  promoted tree, `uv run fedcourts process-digest --all` still prints
  `proc-v8` and exactly the six digests above: this correction touches no
  prompt byte and no registry field, so a moved digest would mean something
  else rode along. The artifact-visible half is the next metrics refresh —
  `metrics/leaderboard.json`'s `frozen_process` block reading `since:
  2026-09-16T00:26:04Z` beside the six digests, where today it carries
  proc-v7's `2026-09-07T00:00:00Z` and proc-v7's six. The lasting check is the
  first released `run-predict` tick after this promotion: its cells are
  stamped after the instant by construction, so each clears `is_frozen`'s time
  limb, and the re-predict cohort's first cells enter the counted record with
  no window behind them.

- **The step-4 entry's evidence, its trade and its tag, stated precisely,
  2026-09-16.** A refinement of the entry immediately above rather than a
  revision of it: that entry landed before its review was resolved, and a
  placeholder is the only editable content an entry ever has, so what the
  review found is recorded here. Nothing below changes a value, a count or a
  conclusion above. What changes is what those readings prove, what the choice
  costs, and two things the tag paragraph left open.

  **The window evidence, re-attributed.** The entry above calls its three
  readings independent proofs that
  `[2026-09-16T00:00:00Z, 2026-09-16T00:26:04Z)` is empty. Only one of them
  proves that. The window is the 26 minutes *before* the carrying merge, and
  the run list and the `main` tip both speak to the interval *after* it. The
  reading that empties the window is the ledger grep — over `data/cases` at
  `545e26e2b`, `"stamped_at": "2026-09-16` returns **0** files, and
  `"stamped_at"` alone returns **482**, so that date grep counts over every
  stamped cell rather than missing a key name. The other two establish that
  the count is **current**: no run started after the merge and `main` carries
  no commit after it, so nothing has minted or landed since the grep was
  taken. That is the argument the entry above should be read as making.

  One reading it did not report belongs beside them, because the bless-moment
  correction reaches further back than the instant does: raising the six
  moments from `2026-09-15T00:00:00Z` to the merge would fire the
  retroactivity tripwire on any blessed-digest cell stamped anywhere in
  `[2026-09-15T00:00:00Z, 2026-09-16T00:26:04Z)`. The same grep for
  `"stamped_at": "2026-09-15` returns **0** files, so that wider interval is
  empty too; the newest stamp anywhere in the ledger is 2026-09-14.

  **What equality costs, since the entry above records only what it buys.**
  The `[bless, instant)` lane exists so a cell can run against a commitment
  already immutable on `main` and simply not count; closing it removes that
  landing place. From here a cell carrying a blessed digest with a stamp
  before the instant fails the ledger tripwire and reddens its data PR, where
  under a late instant it would have been an honestly ledgered, quietly
  uncounted cell. That is the trade
  [process-version.md](process-version.md) describes being taken in the other
  direction, taken this way here because the population it would protect is
  empty: a blessed digest cannot be stamped before the carrying merge except
  on a staging rehearsal, whose publication is fenced to prod-bound runs. The
  cost is recorded rather than left for a later maintainer to meet as a red
  data PR with no entry explaining it.

  **The tag candidate the entry above did not close.** Its placement argument
  shows that neither proc-v8 freeze commit's tree states the blessed digests
  and the instant together, but it does not reach the commit a reader looks at
  next. `689e1281f` — the digest recompute — holds the six digests this
  promotion actually blesses, beside the instant `2026-09-16T00:00:00Z`, which
  precedes the carrying merge by 26 minutes and so fails the auditor's own
  comparison: the very defect step 4 corrects. So it is not the tag's commit
  either, and the step-4 correction commit remains the first tree where
  **both** pre-registered quantities pass the audit. Two further conditions on
  the minting, neither of which that paragraph states. The tag must be
  **annotated**, carrying the pre-registration record in its message as
  [pipeline.md](pipeline.md) requires of the namespace — the one point on
  which `prereg/proc-v6` and `prereg/proc-v7` both lapsed into lightweight
  tags, which is why it is named here rather than assumed. And the deviation
  is now recorded in *Tags* as well as here: that section enumerated
  `prereg/proc-v4` as the sole exception, which this placement makes a second,
  so it names both. The entry above cites that section as asking this of *any*
  deviation; it enumerates rather than rules, and what it sets is proc-v4's
  precedent — which this follows.

  **Two claims narrowed.** The step-0 fills in the two clusters above say the
  three superseded predictor digests "never reached `main`". Since the
  carrying promotion they are in `main`'s history, inside `09395d931`. What
  the **0** counts establish is narrower, and is what the grep actually reads:
  those digests were never a live constant at `main`'s tip and appear on no
  committed cell, the `data/cases` scope being the whole of it. Separately,
  the entry above states that the promotion carrying the correction *is* the
  whole content of that batch. That is a requirement on a batch a maintainer
  composes, not a fact a record may assert in advance, and it should be read
  as the requirement. The property that matters is enforced independently:
  `test_every_enabled_actor_runs_a_blessed_process` fails if the live tree
  computes a digest the map does not hold, so a ride-along that moved a prompt
  byte reddens the promotion PR rather than silently invalidating the tag.

  **The coverage the closed window costs, and what replaces it.** Equality
  makes two live-constants window tests vacuous, and each skips rather than
  fails because both read the window off the module —
  `test_the_pending_window_prediction_is_ledgered_but_not_counted` and its
  store-side twin build a cell stamped inside `[bless, instant)`, and there is
  no such stamp to build. At the `process_version` layer the loss is nil:
  `test_a_window_cell_lands_as_shakedown_rather_than_counting` pins the same
  predicates on patched constants. At the store layer there was no such twin,
  so with `test_a_window_prediction_is_ledgered_but_not_claimable` dormant a
  regression replacing `is_frozen` in `event_has_claimable_prediction` with a
  bare membership check would have kept the suite green. This commit adds
  `test_the_claimable_gate_reads_the_instant_and_not_only_membership`, which
  patches its own window and puts one cell on each side of one instant, so the
  timing limb is pinned whatever the live constants say. Verified by mutation
  rather than by reading: dropping the timing limb from `is_frozen` reddens
  exactly that test's first assertion. Both dormant tests re-arm on their own
  at the next cutover that opens a window.

  The runnable effect check, for the promotion carrying this: `uv run pytest
  tests/test_store.py -k claimable` green with the added test running rather
  than skipped, and `uv run fedcourts process-digest --all` still printing
  `proc-v8` and the same six digests — this commit moves no constant, no
  prompt byte and no registry field, so a moved digest would mean something
  else rode along.

- **Row-blind `codex-baseline` leakage gradings read as unassessed,
  2026-09-21.** No freeze commit and no label bump: nothing here moves a prompt
  byte, a registry field, a stamp or a score. What it adds is a reading rule,
  in `metrics/README.md` (*The leakage exclusion*), for gradings already on
  the ledger. The code-mode lift bullet in the 2026-08-15 entry's rides-along
  list states that the code-mode cells committed before the lift carry no
  lifted rows and never can, that the partition holds three capture regimes,
  and that nothing in a committed artifact names the regime a cell was minted
  under. The regimes are settled here by measurement, and the first gets the
  consequence that bullet left implicit.

  **Regimes**, over every committed `codex-baseline` `retrieval_log.json` at
  `main` `a0a871953` (339 logs). *Row-blind:* `call_source` is null on every
  row of all **180** logs from runs `20260713T190721Z` through
  `20260816T173750Z`, the runs before the lift's carrying promotion
  (`promotion/2026-08-20`, merged `2026-08-20T18:13:40Z`). Those logs carry
  `exec`, `wait`, `send_message` and `wait_agent` rows; each `exec` row's query
  is the program's head slice, cut at 500 characters on 648 rows, naming a
  manifest tool on 527 rows across 127 logs, and 293 rows carry a
  `retrieved_doc_date` surfaced from the combined output — what the grader
  had, with no row per call inside the program. *Manifest-lifted:* the marker
  is set on every row of the **28** logs from `20260820T181919Z` through
  `20260825T231742Z`, the runs between that promotion and
  `promotion/2026-08-26` (merged `2026-08-26T14:46:40Z`, carrying the builtin
  lift), where a program's manifest calls have rows and its builtin calls do
  not. *Both idioms lifted:* the **131** logs from `20260827T155120Z` onward.
  No mixed log exists, so on a `codex-baseline` log the marker's absence is
  the row-blind regime's name; the other two are separated by run id alone.

  **Population.** **30** gradings of **7** row-blind `codex-baseline`
  predictions across four runs (`20260714T120628Z`, `20260716T205846Z`,
  `20260717T214313Z`, `20260816T173750Z`; ten each by `claude-judge`,
  `codex-judge` and `gemini-judge`), every one declaring `mode: forward`.
  **24** read `not_applicable` with no outcome material retrieved, none reads
  `none`, and **6** read `likely` with outcome material retrieved — two
  predictions, all three judges — so within this vintage the declared mode
  did not settle the verdict. Over those seven logs the head slices name a
  manifest tool on 9 rows and 5 rows carry a `retrieved_doc_date`. The
  manifest-lifted regime holds a further **30** gradings of **7** predictions
  (29 `not_applicable`, one `none` — the only `none` in the codex ledger), all
  forward: half-blind, since a program's shell calls, the channel most able to
  reach an outcome, have no rows there.

  **The rule.** An unsuspected verdict on a row-blind or half-blind grading is
  read as a null bit — assessed nothing, scored — never as a clean read; a
  suspected verdict stands. Six of thirty on the ledger (six of twenty-one after the run
  collapse below) is a lower bound on leakage over the vintage, not a rate. A cross-engine leakage comparison over cells before
  `20260820T181919Z` is not a comparison: `claude-baseline` and
  `gemini-baseline` logs of that vintage carry their manifest calls as rows.

  **What moves: nothing rendered.** The leaderboard and claim-score boards
  render their frozen empty state, and none of these predictions can ever
  enter them: the row-blind runs carry no process stamp or `proc-v3`, the
  half-blind ones `proc-v3` to `proc-v5`, none of them a frozen digest. The
  all-versions build is where they count — `fedcourts leaderboard
  --all-versions` reads `assessed: 183, excluded: 20` at `main` `a0a871953` — and that
  count is taken **after the run collapse**, so the ledger counts above do not
  subtract from it: of the 30 row-blind gradings, 21 survive the collapse (15
  unsuspected, 6 inside `excluded`), and of the 30 half-blind, 21 (20
  unsuspected, one inside neither). Whether `assessed` should stop counting
  the unsuspected ones moves a published denominator — to 168 on the row-blind
  cut, 147 with the half-blind cut — so it is left open here, to be decided
  with a stats review before the first leakage-conditioned figure ships.
  Either cut falls on `codex-baseline` alone.

  The runnable effect check, for the promotion carrying this:
  `grep -c "A row-blind" metrics/README.md` reads `1`, and
  `uv run fedcourts process-digest --all` still prints `proc-v8` and the same
  six digests — this entry moves no digest input.

- **A docket naming nobody but the petitioner has its staged filed-document
  text scrubbed of contact details, 2026-09-21.** A **conditioning** entry in
  the *what the pipeline provisions* class, with the properties that class
  carries: no prompt byte and no registry field moves, so no digest moves —
  `uv run fedcourts process-digest --all` at this commit is byte-identical to
  the same command on `staging`, `proc-v8` and the same six digests — and there
  is **no data-visible boundary at all**, because what a cell was provisioned
  with lives in its gitignored `record/documents/` and `prediction.json` carries
  no field separating a cell that read a signature block from one that read a
  placeholder where it stood.
  The boundary exists only here, cells minted on the affected dockets before and
  after it may not be pooled, and a stamped cell resolves to a side of it by
  asking whether its `process_version.pipeline_sha` is an ancestor of the
  carrying promotion's merge commit.

  **What changed.** `provision-snapshot` passes the filed-document text it
  stages under `record/documents/` through a contact-detail scrub before writing
  it, on every document staged for a cell whose provisioned snapshot names
  nobody but the petitioner to write to. Four shapes are replaced by
  the fixed token `[contact detail withheld]` — an email address, a North
  American telephone number, a post-office box, and a street address with any
  unit after it. Nothing else is: a docket number, a date, a reporter citation
  and a court address line written without a street number all survive. Two
  narrowings carry most of that, and both are the kind a corpus of legal prose
  forces: `Ct.`, `Pl.` and `Dr.` are absent from the street-type list, because
  in these filings those words are the institution, the plaintiff and a doctor;
  and the blank-separated telephone spelling is not read at all, because an
  appendix index and an OCR'd column emit 3-3-4 runs of blank-separated digits
  and the scrubbed population is disproportionately the scanned one — a
  narrowing that costs nothing, since it removes no match the ground-truth check
  below finds. No pattern spans a newline, so a match can never take a line
  break with it.

  The scrub is on the staged copy alone — the source PDF, the corpus row and the
  per-case content store are untouched — and each manifest entry carries
  `contact_scrubbed` (whether the scrub ran over this document's staged text)
  and `contact_replacements` (how many details it withheld), so `true, 0` stays
  distinguishable from `false, 0`.

  **What the trigger reads, and why it is not the fee class.** The docket JSON
  never says "pro se": upstream serves a self-represented party as its own
  attorney, the same name in `PartyName` and `Attorney` on the petitioner-side
  block, compared on its first and last tokens so a middle name present on one
  side only does not hide the repeat. The predicate reads that; reads a block
  served with **no** attorney the same way, which is the same fact spelled as a
  gap; and reads a `PrisonerId` on the block as a third
  arm, upstream's own positive marker for an incarcerated party writing from an
  institution — the population whose filings carry a personal address most
  reliably and whose two name fields agree on it least. Any one qualifying block
  is enough. It reads **representation**, which is not the **fee** class
  `salience`'s tier 0 excludes: that one is the docket serial, so a paid
  docket can be self-represented, and the interim, replay and evaluate lanes sit
  outside that gate entirely.

  **All three arms are read off a block the payload actually served**, and that
  bound is the registrable part. An absent or empty `Petitioner` list is
  **unknown**, not unrepresented: the snapshots key space holds two payload
  shapes and the other one, a CourtListener REST docket, carries no counsel
  blocks anywhere — it names nobody because it has nowhere to. Reading that as
  self-representation would key the scrub on a payload shape rather than on a
  fact about the docket, and would take **1,984 of the 2,925** cases below
  instead of **623** — a change to what most cells read, resting on an absence.
  So the scrub fires on evidence rather than on the lack of it, and a docket
  whose counsel the corpus does not carry stages its text as filed.

  **The population, and the route it was read by.** The blob's newest pull stamp
  is `2026-09-20` and its newest stored snapshot `2026-07-13`; the blob on disk
  is not the committed pointer's, so these are the pulled blob's figures rather
  than the committed ref's. The real predicate was run — not a
  re-implementation — over the latest stored payload of every case the blob's
  `snapshots` table holds: of **2,925** such cases, **1,562** carry a
  petitioner-side counsel block and **1,363** carry none. **623 of the 1,562**
  read unrepresented, and those 623 are the whole scrubbed population — the
  1,363 carrying no block read represented, by the bound above. **274** of the
  block-carrying cases mark an incarcerated filer, which is the arm that reaches
  a population the name comparison alone does not. Independently, over the whole
  blob rather
  than the stored payloads, **3,134** of the **16,838** SCOTUS rows carrying a
  petitioner-side entry in the normalized `counsel` list name the party as its
  own attorney — the same reading one level down, and the gradient runs the way
  representation predicts (16.1% of paid cert-form rows with a block, 39.6% of
  IFP ones).

  **What a scrubbed cell loses, run over the real text rather than argued.** All
  **1,562** block-carrying cases in the blob carry at least one of the upstream
  `Email`, `Phone` and `Address` fields on that block, which is the measured
  form of the concern: on a self-represented docket those are an individual's
  own, and the same strings are what the caption and signature block of the
  filing repeat. The scrub itself was then run — the real function, not a
  re-implementation — over every stored document of a case reading
  unrepresented: **924** documents, **389** of which had anything withheld at
  all and **535** nothing, for **1,830** replacements (657 street addresses, 612
  telephone numbers, 405 emails, 156 post-office boxes). The per-document count
  is 1 or 2 on most of the 389 and reaches 52 on a brief carrying a service list
  of firm addresses. Every match in a 100-span sample, and every street and
  telephone match in the heaviest document, is an address or a number — none is
  prose. That census is the bound on the false-positive risk, which is the risk
  that matters here: a pattern matching legal text would delete it from the
  input of the cells this exists to protect, and the manifest would report it as
  a detail withheld.

  **And what it misses, measured the same way**, because a scrub's recall is as
  registrable as its precision and a later reader must not take this entry for a
  coverage claim. The block's own `Email` / `Phone` / `Address` strings are
  ground truth — upstream's copy of what the filing prints — so the check is
  whether the scrub removes them from the staged text that contains them
  verbatim: **78 of 78** emails, **99 of 101** telephone numbers and **118 of
  147** addresses. The address misses are rural-route and highway forms, prison
  unit names, and street types outside the list; the two telephone misses are an
  international number and a separator-free digit run. What a cell loses is the
  strings that were matched and nothing else — the prose around them, the
  citations and the document's line structure survive, the last of them because
  no pattern may span a newline.

  **The staged snapshot beside it is out of scope, and that is the larger
  residual.** `record/snapshots/<date>.json` is the upstream payload verbatim,
  and every petitioner-side block in it carries `Address`, `City`, `Zip`,
  `Phone`, `Email` and `PrisonerId` as labelled keys — so on a scrubbed docket
  the cell holds, one file over and in a more quotable form, the details the
  document text no longer carries, plus a register number no shape-based scrub
  could ever match. Both files are gitignored and neither is uploaded, so the
  exposure is the one `docs/data-sources.md` already names: what a piece of
  reasoning quotes. This entry registers the boundary it moves and no more;
  closing the snapshot half is a separate change over a different file, and it
  would carry its own entry.

  **The cohort this lands over, named because it is the one in flight.** The
  long-conference cohort is the 111 SCOTUS dockets carrying a `claude-baseline`
  cell under a `2026-09-16`/`17`/`18` run id. **108 of them have no payload in
  this blob at all** — the corpus split puts snapshots in the per-case content
  store — so the reading for them is taken one level down, off the blob's
  derived `counsel` column, which is `pipeline.ingest._live_counsel`'s
  normalization of the same per-side blocks: it keeps party, attorney and side
  and **drops `PrisonerId`**, so it answers the first two arms for every cohort
  docket and is blind to the third. On that reading **21 of the 111** read
  unrepresented, every one of them a natural person listed as their own
  attorney: `scotus/73246321`, `scotus/73272489`, `scotus/73291758`,
  `scotus/73292885`, `scotus/73303792`, `scotus/73318133`, `scotus/73318742`,
  `scotus/73335108`, `scotus/73361381`, `scotus/73363408`, `scotus/73369987`,
  `scotus/73374809`, `scotus/73378855`, `scotus/73389313`, `scotus/73391039`,
  `scotus/73500218`, `scotus/73500231`, `scotus/73500232`, `scotus/73500245`,
  `scotus/73500263`, `scotus/9026000173`. Because the third arm is invisible to
  this route, 21 is a floor rather than the count. **Two** further cohort
  dockets carry no petitioner-side entry at all and are not scrubbed: they are
  the whole cohort-level cost of bounding the trigger to a served block, against
  the 88 a payload-shape reading would have swept in.

  **The expected-skill corollary, in the direction this one runs.** A
  post-change cell on an affected docket reads strictly **less** than a
  pre-change one: a placeholder where a contact detail stood. No skill movement
  is predicted, since none of the withheld shapes bears on whether certiorari is
  granted — but a movement in **either** direction across this boundary may not
  be read as a model effect. The negative form is deliberate here too: the
  design supports excluding one reading, not asserting a cause.

  **What does not move.** No base rate re-prices — `pipeline.salience` and
  `pipeline.base_rates` read no document text. No membership rule and no scored
  figure moves. `empty_text` is unchanged in meaning: it is still read off the
  stored text, before the scrub, so `corpus-info --text-coverage` keeps counting
  the same predicate provisioning stamps. Nothing is written to the corpus, so
  the blob and the content store are byte-for-byte what they were.

  **The amendment debt, smaller in kind than the selector entries above.** The
  predict prompt describes `documents.json` as listing what is present, pages
  and truncation, and says nothing about either new key or about the token a
  cell will meet in the text. The prompt is frozen bytes, so the reading rule
  rides the next re-bless, alongside the two `record/documents/` rules already
  owed. It carries **no ordering constraint**: a cell meeting the token loses
  nothing it could have acted on, and the worst it costs is a `data-quality`
  flag spent accounting for a placeholder — unlike the merits-brief debt above,
  where the prompt tells a cell something about its record that is false.

  The runnable effect check, for the promotion carrying this: `uv run pytest
  tests/test_documents.py tests/test_cli_provision.py` green, and `uv run
  fedcourts process-digest --all` still printing `proc-v8` and the same six
  digests — this commit moves no constant, no prompt byte and no registry field,
  so a moved digest would mean something else rode along. The scrub's own effect
  is read on the first cell provisioned from a docket naming no petitioner-side
  counsel: the provisioning step echoes `contact scrub: N detail(s) withheld
  across M staged document(s)` to the run log, and
  `record/documents/documents.json` carries `contact_scrubbed: true` for every
  staged document of that cell with a non-zero `contact_replacements` on the
  ones whose filing carried details. The log line is the surface a pathological
  count would be visible on, the manifest being gitignored with the rest of
  `record/`.
