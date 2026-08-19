# Data sources, terms & PII

The decided position behind the README's *Data & attribution* credit: where the
case data comes from, the terms we operate under, what reaches public git, and how
personal data in court records is handled. For the ingestion mechanics see
[data-pipeline.md](data-pipeline.md); for the security controls see
[SECURITY.md](../SECURITY.md).

## Source and attribution

Case data comes from two upstream providers, through the pipeline's three
ingestion channels (**pull**, **live**, **historical** —
[data-pipeline.md](data-pipeline.md)):

- **[CourtListener](https://www.courtlistener.com/)**, a project of the
  [Free Law Project](https://free.law/): the **REST API** (targeted enrichment —
  the `pull` channel, and the opinion-cluster enrichment that shares its
  budget).
- **supremecourt.gov's per-docket JSON and filed-document PDFs**, served by the
  Court itself — the live SCOTUS channel that owns SCOTUS freshness and loads
  the historical Term set. These are public records with no third-party license
  attached (the CourtListener terms below cover Free Law Project's curation,
  not these records). Design in [live-sources.md](live-sources.md); the
  ingested facts land in the same access-gated corpus under the same
  no-republication posture. Filed documents are stored today as
  pipeline-extracted text; one possible later direction — a direction, not a
  commitment — is landing the historical documents (motions, opinions) on the
  same access-gated S3 store as raw PDFs rather than extracted text only.

A further channel is planned but not yet adopted: Free Law Project's commercial
**database replication** offering, the intended eventual upstream for the
CourtListener roles once funding allows — see *The planned end-state* in
[data-pipeline.md](data-pipeline.md). Adopting it requires reviewing that
agreement's terms alongside the licenses below.

A second such channel is planned and not yet adopted: the **Supreme Court
Database** (SCDB) — the standing academic coding of every Supreme Court
decision since the 1946 Term, and the only realistic route to per-Justice
merits votes at scale. It is the channel [decision-model.md](decision-model.md)
names as one that could populate `Outcome.votes` with the provenance block no
docket text supports today. Its terms are why it is not adopted, and they are
split across two hosts that do not agree:

- **The current home states no license at all.**
  [`scdb.la.psu.edu`](https://scdb.la.psu.edu/) is where the data is now
  published, and none of its homepage, *About*, *Documentation*, *Data*,
  current-release, or *Cite Us* pages carries a license, a terms-of-use
  statement, or anything about redistribution. What they carry is a university
  copyright footer — "Copyright ©2026 The Pennsylvania State University" — and
  a citation request.
- **The legacy host carries a badge and no sentence.** `scdb.wustl.edu` still
  resolves and still serves the old site over plain HTTP (it refuses TLS, so it
  is unreachable to any HTTPS-only client). That page carries a live
  `rel="license"` badge linking
  [CC BY-NC 3.0 US](https://creativecommons.org/licenses/by-nc/3.0/us/) —
  Attribution-NonCommercial, with no ShareAlike and no NoDerivatives term. The
  sentence that would have named the license in prose is **HTML-commented out**
  and renders to nobody, so an image link is the whole of the declaration.
- **Neither states terms for the release we would actually import.** A badge on
  the superseded host is not a licence grant for the Penn State-published 2025
  release, and the publishing host says nothing. **Treat the terms as unknown
  rather than permissive**, and note that the more restrictive reading is the
  safe one precisely because the permissive-looking evidence is the stale half.
- **That is the blocker, and NC is why it matters.** Taking the badge at face
  value, the question is not whether this pilot is commercial — unfunded
  research over public records, publishing no paid product, is the easy case —
  but that NC binds downstream reuse of everything derived under it, and this
  pipeline is built as a durable evaluation harness rather than one paper. An
  adoption decision has to answer that for the project's intended future. Since
  the publishing host answers it neither way, adopting this channel means
  **getting the terms in writing from the maintainers first**, not inferring
  them from a commented-out caption on a host the project has moved off.
- **Attribution is specific and versioned.** The project asks to be cited with
  its full author list and the exact release, because the data is corrected and
  extended in place: "Please be sure to include the specific Version Number;
  e.g., 'Version 2024 Release 01' in your citation, as this will indicate the
  particular version of the database being employed at the time of your
  reference." The named authors are Harold J. Spaeth, Lee Epstein, Michael J.
  Nelson, Andrew D. Martin, Jeffrey A. Segal, Theodore J. Ruger, and Sara C.
  Benesh. The current release is **2025 Release 01** (1 September 2025, Terms
  1946–2024), while the *Cite Us* page still prints the 2024 release — one more
  reason adoption pins the release in the ingesting code and copies that exact
  string into [`NOTICE`](../NOTICE) and the README credit rather than
  paraphrasing it.
- **Host and support.** Penn State: "a project of the Initiative on Legal
  Institutions and Democracy in The McCourtney Institute for Democracy … made
  possible with support from Washington University in St. Louis and the
  National Science Foundation."

**The redistribution question, answered rather than inferred.** SCDB-derived
votes would *not* stay in the access-gated corpus the way CourtListener content
does. They would resolve merits events, so they would land in **public git** as
`data/cases/<court_id>/<docket_id>/events/<event_id>/outcome.json` — vote values
plus a `vote_provenance` block naming the release, keyed to case ids and
public-record docket numbers. That is a redistribution of SCDB's *coded values*,
not merely a derived judgment over them, and it is a stronger claim on the
upstream than anything in *What we redistribute* below, where the qp-topic
artifacts republish no source text and prediction reasoning is original
analysis. So this channel is the one place the public surface would carry
another project's dataset, however thinly — which is precisely why the terms
have to be settled before any value is written, and why an import that cannot
cite a license should not run.

**The join, decided.** **Docket number plus Term** is the primary join: the
docket number is the one the Court itself assigned, the Term disambiguates its
reuse across years, and the pair covers the corpus as it stands — SCDB
publishes a docket-organized cut of both its case-centered and justice-centered
files, so the join is against a shipped organization rather than a
reconstruction. The U.S. Reporter citation (`usCite`) join is the more precise
one and is deliberately **not** primary: it reaches only the corpus rows whose
`citations` column is populated — a small minority, since the column fills only
as the opinion-cluster enrichment backlog (*Pull cadence* below) works through
the cert-granted slice, not from anything SCDB controls. It stays a confirmation
path, not the key. Justice names normalize to the **entry-printed surnames** the
authorship parser already reads — `pipeline.judgment.opinion_author`'s
vocabulary — rather than to SCDB's justice-name or numeric justice-id variables,
so a single spelling serves both the docket-derived authorship recital and any
imported vote list. That parser is advisory today and takes one name token, so
it would have to be hardened for multi-token surnames before it could be the
normalization target in fact rather than in intent.

Two layers of rights apply, and they are different:

- **The underlying records are public.** Federal court opinions and docket data are
  public records of the U.S. federal courts — public domain, and the facts within
  them are not copyrightable.
- **CourtListener's own content is licensed CC BY-ND 4.0** (Attribution-NoDerivatives),
  except where indicated — covering Free Law Project's curation and value-adds, not
  the public-domain records themselves.

Attribution is given in the README *Data & attribution* section and the top-level
[`NOTICE`](../NOTICE), and is required wherever CourtListener content is surfaced.

## What we redistribute

The NoDerivatives term is why the **derived corpus is not publicly republished**.
The raw-fact corpus — every docket, snapshot, judge, and case record drawn from
CourtListener — lives in the **access-gated** private S3 corpus remote, never in
public git (see [data-pipeline.md](data-pipeline.md) → *Storage*). It is an internal
working set, not a public dataset. There is a **second gated location, on the
same terms**: the staging corpus (see *The staging corpus (provisioning
runbook)* in [security.md](security.md)), a lean slice of that same content
copied into its own private bucket pair for integration testing. The NoDerivatives posture travels with the copy — same
access gate, no wider read principal, and nothing published from it — because
what governs is the content, not where it happens to sit.

What does go to **public git** under `data/` is only our **own work product**: the
model-generated predictions, outcomes, and evaluations, keyed by case id, plus the
reasoning text that explains them — and the two qp-topic artifacts
(`docs/qp-topic.md`), the hand-labeled reference set and a labeling run's
per-case labels: subject-matter judgments keyed by case id and public-record
docket number, republishing no source text. One **non-git** public channel is
argued in the same place and nowhere else, carrying two one-day GitHub Actions
artifacts: the extract of stored questions-presented text the labeling run
passes between its two jobs, and the labeler's scanned transcript, which
embeds the same text; on a public repository any logged-in user can download
either for its retention window.
That text is derived from petition PDFs fetched from supremecourt.gov — public
records, outside the CC BY-ND term above — and the channel is accepted for that
run alone, not as a route for corpus content generally. That reasoning may quote or summarize
public-record docket facts in the course of explaining a prediction; it is original
analysis attributing CourtListener as the source, not a republication of their
dataset. The public surface is therefore our derived judgments over public-domain
facts — not a redistribution of the bulk corpus.

## Pull cadence and the API budget

The automated consumer stays within CourtListener's published API limits by design:

- **The supremecourt.gov channels spend no API budget** — the Court's
  site has no metered API; the client is simply polite (browser user-agent,
  ~1 request/second, backoff on errors).
- **SCDB would spend none either.** It publishes no API — access is bulk file
  download only, including CSV and Stata, offered as case-centered and
  justice-centered cuts (each organized by citation, by docket, or by
  issue/legal provision). So that channel's cost is a release pin and a
  re-download when the release moves, not a request budget, and it competes
  with nothing below.
- **`pull` owns the CourtListener API budget**, throttled in-process
  (`courtlistener/ratelimit.py`) to the ceilings set in the prod environment
  (`FEDCOURTS_COURTLISTENER_RPM` / `_RPH` / `_RPD`, wired from repo variables
  to the held Free Law Project tier — see [budget.md](budget.md)), with
  per-run caps in [`config/tracking.yaml`](../config/tracking.yaml) well under
  them.
- **Opinion enrichment shares that budget**, through the same client and the
  same configured ceilings: up to three requests a case (the docket, its
  opinion cluster, then the cluster's first opinion), dropping to two where a
  stored REST-shaped snapshot already links the cluster and to one where the
  docket links no cluster to follow. It is deliberately scoped to
  the **cert-granted SCOTUS slice** — ≈1,250 dockets all-time, ≈120–130 a Term
  ongoing — which bounds a sweep of the standing backlog at ≈3,750 requests and
  a Term's new grants at ≈400, inside the allowance the four pull windows
  leave (they commit ≈360 of the 1,400/day); its own `--max-cases` bounds any
  single run. The
  governor is per-process rather than shared, so the pass is run outside a pull
  window: two processes throttling independently would each stay under the
  ceiling while the account did not. Opinion coverage
  at bulk scale is not a REST problem: the **database replication** channel
  named above remains the intended route to opinion bodies across the whole
  corpus, and nothing here is a step toward reading them out of the API
  instead.

The pilot holds a paid Free Law Project **membership tier** — the top
published tier, so more throughput now means the replication agreement (or
shifting work to the budget-free supremecourt.gov channels), never a code
change to the governor.

**One account, one credential.** The project holds a single CourtListener
account and a single API credential, surfaced under one name everywhere it is
consumed. The rate limits above are the account's, so they are a property of
the membership tier and cannot be widened by how the pipeline is arranged:
splitting work across additional accounts, or issuing a second credential to
raise effective throughput, is **not an available option** — it would violate
the terms the access rests on, and it is the kind of workaround a
throughput problem invites. The honest paths are the ones named above: the
replication agreement, or shifting work to the budget-free supremecourt.gov
channels.

## PII stance

Federal dockets can carry personal data about parties, counsel, and third parties.
Our position is **minimal collection, gated storage, and a hard floor on sensitive
material**:

- **We ingest only what is already in the public upstream records** — no separate
  collection, enrichment, or de-anonymization, and no redaction beyond what
  CourtListener already applies to the public records.
- **Raw facts stay access-gated.** The corpus that holds the full docket detail
  lives in the private S3 corpus remote, not public git. The only PII that can reach
  public git is whatever a piece of reasoning quotes from a public docket while
  explaining a prediction.
- **Sealed, privileged, or otherwise sensitive material is never fed into the
  pipeline** — asserted in [SECURITY.md](../SECURITY.md) and restated here. The
  scope is public-record federal appellate and Supreme Court dockets only.
- **A vote record raises no PII question.** The only people named in an SCDB
  vote list are the Justices, acting as public officials in a published
  decision; nothing about who they are is collected, and the values are their
  official acts rather than personal data.

This is a research project over public court records, not a people-search service;
the design deliberately keeps the bulk personal data out of the public surface.
