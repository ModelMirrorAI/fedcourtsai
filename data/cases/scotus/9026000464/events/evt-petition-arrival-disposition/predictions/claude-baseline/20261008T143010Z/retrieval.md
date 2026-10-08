# Retrieval log

## Corpus (via the cell's corpus service)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7274496 byte(s)`
  Returned eight recent SCOTUS grants, none topical (no originating-court or text filter exists); used only to confirm the service was reachable and to see the shape of recent grants.

## CourtListener MCP

1. `search` (type `o`, court `cafc`, q `"Hamp's Construction" "Secretary of the Army"`, filed after 2026-01-01): one hit, cluster 10882238, *Hamp's Construction LLC v. Secretary of the Army*, No. 24-1528, decided 2026-06-30, status Published.
2. `search` (type `d`, court `scotus`, docket number `26-464`): zero results; the Supreme Court docket is not yet indexed on CourtListener.
3. `get_endpoint_item` (`clusters`, 10882238): confirmed Published, a single combined opinion, no separate writings.
4. `get_endpoint_item` (`opinions`, 11349763, `plain_text`): read the full Federal Circuit opinion. Panel Lourie, Reyna, Cunningham; opinion by Cunningham, J.; unanimous affirmance; forfeiture holdings on the construction-traffic-drawings and absence-of-borings arguments; substantial-evidence deference to the Board's finding that west-bank conditions were visibly worse.
5. `search` (type `o`, court `scotus`, q `"differing site conditions"`, newest first): zero results.

No web searches. No retrieval touched this case's outcome; the petition was docketed 2026-10-07 and nothing has been decided.
