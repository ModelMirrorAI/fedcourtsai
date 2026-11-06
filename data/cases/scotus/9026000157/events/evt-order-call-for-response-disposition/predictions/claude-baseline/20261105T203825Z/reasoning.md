# Reasoning — Singh v. Second Judicial District Court of Nevada (No. 26-157)

**P(grant) = 0.17.** Moment: `response-requested` (Court called for a response on
Sep 22, 2026 after the respondents waived on Aug 21). Snapshot `2026-09-23.json`
shows one distribution (for the 10/9/2026 conference); no response is on the
record yet and I do not infer what it will say.

## Anchor
- `context.json` band `baseline` (sal-v7), frozen `cert_anchor.rate` = 0.0515
  (10-Term lookback). That is my starting point.
- Statpack (paid scored segment) cuts used for shape: amicus `2+` bucket
  (n=1,543) grants ~18% + GVR 4.5%, vs. 2.0% for `0` amici (n=11,427). This
  petition already has three amicus briefs (ACNA, Former EEOC GC et al.,
  Roman Catholic Archbishop of Las Vegas) — a marginal, not additive, signal.
- No committed table conditions on a called-for response; how far the call
  moves me is judgement. A call for response is a low bar (one chambers'
  interest), and most such petitions are still denied, but it lifts a paid
  petition well off the baseline floor.

## Upward adjustments
- QP (`questions-presented.txt`): whether the "neutral principles" approach of
  *Jones v. Wolf* extends beyond church-property ownership to internal
  governance disputes. The petition describes, and the Nevada Supreme Court
  itself acknowledged (App. 10a, 15a), a split: 2d/8th/9th/D.C. Cirs. and
  several state high courts vs. 5th/6th/11th Cirs. and others.
- Published, precedential state high-court opinion; no alternative state
  ground per the petition; elite Supreme Court counsel (Sidley/Northwestern
  clinic).
- Church autonomy is a doctrine several Justices (Thomas, Alito, Gorsuch)
  have repeatedly signaled interest in.

## Downward adjustments
- **Finality/interlocutory posture.** The judgment below resolved an original
  writ petition in the Nevada Supreme Court letting the suit proceed. The
  petition argues finality under *Atlantic Richfield v. Christian* and *Cox
  Broadcasting*, but the Court has repeatedly passed on church-autonomy
  petitions in interlocutory posture. Corpus lookup of No. 25-849
  (USCCB v. O'Connell, the D.C. Circuit companion question the petition itself
  distinguishes) shows it distributed 4 times with ~18 amicus filers including
  states, and still **denied** on 2026-05-26. That is the strongest evidence
  against a grant here: a better-supported petition on the same doctrine was
  turned away within the last six months. The petition's distinguishing points
  (state-court writ = separate action; no appellate-jurisdiction threshold;
  new 5th Cir. *Lutheran Church* decision) are real but not decisive.
- Small, fact-bound congregational dispute (Sikh society bylaws/elections);
  respondents are private individuals who initially waived.
- The Nevada court found the specific bylaws "secular" — the Court might see
  application rather than a clean legal rule.

Net: ~0.17. Uncertainty is wide; the O'Connell denial could reflect only its
federal-appellate-jurisdiction problems, in which case this cleaner vehicle
could be the one the Court was waiting for (upside to ~0.3).

## Other claims
- `relist-increment` 0.96: masked on this moment; the petition will be
  redistributed once the response is in.
- `cvsg-increment` 0.03: private parties, state-court case, no federal interest
  beyond the First Amendment generally.
- `summary-disposition-route` 0.10 | grant: a summary reversal is possible but
  an acknowledged split calls for plenary review.
- `dissent-from-denial` 0.20 | denial: Alito/Thomas/Gorsuch might write as they
  have on church-autonomy denials, but repeated writing is less likely after
  O'Connell. I did not verify whether any Justice wrote in O'Connell (the
  corpus row carries no order text).

## Inputs
Snapshot, `context.json`, `petition.txt`, `questions-presented.txt`
(appendix not read in full). `same-question.json` listed no petitions above
threshold. No BIO yet. CourtListener MCP not used.
