No retrieval beyond the provisioned inputs. That means no `fedcourts query` or `open-events` calls, no CourtListener MCP calls, no web searches, and no statpack read.

One repository-local lookup, for output shape only: I ran a `git ls-files` / `git show HEAD:` over other dockets' `evaluations/claude-judge/*/evaluation.json` files. Its output was set aside unread, apart from a preview listing other cases' paths. I used `schemas/evaluation.schema.json` instead. I read no prediction tree for this event.
