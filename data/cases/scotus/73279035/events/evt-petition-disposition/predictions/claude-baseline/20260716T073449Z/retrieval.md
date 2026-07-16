# Retrieval log — scotus/73279035 / evt-petition-disposition / claude-baseline / 20260716T073449Z

Mode: `forward` (retrieval unrestricted; no outcome exists to leak).

## Corpus lookups (`fedcourts` CLI, ranged backend)

1. `uv run fedcourts query --court scotus --citation "563 U.S. 421" --era 2020s --corpus-backend ranged`
   — stderr: `ranged corpus reads: 417 GET(s), 109117440 byte(s)` — **0 rows returned**.
2. `uv run fedcourts query --court scotus --citation "508 U.S. 248" --corpus-backend ranged`
   — stderr: `ranged corpus reads: 417 GET(s), 109117440 byte(s)` — **0 rows returned**.
3. `uv run fedcourts query --court scotus --topic ERISA --corpus-backend ranged`
   — stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)` — **0 rows returned**.

No similar resolved priors surfaced via the corpus query surface; base-rate context
came from the committed `metrics/statpack.md` (modern discretionary-cert base rate,
CVSG cut at 27.1% grant, relist cut, originating-circuit cut, per-Term paid/IFP
detail in `metrics/statpack.json`). Note: the "Segment base rate by salience band"
table described in the predict prompt is not present in the committed statpack.

## CourtListener MCP lookups

1. `call_endpoint dockets {id: 73279035}` — confirmed this docket (SCOTUS 25-590) is
   **not terminated** (`date_terminated: null`); the forward cell is correctly
   provisioned and no disposition exists.
2. `search type=d court=ca5 q="Aramark Aetna"` — located Fifth Circuit docket
   24-40323 (*Aramark Services v. Aetna Life Ins.*).
3. `search type=rd docket_number=24-40323 court=ca5 q="rehearing"` — en banc
   rehearing petition filed 2026-01-16; court requested a response 2026-01-23;
   response filed 2026-02-12.
4. `search type=rd docket_number=24-40323 court=ca5 q="en banc OR mandate"` — no
   later entries captured; the en banc petition appears still pending as of the
   last docketed entries.

## Web searches

None.
