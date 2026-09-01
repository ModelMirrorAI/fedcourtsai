# Rationale — why P(grant) = 0.60

**Anchor.** This is a Term-2026 application, so the scored baseline pools the
statpack's strictly-prior application-Terms: 2025 (17/226) and 2024 (14/70) →
31/296 ≈ **10.5%**, which clears the pre-registered 50-resolved floor
(`INTERIM_BASE_RATE_MIN_RESOLVED`), so a published baseline exists and I
anchored on it. The committed pack's caveats apply: raw counts, uneven parse
coverage, denial-first collapse of mixed orders, and a scored population
selected higher up the escalation ladder than the pooled cohort — which is
exactly this cell's situation, so a large upward adjustment from 10.5% is
expected for a response-requested application, not evidence of skill.

**Adjustments up from the anchor, in order of weight:**

1. **The United States supports the applicants.** The government's response was
   filed the same day it was requested (Aug 31), and public reporting on the
   filing says the administration's brief defends the FCC notice ("benefits all
   parties equally"). The FCC is defending its own guidance; the applicants are
   effectively carrying the government's case. Government-supported emergency
   applications have been granted at a high rate on the recent shadow docket.
2. **Immediate, aggressive expedition.** The Chief Justice called for a
   response the day the application was docketed, due at noon three days later
   — timed to the general-election window. That is the strongest escalation
   rung, an affirmative act of attention.
3. **A clean jurisdictional off-ramp.** Judge Wilkinson's dissent below argued
   the Fourth Circuit lacked jurisdiction over a non-final staff-level public
   notice. A stay keyed to a likely jurisdictional vacatur does not require the
   Court to bless the guidance on the merits.
4. **Equities.** The guidance had been operative since March 2026; the panel
   changed the status quo mid-cycle and made it effective immediately. Higher
   ad rates paid during the window are unrecoverable.

**Adjustments down (why not 0.75+):**

- The merits text cuts against the applicants: § 315(b)'s lowest unit charge
  attaches to "use" of a station by a legally qualified candidate, and the
  panel majority's reading that it does not reach party-committee purchases is
  textually plausible. Post-Loper Bright there is no deference cushion for the
  FCC's expansion. A textualist majority may see no fair prospect of reversal.
- The applicants are private parties; the government supports but did not
  itself apply, and private-applicant grant rates run lower.
- The resolver reads mixed relief denial-first: any partial or qualified order
  (a stay limited to some applicants or some races, an administrative stay
  followed by denial) scores as ungranted, so P(unqualified grant) sits below
  P(any relief).

Net: 0.60. `granted = 1` and `predicted_disposition = granted` state the modal
outcome consistent with that number.

**Other claims.** `response-requested-increment` = 0.99: the rung already fired
on my frozen record (`response_requested: true`), so the claim is vacuous and
masked; the number is stated for completeness. `referral-increment` = 0.90: an
application of this salience, with the government participating, is
near-certain to be referred to the full Court rather than disposed of by the
Chief alone; the residual is the chance the docket never latches an explicit
referral entry. `amicus-increment` = 0.60: strong latent amicus demand
(broadcasters, party committees, campaign-finance groups) against a very
compressed schedule; the count is 0 now, and a comparable politically salient
August 2026 application (26A203) drew 7 amici in about two weeks.

**Conditioning notes.** `band` is null in `record/context.json` — the normal
interim state — so no cert band or caption-class floor was used, per the
interim-stage rule. No `record/documents/` text was provisioned; the
application and response PDFs are linked on the snapshot but the government's
PDF returned 403 to my fetcher, so my read of the government's position rests
on secondary reporting (SCOTUSblog), not the brief's text — discount
accordingly. Corpus freshness for the priors I quoted: `fedcourts query`
returned rows with `last_live_polled` of 2026-09-01, current as of this run.
The statpack figures are the committed `metrics/statpack.md` in this checkout.

**Where to discount me.** The biggest uncertainty is the merits prong: if the
Justices read § 315(b) the panel's way, the jurisdictional dissent alone may
not carry a stay, and the true probability is closer to 0.4. I also could not
read the CA4 opinions themselves, only reporting about them; the vote line-up
and reasoning below are secondhand.
