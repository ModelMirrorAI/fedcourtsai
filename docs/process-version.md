# Process versioning: which predictions count toward the headline

Predictions committed during the shakedown are real, timestamped
forward calls — irreplaceable forward-stratum data — but they ran under a process
still being corrected. The headline metrics must reflect only a **blessed**
process, counted inside its own **counting window**, without deleting the
shakedown runs (a wipe reads as hiding
results, not rigor). This is the same doctrine as [`sal-v4`](salience.md): a
process change is a **new version**, never an in-place edit, so any past ranking
always replays against the process that produced it.

## What a "process" is, and how it is identified

The process behind one predictor cell is its **prompt template plus the resolved
configuration it ran under** — the engine, the resolved model (the registry
override, else the engine default), the pinned MCP tool manifest, and the
engine's retrieval surface (what a cell can reach beyond the snapshot: the open
web, and for codex the subprocess-network grant). A cell that can reach the open
web answers from a different information set than one that cannot, so the
surface is a process input as much as the model is. The harness stamps each
`prediction.json` / `evaluation.json` with a `ProcessVersion` carrying:

- **`digest`** — a `sha256:` content hash of exactly those inputs (the prompt file
  bytes plus the canonical resolved config). This is the identity that matters:
  the frozen/shakedown partition keys on the digest, so a silent prompt or config
  change is automatically a distinct version. Two predictors that share a prompt
  but differ in model are different processes — different digests.
- **`label`** — a human-readable name (`proc-v1`), sugar for a digest. Never the
  partition key: two different processes cannot hide behind one label, because
  the digest gives them away.
- **`pipeline_sha`** — the checkout commit, as provenance only. It is deliberately
  **not** part of the digest: the commit changes on every unrelated pipeline edit,
  and folding it in would break the frozen set every time predict/evaluate resume
  at a newer HEAD. The digest captures what *defines* the process; the sha records
  which commit *ran* it.
- **`stamped_at`** — when the harness stamped the cell (UTC, timezone-aware).
  Provenance, and — with the digest — the frozen/alpha partition's time key:
  the digest says *which* process ran, the stamp says whether it ran inside
  that digest's counting window. The runner clock is the witness that a run
  postdated the commitment — acceptable because the agent cannot write this
  field, and bounded independently by the workflow run's own timestamps and
  the data commit's date on `main`. A naive value has no defined order
  against the instant and reads as pre-freeze.

The digest excludes documentation that does not change behaviour — the actor's
`description` and the MCP manifest `description` are comments, not process inputs,
so editing one does not re-version anything.

### Harness code is outside the digest, and one case of that has teeth

Everything the harness *does* around the agent rides `pipeline_sha`, not the
digest — deliberately, since otherwise the frozen set would break on every
unrelated pipeline edit. Usually that is harmless: a change to how usage is
totalled or how a log is captured does not change what the agent was answering
from.

**Blind grading is the exception worth naming.** The evaluate cell stages each
prediction under an opaque alias with its identity masked
(`fedcourtsai.blinding`, `docs/outcome-decomposition.md`), and *what gets masked*
is a property of that code, not of the prompt or the registry. So changing the
masking surface — staging a file that was dropped, dropping one that was staged,
widening or narrowing the scrub — changes the evaluator's **information set**
under an unchanged digest. Two evaluations can carry the same digest and have
been formed from different inputs, which is exactly what the digest exists to
rule out. What the harness takes *off* disk counts identically: the cell hides
the committed `predictions/` and `evaluations/` trees for the duration of the
run (`fedcourts hide-cell-record`) and deletes the labeling oracle beside them,
so which directories those steps name — and whether they run at all — move the
information set the same way the mask does.

The discipline that follows, since the mechanism cannot enforce it: treat a
change to the masking surface as a process change even though nothing
re-versions. Land it with the prompt edit that describes it — the prompt bytes
*are* hashed, so a masking change stated in the prompt moves every evaluator
digest and the boundary becomes visible in the data. A masking change made
silently, without a prompt edit, leaves no boundary at all and is the one shape
to avoid; if it is unavoidable, it belongs in a `label` bump and in the freeze
record, not in a commit message alone.

One case the discipline does **not** cover, because it is not a code edit at
all: the scrub reads the live registries and one candidate is staged per
registered predictor, so **adding or retiring a predictor changes every
evaluator's information set** — a different scrub-term set and a different number
of candidates — while moving no evaluator digest, since an evaluator's canonical
config carries no predictor list. That is a routine operation with no boundary
behind it. Until the masking surface is folded into the evaluator's canonical
config (which would make it a partition key rather than an honour system), a
registry change that alters the candidate set belongs in the freeze record
([freeze-record.md](freeze-record.md)) beside the masking changes.

