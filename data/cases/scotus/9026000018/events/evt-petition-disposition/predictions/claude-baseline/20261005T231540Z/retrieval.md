# Retrieval log

## Corpus lookups (`fedcourts`, read-only)

1. `uv run fedcourts paths --court scotus --docket 9026000018 --event evt-petition-disposition --role predictor`
   (path resolution only; no transfer line printed).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   stderr: `ranged corpus reads: 27 GET(s), 6946816 byte(s)`
   Returned recent OT2025/OT2026 grants (Missionaries of Saint John the Baptist
   v. Frederic, Marschner v. Marschner, Rhoney v. Barbosa da Cunha, and several
   substantive applications). Used only as a sanity check on what the corpus's
   "granted" rows look like; none is a comparable prior for a state-petitioner
   mootness question, and none fed the number.
3. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 6`
   stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   Returned recent GVRs (Garcia v. Hobbs, Trevino v. Hobbs, Mullin v. National
   TPS Alliance, two IFP criminal GVRs, Monsanto v. Salas). Confirmed that the
   GVR route in the corpus rides on an intervening decision, which this case
   lacks; informed the summary-disposition-route conditional only qualitatively.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
  "Cert petitions by relist count (paid scored segment)", "Cert petitions by
  CVSG status (paid scored segment)", "SCOTUS cert petitions by Term", and
  "Segment base rate by salience band (sal-v4)" (pooled the state band's
  bracketed `reached` figures over OT2017 to OT2025; arithmetic in
  `reasoning.md`).

## CourtListener MCP lookups

1. `search` type `d`, court `scotus`, docket_number `26-18` (fields: caseName,
   docketNumber, dateFiled, docket_id, absolute_url). Result: 0 hits. Purpose:
   check for docket entries after the provisioned snapshot. Nothing about this
   case's disposition surfaced.
2. `search` type `o`, court `scotus`, query `"capable of repetition" "evading
   review" "Prison Litigation Reform Act" "90 days"`. Result: 0 hits. Purpose:
   check whether the Court has addressed the PLRA 90-day limit under the
   mootness exception. No opinion found.

## Web searches

None.
