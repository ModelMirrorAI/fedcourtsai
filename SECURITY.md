# Security

## Invariants enforced in this repo

The concrete wiring behind each invariant — the GitHub Apps, rulesets, the
`prod` environment, and the IAM roles/policies — lives in the operational
runbook, [docs/security.md](docs/security.md).

- **Pin actions to a full commit SHA**, with the version in a trailing comment.
  `zizmor` (in `lint-actions.yml`) fails the build on unpinned actions; Dependabot
  bumps the pins.
- **Pin Python dependencies to `uv.lock`, and install with `--locked`.** The
  lockfile carries a hash per artifact, so it is the supply-chain control for
  the project's own dependencies — the counterpart of the action SHAs above.
  Every job that installs them goes through
  `.github/actions/setup-python-env`, whose `uv sync --locked` refuses a lock
  that has drifted from `pyproject.toml` rather than re-resolving. Dependabot
  bumps it. The packages `uvx` resolves at run time are *not* in that lock and
  are pinned by version alone: the CourtListener MCP server named in
  `config/predictors.yaml` / `config/evaluators.yaml`, and the workflow linters.
  A third class is pinned by neither: the OS packages four steps install with
  `apt-get` — the labeler's sandbox on `run-analytics`, the same sandbox on
  `integration-test`'s labeler smoke, and the OCR recovery's two binaries on
  `run-repair` and in `run-seed`'s credential-free OCR sweep parse job. They come from the runner image's own Ubuntu
  archive, with no third-party repository and no added signing key, so the trust
  is the runner's rather than ours; an exact version pin would only add a
  failure the week the image rolls, so each OCR step echoes the versions it
  resolved into its run summary instead.
- **Least-privilege permissions.** Every workflow sets top-level `permissions: {}`
  and grants only what each job needs.
