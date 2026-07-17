# Petersen v. Snohomish Regional Fire and Rescue (No. 25-1210) — cert prediction

**Prediction: grant (P = 0.62).** Mode: `forward` (petition genuinely pending;
brief in opposition due August 3, 2026).

## The legal question

Whether an employer defeats a Title VII religious-accommodation claim by
showing merely a *reasonable basis for believing* the accommodation would
impose an undue hardship, or must prove the accommodation would have
*actually* imposed one. The question is a direct sequel to *Groff v. DeJoy*,
600 U.S. 447 (2023): eight firefighters were denied religious exemptions from
a 2021 COVID-19 vaccine mandate, placed on unpaid leave for about seven
months, then reinstated with the very accommodation they had requested. The
Ninth Circuit (150 F.4th 1211) affirmed summary judgment for the employer
under a "reasonable concern" standard, treating the firefighters' rebuttal
evidence (no hardship before or after the enforcement window, neighboring
departments accommodated without incident, the feared contract loss and
uninsured liability never materialized) as legally irrelevant "hindsight."
Rehearing en banc was denied December 17, 2025.

## Why this petition is far above the base rate

The statpack anchors are low: modern discretionary-cert petitions grant at
~2.5–3.3% per Term, ~5.4–6.9% for the paid class (this is a paid petition,
Term 2025). No salience-band table is present in the committed statpack, so I
adjusted from the signal cuts and case-specific facts:

1. **A clean, acknowledged, recent 3-3 circuit split.** Third (*Smith v.
   Atlantic City*), Seventh (*Kluge v. Brownsburg*), and Eighth (*Naylor v.
   County of Muscatine*) require actual hardship; First (*Rodrique v.
   Hearst*), Sixth (*Henry v. S. Ohio Med. Ctr.*), and Ninth (this case)
   accept a reasonable concern. All six decisions are 2025 — the split
   developed within three Terms of *Groff* and is fully percolated. The EEOC's
   regulation and compliance manual side with the actual-hardship circuits,
   adding an agency-conflict hook. The question is purely legal,
   outcome-dispositive below, and cleanly presented on summary judgment.

2. **The Court called for a response.** Respondent waived on May 26; on
   June 2 the Court requested a response (due July 2, extended to August 3).
   A CFR after waiver means at least one Justice is actively interested and
   historically multiplies the grant likelihood roughly an order of magnitude
   over the whole-docket base. The statpack has no CFR cut; the nearest
   committed analog is the relist cut, where 2 relists → 33.6% granted — a
   CFR at this stage is comparable-or-stronger evidence of chambers interest.

3. **Extraordinary cert-stage amicus support.** Fifteen amicus briefs at the
   petition stage, including Nebraska and 21 other states, the General
   Conference of Seventh-day Adventists (via the Becket-adjacent Pepperdine
   clinic), EPPC/former EEOC general counsel, Protect the First Foundation,
   and — notably — Gerald Groff himself and Ronald Hittle (whose own Title VII
   cert denial drew a Thomas/Gorsuch dissent). Cert-stage amicus volume this
   high is empirically one of the strongest grant correlates.

4. **Elite counsel and a favored subject.** Lisa Blatt (Williams & Connolly)
   is counsel of record with First Liberty Institute. The current Court has
   repeatedly granted religious-liberty employment cases (*Groff* itself was a
   unanimous course-correction), and this petition asks it to police lower
   courts' fidelity to *Groff* — an institutional-supervision draw beyond the
   split. The Ninth Circuit opinion is published, and the petition documents a
   district court (*Carlson v. City of Redmond*) already extending its rule.

5. **Ninth Circuit origin.** ca9 is a modest positive in the circuit cut
   (3.0% vs. 2-3% baseline among modern cert petitions) and historically the
   circuit the Court reverses most.

## What holds the probability below ~0.75

- **The BIO is not in.** Respondent (a competent municipal-defense firm) will
  argue the split is illusory — that the "reasonable concern" circuits are
  merely applying ordinary summary-judgment standards to speculative
  rebuttals — and that the record shows undisputed hardship evidence. Split
  characterizations by petitioners sometimes dissolve under a good BIO.
- **COVID-mandate hangover.** The Court declined many vaccine-mandate
  petitions (largely constitutional or injunction-posture ones). This is a
  cleaner damages vehicle unaffected by mootness, but some Justices may
  prefer a non-COVID vehicle; *Kluge*-line cases keep generating candidates.
- **Base-rate humility.** Even top-decile petitions with CFRs and heavy
  amicus support are denied more often than the qualitative signals suggest;
  the modern grant funnel is brutally narrow, and the Court could also relist
  and hold for a different vehicle.

## Net

Starting from the paid-class anchor (~6%), the CFR alone moves the case into
the 25–35% band the relist cut brackets; the acknowledged 3-3 split on a
purely legal, dispositive question, 15 cert-stage amici including 22 states,
elite counsel, and the Court's demonstrated appetite for *Groff*-enforcement
push it well past even that band. I estimate **P(grant, including any GVR
form) ≈ 0.62**, predicted disposition **granted** (plenary grant; no
intervening decision exists to support a GVR, so the grant mass is almost
entirely plenary). No leakage: no disposition exists; nothing outcome-revealing
surfaced in retrieval.

Timing expectation (not scored): distribution for the late-September 2026
long conference after the August 3 BIO, with a realistic chance of one or
more relists before any grant.

## Inputs used

- Snapshot `record/snapshots/2026-07-17.json` (docket through June 29, 2026:
  CFR of June 2, BIO extension to Aug 3, all 15 amicus filings).
- `record/documents/questions-presented.txt` and `petition.txt` (full
  petition text; QP anchored the analysis; no BIO provisioned — not yet filed).
- `metrics/statpack.md` base rates (modern cert by disposition, paid/IFP
  per-Term classes, relist, CVSG, circuit cuts).
- Corpus priors via `fedcourts query` (thin — see retrieval.md) and
  CourtListener MCP / web checks for competing vehicles (none found granted
  on this question).
