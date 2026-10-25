# Reasoning — P(grant) = 0.04

**Inputs read.** Snapshot `record/snapshots/2026-10-25.json` (forward mode,
`band: baseline` under sal-v4, `distribution_count: 1`, no CVSG, Term 2026);
`questions-presented.txt`, `petition.txt` (92 pp., not truncated) and
`brief-in-opposition.txt` (34 pp., not truncated), none OCR-derived. No related
dockets staged (the only link is the extension application 25A1259).

**Anchor.** The frozen band is `baseline` under sal-v4, which matches the
statpack's segment table heading. Pooling the `baseline` bracketed *reached*
rate across Terms 2017–2025 (all rows strictly before OT2026) gives about
**5.0%** (≈644 weighted grants over n≈12,883; per-Term range 3.9%–5.9%, with
the most recent Term lowest at 3.9%). The Ninth Circuit's origin bucket
(granted 2.1% + GVR 1.1% across all petitions) is consistent with that.

**Adjustments up.**
- The Court *requested a response* after the respondent waived. Someone in
  chambers wanted a closer look, which is a real signal relative to the
  baseline pool.
- Four amicus briefs, including religious-liberty groups and employee-side
  bar associations. The petitioner is backed by First Liberty, and the
  underlying topic (*McDonnell Douglas* at summary judgment) has drawn
  repeated interest from Justices Thomas and Gorsuch (*Hittle* denial dissent,
  the *Ames* concurrence), which the petition cites.

**Adjustments down.**
- The decision below is an **unpublished** memorandum disposition. The QP as
  written is fact-bound: it asks whether the courts below credited the
  employer's account, which is error correction rather than a clean legal
  question.
- The petition does not allege a real circuit split on a specific rule. It
  rests on a "chorus of jurists" calling for reconsideration, and the BIO
  answers that the circuits are refining the framework themselves.
- The BIO, from experienced Supreme Court counsel, gives a strong vehicle
  answer: the discharge followed a collision the petitioner twice admitted
  fault for, plus documented traffic violations seen on the bus video. That
  makes it plausible the case "comes out the same under any standard," which
  is exactly the kind of vehicle problem that keeps the Court from
  reconsidering a 50-year precedent.
- The Court denied *Hittle* (2025) on the same broader issue even with two
  Justices dissenting, and it decided *Ames* without reaching the framework.

Net: the response request and amicus support roughly offset the vehicle
problems against the ~5% anchor. I settle a little below it, at **4%**. A
response request often reflects one Justice's interest (here plausibly
Thomas's long-standing *McDonnell Douglas* project) rather than a four-vote
coalition. A summary reversal on the Rule 56 facts is the main way a "grant"
could happen, so I put the conditional summary-route claim at 0.30.

**Increments.**
- *relist-increment* 0.96: the post-BIO redistribution is near-mechanical.
  The only paths to no further distribution are withdrawal or settlement.
- *cvsg-increment* 0.02: no federal party and no federal-program interest
  peculiar to the case.
- *dissent-from-denial* 0.12: Thomas could write or join a statement on
  *McDonnell Douglas*. He did in *Hittle*, but the facts here are a weaker
  platform.

**Uncertainty / discount.** I do not know which Justice prompted the response
request. If the request reflects broader interest in reconsidering *McDonnell
Douglas*, my number is too low. The statpack's `baseline` reached rate does
not condition on a response request, so how much that signal should move the
number is my judgement. I did no live retrieval (see `retrieval.md`). The
references to *Hittle* and *Ames* come from the petition and BIO tables of
authorities plus general knowledge, not from a fetched source.