- **No static key in the runner's process env where untrusted code runs.** The
  Claude and Codex engine *actions* proxy or scope their model API keys so those
  CLIs never hold them. The engines this repo drives directly — Gemini
  everywhere, and all three in the cert back-test and the integration suite's
  engine smoke — are the exception: their key is a scoped step env on the agent
  step, so the control there is the Gemini
  CLI's own sanitizer, which strips every env var it has not been asked to
  allowlist and **refuses to allowlist** any name matching
  `/TOKEN|SECRET|KEY|AUTH|CREDENTIAL|PRIVATE|CERT/i` — so a model key can never
  reach the agent's shell. That strict mode is forced by `GITHUB_SHA`, i.e. in CI
  (the residual: off-CI there is no such barrier, which is a local dev run with
  the dev's own key). The lower-sensitivity CourtListener token is passed as a scoped step env
  in exactly two kinds of deterministic place, whatever the caller: the
  **MCP sidecar composite's launch step**,
  whose background `fedcourts mcp-serve` process inherits it and serves the
  CourtListener MCP tools over localhost HTTP — the cells launch it, and so
  does `integration-test` — its engine-smoke **codex** leg, which exists to
  exercise that very wiring, its engine-actions-smoke legs, whose
  invocation blocks name the client config that sidecar serves, and each
  repro-family leg, which drives one of those blocks against a real
  record — and the collect job's
  **aggregate step**, where the secret scan (below) needs the live value to
  search the run's output for it — a step that parses agent bytes with
  jq/git/tested Python but never executes them. (Pull's ingestion holds the
  same secret under its own name; the two kinds here are the agent
  workflows'. A new caller of the composite is a new *call site*, never a new
  kind of place — the token reaches the launch step's env and stops there.) **No agent step holds it, and no file an agent can read
  carries it:** the client configs name only the sidecar's `localhost` URL, so no
  client-config file on a cell runner carries the token as a literal value for
  the agent's file tools to read. The cells have no REST fallback, so live
  CourtListener access is the MCP sidecar only (the agent calls it by tool
  name, never handling the token), and the token is never in the environment
  while an engine processes adversarial docket text.
  Residual blast radius if the token leaked despite this: it spends pull's
  quota and forces a rotation that touches pull — it is not a model key or a
  GitHub token.
  **The remaining residual is process-level, and the output channel is
  gated.** On-runner step-scoping is not hard isolation for the unsandboxed
  engines: on a claude or gemini cell the sidecar runs as the same user as the
  agent, so a determinedly-injected agent could still read a sibling process's
  environment — what the sidecar removes there is every casual path (no agent
  env, no readable config file, no accidental log). A codex cell runs the agent
  as a separate unprivileged account that cannot read the runner user's process
  environment at all, so even that determined read is closed for it; the
  residual holds only for the same-user engines.
  And the sidecar is deliberately unauthenticated on `127.0.0.1`: anything on
  the runner can spend the token's rate limits *through* it, which equals the
  agent's designed tool access — while off-runner use of the credential now
  requires that process-environment read, a strictly higher bar than the old
  read-the-config-file path.
  Should any secret reach agent output by any means, the exfiltration
  sink is gated: agent free text (`reasoning.md`, a rationale, a flag
  message) is exactly what `validate` deliberately does not read, so before
  anything is pushed the `collect` job runs a **secret scan**
  (`fedcourts scan-diff-for-secrets`) over the run's changed files and the PR
  prose about to be posted: literal containment of the live token in the cheap
  encodings (base64, hex, URL-escaping), credential-shape patterns, and an
  entropy heuristic — whose only candidate-level exemption is the collected
  run's own ledger paths (the `predictions/` / `evaluations/` layouts and the
  cell-relative `<actor>/<run id>[/<file stem>]` /
  `<evaluator>/<predictor>/<run id>` forms), named by `--run-id` with the run
  id segment compared for equality and every free segment pinned lowercase
  and capped far below the heuristic's own minimum, so the skip can hide
  nothing the heuristic would convict standalone.
  That heuristic is off entirely, file by file, for the two files holding
  what a cell's tool calls carried — `retrieval_log.json`, which the harness
  captures, and `retrieval.md`, which the agent writes as its account of the
  same calls — because it would convict them wholesale: their content is
  document addresses, ids and search queries. Containment plus the credential
  shapes carry those two as they do an engine transcript's below. The residual
  is stated per file, since the two are not equally guarded. In
  `retrieval_log.json` it is the 40-63 character window: capture-time
  redaction (below) reads every byte that file keeps on the way in and
  rewrites both the shapes it can name and any unknown run of 64 characters
  or more that scores like credential material, so what passes both layers is
  an opaque run shorter than that. In `retrieval.md`, free text nothing
  rewrites, it is everything from 40 characters up that no shape names and no
  known credential matches. Every other file a cell writes — its reasoning,
  its evaluation, its flags — and the PR prose scanned beside them keep the
  heuristic. A hit **withholds the branch** — nothing is pushed and no
  PR opens; a redacted file/rule/line report (never the matched text) lands on
  the run's step summary and the files stay in the run's cell artifacts for
  maintainer review. The scan fails closed: if its token env is missing, the
  branch is likewise withheld, with a misconfiguration note on that summary
  in place of a findings report. The same command gates two surfaces
  outside a run branch on their own terms, both of them things the
  `qp-topic-label` run's agent wrote and neither of them validated by anything
  else. Its turn-by-turn engine transcript is scanned (`--transcript-file`)
  before it is
  uploaded as a run artifact, with every detector *except* the generic entropy
  heuristic — a transcript's server-generated tool and request ids are
  high-entropy by format, so that rule convicts every real file and the
  artifact could only ever publish empty. The partial labels the run wrote are
  scanned (`--extra-file`) before theirs, with the entropy rule left on: a
  labels line is case ids, docket numbers and vocabulary words, none of them
  high-entropy by format, so the reason to suppress it does not arise. (The
  labels the run *publishes* are a different object, gated by `qp-topics`
  reading every row against the vocabulary and the extract's keys; this file
  is uploaded before that command runs, so it travels whether the gate
  refuses or passes.) Containment of the one credential
  the scan is given there — the engine's own API key — and the
  credential-shape patterns are the *transcript* surface's whole gate, which
  is why it
  fails closed the same way: a hit, or a scan that could not run at all,
  withholds the artifact, and the run's warning and step summary are the
  record. A third agent-written artifact publishes without this command: the
  unpaid `qp-labeler-smoke` leg's own labels file, which takes the containment
  half alone, by a literal `grep` off a PATH pinned to root-owned directories,
  because building the paid lane's fresh-checkout scanner there would mean
  running the agent's own workspace Python with the engine key in its
  environment — the arrangement that scanner exists to avoid
  ([docs/security.md](docs/security.md)). The label-line count on that summary is arithmetic over the file
  rather than anything read out of it, which is why it is stated whether or
  not the file itself travels. A fourth is a merits back-test replay's
  `merits-forecasts` artifact: each cell's allowlisted forecast files and
  event definition (`merits_backtest.kept_forecasts`, written only once the
  last cell has finished, never the provisioned record; the upload step
  applies the same allowlist again and withholds the whole artifact if the
  keep folder holds any other file, since a cell can reach that path, then
  uploads a fresh copy of what passed), kept 30 days and,
  like every artifact of this public repository, downloadable by any
  signed-in GitHub user. The scan (`--extra-file`, entropy rule on, the run's
  own ledger paths exempt by `--run-id`) is its whole gate, and it fails
  closed: a hit, a misconfigured scan, or a kept entry that is not a regular
  file withholds the artifact while the run's report still lands. Two gaps in
  that gate are accepted rather than closed. The scanner runs from the
  checkout the cells held, with all three engine keys in its environment, so
  its import path is not a fresh tree; and a process a cell left behind can
  swap a scanned file before the upload step reads it. Neither reaches a
  credential a cell lacked: a replay cell's parent carries those keys and the
  job's read-only corpus credentials throughout (the same-user residual in
  [docs/security.md](docs/security.md)), and the cell holds web tools under
  the replay contract, so it already has egress. What the gaps defeat is the
  scan as a check on an engine that would publish a key, which is why the
  reachable secret on this surface is a model key, not the CourtListener
  token below. The artifact is consumed by run-evaluate's
  `reasoning-pilot-merits` round, whose plan re-checks the whole tree
  (`merits_calibration.read_kept_run`) before anything reads it and
  republishes the forecast bytes, unscanned again, in the round's 7-day
  `reasoning-pilot-calibration` artifact beside an event definition and
  outcome rebuilt from the corpus: the bytes are the scanned artifact's own,
  and the outcome fields are the ones a committed outcome already publishes.
  Holding that key makes the
  scan's own **import path** part of the gate, and it follows an agent that
  writes freely in the tree the editable install resolves through — so the
  scanner is built from a checkout taken *after* the agent exits and fetched
  from GitHub, into a venv inside that fresh tree, with the package cache and
  the interpreter it is built on inside that tree too, and with the levers
  that put a caller's code inside a process it starts (`PYTHONPATH`,
  `LD_PRELOAD`, an executable `core.hooksPath` in global git config) closed
  alongside. The same job's tree-pristine assertion is a
  separate control for a separate threat, a rigged measurement rather than a
  stolen key, and it gates the measure step rather than the capture: a
  tampered run keeps the agent-written evidence that diagnoses it. The toolchain that
  builds the scanner is held the same way: `uv` is checked against a digest
  recorded before the agent ran, since it sits where the runner user can
  rewrite it, and PATH is pinned to the root-owned directories so `git` is the
  image's. What that isolation still trusts, named rather than implied: the
  action bundles the runner unpacks before a job's first step, which sit in a
  runner-user-writable path and are pinned by identity and not by bytes; the
  runner image's own files, behind the passwordless sudo the runner user
  holds; and anything a process the agent left behind does between steps. What
  it removes is the drop-a-file class on the scanner's **Python import path**
  and on the toolchain that builds it — the class an editable install hands
  over for free. A different surface is
  handled a layer earlier instead: the tool-call log the harness harvests from
  an engine transcript into `retrieval_log.json` records whatever a tool call
  carried, which is not the agent's choice, so
  credential-shaped runs there are **redacted at capture** — rewritten to a
  `[redacted:…]` marker and the run allowed through, rather than costing a
  whole fan-out's model spend to a withheld branch. Redaction is not a gate:
  it spares only the shapes it can name, and what it leaves meets the scan's
  containment and credential shapes — though not, in that file, its generic
  entropy heuristic, which is the residual stated above. The scan is a heuristic and the cell's
  uploaded artifacts remain downloadable from the Actions run by logged-in
  users regardless, so the last line stays what it always was: the *reachable*
  secret is not worth stealing — the single-account, **read-only**
  CourtListener token whose worst case is spending pull's quota and forcing a
  rotation (above), not a model key. No App key and no write-scoped GitHub
  token is delivered to a cell: the Claude step gets a copy of the cell job's
  own token, capped at `contents: read`, and a codex or gemini cell gets none.
  One credential stays in reach, and it is a residual rather than a control:
  the cell jobs hold `id-token: write` for the read-only corpus role, so any
  process in the job can request an OIDC token for the job's environment, and
  every relying party that accepts that subject is reachable with it. Among
  AWS roles, the design leaves only the read-only role reachable: the production
  read-write role's trust names `corpus-write`, an environment only the
  corpus writer jobs bind, and nothing else — an IAM statement the promotion
  gate cannot read, which the maintainer keeps (*`corpus-write` holds the
  production read-write role* in [docs/security.md](docs/security.md)).
  Beyond AWS it is the Claude GitHub App's installation-token exchange, which
  accepts a token from any job in this repository holding `id-token: write`
  and yields one with the App's write grant: an **accepted residual** — the
  App also serves Claude Code's own GitHub access, so it stays installed, and
  no workflow uses the exchange, every `claude-code-action` step passing the
  job's own token (*S3 / the private stores* in
  [docs/security.md](docs/security.md)).
