# Rationale — why P(unqualified grant) = 0.01

## No published baseline

This is an interim (application) cell, moment `arrival`, `forward` mode, Term
2025. The committed statpack's "The interim docket (applications)" section
grounds the scored base rate as the grant rate pooled over resolved
substantive applications from Terms strictly before the cell's, subject to the
pre-registered floor of 50 resolved (`INTERIM_BASE_RATE_MIN_RESOLVED`).
Computing the pool from the section as instructed: the only strictly-prior
Term with resolved substantive applications is OT2024, contributing **47**
resolved (14 granted) — below the floor. So **this cell anchors without a
published baseline**; neither the pack-level 12.3% (n=243, contains the
cell's own Term) nor OT2024's single-Term 29.8% is a permissible substitute.
The section's caption is the current baseline-grounding form, not the older
descriptive-only wording.

`record/context.json` carries `band: null`, the normal interim state — no
salience band applies and I did not anchor on any cert table.

## What the record shows

- **The applicant is pro se.** Allen Watkins of Phoenix, AZ is his own counsel
  of record. CourtListener shows him as a serial pro se litigant in the
  District of Arizona (suits against Santander Consumer USA, Becton Dickinson,
  the Social Security Administration, and Illinois/Arizona state agencies).
- **The respondent is the district court itself** — the application (25A622)
  seeks a stay against the United States District Court for the District of
  Arizona, arising from Ninth Circuit case 25-2374. Naming the tribunal as
  respondent is the classic mandamus-adjacent posture: the applicant is asking
  the Supreme Court to halt his own ongoing district-court proceedings. Such
  requests essentially never satisfy the stay standard (no fair prospect of
  certiorari, no irreparable harm that ordinary appellate review cannot cure).
- **No rung of the escalation ladder has been climbed**: `response_requested:
  false`, `referred_to_court: false`, `amicus_briefs: 0`, in roughly nine
  months on the docket. Every signal that historically precedes an interim
  grant is absent.
- **Corpus priors match the shape.** Recent resolved substantive applications
  with a court as respondent — 26A145 (*Zhong v. Superior Court of
  California*), 26A50 (*Young v. Superior Court of California*) — were denied
  within days, with no response requested, no referral, and no amici, as were
  the recent pro se applications generally (26A147, 26A166, 26A180, 26A75).

## The number

The statpack's 12.3% substantive grant rate describes a population dominated
by represented parties — governments, corporations, capital petitioners — and
is right-shifted by applications that climbed the escalation ladder. This
application shares none of that. I put P(unqualified grant) at **0.01**: not
lower, because the interim resolver machine-matches disposition text and some
residual label noise exists (a mixed or administrative entry misread as a
grant), and because a nine-month-stale record leaves some chance the posture
is not what the single docket entry suggests.

The increments: response-requested 0.02 and amicus 0.01 (nothing has arrived
in nine months and nothing about the application invites either); referral
0.04, slightly higher because a Circuit Justice sometimes refers even a
meritless application to the full Court before denial, and the anomalous
pendency leaves more room for an unusual path.

## Where to discount me

The dominant uncertainty is **snapshot staleness**, flagged in `flags.json`:
a substantive stay application pending nine months with a single docket entry
is far outside the normal disposition window, so the snapshot very likely lags
the true docket (the application may already be resolved, uncaptured). I did
not retrieve this case's current SCOTUS docket state or disposition, per the
leakage rules; the forecast rests on the provisioned snapshot, corpus priors,
and the statpack. If the docket record is complete and the application truly
is under nine months of active advisement, that would itself be a signal of
attention my numbers do not price — but I judge that reading much less likely
than a stale record.
