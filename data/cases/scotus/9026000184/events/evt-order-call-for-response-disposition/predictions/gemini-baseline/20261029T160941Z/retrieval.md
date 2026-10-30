# Retrieval Log

1. `uv run fedcourts query --court scotus --era roberts --disposition denied --limit 5`
   - **Result:** Usage error (`Unknown era 'roberts'; an era is one decade token`, exit code 2). Re-issued with `--era 2020s`.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - **Transfer:** `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - **Result:** Returned 5 recent resolved 2020s SCOTUS rows (`scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9526000555`, `scotus/9526000556`).
3. `uv run fedcourts query --court scotus --docket-number 25A1468 --include-applications --include-open`
   - **Transfer:** `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - **Result:** Returned 1 row (`scotus/73559895`, `docket_number: "25A1468"`, *Defense Distributed, et al. v. Jennifer Davenport, Attorney General of New Jersey*, time-extension application granted 2026-07-07).
