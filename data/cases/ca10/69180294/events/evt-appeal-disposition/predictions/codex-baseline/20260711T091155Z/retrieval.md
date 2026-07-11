# Retrieval

Beyond the provisioned event, snapshot, and context, I consulted the following:

- `metrics/statpack.md`: overall resolved disposition rates and the Tenth Circuit court slice. The latter contains only 34 resolved cases and is not appeal-specific, so it received little weight.
- `tests/cassettes/realistic-grant/reasoning.md`: the repository's captured appeal example, used only to confirm that a granted appeal is represented as reversal/remand in this artifact vocabulary.
- Corpus lookup attempted: `uv run fedcourts query --court ca10 --era 2020s --limit 10 --corpus-backend ranged`. It failed because the remote host could not be resolved. No priors and no `ranged corpus reads` statistics were returned.
- CourtListener MCP opinion search attempted for Tenth Circuit decisions filed before September 20, 2024, using the query `Social Security disability substantial evidence harmless error`. It failed because the service's session store was unavailable. No search results were returned.

I did not query this case, its listed opinion cluster, or its disposition.