The **scoring baseline** is a third member of this list, and one of two with
no data-visible boundary at all. Skill numbers are computed against the
salience-band base rates, and the lookback window that builds them
(`base_rate_lookback_terms` in `config/tracking.yaml`) sits in no actor's
canonical config and is recorded in no artifact field — moving it re-bases
every forward skill number and every backtest per-band skill at once, under
unchanged digests. **Who** computes a scored number sits outside the digest for
the same reason — and the rule covers the numerator as well as the baseline it
is scored against: on the merits and interim stages the rate, the Brier, and
the skill over them are all stamped from harness code rather than computed by
the evaluator, and on **every** stage so is `correct` — the accuracy column's
per-cell bit, which needs no pooled baseline and so takes no cert exemption. A
change there moves how a number was produced without moving
any actor's digest, and belongs in the freeze record beside the window. This is
the standard's own trigger case rather than an aside: the same prompt, the same
definition, the same digest, a different author for the number. The
quantity itself is unchanged in every such move — the harness computes what the
prompt defined — which is exactly why no digest moves and why the freeze record
is the only place the change is visible. (The salience *version* does have a boundary:
`context.salience_version` and the pack's `base_rate_salience_version` make a
per-version cut visible in the data, and the **distribution parse** rides that
boundary rather than needing its own, because a version pins exactly one parse —
`sal-v3` and `sal-v4` differ in nothing else, so the version field *is* the parse
field. What has no boundary is the corpus `distribution_count` column the parse
re-derives: an outcome's signals block records a count and not the reading that
produced it, so a claim resolved across a re-derivation is comparing two readings
with nothing in the artifact to say so. That belongs in the freeze record too.) The pre-registered baseline is therefore
the whole tree at the `prereg/<label>` tag — lookback window included — and a
later window change belongs in the freeze record
([freeze-record.md](freeze-record.md)) beside the masking changes, never in a
commit message alone.

The **provisioning cutoff** is the list's predictor-side member: where a cell's
event declares a moment, provisioning places the cell at that moment
rather than at the corpus's latest snapshot, which moves what the predictor is
conditioned on without touching a prompt byte and so without moving a digest.
It does carry a data-visible boundary — `context.cutoff`, non-null exactly on a
placed cell — so the placed/unplaced transition is separable in the record
rather than pooled silently, which is the property the scoring baseline lacks.
The visibility stops there for a change of cutoff *value*: on an already-placed
cell that leaves `context.cutoff` non-null on both sides, so nothing in the
artifact separates the two conditionings, and the freeze-record entry
registering such a move must itself carry what makes the affected set
reconstructable — the moved rows or a pointer that re-derives them. It belongs
in the freeze record on the same terms as the rest.

A change to the *rule* that bounds the entries inside the cutoff is separable
**where it mints a new value of the field that names the rule** — and only there.
`context.cut_kind` names the rule
— `date`, everything filed strictly before the cutoff, or `arrival-position`,
that rule and a stop at the docket entry which opened the event — and
`cut_anchor_index` locates the boundary the second one takes. So the interim
arrival moment's two conditionings are distinguishable in the record rather than
pooled behind one date, which is what makes such a move registrable by freeze
record alone; a move that left the artifact byte-identical would not be. The
same field is what the replay leakage clock reads, so a boundary tighter than
the cutoff cannot be graded under the looser rule.

Two limits on that, both of which a later entry must check rather than assume. A
redefinition of what an *existing* value means — moving where `arrival-position`
stops, rather than adding a kind — leaves the artifact byte-identical on both
sides, which is exactly the shape the cutoff-value paragraph above refuses; it
is registrable only on those terms, carrying what makes the affected set
reconstructable. And the *earlier* arm of the first such change carries no
positive marker: cells provisioned before the field existed have no `cut_kind`
at all, so the split is `absent` → the new value, and reading the null arm means
knowing that a non-null `cutoff` with no `cut_kind` on an interim arrival event
is the older conditioning. Registering the move is still
required: separability says a reader *can* split the two populations, not that
any published figure has.

**What the pipeline provisions** is the fourth member, and the second with no
data-visible boundary. A change to which filed documents `select_documents`
nominates moves what a cell reads — a widened selector hands it a primary
document a cell before it did not have — under an unchanged digest and with
nothing in the artifact to say so: the documents live in the cell's gitignored
`record/documents/`, and `prediction.json` carries no field separating a cell
that read its petition from one that did not. It is therefore the same shape as
the scoring baseline and takes the same remedy, which is the only one available:
a freeze-record entry, since the record is the only place the boundary can
exist.

A **membership rule** — which cells a published figure is computed over — is the
list's last member and the one that moves no value at all. The scoring funnel's
exclusions live here: the forward-claim rule and the leakage bit
(`metrics/README.md` registers both), each of which drops a cell from every
scored aggregate under unchanged digests, since nothing about which cells count
sits in an actor's canonical config. Two boards built either side of such a rule
are over different populations, which is as unreadable as two built either side
of a re-basing, so a membership rule belongs in the freeze record for the same
reason the baseline does. Its own boundary is the published exclusion block —
`forward_claim` / `leakage_exclusion` on every board — so, like the provisioning
cutoff and unlike the baseline, the change is at least visible in the artifact.

## The stamp is the harness's word, not the agent's

