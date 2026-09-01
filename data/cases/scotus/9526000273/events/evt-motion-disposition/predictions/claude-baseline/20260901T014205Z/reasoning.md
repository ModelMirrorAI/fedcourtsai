# Rationale for the numbers

**P(grant) = 0.03.** The statpack's interim-docket section publishes a scored
baseline for this cell: pooling the resolved substantive slice over
application-Terms strictly before 2026 gives 17/226 (Term 2025) + 14/70 (Term
2024) = 31/296 ≈ **10.5%**, which clears the pre-registered 50-resolved floor, so
this is the baseline my skill is scored against. I adjusted sharply down from it,
for three reasons:

1. **The pooled population is not this application's class.** The substantive
   slice is dominated by government and institutional emergency applications
   (its two recent grants in my retrieval window were of that shape, e.g.
   National Park Service 26A203). A prisoner's stay-of-execution application is
   among the weakest classes in it: the five capital stay applications in the
   corpus's recent window (26A209, 26A175, 26A119, 26A121, 26A54) were all
   denied, as was every one of the 12 recent capital rows I retrieved.
2. **The underlying claim is doctrinally weak.** The lower court is the Superior
   Court of Georgia, Fulton County (25CV017069), and the respondents are the
   Board of Pardons and Paroles, its members, the DOC commissioner, and the
   Governor — a challenge to Georgia's clemency process. *Ohio Adult Parole
   Authority v. Woodard* leaves such claims almost no due-process foothold, so
   the "fair prospect of certiorari" prong is hard to satisfy.
3. **Posture.** The state opposed within three days, and the Court's recent
   practice on last-minute execution stays is stringent. Nothing on the record —
   no requested response, no referral yet, no amicus — shows the Court climbing
   the escalation ladder.

I did not go to zero because capital stays are occasionally granted where the
linked petition (here 26-5211) raises a genuinely cert-worthy question I cannot
rule out from the docket skeleton alone: no petition text or QP document was
provisioned for this application docket, so my read of claim strength is inferred
from the parties, the lower court, and the case posture, not from the filings'
text. That is the main place to discount me.

**Conditioning state.** `record/context.json` carries `band: null` — the normal
interim case — so per the contract I anchored on the interim section's pooled
rate, not the cert band table, and no caption-class floor applies. The section's
own caption now states the pooled strictly-prior rate is the scored base rate
(not descriptive-only), and I read it on those terms.

**Ladder claims.** `referral-increment` = 0.90: the statpack's referred count
(168/340 substantive, right-censored) is a floor for capital stays specifically,
where referral by the Circuit Justice to the full Court is near-universal
practice; I stopped short of higher because a small share of applications are
acted on in chambers or resolve by other routes (withdrawal, mootness).
`response-requested-increment` = 0.02: an opposition is already on file
(voluntarily — the frozen context correctly shows no *request*), so a formal
request would be redundant and the timeline forecloses it.
`amicus-increment` = 0.05: days to disposition, a fact-bound clemency claim, and
zero briefs so far. None of the three has a published baseline; the numbers are
banked, and I stated them as beliefs I would accept being scored on.

**Corpus freshness.** `fedcourts corpus-info` is not runnable in this cell (it
needs a locally pulled blob; the cell reads through the corpus service), so the
vintage evidence is the retrieval itself: the served blob returned priors
resolved through **2026-08-31**, one day before the 2026-09-01 snapshot, so the
corpus read is current for this forecast.

**Mode.** Forward cell. I deliberately did not retrieve this case's own live
docket, the linked 26-5211 docket, or news coverage: the application was ripe for
disposition at snapshot time (opposition filed August 31), so any live retrieval
had a high chance of surfacing the disposition itself, which the contract treats
as a mis-provisioned-cell signal rather than usable evidence. The forecast rests
on the provisioned snapshot, the committed statpack, and corpus priors.
