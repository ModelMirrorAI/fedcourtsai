# Cummins v. Illinois, No. 25-1030 — cert disposition prediction

**Prediction: deny. P(any grant, GVR included) = 0.06.**

## The case

Paid petition from the Appellate Court of Illinois, Second District (PLA denied
by the Illinois Supreme Court, Nov. 26, 2025). St. Charles police responded to a
2:31 a.m. noise complaint, spent 76 minutes knocking and phoning with no
response, saw lights on, a car in the driveway, an ajar interior door, a gun
cabinet in plain view, and — on a neighbor's word corroborated by a records
check — knew the resident had a drug history. They entered without a warrant
"to see if anybody was under any type of medical emergency," found Cummins
asleep on the couch, and he was charged as a felon in possession. The trial
court suppressed; the appellate court reversed on the State's interlocutory
appeal, holding the emergency-aid exception (Brigham City v. Stuart) satisfied.
The question presented is expressly an as-applied challenge: petitioner "does
not challenge the rule of Brigham City or Case," only its application where the
entering officer testified he had no information that "anybody was hurt in
there or that there was an emergency."

## Signals for and against

**For (why this isn't a routine 2–3% paid petition):**

- **Call for response.** Illinois waived (Mar. 2, 2026); the case was
  distributed for the March 20 conference; and on March 16 the Court
  **requested a response**. A sua sponte CFR after waiver means someone in
  chambers flagged the case — the classic pre-grant screen. Nearly all grants
  from the paid docket pass through a CFR, and conditional on a CFR the grant
  rate runs several multiples of baseline (roughly high single digits to low
  teens, vs. the ~2.5–3% modern grant rate in `metrics/statpack.md`).
- Paid, counseled petition (paid petitions grant far more often than IFP), and
  the facts are sympathetic for the defense side: a noise complaint ripening
  into a warrantless 3:47 a.m. home entry with the officers' own testimony that
  nothing changed in the intervening 76 minutes.
- Doctrinal timeliness: the Court decided **Case v. Montana**, 607 U.S. 107,
  earlier in 2026, reaffirming Brigham City and rejecting a probable-cause
  gloss. A Justice policing lower-court over-extension of emergency aid could
  see this as an early test.

**Against (why it still very likely fails):**

1. **Jurisdiction.** The decision below is an **interlocutory** state ruling on
   a pretrial suppression appeal; Cummins has not been tried. Under 28 U.S.C.
   § 1257 / Cox Broadcasting, none of the four finality exceptions plausibly
   applies, and the BIO documents the Court's regular practice of denying in
   exactly this posture (Sneed v. Illinois; Andrews v. New Jersey; Hamm v.
   Tennessee). This is close to dispositive on its own — it bars plenary
   review and a GVR alike, and petitioner's 6-page petition does not engage it.
2. **Pure error correction.** The petition disclaims any challenge to the
   legal rule and alleges no split; it asks only whether the Illinois court
   misapplied Brigham City/Case to these facts. Rule 10 expressly disfavors
   that, and the petition (six pages of argument from a small local office)
   offers no vehicle framing to overcome it.
3. **GVR-in-light-of-Case is unpersuasive.** The appellate decision (July 8,
   2025) predates Case, and it twice glossed prong two as "approximating
   probable cause" — a standard *more* demanding of the State than the one
   Case reaffirmed. The State won below under, if anything, a stricter
   standard, so there is no reasonable probability (Lawrence v. Chater) of a
   different result on remand; the BIO's answer here is convincing, and the
   finality defect independently blocks a GVR.
4. **Timing.** Having just clarified this exact doctrine in Case, the Court is
   unlikely to take another emergency-aid case months later, least of all a
   fact-bound interlocutory one. Denial with, at most, a short statement or
   dissent from denial (the entry facts could draw one) is the modal outcome.

## Calibration

Anchor: modern paid-docket grant rate ~3% (statpack: granted 367 of ~11.7k
resolved modern cert petitions; Term-2025 est. 2.5%). The CFR is the one strong
upward signal and would ordinarily justify ~8–12%. The uncured § 1257 finality
defect, the explicit error-correction framing, and the weakness of the GVR
path each cut that materially. I land at **0.06** — above the CFR-less
baseline, well below an unencumbered CFR case. Disposition: **denied**
(granted = 0). Confidence 0.75.

No relists yet: the June 24 distribution for the September 28, 2026 long
conference is the first post-BIO distribution; if the case is relisted after
that conference, the grant/GVR probability should be revised upward.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-16.json`), the petition text
(including the appellate opinion and suppression-motion appendices),
`questions-presented.txt`, and the State's brief in opposition — all
provisioned under `record/documents/`. Base rates from the committed
`metrics/statpack.md`. Mode: `forward` (pending case; conference date is in
the future). I did not seek and did not encounter any disposition for this
petition.
