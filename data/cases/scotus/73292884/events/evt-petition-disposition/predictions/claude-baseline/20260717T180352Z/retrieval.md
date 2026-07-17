# Retrieval log — scotus/73292884 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Forward-mode cell; retrieval unrestricted. Beyond the provisioned inputs
(snapshot `2026-07-17.json`, `documents/petition.txt`,
`documents/questions-presented.txt`, `record/context.json`, the event
definition) and the committed `metrics/statpack.md` / `metrics/statpack.json`
(read for paid-class and relist/CVSG base rates), I consulted:

## Corpus lookups (`fedcourts query`, service-backed)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   — recent granted SCOTUS priors, to sanity-check what grant-side rows look
   like (distribution counts, salience fields).
   stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
2. Same command re-run to inspect the full field set of one row.
   stderr: `ranged corpus reads: 145 GET(s), 37879808 byte(s)`

`--topic` / `--citation` were not tried: topic is circuit-only and citation is
a known-case lookup; neither fits "post-AFPF disclosure petitions".

## CourtListener MCP lookups

1. `search(type=d, court=scotus, case_name="Gaspee Project")` — 0 results
   (SCOTUS dockets are not in the docket search index).
2. `search(type=d, court=scotus, case_name="Wyoming Gun Owners")` — 0 results.
3. `search(type=d, court=scotus, q="donor disclosure First Amendment")` — 0 results.
4. `call_endpoint(dockets, {court: scotus, case_name__icontains: Gaspee})` —
   validation error (filter not permitted on that endpoint); not retried.
5. `search(type=o, q="\"Gaspee Project\"")` — 15 results; used the top hits to
   confirm the post-AFPF circuit case family upholding disclosure applied to
   issue speech: *The Gaspee Project v. Mederos*, 13 F.4th 79 (1st Cir. 2021);
   *No on E v. Chiu* (9th Cir.); *Rio Grande Foundation v. Oliver* (10th Cir.
   2025, this case's opinion below — metadata only, already in the record).

## Training knowledge (disclosed, not retrieved)

The cert fates of the analogous earlier petitions (*Delaware Strong Families v.
Denn* denied 2016; *Independence Institute v. FEC* summarily affirmed 2017;
*Gaspee Project* denied 2022; *No on E* denied ~2024) come from training
knowledge — CourtListener's SCOTUS docket coverage did not let me re-verify
them within budget. All pre-date this petition and none concerns this case's
own (nonexistent) outcome.

No web searches were run. No lookup touched this case's own disposition; the
case is genuinely pending (BIO due 2026-07-27).