The agent writes `prediction.json` / `evaluation.json`; a post-agent step
(`fedcourts stamp-cell`, in both `run-predict` and `run-evaluate`, before
`validate`) reads that file and injects the `ProcessVersion` derived from the
registry. So a cell's version is what the harness resolved at run time, exactly
as `usage.json` records the engine's own log rather than trusting the agent — a
compromised or hallucinating agent cannot fake its process version. The same
clock discipline reaches past the freeze: the forward/retrospective stratum
boundary keys on the cell's harness clock (`fedcourtsai.integrity.cell_clock`
— the stamp's `stamped_at`; an unstamped **shakedown** cell falls back to its
agent-written `created_at`, safe exactly because an unstamped cell can never
be frozen), so no pre-registration boundary anywhere rests on a clock the
agent controls.

The stamp step is deterministic and local, so unlike the best-effort log
captures beside it, it is **must-succeed**: a missing artifact (a no-output cell)
is a clean no-op, but a registry/prompt inconsistency fails the cell rather than
shipping an unstamped-but-frozen-looking prediction, as does an evaluation
recording a `risk_set` base-rate basis whose salience version does not resolve —
a basis is only readable beside the version it was banded under. An evaluate cell
scores every predictor, so the evaluator stamp covers all of its
`evaluation.json`.

**On a predictor cell the stamp also judges its own copy.** The `context` block
it writes is the provisioned conditioning, which reads as an assertion that the
forecast was formed from the provisioned snapshot; the cell's `input_snapshot`
is the only record of whether it was. Where the two disagree — both normalized
to the provisioned file's day — the stamp records `context.snapshot_uptake`
`unread` and writes a `flags.json` note beside it.

This belongs on none of the lists above, and the reason is worth stating,
because a change to what the harness stamps is exactly the shape they cover. It
adds a field and changes no other byte of the block, so no scoring surface reads
anything it did not read before: no claim's resolvability moves, no base-rate
basis moves, no cell enters or leaves a published population, and no committed
cell is re-stamped. That is what separates it from a masking change, which moves
an information set, and from a membership rule, which moves the population a
figure is computed over. The digest is untouched for the ordinary reason — the
prompt bytes and the resolved registry config are what it hashes. The restraint
is the point: degrading the block instead would have moved a scored number,
which is what would have put this in the freeze record.

**On an evaluate cell the stamp runs after un-aliasing, and the order is not
interchangeable.** The stamp joins each evaluation to the prediction it scored on
the `predictor_id` field, so under a blind-grading alias the join simply misses
and the cell's `claim_scores` block is *silently* absent rather than wrong —
`base_rate_salience_version` too, except where the evaluation records a
`risk_set` basis, which fails the stamp rather than losing its version half —
and, on an interim cell, the harness-stamped `segment_base_rate`, whose
application Term is read off that same prediction. On **both** stamped stages it
also costs the harness-stamped `brier_score`, which needs that prediction's
`probability`, and the skill derived from it: that is the expensive one, because
a null `brier_score` drops the cell from the leaderboard outright rather than
merely leaving a field empty. Not silent, at least — the discard warning fires
where the evaluator wrote a number of its own. So
`fedcourts unblind-evaluations` runs first, then `stamp-cell`, then `validate` —
whose `check_evaluation_targets` resolves the same join and is the loud backstop
for an alias that survived.

### Re-grading a corrected outcome keeps the producing run's stamp

An evaluation grades a prediction against the **committed outcome**, so
correcting an outcome — a disposition relabelled, a judgment fixed — leaves
every evaluation that read the old one recording a stale `correct`, claim
block, and skill record. `stamp-cell --regrade` recomputes exactly those
harness-owned fields and writes them **without** `process_version`: the
committed stamp survives byte-identical, `stamped_at` included.

That is the whole of the design, and the reason is pre-registration. Every
field a re-grade touches is a function of the committed artifacts alone —
recomputing it says nothing about who computed it. The record's *prose*, and
the judgment the numbers sit beside, were produced by the process the stamp
names; a bare re-stamp would move a proc-N artifact's label to whatever the
registry resolves at re-grade time, attributing an older process's work to a
newer pre-registration and silently moving cells across the frozen/alpha
partition the label keys. So the correction changes the record's inputs, not
its attribution. A re-grade therefore **requires** a record that already
carries a stamp — a never-stamped cell has no attribution to preserve and
takes the ordinary stamp — and it refuses `--role predictor` (a prediction
carries no harness-graded field) and `--stamped-at` / `--pipeline-sha`, which
set only the version it declines to write.

Two senses of "re-grade" meet here and must not be confused. The flag is an
in-place **recompute** of the harness-owned fields on the records that exist,
under the stamp they already carry. The sense the leaderboard's collapse counts
— a second `evaluation.json` from a new evaluator run, which supersedes the
first and shows up in `superseded_gradings` — is the route for a changed
*judgment*, and it is the only one of the two that is a second observation.
An outcome correction is not a changed judgment, and minting a run for it would
fabricate an observation; a changed rubric is not an outcome correction, and
recomputing in place for it would rewrite a standing invisibly. See
`metrics/README.md`.

The decisive argument against minting a run for a correction is this page's
subject rather than the collapse's: a genuine evaluator re-run resolves a
**current** stamp. Its `stamped_at` is now — on the far side of `FROZEN_SINCE`
— and its digest is whatever the registry resolves today, so the cell lands in
a pre-registration cohort it was never produced under, and a correction to
ground truth has been recorded as a change of process. Preserving the stamp is
what keeps the two kinds of change distinguishable in the record.

