# Data sources, terms & PII

The decided position behind the README's *Data & attribution* credit: where the
case data comes from, the terms we operate under, what reaches public git, and how
personal data in court records is handled. For the ingestion mechanics see
[data-pipeline.md](data-pipeline.md); for the security controls see
[SECURITY.md](../SECURITY.md).

## Source and attribution

All case data comes from [CourtListener](https://www.courtlistener.com/), a project
of the [Free Law Project](https://free.law/), through two channels:

- the **REST API** (forward freshness — `pull`), and
- the free **quarterly bulk-data exports** on public S3 (historical backfill —
  `seed`).

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
- **`pull` owns the API budget** and is held under the **5 requests/minute, 50/hour,
  125/day** authenticated default by an in-process governor
  (`courtlistener/ratelimit.py`), with the matching ceilings declared in
  [`config/tracking.yaml`](../config/tracking.yaml) (`api_per_minute` /
  `_hour` / `_day`) and a per-run cap well under them.

The budget assumes the **standard authenticated tier** (a free API token). Higher
limits require Free Law Project **membership** or a commercial agreement; if the
project ever needs more throughput, that is the tier to obtain rather than a code
change to the governor.

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
