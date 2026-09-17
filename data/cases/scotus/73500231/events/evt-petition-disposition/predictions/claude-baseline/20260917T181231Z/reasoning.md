# Rationale for the numbers

**P(grant) = 0.004; predicted disposition `denied`.**

## What I read

- `record/snapshots/2026-09-17.json`: paid docket 25-1328, docketed May 29,
  2026 (petition dated March 5, 2026), from the D.C. Circuit (No. 25-5056,
  unpublished order of October 1, 2025; rehearing denied December 5, 2025).
  Entries: petition filed; waiver of response by the United States (June 16);
  distributed for the September 28, 2026 Conference (June 24); injunction
  application 26A37 submitted to the Chief Justice (July 2) and denied by the
  Chief Justice (July 16). Linked with 26A37. Petitioner is pro se and is her own
  counsel of record; the Solicitor General is counsel for respondents.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`,
  `distribution_count` 1, no CVSG, term 2025, `signals_observable` true,
  cutoff null.
- `record/documents/questions-presented.txt` and `petition.txt` (50 pages,
  text extracted, not truncated): eight questions presented, the reasons for
  granting, the related-proceedings list (six prior actions in D.N.M., N.D.
  Cal., D.D.C. and the Federal Circuit against the VA over the same 2017
  probationary appointment and removal). No brief in opposition exists because
  the government waived.

## Anchor

Cert-stage cell, `moment: distribution` shape (the ordinary petition
disposition event; `event.yaml` records no stage or moment, so it reads as
cert). The context band is `baseline` and its `salience_version` (`sal-v4`)
matches the statpack's "Segment base rate by salience band (sal-v4)" table, so
the band table is my anchor. Pooling the baseline column's bracketed `reached`
figures over the eight Terms strictly before OT2025 that the table renders
(OT2017 through OT2024, weighted by their `n`), the risk-set grant rate for a
paid petition that reached `baseline` is about 5.1% (n about 11,580). That is
the yardstick the evaluator scores this cell against. The modern-cert relist
cut puts a petition at relist bucket 0 at roughly 1.7% grant-family (granted
plus gvr), and the CVSG-none cut at roughly 6.3%; the originating-circuit cut
for `cadc` is unusually high (about 7.8% grant family) but that column is
dominated by counseled agency-review petitions and says nothing about a pro se
employment case.

## Adjustments, all downward

1. **Pro se petitioner with a personal, fact-bound set of questions.** Five of
   the eight questions are framed around the petitioner's own MSPB appeal
   number and employment dates. The two doctrinal questions (Lawlor and Parr on
   "finality" for claim preclusion) do not describe a conflict: Lawlor held that
   a prior judgment does not bar claims arising from later conduct, and Parr is
   about appellate finality, so the alleged conflict with Ashbourne v. Hansberry
   is not one a court would recognize. No circuit split is asserted with
   citations to other circuits.
2. **The United States waived a response and no response was called for.** The
   waiver was filed June 16 and the petition then sat through the full summer
   distribution window with no call for a response. On a petition where the SG
   is the respondent, that silence is close to dispositive: the Court almost
   never grants over an unanswered waiver without first calling for a response.
3. **The decision below is an unpublished order** affirming a res judicata
   dismissal, which the Court treats as a poor vehicle even when a question is
   otherwise cert-worthy.
4. **The linked injunction application (26A37) was denied by the Chief Justice
   alone**, without referral to the Court and without a requested response,
   which is the weakest possible signal of interest from the one Justice who
   has looked at the matter.
5. **Serial litigation.** The petition's own related-proceedings list shows
   six prior actions over the same removal, and from general knowledge I
   believe this petitioner has filed several earlier cert petitions arising
   from the same dispute, none granted. I could not confirm that through
   CourtListener in this cell (the MCP server returned HTTP 429 rate-limit
   errors on both attempts, see `retrieval.md`), so treat the prior-petition
   point as recollection rather than a checked fact; the number does not depend
   on it.

Together these place the petition in the lowest stratum of the baseline band.
Denial-reweighted, roughly 97% of relist-0 paid petitions are denied and the
grant-family share is about 1.7%; a pro se, response-waived, unpublished-order,
no-split petition sits well below that bucket's average, and the only grant
route with any mass is a GVR for which no intervening decision exists. I put
P(any grant) at 0.004, which is about one-thirteenth of the band anchor, and I
would not defend a number above 0.01.

## The other claims

- `relist-increment` 0.07: the docket shows exactly one distribution. Most
  paid petitions are never relisted (relist bucket 0 holds roughly 75% of the
  paid scored segment on the statpack's cut, and that count is an upper bound
  because reschedules also add entries). For a petition the Court will deny
  outright, a second distribution entry comes almost only from a reschedule off
  the long conference, so I set this well below the population rate.
- `cvsg-increment` 0.002: the SG is a party. A CVSG is functionally
  unavailable; I leave a sliver for a mis-coded docket entry.
- `summary-disposition-route` 0.85, conditional on a grant: if this petition
  were granted at all it would be by GVR, not plenary review. I keep 0.15 for
  the residual world in which some reformulated finality question is set for
  argument, because the conditional is on an event I consider very unlikely and
  the conditional's shape is correspondingly uncertain.
- `dissent-from-denial` 0.01, conditional on a denial: no Justice has a stake
  in this posture and the Chief Justice has already denied the linked
  application without comment.

## Big case score

0.02. Stakes are one former probationary VA technician's ability to relitigate
an MSPB jurisdiction question already lost in several forums. No public
interest beyond the parties.

## Uncertainty and where to discount me

- The band anchor is a pooled cross-Term figure; the OT2025 live row (reached
  3.9%, n=1140) is lower and still accruing. Either anchor gives the same
  order of magnitude and my adjustment dominates it.
- I could not verify the petitioner's prior cert history because CourtListener
  throttled every request in this cell. That evidence would only push the
  number down further, so its absence cannot make my forecast too low.
- The petition's Lawlor/Parr theory is wrong on the law as I read it, but I did
  not retrieve the D.C. Circuit order itself (the appendix was not provisioned
  and CourtListener was unavailable), so my characterization of the decision
  below rests on the petition's own account of it.
- No merits-shaped uncertainty remains conditional on a denial. The main way I
  am wrong is a reschedule that produces a second distribution entry, which
  scores against `relist-increment`, not against the disposition.