- **Agents get no App credential, never a static one.** The Claude agent
  steps in `run-predict` / `run-evaluate` receive the cell job's own
  short-lived token, capped at `contents: read` by the job's permissions; the
  Codex and Gemini **agent steps** get no GitHub token at all — their
  blocked-channel is `flags.json`, surfaced by the trusted `collect` job. No
  job that runs an agent names an App's private key, since every secret a job
  names reaches its runner. The *workflow*'s `collect` job (a distinct
  `contents: write` App token) does the commit/PR, so a prompt injection in
  docket text cannot reach the dev App's token or its approval bypass. The
  job's OIDC request credential is the residual stated in the item above.
  Issue and docket text stay untrusted input.
- **The engine watchdog holds no credential.** The engine hang bound
  (`scripts/engine-watchdog.sh`; *Graceful degradation on limits* in
  [docs/pipeline.md](docs/pipeline.md)) is trusted repo code that brackets
  **every** engine's cell step: one configured engine deadline per cell job,
  which every engine step's `timeout-minutes` reads and which the watchdog
  fires a margin ahead of, so it can end a step's whole process tree before
  the runner's own timeout. Everything it records stays on the runner — its
  log, a marker, and a shapes-only diagnostics bundle — and leaves through the
  cell's own tail: the disarm step turns a marker into a `::warning::` and a
  step-summary line, records a deadline stop in the cell's `status.json`, and
  carries the bundle into the cell artifact. That tail runs because acting is
  what *concludes* the step. So no step mints a token for it, its arm and
  disarm steps hold no GitHub credential, and the script makes no network
  call.
- **The hidden-record stash is forgeable by the same-user engines, and buys
  nothing a cell does not already have.** Predict and evaluate cells move the
  committed `predictions/` and `evaluations/` trees into a stash under
  `RUNNER_TEMP` for the agent's run and restore them after. A claude or gemini
  agent can write that stash; a codex agent cannot (the codex setup strips
  other access from `RUNNER_TEMP`). The restore shape-checks every manifest
  entry, keeps each destination inside the data root, refuses symlinks and
  never overwrites, and the cell artifact carries only the cell's own event
  directory, which the collect union adds without modifying committed bytes —
  so a planted file is at most an addition the agent could have written into
  its own event directory directly.
- **The reaper gives a cell one runner-local switch, and it is bounded by what a
  cell already faces.** The watchdog ends a step whose required output files all
  exist, parse, and stop changing — so an agent can end its own step early by
  writing them and idling, and a prompt injection in docket text can ask it to.
  On a claude or gemini cell it can also simply create the watchdog's `REAPED`
  marker: those agents run as the runner user unsandboxed (claude
  `bypassPermissions`, gemini `--yolo`), so no runner-local path is out of reach
  (the qp-topic labeler is the one agent held to a narrower grant, and it is not
  a cell). A codex cell cannot — codex runs as a separate unprivileged account,
  and the marker sits under a runner-owned `RUNNER_TEMP` directory (mode 0755
  and not writable by that account; the codex setup additionally strips other
  access from `RUNNER_TEMP`), so this rests on that ownership, not on the uid
  alone. The runner-local marker is therefore forgeable only by the same-user
  engines.
  What either buys is narrow and worth stating exactly: the marker sets
  `agent_ok`, which routes the cell to the run's **ready** PR instead of the
  draft one, and nothing else. `produced` and `validated` still have to hold, the
  collect job still secret-scans and still enforces the `data/` path jail, the
  cell's credential still carries no `contents: write`, and a compliant agent
  could land the same bytes by finishing normally. The residual is that a cell
  which stopped early can present as one that finished — a claim about review
  routing, not a capability. The deadline markers (`FIRED`, `STOOD_DOWN`) are
  forgeable on the same terms, and a planted one buys less still: it sets the
  cell's `engine_deadline` in `status.json`, which only changes the reason the
  draft PR names for a stop — it never readies a cell.
