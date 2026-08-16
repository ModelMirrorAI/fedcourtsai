# Rationale for the numbers

**P(disturbed) = 0.35; judgment = affirmed; votes 6–3.**

## Anchor

The committed statpack's "The merits docket (granted cases)" section publishes
an `excluded` count, so its rate is quotable and is the baseline this cell is
scored against. My grant Term is OT2025 (grant date 2026-05-18, from the
event's `opened_at`). Pooling `disturbed` over `parsed` across the ten grant
Terms strictly before it (2015–2024, of which the pack holds 2017–2024):
359/515 = **69.7%**, well past the 30-parsed floor. Coverage in the pooled
window is solid (e.g. 73/75 parsed in 2024, 52/58 in 2017); the censoring
caution mainly affects Term 2025, which is outside my pool.

## Adjustment — a large downward shade, and why

I moved from 0.70 to 0.35. That is an unusually large shade off the base rate,
so the drivers, in order of weight:

1. **The SG's CVSG position (retrieved, pre-grant, forward-legitimate).** The
   United States recommended granting while supporting respondents on the
   merits (SCOTUSblog's grant coverage: Sauer "recommended the Court grant
   review despite supporting the university's position"; Littler's alert
   corroborates the merits skepticism — the government "questioned whether it
   is appropriate for the Court (rather than Congress) to extend a private
   right of action under Title IX"). I could not fetch the brief PDF itself
   (supremecourt.gov, DOJ, and the SCOTUSblog mirror all returned 403 to my
   fetcher), so this rests on two independent secondary reports rather than
   the primary text — discount accordingly. Historically the SG's merits-side
   amicus position wins well more than half the time; conditioning on it pulls
   P(affirm) toward 0.6+.
2. **Doctrinal fit.** Affirmance is the low-energy path for this Court:
   decline to extend an implied cause of action (Sandoval / Abbasi / Egbert
   method; Cummings in the closest doctrinal neighborhood), with Title VII
   displacement as the rationale — no precedent overruled, Jackson
   distinguished as a retaliation case. The base-rate's ~70% reversal reflects
   mostly cases granted to correct outlier decisions; here the more probable
   grant purpose was to *endorse* the outlier, given signal 1.
3. **Grant-coalition inference.** Petitioners already held an 8–3 circuit
   majority; the marginal cert votes were plausibly Justices content with the
   Eleventh Circuit's rule.

Held against those, keeping the number at 0.35 rather than 0.25: the
petitioners' textual case is strong (North Haven reads "no person" to cover
employment; Cannon + Jackson supply the enforcement syllogism), eight circuits
agree, and this Court's recent statutory employment-discrimination decisions
(Bostock, Muldrow, Ames) show it follows text to pro-employee results. A
textualist crossover (Gorsuch, possibly with Roberts/Kavanaugh) is the real
reversal path, and I do not think it is below one-in-three.

## Field coherence

`judgment = affirmed` (undisturbed), so `granted = 0` and `probability = 0.35`
sits on the correct side of the named judgment. `predicted_disposition` is
`other`, as the merits stage requires. The single declared claim
`judgment-disturbed` restates `probability` exactly. DIG (~0.03) and equally
divided affirmance (~0) live inside the 0.65 undisturbed mass.

## Votes

Modal lineup 6–3 on ideological lines. This is the highest-variance part of
the forecast: conditional on affirmance I'd put 6–3 at roughly half the mass,
with 7–2/5–4 variants splitting the rest; conditional on reversal the lineup
inverts unpredictably (a Bostock-style 6–3 the other way is plausible).
Writing forecasts (Alito majority, Sotomayor principal dissent) are low
confidence and banked, not scored.

## Evidence base and its limits

Forward-mode cell; the judgment does not exist (merits briefing is still under
way — respondents' brief due 2026-08-17). I worked from the provisioned
snapshot (full docket through 2026-08-16), the provisioned petition, BIO, and
QP texts, the committed statpack, and open-web retrieval (SCOTUSblog, Littler)
for the CVSG position and grant coverage. I did **not** read the merits briefs
themselves: the petitioner's merits brief (filed 2026-07-10) and five
petitioner-side amicus briefs are on the docket but supremecourt.gov PDFs were
unfetchable (403), so my read of the merits advocacy is inferred from the cert
papers — a forecast on the cert-stage texts plus the docket skeleton of the
merits calendar, and a reader should discount the ground/breadth propositions
accordingly. The corpus `query` for Cannon/Jackson-citing priors returned no
rows (known citation-coverage gap: only 161 of 590k SCOTUS rows carry citation
data), so no case-level priors informed the number beyond the statpack.

Main uncertainties: (a) the SG's position is second-hand — if the reports
mischaracterize it, my biggest adjustment is unfounded; (b) the salience band
in `record/context.json` (`high`) is a cert construct and was not used, per
the stage rule; (c) whether Gorsuch treats this as a Bostock-style text case
or a Sandoval-style remedies case is close to a coin flip and drives most of
my residual variance.
