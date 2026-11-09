# Corpus Retrieval Log

## Queries Executed

1. **Query 1 — Recent OT2026 / 2020s SCOTUS granted petitions:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
   - Returned: 10 rows (`scotus/73520108`, `scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`).
   - Selection: Included `scotus/73520108` (*Goldman Sachs Bank USA v. Brown*, No. 25-1408, `originating_court = ca4`, granted 2026-11-06 after `distribution_count = 4`) and `scotus/9026000012` (*Association for Education Fairness v. Montgomery County Board of Education*, No. 26-12, `originating_court = ca4`, granted 2026-10-19 after `distribution_count = 3`) in `prior_case_ids` as Fourth Circuit OT2026 comparators showing multi-distribution grant patterns.

2. **Query 2 — Round 1 cert petition in this exact litigation (No. 22-240):**
   - Command: `uv run fedcourts query --court scotus --docket-number 22-240`
   - Transfer line: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Returned: 1 row (`scotus/72475563`, *Jim Justice, Governor of West Virginia, et al. v. Jonathan R., Minor, By Next Friend Sarah Dixon, et al.*, No. 22-240, `originating_court = ca4`, `disposition = denied`, `date_decided = 2022-10-11`, `distribution_count = 1`, `salience_score = 0.0334`).
   - Selection: Included `scotus/72475563` in `prior_case_ids` because it is the prior certiorari petition in this exact lawsuit, which the Supreme Court denied after one distribution when West Virginia sought interlocutory review of the Fourth Circuit's first reversal.

3. **Query 3 — Prior cert petition on structural injunctions / consent decrees cited in the petition (No. 25-165):**
   - Command: `uv run fedcourts query --court scotus --docket-number 25-165`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: 1 row (`scotus/73274852`, *Sault Ste. Marie Tribe of Chippewa Indians v. Michigan, et al.*, No. 25-165, `originating_court = ca6`, `disposition = denied`, `date_decided = 2026-01-12`, `distribution_count = 1`).
   - Selection: Included `scotus/73274852` in `prior_case_ids` because Petitioners expressly cite it (Pet. 27) as a recent petition asking the Court to address structural decrees.

4. **Query 4 — Prior cert petition in a state foster-care structural reform and Rule 23(b)(2) class action cited in the petition (No. 19-765):**
   - Command: `uv run fedcourts query --court scotus --docket-number 19-765`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: 1 row (`scotus/66727435`, *Michael Faust, Director, Arizona Department of Child Safety v. B. K., By Her Next Friend Margaret Tinsley, et al.*, No. 19-765, `originating_court = ca9`, `disposition = denied`, `date_decided = 2020-03-23`, `distribution_count = 1`).
   - Selection: Included `scotus/66727435` in `prior_case_ids` because it is the closest substantive and procedural analogue in the corpus — a state child-welfare director's certiorari petition challenging the Ninth Circuit's decision (*B.K. ex rel. Tinsley v. Snyder*, 922 F.3d 957 (9th Cir. 2019), relied on by the Fourth Circuit below) upholding Article III standing/redressability and Rule 23(b)(2) class certification in a statewide foster-care reform suit.

## External Sources Checked

- None (`courtlistener` MCP tools were not needed because the provisioned `record/documents/` directory already contained the complete petition, the full Fourth Circuit majority and dissenting opinions, the district court's opinion in the appendix, and the lower-court docket summary, and no blinding cutoff was ever approached).