- **No workflow creates a Release or holds a Zenodo credential.** Release
  archiving is Zenodo's GitHub integration: an OAuth grant on the maintainer's
  account (webhook administration across the repositories that account
  administers, no contents access) outside the Actions permission surface. A
  published Release is archived permanently, so publishing one is a maintainer
  step; any `contents: write` credential could create one, which is why no
  workflow does. Automating the dataset deposit would add a credential and
  changes this line. Setup and scope: [docs/security.md](docs/security.md),
  *Zenodo archiving*.
- **No static cloud keys — OIDC for S3.** Workflows that touch the private S3
  stores (the corpus remote and the per-case content store) assume a
  least-privilege IAM role via GitHub OIDC. **Three roles, split by access:**
  corpus writers get a **read-write, append-only** role (get/put/list, **no
  delete**) and every corpus consumer a **read-only** role, so a compromised
  consumer runner cannot tamper with the data. Three controls together mean no
  run can wipe corpus objects: the buckets keep **versioning** on, the
  write-role policy carries an explicit **`Deny` on every delete**, and a
  second `Deny` covers the two delete-equivalent **bucket-configuration**
  changes (versioning and lifecycle configuration) — a lifecycle expiration
  runs under S3's own principal, so a role able to install a rule could expire
  a whole prefix while its own `DeleteObject` calls were still refused. The
  third role is the **staging read-write**
  role — read-only on the production stores, read-write on the staging corpus
  pair alone — so the production stores keep exactly one writer whatever
  happens to it. Every role's OIDC trust is to be scoped to named environments
  of this repo — the production read-write role to `corpus-write`, the read-only
  role to `prod`, `corpus-write`, `staging` (which is what lets the
  pre-promotion integration runs read the corpus), `corpus-check` and
  `corpus-check-auto` (the PR corpus-check lane's approved and unapproved
  paths, under the trigger surface below), the staging read-write role to
  `staging` — and each of those environments restricts deployments to its own
  branches (`staging` also admits the promotion train's `promote/*`
  candidates: commits already on `staging`, created only by the dev App and
  never moved), so a PR-branch job cannot assume any of them. In production the
  split is identity: the read-write role's trust names `corpus-write` alone —
  an IAM statement the promotion gate cannot read, which the maintainer keeps
  (*`corpus-write` holds the production read-write role* in
  [docs/security.md](docs/security.md)). Only the corpus writer jobs bind
  `corpus-write` (`tests/test_workflow_corpus_write.py` pins the binding, and
  the gate checks only the environment: its `main`-only policy and its
  names), so then no `prod`-bound job — no agent cell — can ask for the write
  role, whatever it runs. That removes *agents* from the write role's reach,
  not hostile *parsers*: the writer jobs themselves parse fetched third-party
  content while holding or able to mint it — the pull and seed windows' fetched dockets, and
  the corpus repair job's OCR-recovery, document back-fill and re-cut passes,
  which are not split from it the way the fetching passes are. In staging it stays provenance: any `staging`-bound job could ask for
  the staging write role, which writes only the disposable staging pair, and
  what stops the wrong job asking is review of the code the branch policy
  admits — so a wrongly-writing change fails visibly against the disposable
  staging pair before promotion instead of succeeding first in production. No
  committed file carries credentials or the bucket URL — each job (and
  operator) supplies the corpus address out of band — a base URL, one per
  environment, from which both stores' addresses derive (`fedcourtsai.paths`),
  or a store named on its own — and boto3 reads its credentials from the
  environment.
  Per-workflow role assignments and policies:
  [docs/security.md](docs/security.md).
- **No pipeline agent process holds a cloud credential.** An agent runs over
  third-party docket text, so no corpus credential reaches the process that
  reads it — the one exception being an interactive Claude cloud session
  started in the dedicated corpus environment, which holds a read-only key by
  design and is bounded as the developer-access bullet below states — but the enforcement differs by job, and the guarantee is about the
  process, not the step. In a predict/evaluate cell the read-only role's
  credentials never enter the agent *step* at all: they ride the provisioning
  and sidecar-launch steps as masked step outputs, and the agent reaches corpus
  data only through the sidecar's `localhost` query surface. `run-backtest`
  assumes the role job-wide, so its agent step does carry the variables; there
  the shared runner seam spawns each engine CLI from a **scrubbed base
  environment**, dropping every `AWS_*` name but the region and every
  credential-shaped name that is not the engine's own auth. The qp-topic
  labeling job needs neither, and assumes no role. Which mechanism covers which
  job, and the residual the back-test's shape leaves: *Agent shells hold no
  cloud credential* in [docs/security.md](docs/security.md).
- **The case-summary lane never holds its model key and a corpus credential
  together.** `summarize` reads the corpus in its `plan` and `stage` jobs
  (read-only role) and calls the model in its `generate` job, which assumes no
  role, holds no `id-token`, and fails before its first key-bearing step if an
  AWS credential or OIDC minting is reachable; the staged record crosses as a
  one-day run artifact, which on this public repository any signed-in user
  can download while it exists, and which the lane therefore fills only with
  supremecourt.gov content. The model call carries no tools, so the model reaches
  nothing but the record it is sent. The key is the bound environment's
  Anthropic key, held in this lane by the generate job alone and shared with the
  cells' spend limit, so every run spends only behind the `review` hold or
  the budgeted auto-release that routes a small round past it.
  `tests/test_workflow_summarize.py` pins the split; the lane's contract is
  [docs/case-summaries.md](docs/case-summaries.md).
