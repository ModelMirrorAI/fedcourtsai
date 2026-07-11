# Retrieval

- Consulted `metrics/statpack.md`, particularly the overall and court-level disposition base rates. The Eleventh Circuit slice reports 45 resolved cases: `other` 95.6%, `denied` 2.2%, and `granted` 2.2%.
- Consulted repository label fixtures via a source search, including `tests/cassettes/realistic-grant/reasoning.md` and the matching lines in `src/fedcourtsai/fixture.py`, solely to confirm that this pipeline treats reversal/remand as `granted` and affirmance as `denied` for an appeal-disposition event.
- Attempted CourtListener MCP opinion search: `type=o`, `court=ca11`, query `Rule 4(a)(4)(B)(i) premature notice of appeal postjudgment motion jurisdiction`, filed before 2024-09-01, five results requested. The server returned `REDIS_URL is not set; cannot access session store.` No search results were received.
- Attempted corpus lookup: `uv run fedcourts query --court ca9 --topic '3840 Trademark' --limit 10 --corpus-backend ranged`. The lookup failed before returning any prior because the remote host could not be resolved. No `ranged corpus reads: …` line was printed and no corpus result was received.
- No web searches were performed.
