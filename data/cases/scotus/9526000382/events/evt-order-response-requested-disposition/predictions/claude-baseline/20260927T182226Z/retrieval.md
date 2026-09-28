# Retrieval log

Forward-mode cell; retrieval unrestricted. About 16 calls in total.

## Corpus

- `uv run fedcourts query --court scotus --include-applications --era 2020s`
  — recent SCOTUS application rows (the two September 2026 grants both carried
  a requested response and referral; the same-window denials carried neither).
  stderr: `ranged corpus reads: 7 GET(s), 1703936 byte(s)`.
- `uv run fedcourts paths --court scotus --docket 9526000382 --event evt-order-response-requested-disposition --role predictor`.
- `metrics/statpack.md`, "The interim docket (applications)" section, for the
  pooled strictly-prior base rate.

## CourtListener MCP

- `search` type=d, court=scotus, docket_number=26A382 — no result (the
  application docket is not indexed).
- `search` type=o, q="Strulovitch Bain beis din seruv" — no result.

## Web

- WebSearch: "Strulovitch Bain Supreme Court stay application 26A382 beis din seruv Sotomayor".
- WebSearch: "Malliotakis v. Williams Supreme Court stay application denied 2026 Alito concurring All Writs Act state court" (learned the stay was granted, not denied).
- WebSearch: "Bain v. Strulovitch Appellate Division Second Department stay pending appeal beis din 2026".
- WebSearch: "Yeshiva University v. YU Pride Alliance September 2022 Supreme Court vacates stay 5-4 ..." (confirmed the exhaustion holding and lineup).
- WebSearch: "scotusblog Strulovitch v. Bain rabbinical court emergency application Sotomayor response".
- WebFetch supremecourt.gov docket 26A382 — live docket: Becket Fund amicus brief filed Sept 25, 2026; no disposition.
- WebFetch scotusblog.com "supreme court stays to state courts" (Malliotakis jurisdiction commentary).
- WebFetch Notre Dame Law School news release (Sept 14, 2026) on the filing.
- WebFetch morrisoncohen.com insight on the Westchester decision (neutral-principles reasoning).
- WebFetch findlaw.com, In re Application of Moshe Bain (Sup. Ct. Westchester, June 6, 2025) — motion-to-dismiss ruling, Bain's non-participation in the Rockland arbitration.
- WebFetch ideas.tikvah.org commentary (Sept 25, 2026), paywalled beyond the intro.
- WebFetch law.justia.com Matter of Bain v Strulovitch (2025) — HTTP 403, not read.
- WebFetch courtlistener storage PDF of Malliotakis v. Williams (25A914, Mar. 2, 2026), text extracted locally with pypdf: order granting the stay and Justice Alito's concurrence.

Nothing retrieved disclosed this application's disposition; none exists yet.
