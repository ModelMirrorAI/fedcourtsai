# Rationale for the numbers

**P(disturbed) = 0.45, judgment = affirmed.**

**Anchor.** The committed statpack's "The merits docket (granted cases)"
section publishes an `excluded` count, so its pooled rate is quotable and is
the baseline my Brier skill is scored against. This case's grant date is
2026-04-27 (from the event's `opened_at`), i.e. grant Term OT2025, so the pool
is grant Terms 2015–2024; the pack holds parsed judgments for Terms 2017–2024,
and pooling those rows gives 359 disturbed / 515 parsed ≈ **69.7%** (n = 515,
comfortably over the 30-parsed floor). Coverage caveat quoted per the pack's
caption: recent Terms' `parsed` undercounts `granted` mostly through pendency,
so the nearest Terms in the pool are censored toward quicker dispositions.

**Why I sit 25 points below the anchor.** Five case-specific features, all
pointing the same way:

1. **The grant was quasi-obligatory, so it carries little
   selection-for-reversal signal.** The Third Circuit held that Article III
   forbids the adjudication § 1188(g)(2) is read to authorize — the Court
   near-automatically grants when a court of appeals disables a federal
   statute, whatever the Justices think of the merits. *SEC v. Jarkesy* is the
   on-point precedent for what such a grant can end in: same posture
   (government petition after a circuit condemned agency penalty
   adjudication), and the Court **affirmed** 6–3.
2. **The Court itself added the statutory question.** The petition presented
   only the Article III question; the grant added whether § 1188(g)(2)
   authorizes the adjudication at all, which the BIO had pressed as an
   antecedent, unresolved issue. That deliberately opens a constitutional-
   avoidance route whose natural terminus is an affirmance on alternate
   grounds.
3. ***FCC v. AT&T* (June 4, 2026, 8–1, Roberts) is a bad omen for this
   scheme.** The Court rejected the Seventh Amendment challenge to FCC
   forfeitures *because* those orders bind nobody until the government wins a
   de novo jury trial in district court — and read the power to "impose"
   penalties as consistent with adjudicating them in court. DOL's ARB order is
   final and binding, reviewable only deferentially under the APA, so the
   distinguishing feature that saved the FCC is absent here, and the AT&T
   reading of "impose" maps directly onto § 1188(g)(2)'s "imposing appropriate
   penalties" to support a statutory affirmance. This intervening decision
   (postdating my training data; surfaced via the respondent's merits brief
   and confirmed by web retrieval) is the single largest driver of my
   downweight.
4. **The government's only doctrinal hook is marred on its own facts.**
   *Jarkesy* preserved an immigration public-rights category (*Oceanic Steam*,
   *Lloyd Sabaudo*), but those cases policed conditions of admission at the
   border; here DOL adjudicated what its own regulations call "enforcement of
   contractual obligations," with penalties and back wages computed over 51
   **domestic** workers alongside the 96 H-2A workers. Back wages are a
   classic legal remedy (*Terry*), and the ALJ's own framing was
   breach-of-contract.
5. **Reversal is conjunctive.** The government must win *both* granted
   questions — statutory authorization and Article III. Roughly
   P(statute authorizes) ≈ 0.55 and P(Article III permits | reached) ≈ 0.6
   gives a joint ≈ 0.33 for outright reversal, which is where my modal-reverse
   mass sits.

**Why not lower.** *Jarkesy*'s majority opinion expressly lists immigration
among the historic public-rights categories, and the government's
"conditions on a government-conferred privilege" theory is a fair reading of
*Oceanic Steam*; the three *Jarkesy* dissenters are near-certain government
votes, so the SG needs only two of six conservatives, with Roberts and
Kavanaugh genuinely gettable. SG petitions also win far more often than they
lose. Partial-disturbance routes (splitting penalties from back wages, or a
vacatur that returns the case for the statutory question) add ≈ 0.12. Summing
my outcome distribution (reverse 0.33, affirm-statutory 0.28, affirm-Art. III
0.22, in-part 0.07, vacate 0.05, DIG 0.02, equally divided 0.01) gives
P(disturbed) = 0.33 + 0.07 + 0.05 = **0.45**.

**What I read and what I did not.** I worked from the provisioned snapshot
(full docket through 2026-08-16, including the grant order's exact QPs, the
merits calendar, and the amicus field), the provisioned cert petition, the
provisioned respondent file (which carries both the BIO and respondent's
merits brief on the merits of both questions), and the committed statpack.
The government's merits brief (filed 2026-06-18) is **not** provisioned and I
did not fetch it; I know its cert-stage arguments from the petition, so my
read of the government's best merits case is inference from the petition plus
the respondent's characterizations — discount accordingly. This is a `forward`
cell (mode from `record/context.json`; the judgment does not exist — argument
is set for 2026-11-10), so my retrieval of the intervening OT2025 decisions
(*FCC v. AT&T*, *Sripetch*) and case commentary is legitimate forward signal,
not leakage; nothing outcome-revealing about *this* case exists to find.

**The cert band is not used.** `record/context.json` carries `band: "federal"`
with `distribution_count: 2` — cert-stage observations about the now-settled
grant. Per the stage rule, no merits anchor derives from them and no flag is
owed.

**Main uncertainties, where to discount me.** (a) The vote-lineup and
authorship forecasts are the weakest part — conditional on affirmance I
guessed 6–3 with the liberals dissenting, but a statutory holding could
attract a much broader coalition (AT&T was 8–1), making my dissent picks
wrong even if the judgment call is right. (b) I have not read the argument
transcript (none exists yet); a briefed-moment cell will know more. (c) My
P(statute authorizes) ≈ 0.55 rests on a textual judgment about "imposing"
against AT&T's reading; if the government's merits brief has a stronger
structural answer than the petition suggests, 0.45 is too low by perhaps a
nickel. (d) The pooled baseline's nearest Terms are pendency-censored, which
if anything overstates quick reversals in the pool — a reason my sitting
below the anchor is more defensible, not less.
