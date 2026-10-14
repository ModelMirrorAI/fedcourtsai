# Evaluation — claude-baseline, scotus/73500268 evt-petition-disposition

**Outcome:** GVR (`actual_disposition` gvr, `actual_granted` 1), resolved 2026-10-13 after the October 9 conference, with no further relist.

**Prediction:** `gvr`, P(grant) 0.75. Correct label; Brier (0.75 − 1)² = 0.0625. This is a cert cell and the prediction froze a band (`elevated`, sal-v4), so the segment base rate, skill and basis come from the harness stamp; `correct` / `brier_score` are stamped over and these values are my independent read.

**Reasoning quality 0.88.** This is the most thorough analysis of the three:
- It reads the decision below and finds that its inadvertence analysis is the *Coastal Plains*/*Love* "only when … no motive" formulation that *Keathley* rejected, with no alternative holding on that prong.
- It reads the Court's call for a response correctly, as an engagement signal and the usual step before a GVR.
- It quotes the opposition conceding that a GVR would be "the ordinary limited disposition".
- It explains why the "1 relist" bucket overstates the signal here: the second distribution was a reschedule after the response was called for, not a conference relist.

Its denial case is serious and well argued: strong facts against inadvertence, and the point that *Keathley* reserved the bad-faith question. The 0.75 is somewhat underconfident given its own analysis. The lower court applied the rejected test verbatim, and the respondent conceded the GVR route, which together usually support a figure in the 0.85–0.9 range. That over-hedge is the only real deduction. The document also states its own limits honestly.

**Leakage:** forward cell, with full capture. Every retrieved document is dated 2026-06-11 (*Keathley*) or earlier, and there was no search for this docket's own disposition. Graded `not_applicable`.

**Semantic grades:** none. This is a cert cell.
