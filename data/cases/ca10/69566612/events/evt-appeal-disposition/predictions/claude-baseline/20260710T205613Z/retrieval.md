# Retrieval log — ca10/69566612 evt-appeal-disposition (claude-baseline, 20260710T205613Z)

## Corpus tooling

- `uv run fedcourts query --court ca10 --corpus-backend ranged`
  - `ranged corpus reads: 38 GET(s), 9895936 byte(s)`
  - 20 priors returned (18 `other`, 2 `denied`); no medical-malpractice or
    EMTALA topic among them — nothing on point, used only to confirm the CA10
    cut is thin.
- Read the committed `metrics/statpack.md` for base rates. CA10 row: 34
  resolved, `other` 88.2% / `denied` 11.8% — small n, cert-flavored labels,
  weighted lightly.

## CourtListener

The configured CourtListener MCP server never connected in this cell (its
tools were not discoverable), so I fell back to the CourtListener REST API v4
directly with the provisioned token — same data source, logged here per the
contract:

1. `GET /api/rest/v4/audio/96337/` — oral-argument metadata for this appeal
   (argued 2025-01-21, 1886 s; no panel/judges populated).
2. `GET /api/rest/v4/search/?type=r&q=Koel "Citizens Medical Center"&court=ksd`
   — located the underlying district case, D. Kan. 2:21-cv-02166 (docket id
   59807235), Judge Holly Teeter, cause "28:1331 Fed. Question: Medical
   Malpractice". Search deliberately restricted to `ksd` so the CA10 opinion
   could not surface.
3. `GET /api/rest/v4/docket-entries/?docket=59807235&order_by=-date_filed&page_size=20`
   — final district-court entries: 2023-10-10 summary-judgment order (EMTALA),
   companion Dr.-Fry evidentiary order, and dismissal of state-law claims
   without prejudice. (Incidentally revealed that three post-appeal entries
   exist, Apr–Oct 2025, blank descriptions — not opened, not used; disclosed
   in `flags.json`.)
4. `GET /api/rest/v4/search/?type=o&q=Koel "Citizens Medical"&court=ksd` — 0
   results (no indexed D. Kan. opinion).
5. `GET /api/rest/v4/docket-entries/?docket=59807235&entry_number=178` — located
   the RECAP document for the summary-judgment order.
6. `GET /api/rest/v4/recap-documents/374804441/?fields=plain_text` — full text
   of the 20-page D. Kan. memorandum and order under review (the primary input
   to my analysis beyond the snapshot).

Not retrieved, deliberately: this appeal's opinion cluster
(`clusters/10338143` in the snapshot), the CA10 docket beyond the provisioned
snapshot, and any web coverage of the decision — the cell is marked `forward`
but the snapshot indicates the case is decided, so I treated outcome-adjacent
material as off-limits.

## Web searches

None.
