# Renteria v. New Mexico Office of the Superintendent of Insurance (25-113) — petition disposition

**Prediction: granted (P = 0.70), most likely via a hold followed by a GVR after
*St. Mary Catholic Parish v. Roy* (No. 25-581) is decided, expected around June 2027.**

## The legal question

Petitioners are members of Gospel Light Mennonite Church Medical Aid Plan, an
ACA-recognized health care sharing ministry (HCSM). New Mexico's insurance
regulator (OSI) ordered the ministry to cease operating in-state or register as
an insurer. The Tenth Circuit (over a dissent by Judge Carson) affirmed the
denial of a preliminary injunction, holding petitioners unlikely to succeed on
free-exercise and preemption claims. The petition presents four questions: three
on the meaning of "neutral" and "generally applicable" under *Employment
Division v. Smith* (including whether official hostility alone establishes a
violation), and one on whether the ACA's HCSM exemption preempts New Mexico's
enforcement.

## The governing standard

Cert is discretionary (Sup. Ct. R. 10); the base rate for paid petitions is a
few percent (the corpus statpack's modern discretionary-cert cut shows 9 granted
of 190 resolved, ~5%; Term-2025 resolved petitions run granted 5.6%). The
question is whether this petition's specific signals move it far from that base.

## Docket signals (from the provisioned snapshot, 2026-07-11)

The snapshot shows an exceptionally strong cert-interest trajectory:

1. **Response requested** (Aug 14, 2025) after respondents waived — the Court
   would not do this for a petition headed for a routine denial.
2. **CVSG** (Oct 14, 2025): the Solicitor General was invited to file. CVSG'd
   petitions are granted at rates orders of magnitude above the base rate.
3. **SG amicus filed May 26, 2026.** Web sources consistently report the United
   States recommended the Court **hold the petition pending *St. Mary Catholic
   Parish v. Roy*, No. 25-581** (which overlaps with the first question
   presented) and then dispose of it as appropriate, while concluding the second
   (ACA-preemption) question does not warrant review. I could not read the brief
   PDF directly (supremecourt.gov and justice.gov returned 403 to my fetcher),
   so this rests on secondary summaries — flagged in `flags.json`.
4. **Petitioners' supplemental brief** (June 9, 2026) — the standard response to
   a hold recommendation, urging plenary grant instead.
5. **Distributed for the June 25, 2026 conference, and no order followed.** The
   Term has ended (it is now July 11) with neither a grant nor a denial on the
   docket. That is exactly what a hold looks like from the outside: a denial
   would have appeared on the end-of-Term order lists (corpus priors show other
   petitions from that same 6/25 conference being disposed of on June 29).

## The companion case

*St. Mary Catholic Parish v. Roy* (cert granted April 20, 2026; argument
expected fall 2026) is a Tenth Circuit case about Colorado's universal-preschool
program, presenting whether a lack of general applicability under *Smith*
requires showing unfettered discretion or categorical exemptions for identical
secular conduct. That is the same restrictive Tenth Circuit general-applicability
framework Renteria attacks in QP1–QP2.

## Reasoning to the probability

- **P(the case is in fact being held) ≈ 0.90.** The Court almost always follows
  an SG hold recommendation, and the docket's end-of-Term silence corroborates
  that it already happened.
- **P(St. Mary yields a claimant-favorable clarification of general
  applicability) ≈ 0.85.** The Court grants mostly to reverse, and the modern
  Court has ruled for the free-exercise claimant in essentially every merits
  case since *Hosanna-Tabor* (*Fulton*, *Tandon*, *Kennedy*, *Groff*, *Catholic
  Charities* (9-0), *Mahmoud*).
- **P(GVR | hold and favorable St. Mary) ≈ 0.85.** Renteria is from the same
  circuit, applying the same framework the Court would be revising; the SG
  itself framed the disposition as "as appropriate" after St. Mary; GVR practice
  is generous. The main residual risks are a narrow St. Mary holding that does
  not map onto insurance regulation, or the Court treating the interlocutory
  posture and thin record (the BIO's strongest points) as reason to deny anyway.
- **P(plenary grant despite the hold recommendation) ≈ 0.08** — petitioners'
  supplemental brief pushes for it, and the preemption question (QP4) is
  independent of St. Mary, but the SG called that question not certworthy and
  the Court rarely leapfrogs its own hold.

This repo's outcome labeling maps a GVR to `granted`
(`src/fedcourtsai/pipeline/cert_signals.py`), so the hold→GVR path scores as a
grant. Combining: P(granted) ≈ 0.90 × 0.85 × 0.85 (hold→GVR) + 0.08 (plenary)
≈ 0.73; I round down to **0.70** for the residual uncertainty in the
secondary-sourced SG recommendation. Predicted disposition: **granted** (most
likely as a GVR); the principal alternative is denial after St. Mary
(≈ 0.20–0.25). Expected resolution: end of October Term 2026 (June–July 2027).

No per-justice votes are predicted: a cert disposition (especially a GVR) does
not produce a reliable public vote breakdown.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-11.json` (docket entries,
  parties, counsel — including that the SG and the Alliance of Health Care
  Sharing Ministries appear, and Erwin Chemerinsky represents respondents).
- Provisioned `record/documents/questions-presented.txt`, `petition.txt`
  (truncated, 217 pp.), and `brief-in-opposition.txt` (32 pp.): the petition's
  circuit-split and nationwide-consequences arguments (one state's order can
  strip HCSM members of the ACA exemption everywhere) versus the BIO's
  no-split, interlocutory-posture, no-record vehicle objections.
- Corpus base rates (`metrics/statpack.md`) and `fedcourts query` priors for
  recent granted petitions (timing patterns of the 6/25/2026 conference).
- Web retrieval (forward mode, unrestricted): DOJ/OSG and SCOTUSblog/Cert Pool
  listings for the SG's CVSG brief and the *St. Mary* grant. Details in
  `retrieval.md`.

This is a forward-mode cell: the case is genuinely pending and no outcome
exists to leak. I do not know this case's disposition from training data; it
postdates my knowledge.
