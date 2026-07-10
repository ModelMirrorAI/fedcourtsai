# Data sources, terms & PII

The decided position behind the README's *Data & attribution* credit: where the
case data comes from, the terms we operate under, what reaches public git, and how
personal data in court records is handled. For the ingestion mechanics see
[data-pipeline.md](data-pipeline.md); for the security controls see
[SECURITY.md](../SECURITY.md).

## Source and attribution

Case data comes from two upstream providers, through three channels:

- **[CourtListener](https://www.courtlistener.com/)**, a project of the
  [Free Law Project](https://free.law/): the **REST API** (targeted enrichment —
  `pull`) and the free **quarterly bulk-data exports** on public S3 (the frozen
  historical backfill — bulk `seed`).
- **supremecourt.gov's per-docket JSON and filed-document PDFs**, served by the
  Court itself — the live SCOTUS channel that owns SCOTUS freshness and loads
  the past-Term cert set. These are public records with no third-party license
  attached (the CourtListener terms below cover Free Law Project's curation,
  not these records). Design in [live-sources.md](live-sources.md); the
  ingested facts land in the same access-gated corpus under the same
  no-republication posture.

A further channel is planned but not yet adopted: Free Law Project's commercial
**database replication** offering, the intended eventual upstream for the
CourtListener roles once funding allows — see *The planned end-state* in
[data-pipeline.md](data-pipeline.md). Adopting it requires reviewing that
agreement's terms alongside the licenses below.

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
CourtListener — lives in the **access-gated** private DVC/S3 remote, never in public
git (see [data-pipeline.md](data-pipeline.md) → *Storage*). It is an internal
working set, not a public dataset.

What does go to **public git** under `data/` is only our **own work product**: the
model-generated predictions, outcomes, and evaluations, keyed by case id, plus the
reasoning text that explains them. That reasoning may quote or summarize
public-record docket facts in the course of explaining a prediction; it is original
analysis attributing CourtListener as the source, not a republication of their
dataset. The public surface is therefore our derived judgments over public-domain
facts — not a redistribution of the bulk corpus.

## Pull cadence and the API budget

The automated consumer stays within CourtListener's published API limits by design:

- **Bulk `seed` spends no API budget** — it reads the public bulk exports, which sit
  outside the throttle entirely.
- **The supremecourt.gov channel spends no API budget either** — the Court's
  site has no metered API; the client is simply polite (browser user-agent,
  ~1 request/second, backoff on errors).
- **`pull` owns the CourtListener API budget**, throttled in-process
  (`courtlistener/ratelimit.py`) to the ceilings set in the runner environment
  (`FEDCOURTS_COURTLISTENER_RPM` / `_RPH` / `_RPD`, wired from repo variables
  to the held Free Law Project tier — see [budget.md](budget.md)), with
  per-run caps in [`config/tracking.yaml`](../config/tracking.yaml) well under
  them.

The pilot holds a paid Free Law Project **membership tier**; if the project
ever needs more throughput, a higher tier (or the replication agreement) is
the path rather than a code change to the governor.

## PII stance

Federal dockets can carry personal data about parties, counsel, and third parties.
Our position is **minimal collection, gated storage, and a hard floor on sensitive
material**:

- **We ingest only what is already in the public bulk/API records** — no separate
  collection, enrichment, or de-anonymization, and no redaction beyond what
  CourtListener already applies to the public records.
- **Raw facts stay access-gated.** The corpus that holds the full docket detail
  lives in the private DVC/S3 remote, not public git. The only PII that can reach
  public git is whatever a piece of reasoning quotes from a public docket while
  explaining a prediction.
- **Sealed, privileged, or otherwise sensitive material is never fed into the
  pipeline** — asserted in [SECURITY.md](../SECURITY.md) and restated here. The
  scope is public-record federal appellate and Supreme Court dockets only.

This is a research project over public court records, not a people-search service;
the design deliberately keeps the bulk personal data out of the public surface.
