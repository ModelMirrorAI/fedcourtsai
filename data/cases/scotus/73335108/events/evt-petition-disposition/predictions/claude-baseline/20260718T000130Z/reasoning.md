# Watson v. Mason, No. 25-1279 — cert disposition prediction

**Prediction: deny. P(grant, GVR included) = 0.003.**

## Posture

Henry L. Watson, III, a Wisconsin state prisoner proceeding pro se (paid
docket), petitions from the Seventh Circuit's denial of a certificate of
appealability in his 28 U.S.C. § 2254 habeas case (No. 24-2498, Sept. 12,
2025; rehearing denied Sept. 26, 2025). The underlying conviction is homicide
by negligent handling of a dangerous weapon (Wis. Stat. § 940.08), a
lesser-included verdict on Count 1, after the jury acquitted him on Count 2
(reckless injury of the man who drew on him) on perfect self-defense grounds.
The petition was docketed May 13, 2026; the respondent warden **waived the
right to respond** on June 9, 2026; and the case was **distributed for the
September 28, 2026 long conference** with no relist history (none can exist
yet — the conference has not occurred). This is a forward cell: the outcome
does not yet exist.

## The legal question

The petition's core theory (QP 1, 2, 4) is that Wisconsin Jury Instruction 820
told the jury to weigh self-defense against the "unreasonable risk" element on
Count 1, yet the state courts held post-verdict that Wis. Stat. § 939.48(3)
categorically bars the self-defense privilege where the unintended victim of a
defensive shooting is killed and the crime is negligent homicide — a
contradiction he frames under Boyde, Mullaney/Winship, Lockett, and Estelle v.
McGuire. QP 3 is a Strickland claim that trial counsel pursued a civil-style
JNOV motion not recognized in Wisconsin criminal procedure and failed to
preserve the instructional conflict.

## Why this petition will be denied

1. **Structural cert-stage signals are uniformly negative.** The petitioner is
   pro se; the state waived its response; there is no call for a response, no
   relist, no CVSG, no amicus activity visible on the snapshot. The Court
   essentially never grants plenary review without first calling for a
   response, so the current record posture is at least two steps removed from
   any grant. Distribution to the long conference is where the deny pile goes.

2. **The vehicle is doubly filtered by AEDPA.** This arrives from a **COA
   denial**, so the question technically presented is the Slack v. McDaniel
   debatability standard layered on § 2254(d) deference — an error-correction
   posture the Court almost never takes up, and when it intervenes in COA
   practice it is typically summarily and in capital cases (this is
   non-capital; `bCapitalCase: false`).

3. **The claim is fundamentally a state-law dispute.** Whether § 939.48(3)
   bars the self-defense privilege as to an unintended third-party victim of
   negligent homicide is a question of Wisconsin statutory construction on
   which the Wisconsin Court of Appeals has spoken. Estelle v. McGuire itself
   holds federal habeas does not lie for state-law error; the federal overlay
   (Boyde "reasonable likelihood," Mullaney burden-shifting) depends on
   accepting the petitioner's characterization that the instruction and the
   statute conflict — an issue with no independent federal purchase once the
   state court has construed its own statute.

4. **The strongest-sounding authorities are misapplied.** Lockett and Eddings
   are Eighth Amendment *capital sentencing* mitigation cases; they do not
   govern guilt-phase justification instructions in a non-capital negligent
   homicide case. A cert petition whose lead theory rests on doctrine that
   plainly does not transfer signals weak merits screening to the clerks'
   pool.

5. **No genuine split.** The petition asserts "other jurisdictions" shift
   self-defense burdens differently but names no conflicting decisions.
   Post-Mullaney/Martin v. Ohio burden-allocation law is settled; there is no
   developed circuit or state split presented.

6. **Base rates.** From the committed statpack (modern discretionary-cert
   slice): overall grant rate ~2.5–3% per recent Term; Seventh Circuit
   petitions grant at ~2.0%; zero-relist petitions at 0.8%; no-CVSG petitions
   at 3.0%. The paid fee class runs ~5–8%, but that class is dominated by
   counseled petitions — a *pro se* paid petition behaves like the IFP
   prisoner pool (~1%) or below. Conditioning further on the pro se COA-denial
   posture and the waived response, the realistic grant probability sits well
   under 1%. I set **P(grant) = 0.003**, slightly above pure floor to account
   for residual GVR/summary-action tail risk, though no intervening decision
   of this Court bearing on these questions is apparent, so even the GVR path
   is improbable.

## Disposition call

`denied`, granted = 0, probability = 0.003. Dismissal/withdrawal tails exist
(~2% historically) but denial is far the modal outcome for this profile. No
per-Justice votes predicted: cert denials are unrecorded and nothing here
suggests a noted dissent from denial.

## Big-case score

0.03 — a fact-bound, unpublished-decision, pro se habeas matter with no
national issue, no coordinated amicus interest, and no press profile.

## Inputs used

- Snapshot `record/snapshots/2026-07-17.json` (docket entries, parties,
  fee class, conference distribution).
- `record/documents/questions-presented.txt` and `record/documents/petition.txt`
  (full 27-page petition text; no brief in opposition exists — response waived).
- `record/context.json` (mode: forward).
- Committed `metrics/statpack.md` + `metrics/statpack.json` (per-Term,
  per-circuit, relist, CVSG, and fee-class base rates).
- One `fedcourts query` corpus pull (see `retrieval.md`); rows carried no
  captions, so they informed nothing beyond confirming corpus reachability.
