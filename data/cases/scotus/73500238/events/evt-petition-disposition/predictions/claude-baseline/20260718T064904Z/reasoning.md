# Balwani v. United States, No. 25-1330 — cert prediction

**Prediction: denied. P(any grant, GVR included) = 0.04.**

## The case

Ramesh "Sunny" Balwani, former Theranos president/COO, was convicted on all
twelve counts (two conspiracy, ten wire fraud) and is serving a 155-month
sentence. The Ninth Circuit affirmed; its amended opinion issued December 22,
2025 (163 F.4th 547), denying panel and en banc rehearing. Justice Kagan
extended the cert deadline to May 21, 2026; the paid petition was filed that
day. The Solicitor General **waived the right to respond** on June 9, 2026, and
the petition was **distributed for the September 28, 2026 conference** (the
summer "long conference"). Mode is `forward`: the first conference is more than
two months after the snapshot date, so no outcome exists.

## Questions presented

1. **Napue question** — whether plain-error review may be applied to a Napue
   violation where the prosecution not only failed to correct testimony the
   Ninth Circuit itself called "actually false" (investor-witness Tolbert's
   account that Theranos devices were "employed on the medevac helicopters"),
   but exploited the falsity over a dozen times in closing and rebuttal.
   Petitioner alleges a split with the Second, Fifth, Eighth, and Eleventh
   Circuits and a conflict with *Glossip v. Oklahoma*, 604 U.S. 226 (2025).
2. **Rule 702 question** — whether a court of appeals may excuse a district
   court's complete failure to perform Rule 702(b)–(d) gatekeeping (two lab
   directors tendered as percipient witnesses gave what the panel conceded was
   expert opinion) on the sole ground that the witnesses would have qualified
   as experts on credentials and experience. Petitioner alleges a
   seven-circuit majority rule anchored in en banc authority (*Frazier*,
   *Nacchio*, *EcoFactor*) plus an intra-circuit conflict with *Engilis v.
   Monsanto* (9th Cir. 2025).

## Base rates (committed statpack, Term rows through 2025)

- Modern discretionary-cert petitions: grants ≈ 3.1% of resolved
  (367 granted / ~11.7k resolved, denial-reweighted).
- Term 2025 estimated grant rate: 2.5%; Term 2024: 3.0%.
- Ninth Circuit-originating petitions (modern slice): 3.0% granted.
- Relist signal: 0-relist petitions grant at 0.8%; 2 relists 33.6%; 3+ 21.8%.
  This petition has not yet reached its first conference, so the relist signal
  is unobserved — the unconditional paid-petition anchor applies. Paid
  petitions (this is one, with retained appellate counsel) grant well above
  the blended rate; call the anchor **≈ 4–5%**.

## Signals moving off the anchor

**Downward:**

- **The government waived response.** The Court essentially never grants
  without a response on file; the realistic best case for petitioner at the
  September 28 conference is a call for a response (CFR), which would only be
  the first of several hurdles. The SG's waiver signals the government sees no
  cert-worthy question, and the long conference is where the summer's
  accumulated petitions are overwhelmingly denied.
- **Vehicle problems on the Napue question.** The panel "assume[d] without
  deciding" that a duty to correct attached, resolved preservation against
  petitioner on a record-specific reading of the April 29, 2022 colloquy, and
  alternatively found no effect on substantial rights. The question presented
  is a standard-of-review question layered over a contested preservation
  record with an independent prejudice holding beneath it — three escape
  hatches for a Court inclined to deny. The alleged four-circuit split mixes
  direct-review, § 2255, and AEDPA postures, mostly from 1977–1991; it is
  softer than the petition presents it.
- **The Rule 702 question is at bottom a harmless-error application.** The
  panel found the lay/expert error but held it harmless; the cited
  majority-rule cases (*Frazier*, *Nacchio*, *Sardis*, *Sprafka*) are mostly
  preserved-error/abuse-of-discretion decisions, not holdings about what an
  appellate court may do at the harmlessness step. The Court rarely grants to
  police circuit-level harmless-error practice, and an intra-circuit conflict
  (*Engilis*) is for the Ninth Circuit en banc, which already declined.
- Fact-bound, error-correction flavor overall: a one-defendant fraud appeal
  where the court below found any error harmless on "ample evidence."

**Upward:**

- Genuinely recurring issues: the lay/expert line and post-2023-amendment
  Rule 702 rigor have live circuit tension, and *Glossip* (2025) is a fresh
  hook the amended opinion conspicuously did not address after issuing
  post-*Glossip*.
- Quality paid petition from a published, amended court-of-appeals opinion;
  the panel's own "actually false" finding gives the Napue claim an unusually
  clean factual predicate.
- High salience (Theranos) marginally raises the odds of a CFR or a relist
  look; no companion Elizabeth Holmes petition is on the SCOTUS docket yet
  (checked CourtListener), so there is no linked-case grant pressure.

## Net

Start at ~4–5% for a paid CA9 petition, take a meaningful haircut for the SG
waiver + long-conference posture and the layered vehicle problems, and give a
partial offset for the *Glossip* hook and the recurring Rule 702 issue. That
lands at **P(grant, including GVR) ≈ 0.04**. A GVR path is implausible here
(no intervening decision the Ninth Circuit failed to apply — *Glossip*
predates the amended opinion), so the predicted disposition is a straight
**denial**, most likely at or shortly after the September 28, 2026 conference,
possibly after a CFR-and-BIO detour that ends the same way.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-18.json`), the petition's
questions-presented extract and full petition text under `record/documents/`
(no brief in opposition exists — response waived), the committed
`metrics/statpack.md` base rates, one `fedcourts query` for recent granted
SCOTUS priors (which confirmed granted petitions typically show multiple
conference distributions before the grant), and two CourtListener MCP docket
searches for a companion Holmes petition (none found). No information about
this case's own disposition was sought or encountered.
