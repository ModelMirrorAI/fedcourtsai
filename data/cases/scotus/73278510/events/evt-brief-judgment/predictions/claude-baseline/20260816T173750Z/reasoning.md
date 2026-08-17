# Rationale for P(disturbed) = 0.45

## The anchor, and the deliberate departure from it

The committed statpack's merits section publishes an `excluded` count, so its
pooled rate is quotable and is the baseline my skill is scored against. My
case's grant Term is 2025 (petition granted January 26, 2026). Pooling
`disturbed` over `parsed` across the strictly-prior grant Terms in the
ten-Term window (the table renders 2017–2024; 2015–2016 carry no parsed
judgments and are omitted): 359/515 = **69.7%**, on a pool far above the
30-parsed floor. Coverage note: the pool's nearest Terms are the most
censored (2024 shows 73 parsed of 75 granted, but 2025 only 24 of 50), so
the pooled figure leans on quicker dispositions in recent Terms.

I place this case well below that baseline, at 0.45, for case-specific
reasons:

1. **This Court's anti-literal-breadth pattern in statutory-damages cases.**
   Respondent's core frame — class-action lawyers repurposing a targeted
   1988 statute into a general internet-privacy damages regime — is the
   exact frame that produced unanimous or lopsided narrowing constructions
   in Facebook v. Duguid (TCPA), Van Buren (CFAA), Fischer, Dubin, and
   Snyder. The contextual reading here (interlocking definitions: the
   (a)(1)/(a)(4) verb parallel, the video-specific PII definition, the
   consent provisions) is substantially stronger than the losing side's
   reading was in Bostock, the main plain-text counterexample.
2. **The vehicle-choice signal that usually favors reversal is weak here.**
   The Court denied the defense-side companion petition (NBA v. Salazar,
   No. 24-994) after many distributions and took the plaintiff's petition
   instead — but the petition itself argues at length that this case was
   the only clean vehicle (final judgment, no intervening amended
   pleadings), so the grant direction carries little information beyond
   the split's existence. Resolving a 2–2 split requires taking *some*
   case, and the clean one happened to be a petitioner-side loss.
3. **A lopsided merits amicus field.** Eleven amicus briefs supporting
   respondent (Chamber of Commerce, Meta, MPA, NCTA, News/Media Alliance,
   America's Newspapers, NRF, RLC, ESA, SIIA/CCIA, WLF/TechFreedom,
   Chamber of Progress) against two supporting petitioner (EPIC and
   Prof. Schwartz) plus one for neither party. Amicus imbalance is a
   modest but real correlate, and it also proxies the practical-
   consequences pressure the Duguid line responds to.
4. **Advocacy asymmetry.** Paul Clement argues for respondent.

Pulling the other way, and why I did not go lower: the petitioner's textual
case is genuinely strong (unqualified "goods or services"; the superfluity
of (a)(3)'s "video materials or services" limit under the narrow reading),
it persuaded the Second Circuit and Judge Easterbrook's Seventh Circuit
panel, and Judge Bloomekatz dissented below on plain-text grounds. A
Gorsuch-led textualist coalition adopting it is a live scenario, and the
disturbed branch also collects a possible narrow vacatur keyed to Salazar's
unaddressed used-the-newsletter-to-view-videos allegation. The 69.7% base
rate embodies real grant-to-reverse dynamics I should not dismiss entirely.
Netting these, 0.45 — a substantial bet against the baseline, but the
honest one.

## What I worked from

Forward-mode cell; the judgment does not exist yet (argument is set for
October 14, 2026). I worked from the provisioned snapshot (complete docket
through August 13, 2026), the provisioned questions-presented and petition
texts (the petition text includes the cert-stage appendix descriptions of
the Sixth Circuit majority and Bloomekatz dissent), and the provisioned
respondent file, which carries **both** Paramount's BIO and its merits
response brief (documents.json lists both URLs on the one entry) — so I
read respondent's actual merits-stage introduction and summary of argument.
Petitioner's merits brief and reply are on the docket but not provisioned,
and I did not retrieve their text; my read of petitioner's affirmative case
comes from the cert petition, which the merits brief presumably tracks.
No argument transcript exists yet. This is a briefed-moment forecast made
with respondent's merits advocacy on the desk but petitioner's only in
cert-stage form — discount accordingly.

## Degraded retrieval

The CourtListener MCP sidecar returned HTTP 429 (daily rate limit
exhausted) on my first call, so I had no live CourtListener access; per
the contract I fell back to the provisioned inputs, the committed statpack,
and two web searches (Ninth Circuit VPPA status; the NBA petition's fate).
`fedcourts query` takes only structured filters (court/topic/judge/
citation), none of which could target VPPA subject matter on SCOTUS rows,
so I ran no corpus query and the statpack is my only base-rate source.

## Candor about prior knowledge

This case's cert grant (January 2026) falls at the edge of my training
window: I recognize the case, the circuit split, and the grant. No merits
outcome exists to have leaked — the case is undecided — so this is context,
not contamination, but my doctrinal priors about how this Court handles
literal-breadth statutory readings are trained impressions and a reader
should weigh them as such.

## Main uncertainties

Pre-argument forecasts of merits judgments are soft; oral argument
regularly moves this kind of case by 10–20 points in either direction.
My vote lineup is a modal guess with wide error bars — Kagan, Gorsuch, and
Barrett are each genuinely uncertain between the text and context camps,
and a 9-0 in either direction would not shock. The semantic claims are
written for my modal (affirm) world and fail together with it.
