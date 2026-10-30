# Reasoning — P(unqualified grant) = 0.20

**Inputs used.** I read snapshot `2016-11-04.json`. It is an arrival-position cut holding only the submission entry. No `record/documents/` were provisioned, so I had no application text and forecast from the docket alone. `context.json` shows mode `forward`, band null, no response requested, no referral and 0 amicus briefs.

**Anchor.** The statpack's interim section has no substantive applications parsed for any Term before OT2016: every row from 2015 back is fully unparsed. The strictly-prior pool is therefore 0, below the floor of 50, so **I anchored without a published baseline**. As shape only: the OT2016 row is 8.4% (n=107), and capital execution stays generally run in the low single digits.

**Adjustments.** I adjusted upward because the application is linked to a pending cert petition (16-595) that raises an apparently live post-*Hurst* challenge to Alabama's judicial override. That is the kind of issue on which four Justices might want to hold the case. I adjusted downward because a stay needs five votes and only eight Justices were sitting. Net estimate: about 0.20.

**Disclosure — outcome known from training.** This is a 2016 case placed as a `forward` cell, and I recall from training data how this application was resolved. That makes this cell effectively mis-provisioned, and I have flagged it in `flags.json`. I tried to give the number I would have held from the pre-decision record alone. I did not move it toward the outcome I remember. Even so, the forecast cannot be cleanly blind, and the evaluation should discount this cell.

**Ladder claims.** These reflect ordinary practice on capital stay applications: they are routinely referred to the full Court, formal response requests are rare because the State answers on its own, and amicus filings are rare on an execution-day timetable.
