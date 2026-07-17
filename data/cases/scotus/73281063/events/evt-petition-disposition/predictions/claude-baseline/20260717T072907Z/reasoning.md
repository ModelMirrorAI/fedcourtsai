# Arizona v. Promise Arizona, No. 25-1022 — cert disposition

## The case

Arizona and Attorney General Kris Mayes petition from the Ninth Circuit's
decision in *Mi Familia Vota v. Fontes*, 129 F.4th 691 (9th Cir. Feb. 25,
2025), rehearing en banc denied over eleven dissents, 152 F.4th 1153 (Sept.
22, 2025). The panel majority (Bumatay, J., dissenting) held that Promise
Arizona had associational standing to appeal — on the theory that an unknown
number of its unidentified members "may be" injured by H.B. 2243's
citizenship list-maintenance program — and vacated the district court's
post-trial finding that H.B. 2243 was not enacted with discriminatory
purpose, remanding for a redo of the *Arlington Heights* analysis.

The questions presented are (1) whether Article III permits organizational
standing on a "may be injured" showing, in claimed conflict with *Summers v.
Earth Island Institute*, 555 U.S. 488 (2009), and at least seven circuits
(the Ninth Circuit's *La Raza* exception); and (2) whether the panel
improperly reweighed evidence of discriminatory purpose under the guise of
clear-error review, contrary to *Brnovich* and the *Abbott v. Perez*
presumption of legislative good faith.

This is one of three companion petitions from the same judgment: 25-1017
(Republican National Committee — the NVRA voter-roll and state-form DPOC
questions, plus the LULAC consent decree), 25-1019 (Arizona legislative
leaders — the mail-voting ban plus the intent question), and this one. All
three were briefed together; the United States, a respondent below, filed a
single consolidated brief.

## The decisive facts

1. **The Solicitor General expressly recommended denial of this petition.**
   The Acting SG's May 26, 2026 brief supports certiorari in 25-1017 only and
   argues 25-1019 and 25-1022 should be denied: the discriminatory-intent
   question is interlocutory, fact-bound error correction (the district court
   can reaffirm on remand, especially after *Abbott v. LULAC* (2025) and
   *Louisiana v. Callais* (2026)), and Promise Arizona's standing defect is a
   vehicle problem rather than an independently certworthy question at this
   stage. All private respondents waived responses; the SG's brief is the
   only opposition.

2. **The Court has already followed the SG's script on the lead petition.**
   Per corpus retrieval and public reporting (see `retrieval.md`), the Court
   granted certiorari in 25-1017 on June 29, 2026, after the trio was
   distributed for the 6/18 and 6/25 conferences (one relist). It did **not**
   act on 25-1019 or 25-1022 — no grant, no denial, no redistribution appears
   on this docket through the July 16 snapshot. That pattern — companion
   petitions from the same judgment left undisturbed after the lead is
   granted — is the classic signature of a **hold** pending the merits
   decision in *RNC v. Mi Familia Vota*, expected by June/July 2027.

3. **This petition's questions are severable from the granted ones.** The
   granted case will resolve the NVRA preemption and consent-decree issues.
   The standing/intent questions here concern a different, constitutional
   claim that the Ninth Circuit remanded to the district court; that remand
   proceeds regardless of how the NVRA questions come out. A held companion
   whose issues are orthogonal to the granted case is most often denied when
   the lead case is decided (Arizona can re-petition from an adverse final
   judgment, as the SG noted).

## Base rates and adjustment

From the committed statpack (modern discretionary-cert petitions,
denial-reweighted): overall grant rate ~2.5–3.3% per recent Term; Ninth
Circuit petitions ~3%; one relist raises grant to ~7.6%, two relists to
~33.6%. Mechanically this docket now shows relist-like inactivity, which in
the abstract would push the grant probability into double digits.

But the relist buckets conflate two different dynamics, and this case is in
the second: it is not being repeatedly conferenced as a grant candidate; it
is being carried alongside an already-granted companion. Within that
pattern, the realistic outcome space is:

- **Denied** (at the long conference, or after *RNC v. MFV* is decided):
  the SG's recommended path and the modal disposition for a held companion
  raising severable, interlocutory, fact-bound questions. ~65–70%.
- **GVR** in light of the eventual *RNC v. MFV* decision: plausible because
  this petition attacks the *same judgment* the Court will likely vacate at
  least in part; a GVR would let the Ninth Circuit reconsider the whole
  appeal. GVR counts as a grant on the binary axis. ~10–15%.
- **Plenary grant** (now at the long conference, or next Term, e.g. limited
  to the *Summers* question): the circuit split is real, eleven judges
  dissented from en banc denial, and if the Court rules for the RNC on
  Section 8, the intent claim becomes the last obstacle to H.B. 2243, raising
  the standing question's stakes. But if the Court wanted these questions it
  would most naturally have granted and consolidated on June 29. ~8–10%.
- **Dismissed/other** (e.g., settlement, mootness): ~5%.

That puts P(any grant, GVR included) at roughly 0.20, with **denied** as the
single most likely disposition label.

## Prediction

- `granted = 0`, `probability = 0.20`, `predicted_disposition = denied`.
- No per-justice votes predicted for a cert-stage disposition.

## Big-case score

0.75. The underlying controversy — Arizona's documentary-proof-of-citizenship
and noncitizen voter-roll laws, with the RNC, DNC, the United States, and 25
amicus states engaged — is one of the highest-stakes election-law disputes of
the current Term, and the lead companion is now a granted OT2026 merits case.
This specific petition is the satellite: its own questions (organizational
standing, clear-error review of legislative-intent findings) would be
doctrinally significant if decided, but its likely disposition is denial in
the lead case's shadow.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-17.json`, docket through
June 22, 2026), `questions-presented.txt`, `petition.txt` (52 pp.),
`brief-in-opposition.txt` (the SG's consolidated brief, 41 pp.), the
committed `metrics/statpack.md`, corpus priors via `fedcourts query`, and
CourtListener/web retrieval on the companion dockets only — all detailed in
`retrieval.md`. The cell is `forward` mode; the companion grant of 25-1017 is
public pre-decision information about a *different* petition and is treated
as legitimate forward signal (noted in `flags.json`). No information about
this petition's own disposition exists or was sought.
