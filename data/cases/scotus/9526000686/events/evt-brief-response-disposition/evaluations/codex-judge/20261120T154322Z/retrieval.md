Reviewed the staged record and the interim section of the committed statpack. All three predictions carry the same statpack digest. The local command below recovered the build they used from statpack history.

```sh
UV_NO_CACHE=1 PYTHONDONTWRITEBYTECODE=1 uv run --no-sync fedcourts statpack-at data/cases/scotus/9526000686/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline
```

The command returned build `7ea07eba62d321e1f52ef4712b1dfecf7cda8ede`, matching the frozen digest. I checked its prior-Term counts locally. No corpus query, CourtListener lookup or web search was used for this evaluation.