**A re-grade re-prices against today's pools, deliberately.** The recomputed
`claim_scores` and skill fields are pooled from the statpack and salience
config committed at re-grade time, which may have moved since the stamp — so
the preserved stamp bounds the block's vintage from below rather than pinning
it (`fedcourtsai.integrity.evaluation_clock`). That is the honest choice, and
it is the ordinary stamp's own rule: a harness field is a function of the
committed artifacts *as of the invocation that writes it*. Reconstructing a
stamp-vintage pool would price a corrected outcome against a pack that never
saw the correction — a number matching neither the record it replaces nor
anything a reader can rebuild. The comparability that costs is the operator's
to keep: **re-grade a whole cohort against one committed statpack**, never a
cell at a time across a moving pack. That discipline buys internal consistency
for the set re-graded and nothing wider — the ledger's blocks already spread
across pack vintages from one run to the next, which no re-grade widens, and
the realized-Term column is immune either way, being built from a single
handed-in pack.

Re-grade **every evaluator on the event**, not one. `validate`'s
`evaluation_correct_agrees` collapses to the latest runs and requires the
evaluators to agree on `correct`, so a half-re-graded event fails the ledger —
the check doing its job on a genuinely inconsistent state, not an obstacle to
route around. Read its reach in `metrics/README.md` before relying on it: it
holds the `correct` bit only, and only where two or more evaluators left
stamped gradings of the same cell.

Three more refusals, all judged before the first write so a refusal cannot
leave an event half corrected. **No artifact at all** exits non-zero, unlike
the ordinary stamp's no-op: a re-grade's coordinates are typed by hand, so a
mistyped run id must not read as a correction that landed. A **superseded
run** is refused with the surviving run named, since every scoring surface
collapses to the newest and recomputing the loser moves nothing. And a cell
whose **evaluator-owned Brier trio no longer reproduces** against the corrected
outcome is refused rather than half-corrected: on the stages where the Brier,
the segment base rate, and the skill stay the evaluator's arithmetic, a
correction that moves the outcome's binary would otherwise leave `correct`
recomputed beside a trio scored against the superseded one — the leaderboard
drops that cell from `skill_scored` while keeping it in accuracy, so the two
columns would run over different populations. The remedy is the one the
mispaired-basis guard already names: null the four together, or commit a
re-derivation, then re-grade.

Each target's process scope is echoed as the re-grade goes — `frozen` or
`alpha`, with the label it preserved. Since the operation leaves no
`superseded_gradings` trace, that line is the published-record annotation for a
frozen-scope re-grade: it puts the fact that a claimable cell moved into the
writer run's log and step summary, where it stays greppable without a schema
field or a walk through `data/`'s history.

## Three states: shakedown → not-yet-frozen → frozen

`fedcourtsai.process_version` holds three constants. `FROZEN_PROCESS_DIGESTS`
is the blessed map — the current label's digests, each carrying the instant it
was blessed, the retroactivity record. `FROZEN_SINCE` is the current label's
counting instant. `COUNTING_WINDOWS` is the counting rule itself: one
**window** per blessing of a predictor digest, running from the counting
instant of the label that blessed it until the counting instant of the
successor that stops blessing it (`closes`, null while open), each instant as
its `prereg/` tag records it. Evaluator digests have no window — an evaluator
digest records and never partitions. The labels before `proc-v8` are not
windows: their digests were de-counted under the rule in force when each was
superseded, and stay de-counted. A cell is in one of three states:

- **Shakedown** — a cell written before the stamp existed carries no
  `process_version`. It is never frozen (an absent stamp is in no window), so
  the whole shakedown ledger drops out of the headline for free — no backfill,
  no deletion.
- **Not-yet-frozen** — a stamped cell no counting window contains: a digest
  no window names, or a stamp before its digest's window opened (or at or
  after it closed). Until some stamped cell sits in a window, the frozen
  headline is legitimately **empty** — "no frozen-process evaluations yet" —
  which the leaderboard, the ops report, and the weekly performance digest all
  say in as many words, rather than showing a bare `0` that reads as a
  regression.
- **Frozen** — a stamped cell whose digest has a window containing its stamp,
  and whose window no revocation has de-counted (`is_frozen`). The digest is a
  pure content hash — it says *which* process ran, never *when* — so without
  the window's opening instant, a shakedown run of the very bytes later blessed
  would read as frozen retroactively. Pre-registration means the commitment
  preceded the run; the time cutoff is what says so.

**One counted forecast per predictor and event: the earliest window's.** A
frozen cell is its predictor's *counted* forecast of its event
(`counted_on_event`) unless the same predictor holds a frozen cell on that
event from a window that opened earlier — through a named dispatch, or an
attempt still open at a successor's instant. The earliest window's cell counts
and a later window's counts in no window. "Earliest" is read over windows that
still count: where the earlier window was revoked, a later-window cell stamped
before the revocation stays uncounted and only a forecast made after it can
count, so a revocation never decides which existing forecast is scored. Within
one window the run collapse picks the counted cell among that window's runs,
exactly as it does with one window.

