# Petersen v. Mi Familia Vota, No. 25-1019 — petition disposition

## The case

Arizona's 2022 election laws (H.B. 2492 and H.B. 2243) require documentary
proof of citizenship (DPOC) and residence on the state voter-registration form,
bar registrants without DPOC from voting by mail, and mandate database checks
to identify potential non-citizen registrants. After a nine-day bench trial,
the District of Arizona held the state-form DPOC/residence requirements and the
mail-voting bar preempted by the NVRA (and, for citizenship, barred by the 2018
LULAC consent decree), while finding H.B. 2243 was not enacted with
discriminatory intent. A divided Ninth Circuit panel affirmed the injunction
and reversed the no-discriminatory-intent finding (129 F.4th 691); rehearing en
banc was denied over eleven dissents (152 F.4th 1153). The Supreme Court had
already stayed the injunction against the state-form DPOC requirement in August
2024 (RNC v. Mi Familia Vota, No. 24A164), with three Justices also voting to
allow the mail-voting/presidential-voting provisions.

Petitioners here are the Arizona Senate President and House Speaker
(intervenor-defendants below). Their three questions: (1) whether the NVRA or
the consent decree precludes state-form DPOC/residence requirements; (2)
whether the NVRA preempts the mail-voting bar for registrants without DPOC;
(3) whether the Ninth Circuit improperly overturned the district court's
discriminatory-intent finding (a Brnovich-style clear-error challenge).

## The decisive structural fact

This petition travels with two companions from the same Ninth Circuit
judgment, all vided and distributed together: RNC v. Mi Familia Vota
(25-1017) and Arizona v. Promise Arizona (25-1022). Per the United States'
consolidated response and SCOTUSblog's June 25, 2026 Relist Watch, the
Solicitor General — realigned in this administration to defend the Arizona
laws — **supported certiorari on the RNC petition while opposing this one**
(and Arizona's), evidently steering the Court to the cleanest vehicle.

The Court followed that steer. Public reporting that predates the provisioned
snapshot (Cronkite News, June 29, 2026; AZ Capitol Times, July 1, 2026;
Ballotpedia, July 2 and 7, 2026; NBC affiliates: the Court "agrees to take up
**part of** Arizona proof-of-citizenship voter law dispute") shows the Court
**granted the companion RNC petition (25-1017)** at the end of June 2026, on
the RNC's two questions: the state-form DPOC requirement and the NVRA 90-day
list-maintenance question, for argument in OT2026. Meanwhile this docket's
snapshot (created July 16, 2026) shows no action after the June 25 conference
distribution — 25-1019 was neither granted alongside the RNC petition nor
denied on the ensuing order lists. It is being **held**.

This is legitimate forward signal (a companion's ruling, predating the
snapshot), used per the retrieval contract and disclosed in `flags.json` as
decisive. The outcome of *this* event — the disposition of *this* petition —
remains genuinely undecided.

## What happens to a held same-judgment companion

The Court declined to consolidate this petition at the grant stage despite
having it fully briefed, distributed, and vided at the same conferences —
choosing "part of" the dispute. That choice is informative:

- **Question 1** is now subsumed by the RNC grant. Petersen and Montenegro are
  parties to the same Ninth Circuit judgment, so they benefit automatically
  from whatever the Court decides in 25-1017; no separate grant is needed.
- **Question 2** (mail-voting preemption) drew only three noted votes at the
  August 2024 stay stage — the Court declined to stay that part of the
  injunction. The SG opposed review of it. That reads as fewer than four
  Justices wanting the question now.
- **Question 3** (discriminatory intent) is interlocutory — the Ninth Circuit
  remanded for further Arlington Heights analysis — and the respondents' BIO
  presses that posture hard. The Court rarely takes fact-bound clear-error
  disputes in that stance (the petition itself asks for summary reversal,
  which the 2024 stay lineup does not support for this question).

The standard dispositions for a held companion once the lead case is decided
(expected by ~June 2027) are **denial** or a **GVR** in light of the new
decision. Denial is the modal outcome here: the petitioners get the benefit of
the RNC ruling directly, and their distinctive questions look under-supported.
A GVR is nonetheless a live possibility — if the Court reverses the Ninth
Circuit's NVRA framework (likely, given the 2024 stay and the grant), a GVR
would direct reconsideration of the judgment's remaining holdings (the
mail-voting bar, possibly the intent remand) under the new framework. A later
plenary grant (adding this petition for the same argument at the long
conference, or a next-Term grant on the mail-voting question) is a smaller
tail.

## Base rates and calibration

From the committed statpack (modern discretionary-cert slice,
denial-reweighted): overall grant rate ~2.5–3.3% per recent Term; CA9-origin
petitions ~3%; paid cases much stronger than IFP. The relist cut is the
operative anchor: 2 relists → 33.6% granted; 3+ → 21.8%. This petition has
been distributed for two conferences and carried past the Term's final
conference without denial — deep-relist territory, but with the specific
explanation (a hold behind the granted companion) that shifts mass from
"plenary grant" toward "deny or GVR." The statpack's salience-band table
referenced in the prompt is not present in the committed statpack version, so
I could not use that anchor. Corpus `fedcourts query` pulls for similar
election-law priors returned no rows (see `retrieval.md`).

My allocation:

| Disposition | Probability |
| --- | --- |
| denied (likely after the RNC merits decision, possibly at the long conference) | 0.55 |
| gvr (in light of RNC v. Mi Familia Vota) | 0.25 |
| granted (late consolidation or subsequent plenary grant) | 0.08 |
| granted-in-part | 0.01 |
| dismissed / withdrawn / other | 0.11 |

The dismissed/other bucket is wider than usual because a held petition's
endgame can also be mooted by legislative amendment or settlement over the
~year-long hold, and because same-judgment companions are occasionally
dismissed rather than denied.

**Binary P(granted, GVR included) ≈ 0.34.** Point label: **denied**,
`granted = 0`, confidence 0.55 in the modal label.

## Big-case score

0.7 — the underlying controversy (documentary proof of citizenship, NVRA
preemption, the first major election-administration merits case of the
post-2024 era) is top-tier national news with a 25-state amicus bloc, the DNC,
and the United States as parties. But the lead vehicle is the companion RNC
case; this docket's independent decision-space (mail voting for federal-only
voters, discriminatory intent) is significant yet secondary, and its likeliest
dispositions (deny/GVR) are low-visibility.

## Inputs used

- Provisioned snapshot `data/cases/scotus/73281059/record/snapshots/2026-07-17.json`
  (docket through June 22, 2026; no action after the June 25 conference).
- Provisioned `questions-presented.txt` and `petition.txt` (full petition):
  QPs, procedural history, the 2024 stay, the en banc dissents.
- Provisioned `brief-in-opposition.txt` (AZ AANHPI/LUCHA/Promise Arizona BIO):
  vehicle arguments — interlocutory posture, consent-decree framing, the
  sui generis mail-voting provision.
- Committed `metrics/statpack.md` base rates (relist, circuit, Term cuts).
- Web retrieval (forward mode, logged in `retrieval.md`): SCOTUSblog Relist
  Watch June 25, 2026 (SG's split recommendation; first relist); press
  reports of the June 29–July 2, 2026 grant in companion 25-1017.
