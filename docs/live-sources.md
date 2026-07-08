# Live sources: predicting genuinely pending cases

The design for the **live prediction** track: discovering cases while they are
still pending — minutes-to-hours fresh, not rotation-fresh — and provisioning
predictors with case *content*, not just docket metadata. It complements the
CourtListener channels in [data-pipeline.md](data-pipeline.md): those own the
historical corpus and the budget-governed refresh; this track owns the live
frontier the September cert task predicts on. Only predictions made while an
event is genuinely unresolved land in the **forward** stratum
([metrics/README.md](../metrics/README.md)) — the whole point of this design is
to make that stratum large and honest.

## Why the rotation is not enough

Forward-stratum prediction has two needs the budget-governed pull rotation
cannot meet:

- **Discovery latency.** The rotation discovers new filings within its request
  budget and window cadence — hours to days. A cert petition distributed for
  conference resolves on a known calendar; predicting it requires knowing it
  exists (and that it was distributed) *before* the conference.
- **Input richness.** Cert prediction leans on the questions presented, the
  petition and brief in opposition, and procedural signals (response requested,
  CVSG, distribution). CourtListener's SCOTUS docket records carry little of
  this; the underlying documents none of it.

Neither need is answered by a higher CourtListener tier — a bigger budget buys
faster polling of the same records, not fresher discovery or richer content.

## The SCOTUS live source: supremecourt.gov docket JSON

The Supreme Court's own site serves a structured JSON docket per case:

```
https://www.supremecourt.gov/rss/cases/JSON/<term>-<number>.json
```

Each record carries the full **proceedings list** as dated entries (petition
filed, response requested, briefs, "DISTRIBUTED for Conference of <date>",
disposition orders), **direct PDF links to every filed document** (all filings
are public on the docket since the 2017 e-filing mandate), a **questions
presented** link, the lower court and its docket numbers, parties, and counsel.
This is the authoritative record, fresher than any scrape of it, with **no API
budget** — the constraint that shapes the CourtListener channels simply does
not exist here.

Three access facts shape the client:

- Requests need a browser user-agent (the default programmatic UA is refused).
- There is no push feed and no "list new dockets" endpoint. **Discovery is
  sequential probing**: docket numbers are per-Term sequential (paid petitions
  from `25-1`, IFP from `25-5001`), so a poller probes the next unseen numbers
  and a 404/empty record marks the current frontier.
- Be a polite client: throttle to ~1 request/second, back off on errors, and
  poll on a cadence matched to the docket's rhythm (hourly for the conference
  watchlist, daily for frontier probing) rather than hammering.

## Architecture: a third channel, the same corpus

The live source follows the replica guardrails exactly
([data-pipeline.md](data-pipeline.md), *The planned end-state*): it is a new
**channel**, never a new consumer surface.

- **Ingestion stays channel-agnostic.** The docket JSON maps onto the same
  normalized corpus row in the shared normalization layer (a third
  `CorpusSource`), and the raw JSON — proceedings and document links included —
  is stored as the case's dated **snapshot**, exactly like a REST pull. The
  proceedings list is the docket-entries analogue, so event extraction,
  resolution detection, and replay redaction (which strips entries wholesale)
  work unchanged.
- **The corpus stays the system of record.** Live-ness comes from trigger and
  cadence, not from bypassing the corpus: a watchlist refresh that finds a
  changed docket ingests it and queues `predict` through the same seams the
  rotation uses. Replay integrity, fan-out comparability (every predictor reads
  the same snapshot), validation, and stratification all depend on this — a
  predictor never fetches the live site itself.
- **Identity is reconciled by docket number.** The corpus keys cases on
  CourtListener docket ids, which a petition first seen at supremecourt.gov
  does not have. The join key is the normalized Term-form docket number, which
  both sources carry: a live ingest first looks for an existing SCOTUS row with
  the same normalized number and enriches it; only a genuinely unseen petition
  mints a new row (id allocation for that case is the channel's one real schema
  decision — see the implementation issue).

## The live cert watchlist and conference detection

The consumer this channel exists for: a maintained watchlist of pending cert
petitions, refreshed on a cadence, with **conference membership parsed from the
proceedings** ("DISTRIBUTED for Conference of October 10, 2025"). That yields,
continuously and for free, what the long-conference task needs: the set of
petitions before each conference, discovered while they are pending — so
predictions fire ahead of the conference and score against the order-list
outcome days later, all in the forward stratum.

## Documents: from metadata to content

The document PDFs linked from each docket are the step-change in input quality
— the questions presented and the petition/BIO are the signals cert prediction
actually turns on. Two rules govern their use:

- **The pipeline fetches; agents never do.** Document text is fetched and
  extracted at ingest/provisioning time and attached to what the cell is
  provisioned with, so the snapshot rule ("predict from the snapshot") holds
  and every predictor reads identical inputs.
- **SCOTUS documents are free; circuit documents are not.** supremecourt.gov
  serves all SCOTUS filings at no cost. Circuit-court documents come from the
  RECAP archive when already liberated, else the RECAP Fetch API purchases them
  from PACER at PACER prices — a later, costed extension.

## Later: push for the circuit courts

CourtListener's **webhooks** (docket alerts fire within seconds of PACER
filings; search alerts batch ~5 minutes; retries + idempotency keys built in)
are the right liveness mechanism for the *circuit* dockets the pipeline tracks
— the Big Cases bot (`freelawproject/bigcases2`) is a running reference of
exactly this pattern. Adopting them needs two things this project does not have
yet: a public HTTPS receiver (GitHub Actions cannot receive webhooks, so a
minimal relay converts the webhook into a `repository_dispatch`) and an
organizational agreement with Free Law Project, which belongs in the same
conversation as the database replica. Until then, circuit liveness stays on the
rotation; SCOTUS — where the September task lives — does not wait on it.

## Terms

supremecourt.gov docket data and filings are public records of the U.S. federal
courts, served by the Court itself — no third-party license attaches (contrast
the CourtListener CC BY-ND terms in [data-sources.md](data-sources.md), which
cover Free Law Project's curation, not these records). The same
no-republication posture still applies to the packed corpus as a whole.
