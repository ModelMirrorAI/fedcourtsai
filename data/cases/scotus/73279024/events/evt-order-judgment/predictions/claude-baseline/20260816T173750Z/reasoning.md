# Rationale for the numbers (claude-baseline, 20260816T173750Z)

**P(disturbed) = 0.88, judgment `reversed`.**

## Anchor

The committed statpack's "The merits docket (granted cases)" section
publishes an `excluded` count (67 pool-guard exclusions against 607 grants),
so its rates are quotable. This case's grant date is 2026-03-09 (from the
event's `opened_at`), which is October Term 2025 on the grant-Term axis, so
the scored baseline pools grant Terms 2015–2024; the pack's table renders
Terms 2017–2025, and the strictly-prior rendered rows (2017–2024) are the
pool: 515 parsed judgments, 359 disturbed → **69.7% disturbed** — comfortably
past the 30-parsed floor, so a committed baseline exists and is the bar my
skill is scored against. Coverage caveat: those Terms show 557 granted
against 515 parsed, and the nearest Terms' gaps are mostly pendency, which
censors toward quicker dispositions.

## Adjustments up from 0.70 to 0.88

- **The Solicitor General is the petitioner.** The federal government as
  petitioner wins at rates well above the pooled disturbed rate, and this
  petition was granted quickly (three distributions, no CVSG needed — the SG
  *is* the federal party).
- **The decision below is a divided Ninth Circuit panel** (published,
  2/13/2025, rehearing denied 7/17/2025), with a dissent by Judge VanDyke
  on the finality question (petition App. 52a). A granted federal-petitioner
  case from the Ninth Circuit with a dissent below is the classic
  reverse-shape.
- **The grant looks error-correction-flavored.** The BIO's strongest
  argument was vehicle/splitlessness — that finality disputes are fact-bound
  and the Court routinely denies them — and the Court granted anyway. A
  grant over a no-split BIO in a government case usually signals intent to
  reverse, not to affirm.
- **Doctrinal tailwind on both QPs.** On QP1, *Franklin* and *Dalton* are
  close analogues (a submission that has effect only through another
  actor's decision), and the respondent's theory — that applying for a
  permit is itself final agency action — is aggressive under *Bennett*'s
  consummation prong. On QP2, *Seven County* (2025) shows this Court's
  strong current skepticism of expansive NEPA obligations, unanimously.
- **Two independent routes to reversal.** The government wins if it
  prevails on *either* finality or NEPA displacement; respondent must win
  both QPs to keep the judgment. Compounding two contested questions cuts
  against affirmance.

## What holds the number below ~0.92

- The Court's modern finality cases (*Sackett*, *Hawkes*) run
  pro-reviewability, and respondent has one concrete legal consequence the
  government concedes: under Guam EPA's regulation the renewal application
  automatically extended the prior permit, authorizing continued
  open-burn/open-detonation operations for five years and counting. That is
  a genuinely non-frivolous *Bennett* prong-two theory, and *Biden v. Texas*
  n.7 gives respondent an answer on prong one.
- Respondent's advocacy is strong (Earthjustice, with eleven states as
  amici on its side), and the merits brief reframes the case NEPA-first,
  where the post-2023 statutory text (42 U.S.C. § 4336) gives it a real
  textual argument against implied displacement.
- Mixed outcomes (affirm on finality, reverse on NEPA displacement) still
  count as disturbed, but a DIG (~2%) does not.

## Votes and confidence

Modal lineup is 9-0 on the judgment (the *Seven County* pattern: unanimity
in judgment with a separate writing from the Democratic appointees), so the
per-Justice argmax is `majority` for all nine; the realistic alternative is
7-2 with Jackson and Sotomayor dissenting — I put P(Jackson on the majority
side) only at ~0.55, which is why `confidence` is 0.7 rather than higher.
The Kavanaugh-authorship call is a context forecast, unscored.

## Inputs and their limits

- I worked from the provisioned snapshot (2026-08-16, full docket through
  the argument setting), the provisioned QP text, petition, BIO, **and
  respondent's merits brief** — the provisioned brief-in-opposition file
  carries both the 1/16/2026 BIO and the 7/20/2026 merits brief. This is a
  forward cell (the judgment does not exist; argument is 10/7/2026), so
  that later material is legitimate input.
- **Petitioners' merits brief (filed 5/22/2026) was not provisioned and I
  could not retrieve it**: the CourtListener MCP sidecar returned HTTP 429
  (daily rate limit exhausted) on my first call, and there is no sanctioned
  REST fallback, so I degraded to the provisioned inputs per the prompt.
  The asymmetry means my read of the merits-stage advocacy is
  respondent-side only; I discounted it accordingly (the government's
  positions are well represented by its petition and the docket).
- `fedcourts query` has no free-text filter and its priors are
  cert-disposition rows, marginal for a merits judgment; I ran no
  substantive corpus queries and anchored on the statpack instead.
- `record/context.json` carries `band: "federal"` — a cert construct on
  this granted docket; per the merits-stage rule I did not anchor on it
  and no flag is owed.
- I carry general knowledge of this litigation area from training
  (including *Seven County*, decided 2025, which the petition itself cites)
  but I do not know this case's outcome — none exists.
