# Rationale — why 0.15 and the other numbers

**The cell.** Interim stage, `moment: response-filed`, forward mode. 26A124,
Trump v. California: the government seeks a stay of D. Mass. preliminary
injunction orders (Judge Talwani) barring implementation of the March 31,
2026 executive order "Ensuring Citizenship Verification and Integrity in
Federal Elections" (mail-ballot restrictions, including directing USPS to
deliver mail ballots only per a federal voter list) in the 23 plaintiff
states and D.C. Snapshot as of 2026-08-16: application submitted to Justice
Jackson July 27; response requested same day, due and filed August 3; reply
August 4; supplemental briefs from both sides August 12; roughly a dozen
amicus filings, overwhelmingly opposing the stay. Frozen conditioning:
`response_requested: true`, `referred_to_court: false`, `amicus_briefs: 6`,
`band: null` (normal for interim — I did not derive one or touch the cert
band table).

**Baseline.** The committed statpack's interim section (the scored-caption
version — it states the rows ground the interim stage's scored base rate).
Pooling the resolved substantive slice over application-Terms strictly before
this cell's Term (2026): Term 2025 contributes 16/178 and Term 2024
contributes 14/47, so the pool is 30/225 ≈ **13.3%**, which clears the
pre-registered 50-resolved floor. That is the published baseline I anchored
on. Cautions I carried: the pooled cohort is mostly capital/prisoner
applications, parse coverage is uneven across Terms (2024 is largely
unparsed), and the scored population is escalation-selected relative to the
pooled one, so the number is shape more than truth.

**Adjustments.**
- *Up*: the applicant is the federal government, which won emergency relief
  in the large majority of its 2025-Term applications — a very different
  conditional population from the 13.3% pool. Taken alone this would put the
  number well above the baseline.
- *Down*: (1) the Court did not enter the requested administrative stay and
  has let the injunction stand for twenty days — when this Court intends to
  grant urgent relief it typically moves fast, and commentary (Election Law
  Blog) flags this as possibly the longest-pending emergency election motion
  ever; (2) Purcell-style election proximity — a mid-August stay would change
  mail-ballot administration in 23 states weeks before the November midterms,
  and commentators (Hasen) judge the EO practically unimplementable for 2026
  anyway, which guts the irreparable-harm story; (3) the merits are unusually
  weak — no plausible source of presidential authority over the manner of
  federal elections; (4) the denial-first collapse — partial relief (staying
  some provisions, or trimming scope) resolves as ungranted, and the mixed
  shape is a substantial share of the plausible grant-side mass here. A small
  offset back up: a partial grant phrased without denial language would
  resolve as granted under the matcher.

Net: **0.15** — above the 13.3% pooled baseline on the strength of the
government-applicant conditional, but held close to it by the election-timing
and revealed-preference signals.

**Ladder claims.** `response-requested-increment` 0.02: the rung already
fired (July 27), so the claim is vacuous for this cell and will be masked;
the number is a formality stated honestly. `referral-increment` 0.93: the
harness detects referral by the phrase "referred to the Court" anywhere in
the entry texts, and the full-Court disposition formula itself carries it
("presented to Justice Jackson and by her referred to the Court is …"); a
matter with this many amici and supplemental briefing will not be decided in
chambers. Residual for an entry that omits the recital.
`amicus-increment` 0.12: the frozen count is 6 because the counter matches
"amicus curiae" (singular) only — the docket's seven "amici curiae" entries
are invisible to it — so the claim fires only if a further singular-form
entry lands after prediction time; briefing completed August 12 and I expect
disposition before another amicus wave, with the residual covering continued
pendency drawing stragglers. See flags.json on the counter semantics.

**Uncertainty and discounts.** My largest uncertainty is how much weight the
government-applicant conditional deserves against the election-specific
record: the 2025 shadow docket was lopsidedly favorable to the government,
and if the Court treats this like an ordinary intra-branch injunction fight
rather than an election case, 0.15 is too low. I also cannot read the
supplemental briefs' trigger from the docket (no order directing them
appears), so I inferred their subject from press coverage. The long pendency
is genuinely ambiguous — writings accompany grants as well as denials
(Trump v. CASA took a month and ended in a government win). No provisioned
document text existed for this cell (`record/documents/` absent), so my read
of the application and response is from the docket entries, the snapshot
metadata, and press/commentary retrieval, not the filings' text. The corpus
`query` surface returned mostly time-extension applications and contributed
no usable priors; the anchor came from the statpack. Retrieval surfaced no
disposition of this application (searches and the snapshot agree it is
pending), so the cell is properly provisioned as forward.