- **One scoped exception: developer corpus access.** Three developer flows,
  all read-only, none in a repository secret or a commit. From Codespaces,
  through **user-scoped** Codespaces secrets: the maintainer via IAM Identity
  Center's short-lived SSO tokens — the role-assumed flow, whose read-only
  role also reads the staging pair — and contributors via a dedicated
  read-only IAM user provisioned on demand, scoped to the production stores
  alone. From Claude cloud sessions, through the variables of one dedicated
  personal cloud environment: a second, separate read-only IAM user, under a
  production-only read policy that carries an explicit deny on writes and
  deletes, and that a contributor user is given too. Those sessions act on
  GitHub as the agent account, never with the maintainer's credentials. The
  key is visible to the model and to every command in a session of that
  environment, and Anthropic's environment configuration holds it. So a
  prompt injection — in docket text the session reads, or in web content it
  fetches — could print or send the key, and could also read stored corpus
  content with the commands the session legitimately holds and move it out:
  over the network, since the environment's default level reaches every
  `*.amazonaws.com` host and so any S3 bucket, and over GitHub, where the
  agent account can push branches and post public text. No control fences
  that egress; what bounds it is that the environment is chosen only for
  corpus work (discipline, not a control — any task can be started in it),
  AGENTS.md's rule that stored text never leaves the session, and the key's
  reach: it reads production only and can write nothing. It is rotated and
  revoked by its own runbook (docs/security.md). The exposure a leaked key of
  either user could buy is a republication of access-gated court data the
  pipeline does not itself republish (docs/data-sources.md), not a write: no
  developer principal can write or delete anything, and a billing alarm bounds
  egress abuse. See *Developer access* in
  [docs/data-pipeline.md](docs/data-pipeline.md).
