# Gomez v. Saccoccio, No. 25-1314 — cert petition disposition

## The case

Officer Eric Gomez (Phoenix PD Tactical Response Unit) petitions from the
Ninth Circuit's unpublished memorandum decision, *Saccoccio v. Gomez*, No.
25-66 (9th Cir. Jan. 15, 2026), which reversed summary judgment for Gomez on
both prongs of qualified immunity. During the first night of Arizona's
May 31, 2020 curfew (George Floyd protest period), Gomez shot protester David
Saccoccio in the arm with a single 40-mm frangible foam OC round as Saccoccio
disobeyed commands and climbed a fence into a residential yard; the round
fractured a bone in his arm. The district court (D. Ariz., Humetewa, J.) had
granted summary judgment on both the merits and qualified immunity; the panel
(Hawkins, Rawlinson, M. Smith) reversed, defining the right as that of "an
individual breaking curfew, but not in a crowd, nor posing any immediate
threat to others … not to be shot with a munition that can cause serious
injury," and holding *Nelson v. City of Davis* (9th Cir. 2012) and *Deorle v.
Rutherford* (9th Cir. 2001) "read together" clearly established the violation.
Rehearing en banc was denied February 23, 2026.

## The question presented

Whether combining general principles from two factually dissimilar cases
conflicts with this Court's precedents requiring lower courts to define
rights with specificity and use close factual analogues when deciding whether
a Fourth Amendment right is clearly established. Petitioner expressly does
**not** challenge the merits holding — only the clearly-established prong.

## Governing standard and genre

This is a classic qualified-immunity **error-correction** petition. It
alleges no circuit split; it asks the Court to "again realign the Ninth
Circuit," invoking the line of summary reversals — *Sheehan*, *White v.
Pauly*, *Kisela v. Hughes*, *City of Escondido v. Emmons*, *Rivas-Villegas v.
Cortesluna* — several of which specifically rebuked the Ninth Circuit for
reading *Deorle* "too broadly" (*Kisela*, 584 U.S. at 106). The panel here
rested one holding squarely on *Deorle*, which places the petition almost
exactly in the *Kisela* archetype. Petitions in this genre are resolved by
denial (most often), by summary per curiam reversal without plenary briefing,
or by GVR; a plenary grant is rare.

Two case-specific facts sharpen the archetype:

1. **Zorn v. Linton, 146 S. Ct. 926 (2026) (per curiam)** — verified via
   CourtListener: a published SCOTUS per curiam, No. 25-297, decided
   **March 23, 2026**, quoted in the petition for the "officer acting under
   similar circumstances" specificity requirement. It shows the current Court
   is actively policing clearly-established analysis this very Term, and it
   **postdates both the panel decision (Jan. 15, 2026) and the rehearing
   denial (Feb. 23, 2026)**, so a GVR "for further consideration in light of
   Zorn" is an available low-cost disposition the panel never had a chance to
   apply.
2. **The call for a response.** Respondent (represented by a Phoenix
   civil-rights firm) waived the right to respond on June 8, 2026; the
   petition was distributed for the September 28, 2026 long conference; and on
   **July 14, 2026 the Court requested a response** (due August 13, 2026). A
   CFR after a waiver means at least one chambers flagged the petition as a
   candidate for action — a well-documented positive selection signal that
   multiplies the paid-petition grant base rate several-fold, though most
   CFR'd petitions are still denied.

## Base rates (committed statpack)

- Modern discretionary-cert petitions overall: granted ≈ 3.1% of resolved
  (367 / 11,712 reweighted).
- **Paid** petitions, OT2025: grant rate ≈ **5.4%** (OT2024: 6.9%) — this
  is a paid petition (`sJsonCaseType: "Paid"`), so the paid-class rate is the
  right anchor.
- Originating circuit CA9 (modern slice): granted ≈ 3.0%.
- Relist table (for what lies ahead): 0 relists → 0.8% grant; 2 relists →
  33.6%; the petition has not yet reached conference, so this cut is not yet
  informative, but it shows where the odds move if it is relisted this fall.
- The statpack's salience-band section referenced by the prompt is not
  present in the committed `metrics/statpack.md`, so I adjusted from the CFR
  signal directly rather than from a band base rate (noted in
  `tooling.json`).

## Weighing

Upward from the ~5.4% paid anchor:

- CFR after waiver (strongest docket signal available pre-conference;
  empirically shifts grant odds to roughly the 8–15% range on its own).
- Near-perfect fit to the *Kisela*/*Rivas-Villegas* summary-reversal
  archetype: Ninth Circuit, unpublished, *Deorle* stretched to dissimilar
  facts, interlocutory QI posture (the standard posture for these reversals).
- *Zorn* shows a Court willing to act in this space this Term, and supplies a
  cheap GVR path because it postdates the panel's decision.
- Well-counseled paid petition (city attorney + two private firms), clean
  single QP, no vehicle problems apparent; petitioner concedes the merits
  prong, isolating the clearly-established question.

Downward:

- No circuit split; pure error correction of a non-precedential memorandum
  disposition — the Court routinely lets these go, and several Justices have
  voiced reluctance about error-correction summary reversals.
- The panel's right-definition is at least arguably particularized (it recites
  the specific circumstances), so the Court could see this as fact-bound
  application rather than defiance.
- The BIO (due Aug. 13) may contest the factual framing (the record contains
  officer-testimony inconsistencies the panel highlighted via *S.R. Nehad*),
  which historically deters summary reversal where facts are genuinely
  disputed.
- Most CFR'd petitions — including most QI CFRs — are still denied.

## Probability

Rough decomposition of P(disposition):

| outcome | mass |
| --- | --- |
| denied | ~0.77 |
| summary reversal or plenary grant | ~0.12 |
| GVR in light of *Zorn* | ~0.08 |
| dismissed/withdrawn (settlement on remand) | ~0.03 |

**P(any grant, GVR included) ≈ 0.20.** The single most likely disposition
remains **denied**, so `granted = 0`, `predicted_disposition = "denied"`,
`probability = 0.20`. Timing: with the BIO due August 13 and distribution
likely for the long conference or shortly after, a disposition is most likely
in October–November 2026; a relist at the first conference would be a further
positive update not yet in this forecast.

## Stakes (big_case_score = 0.3)

A 2020-protest less-lethal-force case carries real civil-rights salience, and
any QI reversal draws national coverage; but the petition seeks narrow
error correction of an unpublished decision, not reconsideration of qualified
immunity doctrine, so the likely ceiling (per curiam or GVR) is a modest news
event rather than a landmark.
