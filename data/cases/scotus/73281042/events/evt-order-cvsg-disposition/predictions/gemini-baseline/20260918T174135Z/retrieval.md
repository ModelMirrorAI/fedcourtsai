Read the committed statpack for base rates.

```
cat metrics/statpack.md | grep -A 30 "by CVSG status"
```

Attempted corpus query (failed due to incorrect year format for `--decided-before`, did not retry as the statpack provided the necessary base rate):
```
uv run fedcourts query --court scotus --era roberts --decided-before 2026-06-23 --full --limit 10 "First Amendment antidiscrimination laws diversity equity inclusion"
```