**A grading is gated on its prediction's window.** An evaluation counts where
its own harness stamp is at or after the instant that opened the graded
prediction's window (`graded_in_window`) — not a successor's later instant, so
the gradings a closed window's cells collect after the successor froze count
wherever that instant falls.

**No figure pools windows.** A new model under an unchanged `predictor_id` is
a different forecaster, so every frozen-scope figure is per predictor *and*
window, published under the window's `label` (`process_window` on each board
entry and export row, and the whole registry in each artifact's
`frozen_process.windows`). Every frozen-scope aggregate keys on `predictor_id`,
so the shared stratify pass refuses a ledger in which one predictor's
in-scope cells span two windows rather than average them as one series, and
the big-case agreement does the same; the dataset export, which is per row and
names each row's window, is the one reader that takes such a ledger. Building
per-window strata for those aggregates, and any named cross-window view, is
the work a successor waits on (the next section). A cross-engine comparison is
read only over events on which every compared engine holds a counted cell,
each from one named window; an event split across a closed window and its
successor belongs to no complete grid.

### Two boundaries, two jobs

The freeze commit sets two moments, and conflating them costs a claim in one
direction or a false alarm in the other:

- The **bless moment** — a digest's value in `FROZEN_PROCESS_DIGESTS` — is
  when that process's bytes became immutable on `main`: the merge time of the
  promotion that carried the freeze commit naming it
  (`git log -1 --format=%cI <carrying merge>`), so any auditor can re-derive
  every entry from git. It is the **retroactivity** boundary. A cell stamped
  before it ran against a commitment that could still be edited, so the digest
  was applied to it backwards — retroactive blessing, which nothing licenses,
  and which the ledger tripwires in `tests/test_process_version.py` catch
  over **predictions and evaluations alike**: each half of the ledger is
  walked against its digests' bless moments, so a stamp before its bless
  fails the suite on either side.
  A digest carried forward byte-identical from an earlier label keeps that
  label's bless moment: those bytes have been immutable since then.
- The **counting instant**, `FROZEN_SINCE`, is when the current label's
  cells start counting — it opens every window the label newly blesses — and
  it is deliberately guessed *late* (step 2 below). Cells minted
  in the window between the two — a live-channel cell queued before the
  instant, say — land honestly in the ledger and are de-counted on timing
  alone by `is_frozen`. That is shakedown, not retroactivity, and the trade is
  one-sided on purpose: an instant guessed late costs a few uncounted cells,
  while an instant guessed early blesses runs made while the constant was
  still editable.

So a stamp in `[bless, instant)` passes the tripwire and fails `is_frozen`
(`graded_in_window`, on the evaluation half), which is exactly the intended
reading. The instant sits at or after every bless moment, on an invariant the
suite holds: no predictor digest may be blessed after it, and on a full freeze —
one moment across the whole map — the instant is at or after it. One shape
inverts that: the held-instant evaluator re-bless below leaves the instant
*before* the newly blessed **evaluator** entries' bless moment. That inversion
opens a real gap rather than a harmless one — an evaluation stamped in
`[held instant, new evaluator bless)` passes `graded_in_window`, which tests timing with no
evaluator-digest limb, and so counts under a rubric not yet immutable on `main`. While
that window is open, nothing mechanical holds it shut: the evaluation
tripwire cannot see a digest the map does not yet hold, so what keeps the
gap empty is that cells are minted from `main` — nothing can carry the new
evaluator bytes before the promotion lands them — an audited convention,
not an enforced invariant. What the tripwire adds is detection from the
bless moment on: once the promotion lands the digest, any cell stamped in
the gap reddens the suite, so a violation of the convention is caught at
the re-bless instead of resting on a maintainer's grep.

## What defaults to frozen, and what stays version-blind

The frozen filter lives at the one shared producer both surfaces read
(`store.stratify`, `frozen_only=True` by default — the boards call it directly
so the scored cells and both exclusion
records — `forward_claim` and `leakage_exclusion` — come from one
pass; `iter_stratified_evaluations` is its thin cells-only wrapper), so the
leaderboard headline and the ops report's scored figures can never disagree —
they each pass one boolean. Both CLIs take `--all-versions` for the pooled
shakedown view. The filter partitions on the **prediction's** stamp — the
competitor being ranked is the predictor, and the scored prediction must be its
counted forecast of the event — and additionally requires the evaluation's own
harness stamp to be at or after the instant that opened that prediction's
window (its digest is recorded but not enforced), so a shakedown grading
cannot ride a frozen re-run of its event into the headline.

Three things default to all-versions on purpose, because they are censuses and
diagnostics rather than the headline. The first two admit no other scope; the
third offers a frozen build alongside, and says why that build is not the one
published:

- The **prediction census** (`ledger_cell_counts` — how many predictions and
  events the funnel has) counts everything committed. A frozen scope showing many
  predictions but zero frozen evaluations is the honest shakedown state, and the
  ops report labels that divergence rather than hiding it.
- The **leakage digest** counts every evaluation carrying a leakage grade,
  frozen or not. Shakedown contamination is exactly what it exists to surface, so
  scoping it to frozen-only would blank it during the window it matters most —
  the same posture as the flags and tooling digests beside it.