- **The trigger surface is the trust boundary, and the platform holds it.** No
  **privileged** workflow — one that mints a token, assumes a role, or runs an
  agent — keys on an `issues` event, or on any other trigger class an actor
  outside the write boundary can fire, so nothing an outside actor files reaches
  one at all. Every privileged lane enters one of two ways, and three platform
  facts cover both. A `schedule`
  fires only from the **default branch**, so a cron can run only what a
  maintainer-approved promotion put on `main`. A `workflow_dispatch` is gated by
  GitHub on repository **write**. And every privileged job binds a deployment
  environment whose branch policy pins the ref it may run from — `prod` to
  `main`, `staging` to `staging` and the promotion train's `promote/*`
  candidates (below), `corpus-write`, `corpus-check`,
  `corpus-check-auto` and `website` to `main` — so a
  dispatch from any other ref
  holds no role, no secret, no agent: a job naming an environment as a literal
  is refused at the deployment-branch gate before a step runs, and the three
  branch-resolving workflows (`integration-test`, `run-analytics`,
  `summarize` — the
  carve-out `docs/security.md` describes) resolve an off-list ref to an empty
  auto-created environment the role trusts do not name, failing closed at the
  first credential instead. Repository write is wider than the people who
  should start a run, though — the agent account interactive sessions act as
  holds it — and GitHub lets every write holder dispatch and re-run. So every
  workflow that binds an environment, whatever its triggers, opens with the
  **run gate**, an `authorize` job with no environment, no secret and a
  read-only token that every other job of the run needs: a dispatch proceeds
  only when its dispatcher is a human `config/dispatchers.json` names or a
  pipeline bot it allows for that workflow; a re-run of any run only when its
  re-runner is such a human; a first attempt only for a dispatch or a
  `schedule`, `push` or `pull_request`, every other event refusing. The agent
  account is deliberately absent from that file, and an unreadable file
  refuses everything. **The gate's code is self-contained and owned**: the
  job sparse-checks-out `src/fedcourtsai/run_gate.py`, which imports only the
  standard library, and the allow-list, and runs the module by path with the
  runner's Python in isolated mode, so no change to the package, its
  dependencies or its lockfile — none of them code-owned — can loosen it on
  `staging` without the maintainer. Re-running some of a run's jobs keeps the
  gate's earlier success rather than re-running it, so every job's condition
  also requires the attempt the gate judged, or a re-runner on the list it
  published, and a closing `run-gate` job, which needs every job and so
  re-runs with any of them, **fails** a refused re-run rather than letting the
  earlier attempt's successes stand as a green run
  (`tests/test_workflow_auth_gate.py` pins all three). The gate holds only on
  refs whose workflow carries it, which is why the environment's branch policy
  stays the ref gate beneath it: a dispatch from a branch whose workflow drops
  the gate still reaches no role, no secret and no agent. What it does not
  cover: a refused run still occupies its workflow-level concurrency group
  while it fails (run-repair's corpus jobs pick their skip group instead) and
  stays in the run history; `promote` and `run-ops` stay ungated because they
  bind no environment and name no secret; and repository-level secrets, which
  a job reaches without an environment, are assumed absent (`docs/security.md`
  keeps every secret on an environment). Three jobs dispatch a lane
  themselves with the **dispatch App**, whose token holds Actions write (and
  PR read) and nothing else and whose key only `main`'s code can mint:
  `run-pull`'s `chain-predict` and `run-predict`'s `chain`, each starting an
  input-less `run-predict` on `main`, and the promotion train's
  `dispatch-gate`, starting the side-effect-free `integration-test` `gate`
  suite at a frozen `promote/` candidate, once per head. The allow-list admits
  the App for those two workflows alone. A dispatch from it enters through the
  same gates as a maintainer's and reaches the same code; the round it starts
  still waits on the review hold unless its own plan is within the
  auto-release caps and budget. The train's suite has no review hold: it
  spends staging's engine keys unattended — about one paid suite per
  candidate, outside the auto-release budget — bounded by the train's own
  daily cap (`max_gate_dispatches_per_day` in the code-owned
  `config/promotion-train.yaml`) and by never re-dispatching at a head.
  run-evaluate's pilot rounds (`reasoning-pilot`, `reasoning-pilot-merits`)
  spend outside the budget the other way: they always wait on the `review`
  hold, but they commit nothing, so their measured spend never reaches the
  ledger the trailing budget is projected over, and the manual release is
  their only bound. The
  pull window chains only on a forecast-relevant change, and neither chain job
  dispatches while a promotion is about to merge.
  Three workflows *do* take an outside-reachable trigger — `ci.yml`,
  `lint-actions.yml` and `codeql.yml` on `pull_request`, which any fork
  contributor fires — and they are the shape that makes the rule readable rather
  than an exception to it: each carries top-level `permissions: {}`, binds no
  environment, names no secret, and mints no token or role, so a fork PR's run
  reaches nothing. Privilege and outside reachability are disjoint here, not
  merely rare together.
  One lane runs **PR-head code with a credential**, and it is the one place
  the environment's branch policy does not mean what it means elsewhere:
  `corpus-check` ([docs/corpus-check.md](docs/corpus-check.md)) runs the
  check a same-repository PR by a listed author declares, at that PR's head,
  with the corpus read-only role. Its triggers are the same two — a
  `schedule` and an input-less `workflow_dispatch`, so the workflow binding
  the environment is always `main`'s — but the code it runs is not the ref's,
  so the branch policy is met only on paper. Four things bound it instead.
  The `corpus-check` environment's **required reviewer** — the maintainer
  alone, no other user and no team: the maintainer approves a named head SHA
  and command, reading a diff pinned to that SHA,
  and the run then takes both from the plan, never re-reading the PR; the
  lane plans nothing, and the promotion gate refuses, while the environment
  lacks that reviewer or its `main`-only policy, since the read-only role's
  trust makes an unprotected `corpus-check` environment that role for any
  write holder's branch workflow. The **account**: the head's install and the
  check run as a separate unprivileged account with no sudo, no cron or `at`,
  no unprivileged user namespaces and no route to the platform's metadata
  endpoints, which cannot read the runner's process environments, home, temp
  files, workspace or install root — each proven as the account before PR
  code runs — so the job's OIDC request pair, its runtime token, its step
  files and its log are out of the PR code's reach: it can mint no OIDC token
  for any audience (the Claude GitHub App's token exchange included), save no
  cache entry, upload no artifact. Every process the account owns is killed
  after each phase, and one that survives fails the run. A Linux account is
  not a sandbox, though: a kernel privilege escalation from that account
  reaches root and, through it, the runner's tokens. The approval and the
  read-only trust are why even that is bounded — the code ran because the
  maintainer approved it, and the most any token it could mint reaches is the
  read-only role.
  The **trust**: what the account holds is the read-only role's session, which
  reaches every store read-only and nothing it can write; and because the job
  itself holds `id-token: write`, no role but the read-only one, in any
  account or cloud, and no other OIDC exchange may accept
  `environment:corpus-check`, which holds that role, its region and the
  corpus address and no other credential. And the **cache rule** below. What
  stays open is network egress, the read-only session for the rest of its
  hour, and the kernel itself.
  The lane's invariant is precise: **no PR-supplied code runs with the corpus
  credential without the maintainer's approval.** One kind of request skips
  the approval because it supplies no code: a block that asks for `main`'s
  code (`at: main`) and names a `uv run fedcourts` subcommand on the
  maintainer-owned auto allowlist (`config/corpus-check.yaml`: read-only
  queries that print counts and identifiers, each one's full option surface
  pinned by the maintainer-owned `tests/test_corpus_check_auto_surface.py`, and
  the allowlist re-checked by the job itself before it runs) runs in a
  separate job binding
  the reviewer-less `corpus-check-auto` environment, whose tree is the run's
  own commit of `main` — the PR head is never checked out or fetched, and the
  parsed command line is all the job takes from the PR. That environment's
  `main`-only branch policy is its control: the plan routes nothing to it
  while the policy is missing, the promotion gate refuses a promotion until it
  holds the policy and nothing but the read-only role's three variables, and
  the read-only role is the only role, and its trust the only OIDC exchange,
  that may accept `environment:corpus-check-auto`. Every other request — any
  PR-head code, any `scripts/checks/` script, any unlisted subcommand, any
  doubt about the allowlist or the environment — waits on the approval. Like every workflow that binds an environment,
  the lane opens with the run gate: the schedule passes it, and a dispatch or
  re-run proceeds only for a human `config/dispatchers.json` names — a re-run
  of the check also needs a fresh approval. The requester list (`config/corpus-check.yaml`) is maintainer-owned,
  and the lane's result comment comes from a separate job that runs no PR
  code, treats the run's outputs as untrusted, and records the posted body's
  sha256 in its own run summary — the check that tells a real result from one
  any write holder's workflow could post as the same bot.
  `tests/test_workflow_auth_gate.py` sweeps the whole workflow
  directory for a reachable trigger, pins the five privileged lanes to those
  two, and requires every job that mints a token, assumes a role, or runs an
  agent — directly or through a composite that does — to bind one of the
  branch-policied environments, `corpus-check` and `corpus-check-auto`
  admitted for their own workflow alone — so a workflow added later inherits
  the boundary. Behind all of it the `review` hold remains the
  thing between a plan and any spend, on every round alike — save one bounded
  carve-out: a predict, evaluate or summarize round whose own plan is within
  the auto-release caps and budget (`config/review-hold.yaml`; any knob at 0
  turns it off) binds the reviewer-less `review-auto` instead. The back-test
  has no such carve-out. The per-round and daily caps bound **estimated**
  spend (the planning rates over the round's own minted matrix, or a summary
  plan's upper estimate); actual spend can exceed the estimate, since retries
  spend and the rates price some engines low. The trailing budget projects
  measured spend from the committed ledger, plus an in-flight allowance, plus
  the round's estimate, and must sit below the `spend` backstop's ceiling or
  every round holds. Both read the collected ledger, so both are **ex post**
  in what they measure: they lag the rounds they bound, and the backstop stops
  the next round, never the current one. The knobs, the planning rates and the
  decision code are maintainer-owned (`.github/CODEOWNERS`). The daily cap
  counts the larger of two records, the `review-auto` deployments and the
  auto-released commits on `main`, across the three lanes. A write holder,
  which includes the agent account interactive sessions act as, can prune the
  deployment list or edit an unmerged collect PR, so each record alone is
  tamperable; `main`'s history is not, once a round's commit has landed.
  The claude/codex agent steps on `run-predict` / `run-evaluate` allow exactly
  two bot logins through their own actor checks (the claude action's
  `allowed_bots`, the codex action's `allow-bot-users`), pinned to the data
  App's and the dispatch App's own logins and never `*`. Those actions refuse
  a bot actor by default, and an unattended round's actor is not a requester at all — it is whatever
  GitHub attributes the cron to, which on a repo whose deterministic writers
  push to the default branch can be that login — so the grant is what keeps a
  round from dying on an attribution it does not control.
  `tests/test_workflow_agent_bot.py` locks the pin in. It grants nothing a
  round could not already do: the round is running because a cron or a
  write-gated dispatch started it, and it spends only if a reviewer releases
  the hold or its plan is within the auto-release caps and budget. The allowance also
  names the dispatch App's login, since a chained predict round runs as that
  App; `run-evaluate` and the action-path smoke carry the same pair because the
  cells' invocation surface is held in lockstep. The App's token holds
  `actions: write`, which could start any workflow; the two chain jobs that
  mint it start nothing but `run-predict`, and the train's job nothing but
  `integration-test` `scenario=gate` at a candidate, pinned by
  `tests/test_workflow_dispatch_chain.py`. The gemini steps and `run-backtest` set no such
  allowance.
- **Branch protection and the deployment boundary.** `main` requires a PR
  passing `gate`, `paths`, `promotion-gate`, and `main-base`; the **data App**
  is that ruleset's sole bypass actor, so the deterministic writer jobs (`run-pull`,
  `run-seed`, `run-repair`, and `promotion-record`) push corpus facts and the
  promotion record straight to `main` while everything agentic goes through
  that PR — enforced
  by identity, since the agent workflows authenticate as a separate **dev
  App** that bypasses no required check. `main: require approval` requires
  one approving review, which only the `maintainers` team can give, and
  bypasses it for the dev App's pull requests (what lets its three unattended
  lanes land, by the jobs' own merge call — GitHub's auto-merge never
  exercises a bypass, and the call's doing so is unverified until its first
  production run; still bound by the checks), for the data App, and for any pull request an
  admin merges (how the maintainer's own lands, since GitHub does not let an
  author approve their own). So a promotion — opened by the dev App — merges
  on the maintainer's approval of its head: the promotion train executes that
  decision with the dev App's recorded bypass, merging a frozen candidate only
  after re-reading that an approver `config/promotion-train.yaml` names
  approved exactly its head with nothing requested since, pinned to that head
  and still bound by the required checks. Otherwise it merges through a
  recorded bypass: the admin role's, or a dev App token with contents write,
  whose jobs merge nothing but their own lane's PR (or the approved candidate),
  run no agent, and change only by an approved promotion. The candidates live under
  `promote/**`, which two branch rulesets let only the dev App create and
  nobody but the admin role move or delete.
  Code and config reach `main` only as a gated
  promotion batch from `staging` — except the `promotion-record` writer's
  one-parent record commit, jailed byte-equal to its plan, touching only
  `src/fedcourtsai/process_registry.json` and `docs/freeze-record.md` — whose own ruleset requires a PR passing `gate`
  and `paths` (sole bypass: the repository admin role, for the maintainer's
  deterministic sync push — no App bypasses it, and the `sync-staging`
  workflow's write token reaches the branch only through a PR that satisfies
  the same checks). On the paths `.github/CODEOWNERS` names — the permission
  surface, this security posture and its authorization check, the promotion
  gate and lane machinery, and the agent configs — it also requires a code
  owner's review. That review binds every identity but the admin role.
  Interactive agent sessions act as a separate machine account,
  `modelmirror-agent`, which holds write through the `agents` team and no
  bypass on any ruleset, so both review rules bind them; a session that holds
  the maintainer's credentials instead holds the admin bypass, and for it
  they stay `AGENTS.md`'s discipline. A ruleset with **no** bypass blocks force-pushes and branch
  deletion for everyone, so the committed *history* of the predictions,
  outcomes, and evaluations under `data/` is immutable — every forward change
  is a new, attributable commit. Forward deletions of ledger records are
  confined to two bounded channels: the maintainer-reviewed `cleanup/*` PR
  lane, and the writer lanes' bounded repair sweeps — run-seed's attribution
  repairs, and run-repair's dispatch-gated removal of merits events whose
  docket carries no cert grant — each of whose CLI refuses to apply above a
  per-run blast-radius cap, and each of which stages its ledger deletions into
  the same commit as the corpus pointer they must match. Secrets and the
  production read-only S3 role ARN live in the
  `prod` environment, whose deployment branches are restricted to `main`: a
  workflow authored on a PR branch runs without them. The production
  read-write role's ARN lives in `corpus-write`, also restricted to `main`,
  with copies of the few names the corpus writer jobs read; only those jobs
  bind it, and the promotion gate's admin-read stage refuses while it admits
  anything but `main` or holds a name they do not read. Another environment,
  `staging`, is restricted to the `staging` branch and the `promote/*`
  promotion candidates and holds the read-only
  role, its own engine keys for the pre-promotion integration runs, the
  staging read-write role. A `website` environment, restricted to `main`,
  holds one third-party key, the email list's Buttondown key, for the one job
  that drafts the weekly public update (`docs/security.md`); the promotion
  gate's admin-read stage refuses while it admits anything but `main`, holds
  anything but that key and the draft's tag id, or the key's name is also a
  repository or organization secret. Another, `review`, holds no secret and no role and admits
  `main` and `staging`; beyond that its content is a required-reviewer rule,
  and it exists only as the audit-logged hold
  between a plan that would spend and the spend — run-predict, run-evaluate,
  run-backtest and summarize all bind it; one environment serves every spend
  hold rather than each minting its own. What each hold covers differs by what
  the trigger already gates: the two fan-outs and summarize put every run
  behind it, scheduled or dispatched — except a round auto-released within
  the auto-release caps and budget, which binds the reviewer-less
  `review-auto`, whose deployments are one of the shared daily cap's two
  counts (a summarize staging rehearsal never does: `review-auto` admits
  `main` alone) — while run-backtest
  holds its **scheduled** fortnight and lets a `workflow_dispatch` through, since
  a dispatch is a human choosing the parameters and its `engine` input defaults
  to the free offline stub. The promotion gate's
  admin-read stage verifies the rule is present, because an auto-created
  environment is unprotected and an unprotected hold releases instantly.
  Self-review is deliberately permitted: with a single maintainer the hold is
  a deliberateness gate — an explicit, audit-logged reading of the plan before
  the spend — not two-person control, and blocking the run's own actor would
  make a maintainer-dispatched run unreleasable. Revisit if a second maintainer
  joins. The `staging` environment also carries the **staging read-write
  role**'s trust — the only credential in the system that can write a corpus
  store other than through the `corpus-write` writers, read-only on production and
  read-write on the staging bucket pair alone, so production's single-writer
  discipline is unchanged and the worst a staging-bound write can corrupt is
  the re-seedable fixture the refresh lane rebuilds in one dispatch. Until an
  admin deletes it, it also still holds the unused `fedcourtsai-staging` App's
  client id and key, which no workflow references (*The GitHub Apps* in
  [docs/security.md](docs/security.md)).
- **Prompt-injection awareness.** Third-party text is untrusted input, and it is
  the input a cell actually reads: the docket, the filed documents provisioned
  under `record/documents/` (party-authored), and — on an evaluate cell — the
  majority opinion staged at `record/opinion/` (on a pilot round, every
  writing of the decision beside it), which quotes whatever the
  parties put in front of the Court. No round takes a case list from anything a
  requester wrote, since the matrix is derived from committed corpus state.
  Agents are instructed to treat all of it as data, not instructions, and the
  cell's credential carries no `contents: write` — its output rides to `collect`
  as an artifact, so injected text cannot push code.
- **The ledger carries no agent instructions.** Cells of every engine read files
  under `data/`, and Claude Code, Codex and gemini-cli each load instruction files
  (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, …) or config directories (`.claude/`,
  `.codex/`, `.gemini/`, …) from the tree they work in. An added file with such a
  name, or any file under such a directory, at any depth and in any case,
  therefore fails the `data/` path jail: producer-side in `collect`, which
  demotes the run PR to a draft, and again in the required `paths` check, which
  blocks its merge. A test pins that none exists under `data/`; every other PR
  into `main` meets it in the required `gate`. The deterministic writers that
  push to `main` write only code-derived file names, so they are safe by
  construction; the jail does not run on them, and the test catches a violation
  only after the fact, in the CI run on `main` that follows the push.
- **`persist-credentials: false`** on read-only checkouts.
- **No credential-holding job restores a cache.** An Actions cache is shared
  across a repository's runs: any job can save an entry under a key nothing has
  claimed yet, and a later job restoring that key runs what it holds. A job
  that parses third-party content could therefore plant an entry, and so could
  PR-head code in the `corpus-check` lane were its account separation to fail.
  So every job installs through
  `setup-python-env` with the cache off unless
  `tests/test_workflow_cache_restore.py` allows it, an allowed job is checked
  to hold no credential, no secret, no deployment environment and no write
  grant, and its result is no required check or gate evidence; the same test
  refuses every other cache mechanism in any workflow or composite, and that
  the repository root carries a `package.json` a `setup-node` would cache
  from. A remote action's internal caching is outside what the test can read,
  so it is reviewed when the action's pin is added or bumped.
- **Secrets are never written to `data/` or logs.** The `validate` gate, the
  collect job's secret scan (which withholds a run branch rather than push
  secret-shaped content), and review on every agent PR are the backstops.

## Reporting a vulnerability

Please report security issues **privately**, not in a public issue — use
[GitHub private vulnerability reporting](https://github.com/ModelMirrorAI/fedcourtsai/security/advisories/new)
(Security → Report a vulnerability). We aim to acknowledge within a few days
and ask for a reasonable window to remediate before public disclosure. Do not
include privileged, sealed, or otherwise sensitive court material in a report.

## Scope & disclaimers

These are experimental model predictions, not legal advice. Do not feed privileged
or sealed material into the pipeline. For data terms, redistribution, and the PII
stance, see [docs/data-sources.md](docs/data-sources.md).
