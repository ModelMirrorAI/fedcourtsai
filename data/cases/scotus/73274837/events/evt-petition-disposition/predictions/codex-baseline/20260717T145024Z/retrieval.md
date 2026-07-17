# Retrieval beyond provisioned inputs

## Corpus tooling

- Attempted: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '597 U.S. 1' --citation '602 U.S. 680' --limit 10`
  - Result: `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): [Errno 1] Operation not permitted`
  - No `ranged corpus reads: …` line was printed because the request did not reach the service.
- Consulted `metrics/statpack.md` and `metrics/statpack.json` for modern cert, relist, Term, and paid-petition base rates.

## CourtListener MCP

1. Opinion search for `"Gator's Custom Guns" Washington`; found *State v. Gator's Custom Guns, Inc.*, 568 P.3d 278 (Wash. 2025), cluster 10572433.
2. Cluster lookup 10572433 for docket and sub-opinion metadata.
3. Opinion lookup 11039021 for the Washington Supreme Court's combined opinion text.
4. Opinion search for `Benson "large capacity magazines" Second Amendment`.
5. Opinion search for `Bensen magazine Second Amendment` to check the spelling shown in a snapshot document filename.
6. Opinion search for `"large-capacity magazines" "common use" Bruen`, limited to decisions after June 22, 2022; surfaced *Duncan*, *Lamont*, and the 2026 Seventh Circuit litigation.
7. Cluster lookup 10925244 for *Barnett v. Raoul* metadata.
8. Opinion lookup 11392781; the requested text field was empty.
9. Cluster lookups 10925238, 10925239, 10925241, and 10925237 for the consolidated Seventh Circuit cases.
10. Opinion lookups 11392775, 11392776, 11392778, and 11392774 for the consolidated Seventh Circuit decision; the retrieved opinion states that the court reversed an injunction and upheld the Illinois restrictions, with a dissent.
11. SCOTUS opinion search for `Wolford`, limited to decisions after January 1, 2025; found *Wolford v. Lopez*, cluster 10880241.
12. Cluster lookup 10880241 for *Wolford* docket and sub-opinion metadata.
13. Opinion lookup 11347760 for the June 25, 2026 *Wolford* opinion and syllabus.
14. Cluster lookup 10804155 for *Benson v. United States* metadata.
15. Opinion lookup 11270885 for the March 5, 2026 divided D.C. Court of Appeals panel opinion concerning magazines over ten rounds.
16. SCOTUS opinion search for case name `Snope`; no results.
17. SCOTUS opinion search for `Snope v Brown 145 S. Ct. 1534`; no results.
18. Cluster lookup 10360607 for *Duncan v. Bonta*, 133 F.4th 852 (9th Cir. 2025).
19. Opinion lookup 10827195 for the en banc Ninth Circuit opinion and summary in *Duncan*.

No general web search was used, and no search sought this petition's disposition.
