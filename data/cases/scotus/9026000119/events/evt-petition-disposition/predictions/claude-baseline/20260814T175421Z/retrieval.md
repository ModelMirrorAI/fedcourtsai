# Retrieval log — claude-baseline, 20260814T175421Z

Beyond the provisioned inputs (snapshot 2026-08-14, `event.yaml`,
`record/context.json`, `record/documents/` petition + questions-presented) and
the committed `metrics/statpack.md`:

## CourtListener MCP

1. `search` (type `d`, court `gud`, q `Moylan OR "Attorney General of Guam"`)
   — located the collateral federal litigation the petition alludes to:
   *Moylan v. Supreme Court of Guam*, D. Guam 1:26-cv-00007 (filed
   2026-03-24), *Attorney General of Guam v. Supreme Court of Guam*, D. Guam
   1:26-cv-00008/-00009 (filed 2026-03-24/25). Public filings predating the
   snapshot; used as forward signal that an alternative federal forum is
   already engaged.
2. `search` (type `o`, court `scotus`, q `"Supreme Court of Guam"`) — the
   Court's historical treatment of petitions from the Supreme Court of Guam:
   one modern grant (*Limtiaco v. Camacho*, 549 U.S. 483 (2007)) against a
   string of denials (*Moylan v. Territory of Guam* (2011), *Quinata* (2011),
   *Ilagan v. Ungacta* (2013), *Enriquez* (2014, 2016), *EIE Guam Corp.*
   (2000)).

Neither query sought or surfaced this petition's own disposition (none exists
— forward cell; the petition was docketed 2026-07-27).

## Corpus tooling

No `fedcourts query` / `open-events` calls: the query surface is filter-only
(`--court`/`--disposition`/`--era` are the populated filters on SCOTUS rows)
and cannot isolate "petitions from the Supreme Court of Guam" or this topic,
so it would have returned generic SCOTUS priors adding nothing to the
statpack's band/relist/CVSG cuts, which I used instead. No `ranged corpus
reads` lines to record.