- The **big-case board** (`metrics/big-cases.{json,md}`) pools every version by
  default, unstamped cells included, and carries a `frozen` **comparison scope**
  beside it (`fedcourts big-cases --process-scope frozen`). It publishes what the
  panel said about a case's stakes, not how well it said it — a stakes read
  resolves against nothing, so there is no performance claim for a partition to
  protect. The default stays all-versions because scoping it does not thin the
  board evenly: a resolved case is never re-predicted, and the re-predict rule
  re-owes only the cert distribution, the CVSG and the three interim moments, so
  a case sitting at a cert arrival moment or at either merits moment is never
  refilled either. The frozen build is therefore a live-cert-and-interim slice of
  a selected population rather than a smaller copy of the whole, which is a
  legitimate thing to look at and the wrong thing to publish as the census. Both
  builds stamp `process_scope` and the `frozen_process` record they key on, the
  frozen one publishes its hold-out as `cases_out_of_scope`, and the artifact's
  own scope-aware `version_scope` and `population` provenance strings say which
  population the reader has — because the surrounding boards' frozen default
  makes the other reading the available one. `process_label` on either build is
  what a prediction minted today would stamp and is a filter on nothing.

The generic back-test is process-independent (it replays reference baselines, not
the tournament predictors), so it carries no process version.

## Freezing: the cutover procedure

The freeze centers on a deliberate, reviewable **two-constant commit**, made
when the process is settled and the first frozen predictions are about to
land; recording and tagging that commit complete the procedure:

0. Confirm no stamped cell already carries a digest you are about to bless.
   Grep `main` for each one — `git fetch origin main && git grep -l
   '<digest>' origin/main -- data/cases | wc -l` must be 0 per digest —
   because data commits land there directly and never ride `staging`. (The
   unscoped form, `git grep -l '"process_version": {' origin/main --
   data/cases`, counts every stamped cell in the ledger and is the wider
   census the freeze record reports beside it; the object form, because a
   rewritten cell can carry a `"process_version": null` key without a stamp.
   Stamped cells under *superseded* digests are the ordinary ledger, not a
   finding.) A **prediction**
   carrying a to-be-blessed digest is retroactive blessing by construction: it
   ran under bytes that only this freeze makes immutable, so it necessarily
   predates the digest's bless moment, the tripwire fires on it, and the
   freeze commit cannot land green — which makes this step a precondition
   rather than a note. An **evaluation** carrying one fails its own tripwire
   the same way, so both halves are preconditions the suite enforces — at
   the promotion PR, whose merge-preview checkout holds `main`'s ledger; a
   staging run walks a ledger that lags it, which is why the grep targets
   `origin/main`. Record what the grep found in the freeze record either way,
   and **re-run it at promotion time**, since cells land continuously and the
   authoring-time check can go stale.
1. Read the current digests: `fedcourts process-digest --all` prints the label,
   role, id, and digest of every enabled predictor and evaluator.
2. Paste the digest(s) to bless into `FROZEN_PROCESS_DIGESTS` in
   `src/fedcourtsai/process_version.py`, set `FROZEN_SINCE` beside it — a test
   pins that the two move together — and edit `COUNTING_WINDOWS` to match:
   append one window per newly blessed **predictor** digest, labelled with the
   new label and opening at the instant, and set `closes` to the instant on
   every window whose digest this label stops blessing. Never delete a window:
   a closed window's cells keep counting, and a test fails the suite if a
   `proc-v8` predictor digest leaves the registry without a close. Each digest's value is its **bless
   moment**, which is not known yet at this step: it is the merge time of the
   promotion that will carry this commit, so write a placeholder here and
   correct it at step 4 against the merge that actually landed. **Guess this
   one early** — this commit's own date is the safe floor, since the carrying
   merge is necessarily at or after it — because the two forecasts want
   opposite directions. A bless moment left forecast *late* fires the
   tripwire on every honest cell minted between the real merge and the
   correction, reddening `main`'s data PRs; forecast early it merely fails to
   catch a retroactive cell that step 0 already proved does not exist. A
   digest carried forward byte-identical from the prior `prereg/` tag keeps
   that label's bless moment verbatim — copy it across rather than re-dating
   it.

   The instant is the other direction. It must be **at or after the moment the
   commitment becomes immutable on `main`** (the promotion merge that will
   carry this commit) and before the first run you intend to count. Choosing
   it generously late errs conservative: whatever runs between that merge and
   the instant lands in the ledger as shakedown, honestly stamped and simply
   uncounted, while an instant before the merge would bless runs made while
   the constant was still editable. The promotion date is a forecast here
   too — for the instant, guess late. Late is safe on retroactivity, which is
   why it is the direction to guess, but it is not free: a cell minted in that
   window carries a blessed digest and still fails `is_frozen`'s time limb, so
   the pre-freeze re-predict rule re-owes its event and the round is paid for
   twice. Where the merge is known before the instant must be — a correction
   at step 4, or a freeze whose promotion has already landed — the merge's own
   instant is the value that satisfies the rule and leaves no gap at all.
3. Commit. Because the digest excludes `pipeline_sha`, the blessed map survives
   unrelated pipeline commits — predict/evaluate can resume at a newer HEAD and
   still match.
