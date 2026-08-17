# Rationale — why P(unqualified grant) = 0.30

## What this cell is

An interim-stage cell at the `response-requested` moment: application 26A124,
*Trump v. California* — the federal government (SG Sauer as counsel of record)
seeks a stay, submitted to Justice Jackson, of a First Circuit ruling
(No. 26-1774) in the multistate challenge to an executive order on federal
election administration (the respondents' opposition is captioned "Elections
EO 2.0"). Mode is `forward`; the frozen context shows `response_requested:
true`, `referred_to_court: false`, `amicus_briefs: 6`, `band: null` (the
normal interim state — no cert band anchoring, correctly).

## The anchor

The committed statpack's "The interim docket (applications)" section carries
the scored-base-rate caption. My application Term is 2026 (26A124), so the
pool is Terms strictly before it: 2025 contributes 178 resolved substantive
applications (16 granted) and 2024 contributes 47 (14 granted) — 225 resolved,
30 granted, a pooled rate of **13.3%**, clearing the pre-registered floor of
50. That is the baseline my number is scored against. Its cautions apply: the
pool is unconditioned on the escalation ladder while this cell was selected on
it, and the escalation-signal counts are right-censored — I read them as shape
only.

## Adjustments

**Up from 13.3%, substantially:**
- The applicant is the federal government through the Solicitor General. The
  pooled rate is dominated by pro-se and prisoner applications; government
  applications resolve far above it, and over OT2024–2025 the government's
  emergency applications succeeded at a majority rate.
- This application sits at the top of the escalation ladder: a response was
  requested the day it was filed, briefing ran to a reply and paired
  supplemental briefs, and thirteen amici filed at the stay stage — the Court
  is treating it as a major case.

**Back down, for three reasons:**
- **The denial-first collapse.** A multi-provision executive order invites a
  partial stay — relief on narrower provisions, denial on the core — and a
  mixed order resolves as ungranted. `probability` prices only an unqualified
  grant, and on this shape the mass on partial relief is significant.
- **The merits ground is weak for the applicants.** Unilateral presidential
  authority over election administration runs against the Elections Clause's
  allocation to states and Congress; the government lost below and needs a
  fair prospect of reversal.
- **The equities near an election.** The injunction preserves the pre-order
  status quo for administering the November 2026 midterms; a stay would itself
  change election administration close to the election, so the
  Purcell-style instinct favors leaving the injunction in place.

Landing point: **0.30** — well above the pooled 13.3% on the government-
applicant and escalation signals, held below even odds by the partial-grant
collapse and the elections posture. `predicted_disposition: denied` with
`granted: 0` follows from probability < 0.5.

## The increment claims

- `response-requested-increment` **0.03** — the rung already fired (this
  moment's definition), so the harness resolves it vacuous; the number is
  P(a further call for response), which is small now that supplemental
  briefing has already happened.
- `referral-increment` **0.85** — not yet referred on the frozen context; an
  application of this magnitude will be decided by the full Court, and the
  docket ordinarily records the referral. Residual doubt is whether the entry
  appears rather than whether the full Court acts.
- `amicus-increment` **0.30** — the frozen count is 6, but the snapshot shows
  13 amicus filings; the 6 matches exactly the singular-form "Brief amicus
  curiae" entries, so the counter appears to skip the seven "Brief amici
  curiae" (plural) entries (flagged in `flags.json`). I priced the claim
  assuming the resolver counts the same way — the increment then requires a
  *new* singular-form brief after prediction time, unlikely with briefing
  closed but possible if disposition slips. If the resolver instead counts all
  amicus entries, the claim resolves true immediately and my number is too
  low; that resolver-consistency uncertainty is folded into the 0.30.

## Where to discount me

- No `record/documents/` were provisioned — no application, opposition, or
  brief text was on my desk. My read of what the executive order does is
  inferred from the docket text, party lineup, and filing captions only.
- The CourtListener MCP server was rate-limited (HTTP 429, daily quota
  exhausted) on my one search attempt, so I could not read the First Circuit
  ruling or the application PDF. I degraded to the provisioned snapshot, the
  statpack, and corpus priors, per the prompt's degradation rule.
- The corpus `query` surface returned mostly time-extension applications;
  no closely comparable government-applicant stay prior surfaced, so the
  government-applicant uplift rests on general knowledge of the OT2024–2025
  emergency docket rather than a corpus-measured cut.
- The gap between my 0.30 and the 13.3% baseline is a large claimed
  adjustment; if the Court treats this as an ordinary-course denial the
  baseline would have been the better number.
