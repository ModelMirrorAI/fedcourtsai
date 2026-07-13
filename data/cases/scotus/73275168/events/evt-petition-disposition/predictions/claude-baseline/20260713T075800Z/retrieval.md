# Retrieval log — scotus/73275168 / evt-petition-disposition / claude-baseline / 20260713T075800Z

Mode: `forward` (pending case; retrieval unrestricted). This case's own outcome
was never sought — it does not yet exist.

## Corpus lookups (`fedcourts`, ranged reads against the remote)

1. `uv run fedcourts query --court scotus --topic "sentencing guidelines commentary deference" --limit 8`
   — similar resolved priors. **0 rows.**
   `ranged corpus reads: 3 GET(s), 786432 byte(s)`
2. `uv run fedcourts query --court scotus --topic "sentencing guidelines" --limit 8` — **0 rows.**
   `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --topic "sentencing" --limit 10` — **0 rows.**
   `ranged corpus reads: 3 GET(s), 786432 byte(s)`
4. `uv run fedcourts query --court scotus --topic "criminal" --limit 5` — **0 rows.**
   (same shell invocation as #5)
5. `uv run fedcourts open-events --court scotus --docket 73275168` — confirmed the
   single open event `evt-petition-disposition`.
   `ranged corpus reads: 3 GET(s), 786432 byte(s)` (combined stderr for #4+#5)

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition"
  (Term-2025 slice, denial-reweighted grant rate 4.9%); originating-circuit cut
  (ca7 row: 8 resolved, all denied — small n); relist and CVSG cuts unpopulated.

## Web searches (engine-surfaced)

1. `Supreme Court cert granted Sentencing Guidelines commentary deference Kisor Loper Bright 2026`
   — purpose: determine whether a companion case on the same question presented
   was granted (explaining Poore's relist-then-silence pattern). Found the
   April 20, 2026 grant in *Beaird v. United States*, No. 25-5343
   (Sentencing Law & Policy blog; fd.org; AFPF; lisa-legalinfo.com).
2. `"Beaird" Supreme Court 25-5343 Stinson certiorari granted amicus appointed`
   — purpose: verify the *Beaird* grant date, the limited question presented,
   and the appointment of Anthony Dick as amicus to defend *Stinson*
   (SCOTUSblog case file; supremecourt.gov docket 25-5343; Wikipedia;
   ArentFox Schiff alert). Both searches concerned related litigation, not this
   petition's disposition.

## CourtListener MCP

No CourtListener MCP calls — the provisioned snapshot, filed-document texts,
and the two web searches above answered everything this prediction needed.
No REST fallback used.