4. Once the promotion carrying the commit lands on `main`, **record the bless
   moment and verify the instant before minting anything immutable**. Read the
   carrying merge's date once — `git log -1 --format=%cI <promotion merge>` —
   and use it twice. First, write it as the value of every digest this commit
   *newly* blesses in `FROZEN_PROCESS_DIGESTS`, replacing step 2's forecast
   (carried-forward digests keep their earlier bless moment); the ledger
   tripwire reads these, so a forecast left uncorrected either fires on honest
   cells or lets a retroactive one through. Second, the instant: the literal
   in the file must be at or after that same date. The windows move with it:
   every window this label opens opens at the instant, and every window it
   closes closes there too, so a bumped instant is bumped in all three places —
   a test holds every `closes` to some window's `opens`.

   The two corrections travel differently, because only one of them is a
   pre-registered *choice*. **The instant is**, so an instant that came in
   early must be bumped in a follow-up promotion landed **before** tagging —
   the `prereg/` namespace blocks update and deletion, so a tag minted over a
   bad instant burns the label. **The bless moment is not**: it is a fact
   about git that the constant merely restates, and it cannot be in the tagged
   tree at all when the tag sits on the freeze commit, since the merge that
   establishes it has not yet happened. So what must be right before tagging
   is the *record*: the freeze-record entry carries the git-verified bless
   moment and the `git log` command that yields it, and the constant's
   correction rides the ordinary next promotion. What the tag pre-registers is
   the blessed digests and the instant. (One label shape is
   audited differently: an
   evaluator-half re-bless that deliberately holds the instant — the second
   supersession note below — replaces this date comparison with the
   predictor-digest byte comparison, and its gap check covers only cells
   stamped under the *newly blessed* digests, which step 0 proves are none.)
   On a slip — an instant that fell *before* the carrying merge — a cell
   stamped in the gap would read as frozen although it ran while the constant
   was still editable. Recording the true bless moment catches that
   mechanically on **both halves**: such a cell predates its digest's bless
   and its ledger tripwire fires on it, prediction and evaluation alike.
   (`graded_in_window` still tests timing with no evaluator-digest limb — a
   gap cell fails its tripwire even where that filter would count it.) Bump past
   anything the tripwires find. Only then record the commit as the cutover in
   [freeze-record.md](freeze-record.md) and tag it `prereg/<label>`
   (e.g. `prereg/proc-v1`): an annotated tag in the `prereg/` namespace the
   *Tags* section of [pipeline.md](pipeline.md) describes, protected against
   update and deletion so the freeze point stays findable and immovable. The
   after-the-fact auditor's check is the same comparison, against the
   promotion that carried the freeze commit to `main`:
   `git log -1 --format=%cI promotion/<YYYY-MM-DD>` — the literal in the file
   must be at or after that date. Name the tag pointing at the **carrying
   merge itself** (a same-day second batch carries a `-2` suffix, and the
   bare date resolves to the earlier, weaker comparison). (`prereg/<label>`'s own tagger date is not
   the witness: the tag is minted after this check, so it may legitimately
   fall on either side of a correctly chosen instant.)

From that commit forward, the first long-conference prediction lands under the
stamped, frozen process and the headline fills in. When the process later changes
materially, bump `CURRENT_PROCESS_LABEL` to the next label; the old label's cells
keep their stamp and remain replayable against the process that produced them,
never overwritten.

**Re-freezing with nothing counted under the prior label** is a supersession,
not an extension: the new freeze commit *replaces* the superseded label's
digests in `FROZEN_PROCESS_DIGESTS` (the map holds one blessed process per
actor) and closes their windows at the new instant, exactly as the third shape
below does — here the closed windows simply hold no cell. The procedure above runs in full
for the new label — including step 0's grep, which is what proves the
supersession de-blesses nothing — and the freeze record in
[freeze-record.md](freeze-record.md) must state the count of cells ever stamped
under the superseded label (zero, or listed). The superseded `prereg/` tag
stays: the namespace blocks deletion, and the tag remains the honest record
that the label was registered and then superseded before any cell ran under
it. Its headline is legitimately empty forever.

**Re-blessing the evaluator half while the prior digests carry counted
cells** is the second supersession shape, and it swaps which checks do the
work. The evaluator entries are the freeze *record*, never the counting
filter — an evaluation's digest never partitions the headline, though its
retroactivity is tripwired against the bless moment while the digest stays
in the map; only its timing is gated for counting (`graded_in_window`) —
so replacing them de-counts nothing, and it also takes their cells out of
the tripwire's reach (harmless for cells that already passed); the freeze
record in [freeze-record.md](freeze-record.md) must name the replaced digests and
the count of counted cells graded under them, since the constant no longer
does. Where the predictor digests are **byte-identical** to the prior
`prereg/` tag's, `FROZEN_SINCE` holds rather than moves: the instant does
no work for anything newly blessed — nothing can carry the new evaluator
bytes before the carrying promotion lands them on `main`, and step 0
proves nothing already does — while moving it forward would drop every
stamped prediction from the headline for a change that touched no
predictor byte, and opens no window. Step 4's date comparison is therefore not such a label's
audit (held deliberately, the instant *precedes* the carrying promotion);
the auditor's check is the byte comparison instead — the predictor digests
under the new tag must equal the prior tag's, whose own
instant-versus-promotion audit stands. One consequence to record beside
the count: the evaluator digest records but never partitions, so grading
series pool across the rubric boundary the re-bless introduces, and the
freeze record states the exposure.

