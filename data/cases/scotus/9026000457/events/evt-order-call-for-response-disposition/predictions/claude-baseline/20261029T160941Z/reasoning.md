# Why P(grant) = 0.16

**Inputs read.** Snapshot `2026-10-27.json` (forward mode, date cut at 2026-10-28; band
`baseline` under `sal-v4`, distribution_count 1, no CVSG). Documents: `questions-presented.txt`,
`petition.txt` (full, not truncated), `party-letter.txt` (petitioner's request to put off
distribution until the amicus window closes). I did not read `appendix.txt` beyond what the
petition quotes from it. No brief in opposition exists yet: Mississippi waived, then the Court
called for a response, so I have nothing from the State's side to weigh.

**Anchor.** The statpack's `sal-v4` "Segment base rate by salience band" table, `baseline` column,
bracketed `reached` figure, pooled over the Terms before 2026 that it shows (2017–2025): about
4–6% per Term (e.g. 2025 4.0% n=1314, 2024 5.9% n=1274, 2023 5.9% n=1312), so roughly 5%. I did
not use the 2026 row (1.8%, n=169), which is my own Term and mostly early denials. The
petitioner is a private corporation suing a state officer, so `baseline` is also the
caption-class floor.

**Adjustments up.**
- *Response requested.* No committed table conditions on it. My judgement is that a call for a
  response on a paid petition from a repeat Supreme Court firm roughly doubles the band rate. It
  shows that someone in chambers saw the petition as worth a look, but the bar is low.
- *Stakes and federal interest.* Twenty-two state laws; litigation pending in five more circuits;
  the United States has filed amicus briefs for the manufacturers in about a dozen appeals, and
  says these laws facially violate the Supremacy Clause. The amicus cut (paid scored segment) gives
  10.3% granted at 1 brief (n=1162) and 18.4% at 2+ (n=1543). This petition is at 1 now and probably
  heading to 2+.
- *Close en banc votes.* The Eighth Circuit denied rehearing en banc by one vote, with dissents
  (as the petition reports it).

**Adjustments down.**
- *The split is softer than pleaded.* The Fourth Circuit panel decisions were vacated when that
  court granted rehearing en banc. The D.C. and Third Circuit cases are about HHS's own authority
  over contract pharmacies, not about state preemption. So the Court has an easy reason to wait
  for the Fourth Circuit en banc.
- *Prior denial.* McClain (No. 24-118) was denied after one distribution (corpus query below).
- *Vehicle.* The case is interlocutory (a preliminary-injunction denial) and was decided by a short
  panel opinion bound by an earlier panel's precedent (AbbVie v. Fitch).
- *Holding.* A hold for the Fourth Circuit or another vehicle could end in a later denial, or in a
  GVR if a companion case is granted. A GVR would count as a grant, which adds a little.

Putting these together lands at about 0.15–0.18, so I wrote 0.16. My biggest uncertainty is
whether the Court treats the federal government's lower-court position as a reason to act now or
to CVSG. A CVSG (I put it at 0.25) would raise the grant chance a lot (the CVSG cut gives 29.3%
granted, n=164), and that path is part of the 0.16.

**Claims.** `relist-increment` 0.95 (the harness masks it on this moment anyway). `cvsg-increment`
0.25. `summary-disposition-route` 0.05 conditional on a grant: there is no intervening decision to
GVR on, apart from a held-then-GVR path. `dissent-from-denial` 0.12 conditional on a denial. The
`order-writers` numbers sum to about 0.195, a bit above 0.12, because several Justices could join
one writing as co-signers. That is broadly consistent.

**Caveats.** I made no web or CourtListener retrieval, so the facts about other circuits and the
United States' briefs are the petition's account, not checked. I did not read the case summaries
under `summaries/`.
