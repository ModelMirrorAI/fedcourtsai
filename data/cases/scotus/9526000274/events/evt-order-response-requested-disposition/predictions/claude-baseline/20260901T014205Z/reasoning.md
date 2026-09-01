# Rationale — why these numbers

## The record

The snapshot (2026-08-31) shows: an emergency stay application (26A274)
submitted to the Chief Justice on August 28, 2026 by the National
Republican Congressional Committee et al. (with the NRSC), against
respondents Sherrod Brown, Jon Ossoff, Roy Cooper, and Kristen McDonald
Rivet (Democratic Senate candidates, Elias Law Group) and the United
States and FCC (Solicitor General as counsel); a response requested by
the Chief Justice on August 31, due noon September 3; and — notably — a
response from the United States and the FCC already filed on August 31.
Lower court: CA4 No. 26-1785. My cell's frozen context: `mode: forward`,
`response_requested: true`, `referred_to_court: false`,
`amicus_briefs: 0`, `band: null` (the normal interim state — no cert
band, and I anchored on none).

Forward-mode retrieval (see `retrieval.md`) established the substance:
the FCC Media Bureau's March 30, 2026 public notice said party
committees and joint fundraising committees making coordinated buys
qualify for the lowest unit charge under 47 U.S.C. §315(b); a divided
CA4 panel (Judge King writing, Judge Wilkinson dissenting) held on
June 19 that the statute unambiguously limits the LUC to candidates and
vacated the guidance; the CA4 then denied a stay 2-1 and made its
judgment effective immediately (entered August 25); and the government's
SCOTUS response supports the applicants, arguing the candidate
challengers lack Article III standing, the court of appeals lacked
statutory (Hobbs Act) jurisdiction over a non-final staff-level notice,
and the decision misreads §315(b).

## Anchor

The statpack's interim-docket section grounds the scored baseline:
pooling the resolved substantive slice over application-Terms strictly
before this one (Term 2025: 17/226; Term 2024: 14/70) gives
31/296 ≈ **10.5% granted**, and 296 clears the pre-registered floor of
50, so a published baseline exists for this OT2026 cell. (The prompt's
worked example predates this pack's coverage; I computed the pool from
the section as instructed.) The caveats travel with it: the escalation
columns are right-censored and not as-at-prediction, and the scored
population is selected on the very rungs this application has climbed.

## Adjustments — 10.5% up to 0.62

The pooled rate is the unconditioned substantive slice; this application
sits far above it on every dimension the ladder proxies for:

- **Response requested** (the strongest rung, and this cell's defining
  moment): the Court acted affirmatively within one business day, on a
  three-day clock — consistent with intent to decide before the LUC
  window opens September 4. In the pack's slice only 55 of 340
  substantive applications ever drew a response request; grants
  concentrate heavily in that pool.
- **The federal government supports the stay.** The SG's emergency
  applications and the applications the SG supports have fared very
  well on the recent shadow docket. The government filed its supporting
  response the same day the response was requested — it wanted this
  granted quickly.
- **A dissent below and jurisdictional off-ramps.** Wilkinson's dissent
  (statute ambiguous; the FCC should have gone first) plus the
  standing/finality arguments mean the Court can grant without
  committing to the applicants' merits reading.
- **Equities/status quo framing favors applicants**: the CA4's
  immediately-effective mandate changed the regime that had governed ad
  sales since March, on the eve of the pricing window.

Against, and why I stop at 0.62 rather than higher:

- **The statutory text is a real obstacle**: §315(b) runs to "a legally
  qualified candidate," and the panel majority found it unambiguous.
  If the Court thinks the CA4 is right on the merits, the likelihood of
  success prong fails regardless of the equities.
- **Irreparable harm is economic** (higher ad rates), the classically
  weak form, even if unrecoverable.
- **Private applicants**, not the government itself — the near-automatic
  grant pattern of recent SG applications does not fully transfer.
- **The interim resolver reads mixed relief denial-first**: my number is
  P(unqualified grant), so any granted-in-part shape counts against me.
  Here the requested relief is unitary (stay one judgment), so the mixed
  risk is modest but nonzero.

A close recent comparator from the corpus: 26A203 (NPS v. National Trust
for Historic Preservation) — substantive application, response requested
the day it was filed, referred, granted within about two weeks; but that
was the government as applicant, so I discount from its shape.

## The other claims

- **response-requested-increment 0.02**: vacuous by construction at this
  moment — the request is the event's opening act; the harness masks it.
- **referral-increment 0.85**: contested, nationally salient, and
  government-supported applications of this profile are almost always
  referred to the full Court rather than resolved in chambers; the
  residual 0.15 covers the Chief acting alone on a fast clock and the
  parser never latching an explicit referral entry.
- **amicus-increment 0.50**: zero on the record; well-organized,
  motivated amici (broadcasters, party committees, campaign-finance
  groups) against a very short window — likely under a week to
  disposition. Genuinely uncertain, hence 0.50.

## Uncertainty and discounts

The largest uncertainty is how the Court weighs the clean-looking
statutory text against the jurisdictional defects — a denial with a
statement that the applicants may return via certiorari is a live path I
may be underweighting. My vote block is a conventional 6-3 lineup for a
politically valenced emergency grant; it is elicited, unscored at this
stage, and low-confidence — shadow-docket grants often issue without
recorded votes. No filed-document text was provisioned
(`record/documents/` absent for this case), so my read of the
application's and the government's arguments comes from press and
secondary coverage, not the filings' own text: the supremecourt.gov PDFs
returned HTTP 403/429 to my fetches. Discount my merits characterization
accordingly.
