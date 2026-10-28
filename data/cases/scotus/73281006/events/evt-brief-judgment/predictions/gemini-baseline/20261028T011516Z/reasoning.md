# Predictor Rationale (`reasoning.md`): *Daniel Grand v. City of University Heights, Ohio, et al.* (No. 25-965)

## I. Summary of Numbers and Mode

- **Cell / Moment:** `evt-brief-judgment` (`stage: merits`, `moment: briefed`, `mode: forward`, `cutoff: 2026-10-24`).
- **Input Snapshot:** `2026-10-24.json` (truncated to cutoff `2026-10-24`).
- **Provisioned Documents Read:** Worked entirely from the provisioned record in `data/cases/scotus/73281006/record/documents/` (`questions-presented.txt`, `merits-brief-petitioner.txt`, `merits-brief-respondent.txt`, `merits-amicus-united-states.txt`, `appendix.txt`, `petition.txt`, `brief-in-opposition.txt`, and `cert-reply.txt`). No oral argument transcript is provisioned or available (argument is set for December 9, 2026), and no external retrieval beyond the provisioned inputs was performed.
- **Top-Level Forecast:** `probability` = `0.85` (P(judgment below disturbed)), `granted` = `1`, `judgment` = `vacated`, `predicted_disposition` = `other`, `claims[judgment-disturbed]` = `0.85`.
- **Big Case Score:** `0.65` — the case addresses a recurring, high-salience circuit split over whether *Williamson County*'s Takings Clause finality requirement applies to First Amendment and RLUIPA claims arising out of municipal land-use disputes (attracting an amicus brief from the United States and over two dozen religious-liberty, state, and municipal amici), though the case's idiosyncratic facts and Petitioner's post-grant move from University Heights somewhat narrow its practical reach.

## II. Base-Rate Anchor from `metrics/statpack.md`

Per the merits-stage rules in `.github/prompts/predict.md`, the salience band in `context.json` (`band: high`) is a cert-stage artifact and is not used. Instead, I anchor on **"The merits docket (granted cases)"** table in `metrics/statpack.md` (which publishes the required `excluded (not in granted)` column):
- **Case's Grant Term:** Certiorari was granted on June 30, 2026 (`ProceedingsandOrder` in `2026-10-24.json`), which falls in **OT2025** (`grant_term = 2025`).
- **Strictly Prior 10-Term Pool (`2015 <= T < 2025`):** The merits table in `metrics/statpack.md` renders 8 grant Terms strictly before OT2025 (OT2017 through OT2024; OT2015 and OT2016 have no parsed judgments in the table):
  - **OT2024:** 51 disturbed / 76 parsed (67.1%; 79 granted, 34 excluded)
  - **OT2023:** 35 disturbed / 56 parsed (62.5%; 56 granted, 13 excluded)
  - **OT2022:** 51 disturbed / 73 parsed (69.9%; 73 granted, 1 excluded)
  - **OT2021:** 46 disturbed / 65 parsed (70.8%; 65 granted, 3 excluded)
  - **OT2020:** 61 disturbed / 74 parsed (82.4%; 81 granted, 4 excluded)
  - **OT2019:** 46 disturbed / 58 parsed (79.3%; 60 granted, 2 excluded)
  - **OT2018:** 54 disturbed / 79 parsed (68.4%; 82 granted, 3 excluded)
  - **OT2017:** 34 disturbed / 56 parsed (60.7%; 57 granted, 6 excluded)
- **Pooled Strictly-Prior Merits Base Rate (OT2017–OT2024):**
  - Total `granted`: `79 + 56 + 73 + 65 + 81 + 60 + 82 + 57 = 553` (plus `66` excluded before the cohort).
  - Total `parsed` (coverage = `537 / 553 = 97.1%`): `76 + 56 + 73 + 65 + 74 + 58 + 79 + 56 = 537` (well above the 30-case minimum floor).
  - Total `disturbed`: `51 + 35 + 51 + 46 + 61 + 46 + 54 + 34 = 378`.
  - **Pooled `P(disturbed)` base rate:** `378 / 537 = 70.39%` (~`0.704`), composed of `241` reversed (`44.9%`), `125` vacated (`23.3%`), `12` affirmed-in-part (`2.2%`), against `143` affirmed (`26.6%`), `12` DIG (`2.2%`), and `4` equally divided (`0.7%`).

