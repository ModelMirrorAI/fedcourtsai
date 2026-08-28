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
commit and date, and the promotion-time re-run of step 0's stamped-cell grep —
so it carries them as explicit `<FILL: …>` placeholders, and those placeholders
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
  <FILL: promotion tag> (merge commit <FILL: merge commit>, merged
  <FILL: merge timestamp>). No freeze procedure fills those three: the freeze
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
