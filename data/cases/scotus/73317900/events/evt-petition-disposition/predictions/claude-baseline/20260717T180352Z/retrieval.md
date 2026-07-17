# Retrieval log — scotus/73317900 evt-petition-disposition (claude-baseline, 20260717T180352Z)

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --disposition gvr --era 2020s`
   — pulled recent SCOTUS GVR priors (e.g., *Whitton v. Dixon* 25-580,
   *FBI v. Fazaga* 25-430, *Bannon v. United States* 25-453, *Full Play
   Group* 25-390) to calibrate the GVR reference class. The first
   invocation's stderr transfer line was consumed by an output pipe and not
   captured; an immediate identical rerun (warm service cache) printed:
   `ranged corpus reads: 0 GET(s), 0 byte(s)`.
2. Base rates: read the committed `metrics/statpack.md` (modern
   discretionary-cert grant rates, per-Term table, relist/CVSG/circuit cuts).
   No salience-band section is present in the committed statpack version.

## CourtListener MCP lookups

1. `search` (opinions, scotus, q=`Jules "Andre Balazs"`) — located the
   *Jules v. Andre Balazs Properties* decision, No. 25-83, decided 2026-05-14
   (cluster 10858761).
2. `call_endpoint` (clusters, id=10858761) — confirmed author
   (Sotomayor, J.) and date.
3. `search` (opinions, scotus, docket 25-83, q=`"jurisdictional anchor"
   "Second Circuit"`) — attempted snippet retrieval; the search index exposed
   no snippet field, so this returned only the case row.
4. `call_endpoint` (opinions, id=11326163, fields=plain_text) — retrieved the
   *Jules* slip opinion text: unanimous affirmance of the Second Circuit,
   holding a court that stayed a pending action under FAA § 3 retains
   jurisdiction over §§ 9–10 motions without an independent jurisdictional
   basis.

## Web searches

None.

## Leakage discipline

All retrieval concerned *Jules* (a companion/lead case decided 2026-05-14,
before this snapshot) and historical corpus priors. Nothing was retrieved
about this petition's own disposition, which does not yet exist (forward
mode).
