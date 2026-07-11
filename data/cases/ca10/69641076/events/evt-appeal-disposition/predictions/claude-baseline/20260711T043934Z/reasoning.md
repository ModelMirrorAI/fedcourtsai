# Zhang v. Federal Home Loan Bank of Topeka — Tenth Circuit No. 24-3029 (appeal disposition)

**Prediction: affirmance (`denied`), P(granted) = 0.08.** In this event's
vocabulary I read `granted` as the appellant obtaining relief (reversal or
vacatur, in whole or in part) and `denied` as affirmance of the judgment below.

## The case

Qinghua (Josh) Zhang and Steven Craig Heiland, both senior-management-level
vice presidents, sued their former employer, the Federal Home Loan Bank of
Topeka, in the District of Kansas (No. 5:19-cv-04073, filed August 2019),
alleging retaliatory termination for whistleblowing in violation of Title VII
and Kansas common law (retaliatory discharge); Zhang also alleged termination
based on his race. The Bank's summary-judgment motion was **denied** in April
2021 (Judge Sam Crow), and the case was tried to a jury over five days before
Judge Toby Crouse in August 2023. Plaintiffs' timing evidence was striking —
Zhang was fired the morning after emailing his boss to report discrimination
and legal violations; Heiland was put on leave the morning after Zhang named
him as a witness while rejecting a severance package — but the Bank presented
evidence that Zhang was terminated for insubordination and unsatisfactory
progress and Heiland for anti-harassment and IT-security policy violations.
On August 10, 2023, the jury returned a **verdict for the Bank** on all
claims, and judgment was entered the same day.

Plaintiffs moved for a new trial under Rule 59. On January 25, 2024, Judge
Crouse denied the motion in a seven-page memorandum and order. Plaintiffs
filed a notice of appeal on February 23, 2024 (timely: the Rule 59 motion
tolled the appeal clock), producing Tenth Circuit No. 24-3029. Trial
transcripts were filed in spring 2024. The snapshot's sole appellate docket
entry (February 14, 2025, "Case termination for order and judgment") shows
the appeal was resolved by unpublished order and judgment roughly a year
after docketing; the snapshot records no oral-argument date and no audio.

## The appellate issues and their standards of review

The Rule 59 motion is the best available map of the appeal, and every issue
in it faces a deferential standard:

1. **Omitted jury instruction** (plaintiffs' proposed explainer on what Title
   VII is, offered to differentiate the federal and state punitive-damages
   claims). The district court found the objection **unpreserved** — raised in
   writing but not renewed on the record at the instructions conference as
   Rule 51(c)(1) requires — so the Tenth Circuit would review only for plain
   error, a nearly insurmountable standard in a civil case. The court also
   held, alternatively, that the instructions as a whole accurately stated
   what Zhang had to prove.
2. **The answer to the jury's question** (whether "violation of rules,
   regulation or …" covered internal Bank policies). The answer directed the
   jury back to Instruction 12 and restated that qualifying violations must be
   of state or federal law, not internal policy — and plaintiffs *agreed* on
   the record that jurors should be directed to Instruction 12, objecting only
   to repeating its language. Reviewed for abuse of discretion, with an
   invited-error/waiver overlay; the answer tracks the "concrete accuracy"
   duty rather than violating it.
3. **Rule 408 exclusion of the severance offer.** Plaintiffs wanted the
   severance package admitted to show the Bank did not believe its own
   insubordination story. The district court excluded it as a compromise
   offer whose proffered use — inferring the Bank knew its position was weak —
   is exactly what Rule 408 forbids. Abuse-of-discretion review plus a
   harmless-error hurdle. This is the appellants' most colorable issue (there
   is authority elsewhere that a unilateral severance offer made before any
   dispute has crystallized is not a Rule 408 "compromise" of a "disputed
   claim"), but the district court's reasoning sits comfortably within Tenth
   Circuit law (*SCO Group v. Novell*; *Eisenberg*), and even a debatable 408
   call rarely upends a five-day trial on harmlessness review.
4. **Verdict against the weight of the evidence.** A Rule 59 denial is
   reviewed for manifest abuse of discretion, and the verdict stands if it has
   any basis in fact. The order recites competing evidence on both sides; the
   Seventh Amendment framing in the order (*Burke v. Regalado*; *M.D. Mark*)
   is standard and correct. This issue is effectively hopeless on appeal.

## Why affirmance is the strong favorite

- **Posture.** An appellant challenging a civil jury verdict on unpreserved
  instructional error, discretionary evidentiary rulings, and weight-of-the-
  evidence grounds is in one of the least reversal-prone postures in federal
  appellate practice. There is no de novo issue anywhere in the Rule 59
  motion. Unlike a summary-judgment appeal, there is no legal ruling to
  re-run without deference; plaintiffs already got their jury.
- **The district court's order is careful and conventional.** Each ruling is
  supported with on-point Tenth Circuit authority; nothing in it reads as an
  outlier a panel would need to correct.
- **Form of disposition.** The termination entry shows resolution by
  unpublished "order and judgment," the Tenth Circuit's vehicle for routine
  dispositions, and the snapshot reflects no oral argument — both correlate
  strongly with affirmance.
- **Base rates.** Federal courts of appeals reverse in roughly 8–12% of civil
  appeals overall, and less often where every issue is reviewed deferentially
  after a jury trial. The corpus's CA10 cut is thin and off-point (34 resolved
  cases: 88.2% "other", 11.8% "denied"; no employment-appeal analogue
  surfaced by `fedcourts query`), so I weight the doctrinal posture and the
  general appellate base rate over corpus-specific numbers.

## What could drive a reversal (why P(granted) is 0.08, not 0.02)

- The **Rule 408 issue** has genuine doctrinal texture: whether a severance
  package offered at termination, before litigation or even a demand, is an
  offer to compromise a "disputed claim." If a panel took that view, the
  exclusion of evidence plaintiffs framed as their pretext centerpiece could
  conceivably be prejudicial, given the sharp temporal-proximity facts.
- The timing evidence is vivid enough (termination the morning after a
  protected report) that a panel troubled by the trial rulings would have a
  sympathetic record for finding prejudice.
- Against both: harmless-error review, the jury's rejection of the claims on
  a full record, and the unpublished-disposition signal.

Rough allocation across dispositions: denied (affirmed) ≈ 0.87; granted or
granted-in-part (any reversal/vacatur) ≈ 0.08; dismissed ≈ 0.02 (the notice
of appeal appears timely, so a jurisdictional dismissal is unlikely);
other ≈ 0.03.

No per-judge votes: the panel's composition is not in the snapshot or in
anything I could retrieve without touching the decision itself.

## Caveats

- `record/context.json` says `forward`, but the snapshot's only docket entry
  (2025-02-14, "Case termination for order and judgment") shows the appeal
  has in fact been decided. I treated the cell as a de facto replay: I did
  not retrieve the Tenth Circuit's order and judgment, the linked opinion
  cluster, or any coverage of the decision, and I have no reliable prior
  knowledge of this case's outcome. Details in `flags.json`.
- While listing the *district* docket (pre-decision record), I incidentally
  saw the descriptions of its two most recent entries — "Letter re Writ of
  Certiorari" (July and October 2025) — which postdate the appellate decision
  and imply a cert petition was later filed, weakly suggesting the appellants
  lost below. I did not open those entries, and my probability rests on the
  pre-decision record; it would be the same number without the sighting.
  Disclosed in `flags.json`.
- The CourtListener MCP server failed on every call in this cell (a
  server-side session-store misconfiguration), so I used the CourtListener
  REST API directly — the same data source; calls listed in `retrieval.md`.