**Re-blessing the predictor half while the prior predictor digests carry
counted cells** is the third supersession shape, and it **closes** the prior
windows; it de-counts nothing. The successor's freeze commit sets `closes`, at
its own counting instant, on the window of each predictor digest it stops
blessing, and appends a window for each digest it newly blesses. Every cell
that counted inside a closed window keeps counting, reported under the label
that opened it; a digest carried forward byte-identical keeps one unbroken
window across both labels; and a digest blessed again after its window closed
opens a second one. The successor's instant is not a gate on the closed
windows' gradings — `graded_in_window` reads the instant that opened the graded
prediction's window — so the gradings those cells collect after the successor
froze count as they would have without it.

A successor that closes windows carries the disclosures its freeze-record entry
owes: the closed windows' resolved and pending counts at its instant, and
evidence for the process change other than the closed windows' boards (the
close is decided while some of their outcomes are visible, so it must not be
chosen by score); the number of **split events**, on which some engines' counted
cells come from a closed window and others' from the successor; per engine, how
many of the successor's counted events hold a failed or missing
earlier-window attempt, since the successor's population is the events the
closed window did not reach and that population is selected, not random; and,
where it is a full freeze, the count per evaluator digest of closed-window
cells graded under the successor's rubric, since a window's figure can then pool
rubrics. An unbroken window licenses no other pooling: a salience, baseline,
evaluator or other boundary registered elsewhere still cuts inside it.

**No predictor-half re-bless lands on `main` until per-window strata are
built.** The frozen scope, the counting rule, the run collapse, evaluation
staging, the dataset export and the re-predict rule all read the windows. The
leaderboard, the claim scores, the ops report and every other aggregate over
the stratify pass still key on `predictor_id` alone, so rather than pool a
predictor's windows they refuse the ledger the moment one predictor's
in-scope cells span two; the big-case agreement and the tool-usage
usefulness block (keyed on the engine) do the same. A successor landed before
those surfaces break out by window would stop every frozen-scope board from
building, so a test fails the suite while any window carries a `closes`. A
bless that adds a window for a new predictor id closes nothing, yet ranks an
engine whose window opened later beside the earlier ones over a different span
of events — the selected-population comparison this section rules out — so a
second test fails the suite while any window opens after the earliest. Both
are removed in the change that builds per-window strata. The evaluator-agreement
view is keyed on the evaluator and pools the predictors' windows by design,
since it compares graders rather than forecasters; a figure over it states
the windows its cells span.

**Revoking a window** is the one route by which counted cells are de-counted,
and it is for a defect that invalidates the window's forecasts, never a better
process. It sets `revoked_at` on the window — only on a window a successor has
already closed, since revoking an open one would leave its digest blessed and
the backlog would re-mint the re-owed events under the very process found
defective, and at or after the merge of the promotion that carries the
revocation — on a dated freeze-record entry that
states the defect and shows it from committed artifacts without reference to
any outcome, made while the affected outcomes are unknown — or disclosing the
slice that had already resolved, and then publishing the revoked window's
figures over that slice beside the entry, so the exclusion is visible rather
than silent. A revoked window's cells leave every frozen-scope artifact; its
still-forward events are re-owed afresh under the re-predict rule below; and a
later-window cell stamped before the revocation stays uncounted, so revoking
never promotes a forecast that was already made. The labels before `proc-v8`
were de-counted by the shape that preceded windows — replacing the predictor
digests outright, licensed by a shakedown declaration dated before the
de-counted claim window's outcomes — and the freeze record carries each of
those declarations.

**What a de-count leaves the predict backlog owing.** A cell that counts
nowhere — unstamped, under a de-counted pre-`proc-v8` digest, stamped before
its window opened, or in a revoked window — sits on an event that may still be
**open**, and there nothing has been published yet. When it resolves, the
grading lands outside the frozen scope and the event is consumed for nothing.
The predict backlog is otherwise version-blind (a committed prediction is a
committed prediction), so it would report every such event covered and derive
no work at all.

It does not. The deriver **re-owes** a cell on such an event, for each
predictor whose every committed cell on it is de-counted, while the event is
still genuinely forward and its declared moment is still open — the re-predict
rule, whose predicates and moment allow-list are in [cli.md](cli.md). A
**closed** window's cell is not de-counted, so a supersession re-owes nothing:
an event on which a closed window holds a counted cell stays covered, and the
successor's backlog reaches only the events its predecessor did not. A
revocation's real cost, by contrast, is not only the counted cells it drops but
a re-forecast of every open event the revoked window covered, bounded by the
moments still open when it lands; the entry that registers it states the
cohort and its expected size **before** any of its outcomes are observable.

## A note on local runs

The local `local-cascade` path produces cells but does **not** run the
`stamp-cell` step (that is a workflow step, not part of the runner). So a local
cascade's cells are unstamped and appear only under `--all-versions`. This is
intended: the frozen headline is the production tournament, not a developer's
local exercise.
