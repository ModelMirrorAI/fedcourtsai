# Retrieval beyond provisioned inputs

## Committed statistical context

- Read the merits, per-Justice merits-vote, and authorship portions of `metrics/statpack.md` and `metrics/statpack.json`. Only eligible prior Terms informed the quantitative anchor and writing/vote references. OT2025 metadata was visible during structural inspection but was not used in those references. A read-only statistical-review agent independently verified the pooling arithmetic and coverage limits.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` to request source-corpus vintage. It failed because the service backend has no client-side connection; no vintage or case data was returned. No `query` or `open-events` lookup was used, so there are no ranged-corpus-read transfer lines to report.

## General predecessor law, CourtListener MCP

1. `search(type="o", citation="564 U.S. 410", num_results=1)` returned American Electric Power Co. v. Connecticut, decided June 20, 2011, including lead opinion ID **7263682**.
2. `search_document(opinion_id=7263682, query="state law", snippet_size=700)` checked the federal-common-law displacement/state-law preemption distinction, including the discussion at 564 U.S. 429–430. Used as a constraint on the forecast, not as a disposition of this case.
3. `search(type="o", citation="479 U.S. 481", num_results=1)` produced an unrelated district-court result, Register v. Cameron & Barkley Co. Only the returned search metadata/snippet was visible; it was not used as authority and its full opinion was not opened.
4. `search(type="o", court="scotus", case_name="International Paper Co. v. Ouellette", num_results=1)` located the January 21, 1987 Supreme Court decision, lead opinion ID **9430783**.
5. `search_document(opinion_id=9430783, query="affected State", snippet_size=450)` checked the Clean Water Act's source-state/affected-state allocation and the concern that affected-state tort liability could override permitting choices. Used by analogy; not treated as a Clean Air Act holding.

No CourtListener search sought this case, its subsequent history, its disposition, or decision coverage. No direct CourtListener REST access was attempted.

## Unproductive web attempts

- Attempted general predecessor searches for `site.supremecourt.gov opinions American Electric Power Connecticut displaced federal common law state law 2011 10-174` and `site.loc.gov International Paper Ouellette 479 U.S. 481 source state nuisance`.
- Attempted to open the Supreme Court's AEP opinion PDF at the official opinions/10pdf/10-174.pdf path.
- Both web tool invocations returned no usable content. No facts or outcome information came from them; the usable predecessor-law checks were the MCP lookups above.

## Local support and review

Read the task contract, output schemas, and local path/serialization and claim-validation helpers. Ran the predictor `paths` command. An initial CLI attempt could not write its default uv cache; setting `UV_CACHE_DIR=/tmp/uv-cache` resolved that environment issue. Independent transcript analysis used only this cell's provisioned transcript and features. No other predictor/evaluator output, outcome artifact, or labeling-measurement artifact was read.
