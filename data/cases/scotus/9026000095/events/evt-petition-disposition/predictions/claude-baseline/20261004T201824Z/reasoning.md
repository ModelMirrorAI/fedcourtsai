# Rationale for the numbers

**P(grant) = 0.003; predicted disposition: denied.**

## Anchor

`record/context.json` freezes `band: baseline` under `sal-v4`, mode `forward`,
`distribution_count: 1`, `cvsg_date: null`, Term 2026. The statpack's
"Segment base rate by salience band (sal-v4)" table matches the context's
version, so I anchor on the `baseline` band's bracketed `reached` rate pooled
over the nine Term rows strictly before OT2026 (OT2017 to OT2025). Weighting
each Term's bracketed rate by its risk-set `n` gives roughly 5.0 percent
(about 637 grants over 12,720 reached petitions). That is the yardstick the
evaluator scores skill against, and it is the rate for the paid, private-
petitioner population that reached the weakest band, most of which never
relists.

## Adjustments down (large)

1. **Pro se petitioner, four pages of argument.** The petition cites three
   cases (Murchison, Caperton, Williams), alleges no split, states no facts
   about the alleged bias, and claims the question is "important" without a
   single example beyond the petitioners' own case. Pro se paid petitions grant
   at a small fraction of the paid-segment rate.
2. **Finality under 28 U.S.C. § 1257 is doubtful.** The underlying municipal
   nuisance action is still pending in the Superior Court; what is under review
   is the California courts' refusal to grant writ relief against an
   interlocutory recusal ruling. The BIO presses this point first and it is a
   threshold bar.
3. **Preservation.** The BIO, quoting the verified disqualification statement
   and the Court of Appeal writ petition (reproduced in its appendix), says the
   statement invoked only California Code of Civil Procedure sections 170.1
   and 170.3 and cited no federal due-process authority. The petition's
   contrary assertion ("expressly invoked the Due Process Clause") is directly
   contradicted. The Court will not take a federal question first raised in
   the petition for review.
4. **The QP's factual premise is contradicted.** The question asks about a
   denial "without any reasoned analysis," but the trial court issued a
   six-page order addressing timeliness, the tentative nature of the ruling,
   the adverse-rulings rule, and California's objective appearance standard,
   plus a verified answer. The Court of Appeal's one-line denial of writ
   relief is ordinary California practice.
5. **Merits weakness.** The alleged bias consists of adverse rulings and a
   tentative fee ruling. Under Liteky and the Caperton line, that is not a
   constitutional recusal case. Even a sympathetic Justice would have nothing
   to work with.
6. **Independent state ground.** The timeliness ruling under section
   170.3(c)(1) is an adequate and independent state ground for most of the
   allegations.
7. **Docket signals.** One distribution, no relist, no CVSG, no amicus. The
   linked stay application 26A145 was denied by Justice Kagan, refiled, and
   denied by the full Court on September 4, 2026 without noted dissent; a
   stay denial with no noted dissent on the same facts is a weak but real
   signal that no Justice sees a live question here.
8. **Originating court cut.** The statpack's "Court of Appeal of California,
   Second Appellate District" row shows a grant rate under 1 percent with GVRs
   at about 4.6 percent, and the GVRs come from intervening-decision cohorts
   this case has no candidate for.

Together these put the case well below even the relist-0 bucket's 1.2 percent
grant rate in the paid scored segment. I settle at 0.3 percent, which leaves
room for the irreducible chance of an unexpected GVR or hold that I cannot see
from the record.

## Timing consideration

Today is October 4, 2026; the petition was distributed for the September 28
long conference. The corpus (pulled today) already records a grant for another
OT2026 paid petition, No. 26-104, distributed for the same conference, so the
long-conference grant orders have issued and this petition was not among them.
This is public pre-snapshot information about the Court's calendar rather than
this case's outcome, and it is noted in `flags.json`. It moves the relist
probability down (a relist would ordinarily have been posted before the
Monday order list) and leaves the grant number essentially where the record
alone would put it. I did not retrieve this case's own docket or any order
list, and I do not know its disposition.

## The other claims

- **relist-increment 0.06.** Most baseline petitions at one distribution are
  never relisted; here the conference has already passed and no relist entry
  appears on a snapshot polled six days after it. I keep a residual for a
  late-posted relist.
- **cvsg-increment 0.001.** No federal interest of any kind.
- **summary-disposition-route 0.6 (conditional on grant).** If the Court
  granted at all it would almost certainly not hear argument; a GVR or per
  curiam is the only realistic shape. There is no intervening decision to GVR
  in light of, which is why I do not go higher.
- **dissent-from-denial 0.01.** Pro se, fact-bound, interlocutory, no
  Justice-flagged interest.

## Stakes

`big_case_score` 0.03: a local short-term-rental enforcement dispute between
two homeowners and a city, with a recusal question that affects no one else.

## Inputs used and their condition

- Snapshot `record/snapshots/2026-10-04.json` (polled today, docket JSON
  generated 9/29/2026), `record/context.json`, `event.yaml`.
- `questions-presented.txt` and `petition.txt` (full text, 9 pages).
- `brief-in-opposition.txt` (25 pages, read through the statement of the case
  and table of contents of its reasons; the preservation, finality,
  independent-state-ground and reasoned-order points are all taken from it).
- `application.txt` has `empty_text: true` (a scanned 24-page stay application
  with no text layer); I treated it as content-unavailable and did not infer
  anything from it beyond the docket text of its denial.
- `metrics/statpack.md`: salience band table (sal-v4), relist-count, CVSG, and
  originating-court cuts.
- One `fedcourts query` for recent OT2026 priors (see `retrieval.md`). No
  CourtListener MCP lookups were needed; the provisioned record was sufficient.

## Where to discount me

The grant number is as low as I am willing to go for any paid petition. If the
evaluator sees a relist on the docket, my relist-increment number was wrong and
the grant number should be read as modestly too low, though still far below
the band rate. The BIO is the only source for what the disqualification
statement actually said; I did not read the petitioners' supplemental briefs
or reply (not provisioned), which may contest the preservation point.
