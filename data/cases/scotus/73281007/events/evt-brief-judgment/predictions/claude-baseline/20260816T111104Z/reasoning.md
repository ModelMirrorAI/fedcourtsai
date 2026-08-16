# Rationale for P(disturbed) = 0.45

## Anchor

The committed statpack's merits section publishes an `excluded` count, so its
rate is quotable. Pooling the per-Term disturbed counts over grant Terms
strictly before this case's — grant date 2026-04-27, so grant Term 2025, pool
2015–2024, of which the pack holds 2017–2024 — gives 359 disturbed / 515
parsed ≈ **69.7%** (well above the 30-parsed floor). That is the baseline this
cell's skill is scored against. Coverage caveat quoted per the pack's terms:
the parsed slice covers 515 of the pooled Terms' grants, and the nearest Terms
are the most pendency-censored.

## Why I sit 25 points below the anchor

I moved from 0.70 to 0.45 on five case-specific features, each visible in the
pre-decision record:

1. **The government must win both granted questions; Sun Valley needs one.**
   Reversal requires holding both that 8 U.S.C. §1188(g)(2) authorizes DOL's
   conclusive in-house adjudication (QP2) and that Article III permits it
   (QP1). Either a statutory-avoidance holding or a Jarkesy-extension holding
   ends in affirmance. A conjunction of two contested propositions should not
   sit at the all-grants base rate.
2. **The Court added the statutory question itself.** The petition presented
   only the Article III question (petition text, QP page); the grant is
   "limited to" two questions, the second statutory. The BIO's lead argument
   was precisely that the statute says nothing about where liability is
   adjudicated. A Court that adds an antecedent avoidance question sua sponte
   is keeping an offramp that only Sun Valley can use.
3. **The grant carries little reversal signal.** The SG petitioned from the
   first court of appeals to invalidate a federal statute's application
   post-Jarkesy; the Court grants that posture near-automatically (Jarkesy
   itself arrived the same way — and was affirmed 6-3 against the SG).
4. **The doctrinal center of gravity.** Under Jarkesy's framework the remedies
   here look bad for the government: civil penalties ("all but dispositive"
   per Jarkesy) plus back wages that function as contract damages for breach
   of job-order terms DOL itself has called contractual. The intervening
   decision in FCC v. AT&T, 608 U.S. ___ (June 4, 2026) — verified via
   CourtListener — cut *for* the agency there only because §504 guarantees a
   de novo jury trial before any obligation attaches; DOL's H-2A scheme has no
   such feature (ARB order conclusive, deferential APA review only), so the
   case that cabined Jarkesy simultaneously sharpened the line this scheme
   falls on the wrong side of.
5. **Alignment of the briefing war.** The respondent-side merits amicus wave
   (Chamber, NFIB, Cato, NCLA, WLF, PLF, SLF, TPPF, Atlantic Legal, Meese/
   Mukasey/Calabresi/Lawson, Wurman, former DOL officials, Altria) is the
   coalition this Court's Article III majority has repeatedly sided with;
   the government's support (AFL-CIO, Public Citizen, CAC, admin-law
   professors) comes from the Jarkesy dissent's side.

## Why not lower

Three genuine forces keep me near a coin flip rather than at 0.3: the SG's
petitioner win rate is high even discounting the quasi-automatic grant; the
immigration public-rights line (Oceanic Steam, Lloyd Sabaudo) is the single
strongest historical category the government could ask for, and Jarkesy's own
majority cited it approvingly — Roberts assembled 8 votes to cabin Jarkesy in
FCC v. AT&T and could plausibly do it again here with the three liberals,
Kavanaugh, and one more; and the H-2A scheme is a federal licensing/benefit
program where the "condition on a government-granted privilege" frame
(Oil States-adjacent) has real purchase.

## What I read and what I did not

Provisioned inputs: the snapshot (full docket through Aug 11, 2026, argument
set Nov 10, 2026), the QP text, the cert petition text, and the
`brief-in-opposition` document — which in this cell concatenates the BIO with
the respondent's July 27 merits brief (two URLs in `documents.json`), so I had
respondent merits advocacy in text. I did not retrieve the government's June
18 merits brief; its theory is fully stated in the petition (Oceanic/public
rights), so my read of petitioner's merits case is from the cert-stage
document plus the docket. Forward cell, retrieval unrestricted: I verified FCC
v. AT&T's holding and lineup on CourtListener (it postdates my training) and
pulled corpus priors for context. This forecast is briefed-moment: it uses
both sides' merits positions, not the docket skeleton alone.

The cert-stage salience band in `record/context.json` (`federal`) scores grant
likelihood, which is settled; per the stage rule I did not anchor on it.

## Uncertainties, and where to discount me

- **Coalition uncertainty dominates.** The outcome turns on whether Roberts
  and Kavanaugh see this as Oceanic's immigration category (reverse) or
  Jarkesy's contract-and-penalties core (affirm). I have no strong evidence on
  that beyond FCC v. AT&T's revealed preferences, which point modestly both
  ways. Genuinely 0.40–0.55 territory; 0.45 is a judgment call.
- **The vote block is my modal-scenario lineup**, not per-Justice independent
  maxima; if affirmance comes on statutory grounds the coalition could be
  7-2 or larger and my dissent calls for Roberts/Kagan/Jackson would be wrong
  even though the judgment call was right.
- **Court composition** is assumed unchanged through decision day (no vacancy
  or recusal on the record).
- Sun Valley's wound-down operations create a small mootness/DIG tail I price
  at ~2%.
