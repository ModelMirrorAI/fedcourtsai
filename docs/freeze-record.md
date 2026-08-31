# Freeze record

The append-only record of process-version freezes and their supersessions, of
the **masking-surface** changes that move what reaches an evaluator's
information set under an unchanged digest, of the **scoring-baseline** changes
that move a measured number the same way, of the **provisioning cutoff** that
moves what a predictor is conditioned on, and of the boundaries a published
figure may not be pooled across.

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
  with it: the raw figures (n = 13,341; **+0.146pp** raw and as-published,
  since the statpack always read the stored weights) are the registered
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
  to 5.4pp. Provenance confirms the class: `capital_case` latches from the
  upstream boolean as well as the number parse, so the flag never attributed
  a stored weight to a defeated parse, and the blob — read after the
  normalization pass the parent entry named as owed converged the 462 marked
  spellings into the latched flag — holds no word-marked asterisk spelling
  at all (7 asterisk rows corpus-wide, every one a circuit-court row, none a
  SCOTUS marking). The repo's standing invariants said so independently — the
  budget's paid-census note, and the caption and distribution censuses, which
  raise on any scored-segment row with `sample_weight != 1`. Evidence read
  from the blob pulled 2026-08-31 (newest stored snapshot 2026-07-13).

  **What this entry changes and what it leaves.** The withdrawal corrects a
  *projection* the capital-marking entry published beside its registered
  figures; the entry's registered raw deltas, its scored-segment
  re-partition, and its pooling rule are untouched. No counted figure moves:
  the stored weights were right all along, and every committed board already
  read them. The rule's latent over-derivation — the probed-vs-kept gap,
  which `backfill_live_signals`'s NULL-only predicate scoped correctly by
  accident — remains open in code; the code half of this correction is owed
  separately: extract the rule as a named function and guard it on density
  (a denial with an off-grid live-slice sibling in its own (Term, stream)
  cell is in an enumerated range and stays at weight 1).
