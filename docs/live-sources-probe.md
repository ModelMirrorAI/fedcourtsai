# Live-source reachability probe: findings & Term floor (#523)

The gate on the live-channel loader ([live-sources.md](live-sources.md)): probe
`supremecourt.gov/rss/cases/JSON/<term>-<number>.json` per October Term, walking
backward from the current one, before writing any ingest code. Run 2026-07-10
from a dev container (77 requests, ~1 req/s, browser UA, zero errors or
throttle pushback):

```bash
uv run fedcourts probe-live-terms --max-term 25 --min-term 15
```

| OT | served | doc-linked entries | documents | QP | disposition order |
|----|--------|--------------------|-----------|----|-------------------|
| 25 | 7/7 | 27/65 | 71 | 0/7 | 7/7 (cert denied x7) |
| 24 | 7/7 | 19/42 | 49 | 0/7 | 7/7 (cert denied x7) |
| 23 | 7/7 | 14/30 | 38 | 0/7 | 7/7 (cert denied x6, cert dismissed x1) |
| 22 | 7/7 | 78/111 | 217 | 1/7 | 7/7 (cert denied x6, cert granted x1) |
| 21 | 7/7 | 24/44 | 66 | 0/7 | 7/7 (cert denied x7) |
| 20 | 7/7 | 0/37 | 0 | 0/7 | 7/7 (cert denied x7) |
| 19 | 7/7 | 2/41 | 5 | 0/7 | 7/7 (cert denied x7) |
| 18 | 7/7 | 2/37 | 5 | 0/7 | 7/7 (cert denied x7) |
| 17 | 7/7 | 0/42 | 0 | 0/7 | 7/7 (cert denied x6, cert dismissed x1) |
| 16 | 1/7 | 0/7 | 0 | 0/1 | 1/1 (cert denied x1) |
| 15 | 0/7 | — | 0 | 0/0 | 0/0 (—) |

Sample per Term: paid 1, 100, 400, 800; IFP 5001, 5500, 6000 (low paid and low
IFP numbers exist in every real Term, so an all-missing Term reads as "not
served"). Machine detail rides in the probe's `--report-out` JSON.

## Findings

- **JSON availability: 100 % for OT2017–OT2025**, every number, paid and IFP.
  OT2016 serves only a late-docketed straggler (16-800, docketed Dec 2016 —
  after the e-filing cutover); OT2015 serves nothing. The e-filing-era working
  assumption holds exactly.
- **Schema is stable across every served Term.** One common core key set
  (CaseNumber, DocketedDate, LowerCourt(+CaseNumbers), Petitioner(+Title),
  ProceedingsandOrder, RelatedCaseNumber, bCapitalCase, the sJson\* metadata)
  is identical OT2017→OT2025; the rest (Respondent\*, AttorneyHeader\*,
  DiscretionaryCourtDecision, LowerCourtRehearingDenied, QPLink, entry-level
  Links, Other) appear per-case, not per-era. One normalizer mapping covers the
  whole range; the optional keys must simply be optional in it.
- **Disposition orders are machine-matchable: 64/64 served records** matched a
  cert-disposition signal (`pipeline.cert_signals.match_disposition_signal`,
  the shared cert-order patterns) in plain `ProceedingsandOrder` text — e.g.
  "Petition DENIED." So the loader's ingest-time resolution (#523) and the
  live channel's outcome capture (#473) work off the shelf; every sampled
  decided petition would land resolved with a machine-readable cert label.
- **Document links have a much higher floor than the JSON: ~OT2021.** Links are
  healthy OT2021–OT2025 (petitions, appendices, BIOs; the one sampled granted
  case carries 217 documents) but near-zero OT2017–OT2020 (0–2 linked entries
  per Term) even for paid cases — the records exist, the proceedings text is
  full, but the `Links`/`DocumentUrl` fields are absent. This looks like a
  rolling retention window (~5 Terms), not an e-filing boundary. Two
  consequences: (a) document-rich replay cells (#474: petition text, QP) are
  only JSON-servable for ~OT2021+; (b) **forward-mode document fetching should
  happen near filing time** — links visible today may not be served in five
  years, so provisioning at ingest (already the design) is also the archival
  strategy. Worth a re-probe check when the loader lands to confirm the
  window's edge.
- **`QPLink` is rare on denied petitions** (1/64, the granted case). The
  questions presented for the typical denied petition must come from the
  petition PDF itself (whose first pages carry the QP), not a dedicated link —
  sizing input for #474's extract-vs-link decision.
- **Politeness posture confirmed**: browser UA required (default UA → 403,
  verified), 1 req/s sustained with zero 403/429/5xx across the run.

## Term-range decision

- **Loader floor: OT2017** — full JSON + proceedings coverage; every decided
  petition lands with a machine-readable cert label. This is the floor for the
  corpus/backtest breadth (denial base rates, calibration strata).
- **Document-rich floor: OT2021** — the slice where replay cells can be
  provisioned with petition/QP/BIO text (#474). #523's stratified sampling
  should therefore draw its document-dependent strata from OT2021+, and treat
  OT2017–OT2020 as metadata+proceedings-only rows.
