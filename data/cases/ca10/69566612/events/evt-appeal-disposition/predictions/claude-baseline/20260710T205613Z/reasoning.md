# Koel v. Citizens Medical Center — Tenth Circuit No. 23-3232 (appeal disposition)

**Prediction: affirmance (`denied`), P(granted) = 0.18.** In this event's
vocabulary I read `granted` as the appellant obtaining relief (reversal or
vacatur, in whole or in part) and `denied` as affirmance of the judgment below.

## The case

Ricky Koel suffered an occult ruptured globe of the right eye in a farm
accident and sought emergency care at Citizens Medical Center ("CMCI"), a small
rural hospital in Colby, Kansas. The on-call ER physician (a family-medicine
hospitalist), a PA, and a consulting local optometrist examined him; a CT scan
was read as showing "right intraocular hemorrhage and possible component of
right globe rupture." Koel was discharged with medication and a next-morning
appointment with an ophthalmologist in Garden City, who sent him to a Wichita
retina specialist for same-day surgery. He ultimately lost the vision in that
eye. Koel, who was uninsured ("self-pay"), sued CMCI under EMTALA (42 U.S.C.
§ 1395dd) on two theories — inappropriate medical screening and release without
stabilization — plus state-law malpractice claims against CMCI, the ER
physician, and the optometrist.

On October 10, 2023, Judge Holly Teeter (D. Kan. 2:21-cv-02166) granted CMCI
summary judgment on both EMTALA theories, denied Koel's cross-motion, denied
his motion to exclude the defense ophthalmology testimony of Dr. Fry, and
declined supplemental jurisdiction over the state-law claims, dismissing them
without prejudice. This appeal followed; the Tenth Circuit heard oral argument
on January 21, 2025 (~31 minutes of audio). The panel is not identified in the
snapshot or the audio metadata.

## The legal question and governing standard

Summary judgment is reviewed de novo. The EMTALA merits are governed by
settled, and fairly strict, Tenth Circuit law:

- **Screening** (§ 1395dd(a)): a hospital satisfies the "appropriate medical
  screening examination" duty by applying its own standard screening
  procedures uniformly; EMTALA is not a federal malpractice statute, and
  "slight" or de minimis deviations from policy are not actionable. *Repp v.
  Anadarko Mun. Hosp.*, 43 F.3d 519 (10th Cir. 1994); *Collins v. DePaul
  Hosp.*, 963 F.2d 303 (10th Cir. 1992); *Phillips v. Hillcrest Med. Ctr.*,
  244 F.3d 790 (10th Cir. 2001).
- **Stabilization** (§ 1395dd(b)–(c)): the duty attaches only when the
  hospital *actually determines* that an emergency medical condition exists —
  a subjective, actual-knowledge standard. *Urban ex rel. Urban v. King*, 43
  F.3d 523, 526 (10th Cir. 1994). A "possible" diagnosis or an entry on the
  differential is not a determination.

## Why affirmance is the likely outcome

1. **The screening record is thick, not absent.** Koel was seen promptly by a
   triage nurse, a PA, and a physician; a CT was ordered and read by a
   radiologist; an optometrist performed a slit-lamp exam and Seidel test and
   consulted the regional ophthalmologist by phone. Under *Repp*, the
   plaintiff's theory reduces to a list of claimed policy deviations
   (physician-to-physician consult rule, on-call/specialist-list provisions,
   not forwarding the CT to Dr. Fry). The district court worked through each
   and found them either non-violations or de minimis; that analysis tracks
   circuit law closely, and the contrast case it invokes (*Correa*, 1st Cir. —
   no screening at all) is apt. Recasting standard-of-care arguments as policy
   violations is exactly what *Repp*/*Phillips* forbid.
2. **The stabilization theory collides with *Urban*'s actual-knowledge
   standard.** The only test result said "possible" globe rupture, the
   treating physician testified the possibility was already on his
   differential, and no provider diagnosed an actual rupture before discharge.
   Koel's willful-blindness argument was raised first in reply (a preservation
   problem) and rests on inference, not record evidence. The panel would have
   to extend *Urban* — or convert "possible EMC + severe symptoms" into
   constructive knowledge — to reverse, and the Tenth Circuit has repeatedly
   declined to loosen EMTALA into a negligence regime (*Genova v. Banner
   Health*, 734 F.3d 1095 (10th Cir. 2013)).
3. **Base rates.** Federal courts of appeals reverse in only roughly 8–12% of
   civil appeals; reversal rates for argued cases run higher (argument is
   granted in closer cases — this one was argued, which is why my probability
   sits above the raw base rate), but plaintiff-side EMTALA appeals from
   summary judgment are affirmed at high rates given how narrow the statute
   is. The corpus's CA10 cut is thin (34 resolved cases, none on point:
   88.2% "other", 11.8% "denied") and the retrieved CA10 priors contained no
   medical/EMTALA analogue, so I weight the doctrinal posture and the general
   appellate base rate over corpus-specific numbers.

## What could drive a reversal (why P(granted) is 0.18, not 0.05)

- **The facts sit in EMTALA's heartland.** An uninsured, self-pay patient at a
  rural ER; a consulting optometrist who worked for free and worried about
  "wasting" a surgical team; a physician who testified he weighed a
  five-figure transport bill in not recommending transfer. EMTALA exists
  precisely to police economically motivated non-treatment (*Roberts v. Galen
  of Va.*, 525 U.S. 249 (1999) — no improper motive required), and a panel
  moved by this record could find a jury question on disparate treatment.
- **The knowledge question is genuinely contestable.** A radiologist told the
  treating physician the CT showed globe margins "somewhat irregular" and
  "some degree of right globe rupture possible"; the physician then discussed
  vision-loss risk and possible transfer with the patient. A panel could hold
  that a reasonable jury may infer the hospital had "determined" an emergency
  medical condition (the statutory definition turns on acute symptoms whose
  neglect risks serious organ dysfunction, not on a confirmed diagnosis), and
  that summary judgment improperly resolved that inference against the
  non-movant. That would be a partial reversal (`granted-in-part`) — the
  screening ruling looks materially safer than the stabilization ruling.
- The evidentiary ruling on Dr. Fry is reviewed only for abuse of discretion
  and the district court found summary judgment supportable without his
  testimony, so it is unlikely to carry the appeal by itself.

Rough allocation across dispositions: denied (affirmed) ≈ 0.78; granted or
granted-in-part (any reversal/vacatur) ≈ 0.18, with partial reversal on the
stabilization claim the likelier grant shape; dismissed/other ≈ 0.04.

No per-judge votes: the panel's composition is not in the snapshot, the
argument-audio metadata, or anything I retrieved.

## Caveats

- `record/context.json` says `forward`, but the snapshot's only docket entry
  (2025-02-24, "Case termination for opinion") indicates the appeal has in
  fact been decided. I treated the cell as a de facto replay: I did not
  retrieve the Tenth Circuit's opinion, the disposition, or any coverage of
  the decision, and I do not have reliable prior knowledge of this case's
  outcome. Details in `flags.json`.
- While pulling the *district* docket (pre-decision record), I incidentally
  saw that three post-appeal entries exist there (April–October 2025) with
  blank descriptions. Entry dates alone are ambiguous (mandate, costs, or
  remand proceedings all fit) and I did not open them or use them as signal;
  disclosed in `flags.json`.
- The CourtListener MCP server was not available in this cell; I used the
  CourtListener REST API directly (same data source, calls listed in
  `retrieval.md`).
