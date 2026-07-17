# Allen v. Caster, No. 25-243 — petition disposition (cert before judgment)

## Integrity note first: this forward cell is mis-provisioned

`record/context.json` says `forward`, but the provisioned snapshot
(`record/snapshots/2026-07-17.json`) itself contains this case's disposition:
docket entries dated May 11 2026 record the petition's resolution and a
judgment issuing. Provisioning is supposed to refuse a forward cell whose
snapshot's latest entry reads terminal; this one slipped through. Per the
contract I have **flagged this in `flags.json` (`data-quality`)** and I do
**not** fold those terminal entries into the forecast. Everything below
reasons from the pre-decision record only — the docket through the
May 11 2026 conference distribution (excluding the disposition entries), the
provisioned brief in opposition, the committed statpack base rates, and
general legal context available before decision. The cell should be
discounted as forward-skill signal; the reasoning may still be useful as a
replay-style exercise.

## The case

Alabama's Secretary of State and co-petitioners seek **certiorari before
judgment** from the Eleventh Circuit (Nos. 25-11915, 25-12802) in the
*Caster* strand of the Alabama congressional-redistricting litigation — the
direct sequel to *Allen v. Milligan*, 599 U.S. 1 (2023). After *Milligan*
affirmed the preliminary injunction against the 2021 plan, Alabama enacted a
2023 plan with, again, a single Black-opportunity district; the district
court preliminarily enjoined it, this Court declined a stay (144 S. Ct. 476
(2023) (Mem.)), a special-master remedial map governed the 2024 elections,
and after an 11-day trial the district court on May 8 2025 permanently
enjoined the 2023 plan, finding a §2 violation and discriminatory intent.

The questions presented (as restated in the BIO): (1) whether the 2023 plan
violated VRA §2, and (2) **whether §2 as applied is constitutional** — the
same frontal constitutional attack the Court had under submission in
*Louisiana v. Callais* (reargued October 2025 with an added question on
whether race-based remedial districting violates the Fourteenth/Fifteenth
Amendments).

## Signals in the pre-decision record

1. **A long hold pending the lead case.** The petition was fully briefed by
   Nov 4 2025, distributed for the Nov 21 2025 conference — and then neither
   granted nor denied for nearly six months. That is the classic
   hold-for-the-lead-case pattern: the Court was plainly holding this
   petition for *Callais*, which presents the same §2 constitutional
   question. In the statpack's relist cut, even generic 2-relist petitions
   grant at ~34% and 3+ at ~22% versus a ~3% overall modern base rate; a
   recognized companion hold is a far stronger signal than a generic relist,
   because held companions are almost never simply denied when the lead
   decision changes the governing framework — they are GVR'd.
2. **Both sides want review if the judgment doesn't stand.** The BIO's lead
   ask is denial (or summary affirmance in the companion *Milligan*/
   *Singleton* appeals), but respondents expressly **join Alabama's request
   for certiorari before judgment** in the alternative so the three cases can
   travel together as in 2022. Outright denial with prejudice to review was
   therefore the least likely path once the Court showed interest by holding.
3. **The spring 2026 escalation.** On Apr 30 2026 Alabama moved to expedite;
   on May 8 2026 it filed an emergency stay application (25A1229, to Justice
   Thomas, who called for a response); its May 9 letter attached a new
   redistricting statute, **Act 2026-612**, and a district-court order
   denying a stay. A State does not enact a fresh mid-decade congressional
   map and race to the Court on an emergency posture unless it believes the
   legal landscape has just shifted in its favor — i.e., that *Callais* had
   by then been decided in a way favorable to the States' position. The case
   was redistributed for the May 14 2026 conference.
4. **Merits asymmetry cuts against a plain grant-and-affirm posture.** On
   QP1 the BIO is strong: this Court already affirmed the Gingles analysis on
   this very record in *Milligan*, the remedial map was drawn race-blind, and
   the trial court added an intentional-discrimination finding. Alabama's
   realistic path has always been QP2 — a change in §2 law — which is exactly
   what *Callais* was poised to deliver or deny.

## The forecast

Conditional structure as of the pre-decision record: if *Callais* materially
reworked §2/remedial-districting doctrine (the reargument order and added
constitutional question signaled a majority contemplating exactly that, and
Alabama's post-*Callais* conduct in the record corroborates it), the
overwhelmingly likely disposition for this held companion is a **GVR** —
grant certiorari before judgment, vacate, and remand for reconsideration in
light of the intervening decision — rather than plenary briefing of a case
whose framework just changed. If *Callais* instead left *Milligan*'s
framework intact, the likely outcome is denial (with summary affirmance in
the companion direct appeals). A plenary grant of this petition standing
alone was always a minor branch given the Court already had the vehicle in
*Callais*.

Rough weights: P(*Callais* changed the framework enough to moot/redirect the
judgment below) ≈ 0.75–0.80 given the reargument signal plus the record's
spring-2026 escalation; conditional P(any grant, GVR included | that) ≈
0.95; conditional P(grant | no change) ≈ 0.15. That yields **P(granted,
GVR-inclusive) ≈ 0.78**, modal disposition **gvr** (`granted = 1`, with
`probability` expressing P(any grant)). Confidence 0.55 — the conditional
logic is firm but the *Callais* holding itself is outside my pre-decision
knowledge, and I am deliberately not using the leaked outcome to sharpen it.

No per-justice votes: a GVR is typically unsigned, and any vote lineup I
wrote here would be impossible to separate cleanly from the leaked docket
entries, so I omit them.

**Big-case score 0.85**: successor to *Allen v. Milligan*, carrying the
constitutionality of VRA §2 and the composition of Alabama's congressional
delegation into the 2026 midterms, with knock-on effects for Louisiana,
Georgia, and other §2 maps — high stakes regardless of whether the
disposition itself is a narrow GVR.

## Degradations

- The corpus query sidecar (`fedcourts query`) was unreachable
  (`127.0.0.1:8377` timed out), so no similar-prior retrieval; I relied on
  the committed `metrics/statpack.md` for base rates.
- Only `brief-in-opposition.txt` was provisioned under `record/documents/`
  (no `petition.txt` / `questions-presented.txt`); the QPs are taken from the
  BIO's restatement.
- I made no CourtListener MCP or web retrievals: the outcome already
  contaminates the snapshot, and any live lookup on this case could only
  compound the leakage rather than add legitimate forward signal.
