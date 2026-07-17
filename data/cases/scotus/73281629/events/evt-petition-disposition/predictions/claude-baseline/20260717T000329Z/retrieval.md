# Retrieval log — scotus/73281629 evt-petition-disposition (claude-baseline, 20260717T000329Z)

Mode: `forward` (retrieval unrestricted; case confirmed still pending).

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "29 U.S.C. § 1024" --citation "72 F.3d 686" --citation "557 F.3d 781"`
  → 0 rows. stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
- `uv run fedcourts query --court scotus --topic ERISA`
  → 0 rows. stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- Read committed `metrics/statpack.md` for base rates (modern discretionary-cert
  disposition split, originating-circuit, relist, CVSG, and per-Term tables; this
  statpack version carries no salience-band table).

## CourtListener MCP

- `search(type=d, court=scotus, case_name="Premera")` → 0 results.
- `search(type=r, court=scotus, q="Premera")` → 0 results.
- `search(type=r, court=scotus, q="1024(b)(4)")` → 0 results.
  (SCOTUS dockets are not in the RECAP index; no further MCP calls made.)

## Web searches

- "Premera Blue Cross v. M.S. certiorari petition Supreme Court administrative
  services agreement ERISA 104(b)(4)" — no cert petition by Premera found; the
  Tenth Circuit's 2024 decision appears to have ended at the appellate level.
  Sources consulted: [Your ERISA Watch on M.S. v. Premera](https://www.yourerisawatch.com/2024/10/tenth-circuit-issues-mixed-ruling-in-mental-healthcare-suit-raising-parity-and-disclosure-claims/),
  [Justia — M.S. v. Premera (10th Cir. 2024)](https://law.justia.com/cases/federal/appellate-courts/ca10/22-4056/22-4056-2024-10-01.html).
- "Zavislak v. Netflix certiorari 25-1142 ERISA disclosure Supreme Court" —
  practitioner commentary on the Ninth Circuit decision and the CFR'd BIO;
  nothing postdating the July 15, 2026 distribution, nothing outcome-revealing.
  Sources consulted: [GT L&E Blog on Zavislak v. Netflix](https://www.gtlaw-laborandemployment.com/2025/10/erisa-document-disclosure-zavislak-v-netflix-inc-and-the-ninth-circuits-narrow-reading-of-section-104/),
  [Mealey's — Respondent urges denial](https://www.mealeys.com/mealeys/mealeys-erisa/articles/2494387/respondent-to-high-court-deny-petition-in-erisa-disclosure-case),
  [Law360 — Netflix urges justices not to disturb 9th Circ. ruling](https://www.law360.com/healthcare-authority/policy-compliance/articles/2493873).

Total: 2 corpus CLI calls, 3 MCP calls, 2 web searches — within the ~25-call budget.
