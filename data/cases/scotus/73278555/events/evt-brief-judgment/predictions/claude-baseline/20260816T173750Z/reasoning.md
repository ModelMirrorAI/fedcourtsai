# Reasoning — why P(disturbed) = 0.66, judgment = vacated

## Anchor

Grant date January 16, 2026 → grant Term **OT2025** (taken from the grant
order on the docket; the companion `evt-order-judgment` was opened 2026-01-16).
The statpack's "The merits docket (granted cases)" section publishes an
`excluded` count, so its rate is quotable as the scored baseline. Pooling the
ten grant Terms strictly before 2025 (2015–2024), the pack holds rows for
2017–2024 only: disturbed 50+34+49+46+57+42+50+31 = **359** over parsed
73+55+72+65+69+54+75+52 = **515** → **69.7%**, comfortably past the 30-parsed
floor. Coverage beside that figure: those Terms show 557 granted against 515
parsed (plus 57 excluded by the pool guard), so censoring in the pooled window
is modest; I did not use the 2025 row (the case's own Term) or the pack-level
69.8%.

## Adjustments

**Down from 0.697 to 0.66**, a net negative adjustment driven by one signal
with several partial offsets.

Down:
- **The United States supports respondents.** The SG (with DOL alignment —
  DOL's own press release urges affirmance) filed a merits amicus on July 9,
  2026 in the respondents' window and moved for divided argument. A merits-stage
  SG brief against disturbance is the strongest single affirm-side signal a
  granted case can carry, and it flips the posture of *Hughes* (where the SG
  supported the plan participants).
- **An affirm-with-clarification exit is genuinely open.** The CA9 panel (and
  Berzon's concurrence, which respondents quote) disclaimed an "always"
  requirement, so the Court can affirm while restating the rule as ordinary
  *Twombly* plausibility — respondents' brief is built to make that easy — and
  this Court is broadly sympathetic to pleading-stage screening of ERISA suits
  (*Dudenhoeffer* itself stressed careful 12(b)(6) scrutiny).
- Heavyweight respondent-side amicus field (Chamber, ICI, NAM, ABC, AIC) and
  top-tier respondent counsel (Lisa Blatt).

Up (partial offsets, keeping the number near the baseline rather than far
below it):
- **The grant itself leans corrective.** The Court granted the plaintiffs'
  petition, framed in *Hughes*'s anti-categorical language, over a BIO whose
  lead argument was no-split/percolation — and held the defense-side vehicle
  (*Parker-Hannifin*, No. 24-1030) rather than granting it. A Court content
  with the meaningful-benchmark regime had an easy denial.
- **The line's track record.** *Dudenhoeffer*, *Tibble*, *Hughes*,
  *Cunningham* — every recent ERISA pleading/duty case disturbed a
  circuit-crafted shortcut, unanimously; Intel lost *Sulyma* 9-0 in this same
  litigation.
- Petitioners' merits framing (atextual heightened standard vs. holistic
  plausibility) maps exactly onto the reasoning that carried those cases.

## Coherence of the fields

`judgment = vacated` is the modal single label (~45%), with affirmed ~34%,
reversed ~8%, affirmed-in-part ~5%, DIG/equally-divided ~2-3% jointly, other
mass in rounding; P(disturbed) = vacated + reversed + in-part ≈ 0.66 is the
scored binary, `granted = 1` restates it, and `judgment-disturbed`
equals `probability` exactly. The all-majority vote block reflects that both
modal outcomes in this line arrive unanimous or near-unanimous; per-Justice
P(dissent) never exceeds ~20% for anyone (highest for Alito/Thomas in a
vacate world, for the three Democratic appointees in an affirm world, and those
scenarios partially cancel).

## What I worked from, and where to discount me

I worked from the provisioned snapshot (full docket through the August 12
CIRCULATED entry), the QP text, the cert petition, and the bundled
respondents' filings — the December 2025 BIO **and Intel's July 2026 merits
response brief**, which the pipeline delivered under the `brief-in-opposition`
document (truncated at 98 pages; see flags). Forward-mode web retrieval
confirmed the SG/DOL position and *Parker-Hannifin*'s held status. I did
**not** have the petitioners' merits brief text, the SG brief text
(supremecourt.gov returned 403 to fetches), or any argument transcript (none
exists yet — argument is October 6, 2026), so my read of the petitioner-side
merits case is inferred from the cert petition and secondary coverage.
Main uncertainties: (1) how much weight this Court gives an SG amicus urging
affirmance in a statutory pleading case — my 0.03-0.04 net downward move may
understate it; (2) whether "vacate vs. affirm on clarified reasoning" is closer
to a coin flip than my 45/34 split — the two opinions could share 90% of their
text and differ only in the bottom line; (3) one corpus `query` (citation
filter) returned empty on a known coverage gap, so my priors here rest on the
statpack and general knowledge of the ERISA line rather than retrieved corpus
rows.
