# Evaluator Retrieval Log — `scotus/9526000686` (`evt-brief-response-disposition`)

## Local Committed Reference Reads

- Read `metrics/statpack.md` and `metrics/statpack.json` (lines 575–1450) to verify the committed OT2016–OT2025 interim finer-reading counts, `private` × `capital` applicant-class cuts, and `response-filed` moment counts cited in predictor rationales. All predictors shared the committed `statpack_digest` (`sha256:51adef9eb718f3df6423188358b9c32ada5eda492c113a279dca2a17bbba64c4`), so `fedcourts statpack-at` was not needed.

## Corpus CLI (`fedcourts`) Lookups

- None (`used_corpus_query: false`).

## CourtListener MCP Lookups

Used solely to verify lower-court holdings and factual representations cited in predictor `reasoning.md` files (never used to grade `predicted_reasoning.md`, which was evaluated strictly against the staged record):

1. `mcp_courtlistener_read_document` (`opinion_id=11528932`, full read)
   - Returned the Florida Supreme Court's November 13, 2026 per curiam opinion in *Thomas M. Overton v. State of Florida & Thomas M. Overton v. Secretary, Department of Corrections*, Nos. `SC2026-1724 & SC2026-1725` (`26,614` chars, 17 slip pages), confirming what claims were decided below and on what procedural or merits grounds.
2. `mcp_courtlistener_read_document` (`opinion_id=11516852`, `chunk_index=0`, `chunk_size=16000`) and `mcp_courtlistener_read_document` (`opinion_id=11516852`, `chunk_index=1`, `chunk_size=16000`)
   - Returned chunks 0 and 1 (`32,127` total chars) of the Florida Supreme Court's October 29, 2026 opinion in *Jesse Guardado v. State of Florida*, No. `SC2026-1605`, verifying the factual background of the cited comparator opinion.

## Web Searches

- None.
