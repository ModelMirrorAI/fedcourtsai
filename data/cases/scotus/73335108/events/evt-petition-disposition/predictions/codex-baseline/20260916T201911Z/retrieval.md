# Retrieval record

## Local material beyond the provisioned case inputs

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, flags, and tooling schemas for the output contract.
- Ran `uv run fedcourts paths --court scotus --docket 73335108 --event evt-petition-disposition --role predictor`. The first attempt failed on the default cache's read-only filesystem; the same command with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. No outcome was read.
- Read the committed `metrics/statpack.md` modern-cert disposition, paid-segment relist/CVSG, sal-v4 prior-Term band, and originating-circuit sections. Used the band table for the grant anchor; circuit rows did not supply a numerical adjustment.
- Used a local Python calculation to pool the displayed 2017-2024 baseline reached rates by their weighted denominators, obtaining n=11,580 and approximately 0.0512025. Inspected only top-level keys and date-like scalar metadata of `metrics/statpack.json` for freshness information; no build timestamp was exposed.
- No `fedcourts query` or `open-events` call; no ranged-corpus transfer line was produced. No CourtListener MCP call.

## Web retrieval

All searches were for general legal context, not this case or its outcome.

1. Attempted searches: `site.law.cornell.edu rules supremecourt rule 10 certiorari erroneous factual findings` and `site.supreme.justia.com cases federal us 502 62 Estelle McGuire habeas state law`. No usable result payload was returned.
2. Attempted to open `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx` twice; no usable page payload was returned.
3. Attempted searches for `Supreme Court Rule 10 erroneous factual findings` and `Estelle McGuire 502 U.S. 62 67 68 province federal habeas`; no usable result payload was returned.
4. Attempted to open `https://www.law.cornell.edu/rules/supct/rule_10`, then `https://tile.loc.gov/storage-services/service/ll/usrep/usrep502/usrep502062/usrep502062.pdf`, then the Cornell Rule 10 page again. These calls returned no usable payload.
5. Further browser attempts to open the Cornell Rule 10 page likewise returned no usable payload. No successful paired browser retrieval is claimed.
6. Ran credential-free `curl -L --fail --silent https://www.law.cornell.edu/rules/supct/rule_10`, stripped HTML with `sed`, and selected the discretionary-review and error-correction paragraphs with `rg`. This returned usable Rule 10 text. In the same shell call, fetching `https://supreme.justia.com/cases/federal/us/502/62/` and searching for the relevant phrases returned no usable excerpt.
7. Attempted `curl -L --fail --silent https://tile.loc.gov/storage-services/service/ll/usrep/usrep502/usrep502062/usrep502062.pdf | pdftotext - -` followed by relevant phrase selection. The command failed because `pdftotext` was unavailable; no opinion text was obtained from that attempt.
8. Ran `curl -L --fail --silent https://www.law.cornell.edu/supremecourt/text/502/62`, stripped HTML with `sed`, and selected the habeas/state-law and instructional-context passages with `rg`. The returned Estelle opinion text confirmed the legal standards used in reasoning.md. This opinion predates the petition. Cornell's Rule 10 and Estelle reproductions were the usable external sources.

No current docket search, subsequent-history lookup, target disposition retrieval, or external retrieval of this case's lower-court materials was performed.