## III. Adjustments from the Base Rate (`0.704` → `0.85`)

### 1. Upward Adjustments (+0.21)
- **Direct Continuity with *First Choice Women's Resource Centers, Inc. v. Davenport*, 146 S. Ct. 1114 (2026):** Just last Term, this Court held 9–0 that a state attorney general's non-self-executing subpoena objectively chilled First Amendment association rights and created a ripe Article III injury without awaiting state-court enforcement, while explicitly noting that it was "setting aside the question whether a Takings Clause rule might be properly transposed into the First Amendment context," 146 S. Ct. at 1128. Granting Grand's *pro se* petition (after requesting a response and relisting through June 2026) demonstrates that the Court took this case specifically to answer the question reserved in *First Choice* and correct the Sixth Circuit's categorical extension of *Williamson County* to First Amendment and RLUIPA claims.
- **United States Amicus Support (`merits-amicus-united-states.txt`):** The Solicitor General filed a merits amicus brief supporting Petitioner (following the United States' voluntary amicus brief in the Sixth Circuit, Pet.App.94a–114a) and moved for divided argument. My forecast closely follows the Solicitor General's analysis: the Sixth Circuit erred by treating *Williamson County*'s Takings Clause finality standard as a blanket prerequisite for all twelve of Grand's constitutional and RLUIPA counts, even though (1) *Williamson County* rests on the nature of the Just Compensation Clause, (2) RLUIPA expressly keys standing to Article III (42 U.S.C. § 2000cc-2(a)), and (3) Grand sought retrospective damages for already-completed past chilling and religious discrimination that no subsequent zoning decision could undo.
- **Concession on Retrospective Harms:** Even Respondents (represented by Lisa Blatt and Williams & Connolly) do not defend a categorical rule that *Williamson County* bars genuine pre-enforcement chilling claims or completed past-damages claims on the merits; instead, they pivot to arguing that Grand's claims are substantively about how the zoning code applies to his land use, that he lacked an objectively credible fear of enforcement once the City clarified its position, or that he forfeited standalone chilling/retrospective theories below. Those arguments are classical remand issues rather than justifications for the Sixth Circuit's blanket jurisdictional dismissal.

### 2. Downward Adjustments and Uncertainties (-0.064)
- **Petitioner's Move Out of University Heights (DIG / Partial Mootness Risk):** The docket snapshot (`2026-10-24.json`) shows that on September 18, 2026, Petitioner filed a letter notifying the Court that he moved out of the City of University Heights, prompting a response letter from Respondents (Sept. 21), a reply letter from Petitioner (Sept. 23), and a September 29 order extending briefing and authorizing a 4,000-word sur-reply by Respondents "solely addressing the effect, if any, of petitioner's move out of City of University Heights, on or before December 2, 2026." While Petitioner's retrospective damages claims under § 1983 and RLUIPA keep the case alive under *Uzuegbunam v. Preczewski*, 592 U.S. 279 (2021) (Resp. Br. 18 & n.14), the mootness of prospective injunctive and declaratory relief slightly increases the risk of a DIG (~`0.05`–`0.06`) or an affirmance on alternative threshold/preservation grounds (~`0.09`–`0.10`), since the letters and sur-reply are not among the provisioned documents.
- **Factual Ambiguity Created by Petitioner's Initial Email:** As Respondents document heavily (Resp. Br. 7–15, 38–42), Grand's initial January 19, 2021 email announced "the inauguration of the Shomayah Tefillah Beis Hakeneset," introduced a named Rabbi, referred to a "shul entrance," and urged recipients to "spread the word," and two Planning Commissioners later expressed in private emails that a 10–15 person home prayer group did not require an SUP at all. While this does not salvage the Sixth Circuit's blanket jurisdictional holding—especially given the Mayor's March 23 public warning that the cease-and-desist order remained in effect—it makes **vacatur and remand** (`vacated`) more likely than outright reversal (`reversed`), so that the Sixth Circuit can untangle claim-by-claim preservation, mootness of prospective relief, and the merits in the first instance.

## IV. Per-Justice Votes and Authorship Calibration

### 1. Per-Justice Merits Votes Reference (`metrics/statpack.md`)
Pooling the **"Per-Justice merits votes (complete lineups)"** section across the five Terms strictly before `grant_term = 2025` (OT2020–OT2024; `40 + 51 + 46 + 48 + 53 = 238` complete signed lineups, `228` with a plain judgment):
- **Roberts:** With judgment `224 / 238` (`94.1%`); Disturb `159 / 228` (`69.7%`).
- **Kavanaugh:** With judgment `227 / 238` (`95.4%`); Disturb `165 / 228` (`72.4%`).
- **Barrett:** With judgment `211 / 232` (`90.9%`); Disturb `150 / 220` (`68.2%`).
- **Gorsuch:** With judgment `183 / 236` (`77.5%`); Disturb `152 / 222` (`68.5%`).
- **Alito:** With judgment `188 / 235` (`80.0%`); Disturb `138 / 222` (`62.2%`).
- **Thomas:** With judgment `187 / 238` (`78.6%`); Disturb `140 / 227` (`61.7%`).
- **Kagan:** With judgment `181 / 238` (`76.1%`); Disturb `152 / 223` (`68.2%`).
- **Jackson (OT2022–OT2024):** With judgment `112 / 147` (`76.2%`); Disturb `95 / 139` (`68.3%`).
- **Sotomayor:** With judgment `172 / 238` (`72.3%`); Disturb `149 / 222` (`67.1%`).

Because *First Choice* (2026) and *Pakdel* (2021) were both 9–0 and the Solicitor General's claim-specific framework allows the liberal Justices to join a vacatur and remand without pre-judging the City's fact-bound defenses or the mootness of prospective relief, I predict `majority` votes for all nine Justices.

### 2. Authorship Distributions (`majority-author` and `separate-writers`)
From `metrics/statpack.json` (`authorship.terms` for OT2020–OT2024, covering `247` decisions), each Justice's baseline share of majority opinions is roughly `10%–13%`, while separate-writing rates per sat decision (`separate / sat` over OT2020–OT2024) are:
- **Thomas:** `64 / 238` (`26.9%`) → forecast `0.28`
- **Jackson (OT2022–OT2024):** `38 / 147` (`25.9%`) → forecast `0.26`
- **Gorsuch:** `57 / 236` (`24.2%`) → forecast `0.20` (slightly reduced from baseline because he is the modal `majority-author` at `0.25`)
- **Sotomayor:** `48 / 238` (`20.2%`) → forecast `0.22`
- **Alito:** `40 / 235` (`17.0%`) → forecast `0.22` (elevated for a religious-liberty / Free Exercise case)
- **Kavanaugh:** `32 / 238` (`13.4%`) → forecast `0.16`
- **Barrett:** `23 / 232` (`9.9%`) → forecast `0.12`
- **Kagan:** `19 / 238` (`8.0%`) → forecast `0.10`
- **Roberts:** `7 / 238` (`2.9%`) → forecast `0.04`

For `majority-author`, I weight **Gorsuch** (`0.25`) highest because he authored *First Choice* (2026) where this exact question was reserved, followed by **Roberts** (`0.15`), **Barrett** (`0.14`), and **Kavanaugh** (`0.13`) as consensus institutional authors, with **Alito** (`0.08`), **Kagan** (`0.07`), **Thomas** (`0.06`), **Jackson** (`0.06`), **Sotomayor** (`0.05`), and **per-curiam** (`0.01`), summing to `1.000`.
