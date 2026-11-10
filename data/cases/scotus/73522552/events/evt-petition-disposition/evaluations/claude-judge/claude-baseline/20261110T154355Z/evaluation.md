# Evaluation — claude-baseline, scotus/73522552 (Isaacson v. Moses, No. 25-1411), evt-petition-disposition

**Stage:** cert (forward, `distribution` moment, snapshot 2026-10-06). **Outcome:** denied on November 9, 2026, after one post-briefing distribution (Oct 7, for the Nov 6 conference). There was no CVSG and no noted dissent.

## Score
- Predicted `denied` at P(grant) = 0.10. `correct` = 1. Brier = (0.10 − 0)² = **0.01**.
- The segment base rate and skill are the harness's stamp; see the stamped segment base rate.

## Reasoning (reasoning_quality 0.85)
This is the strongest analysis of the three. The anchor is a correct pool of sal-v4 `baseline` reached rates over OT2017–OT2024 (≈5.1%), and the terminal relist and CVSG cuts are read only for shape. The adjustments are balanced in both directions, and each is grounded in material the candidate retrieved and disclosed:
- **Up:** the response request, the Chamber amicus, and the growing, conceded split.
- **Down:** three recent denials on the same question (22-389, 24-259, 24-464). The most telling is *Isaacson v. Meta*: the same petitioner, response requested, and denied at the first conference after briefing. The candidate also cites the lopsided split, the low stakes, the objector posture, a pending Rule 23 rulemaking suggestion, and the government's waiver in the companion petition.

The *Isaacson v. Meta* analogy predicted the actual path almost exactly. The stated bounds (0.07–0.15) are a reasonable expression of uncertainty. The candidate also discloses its limits candidly: partial reads of the amicus brief and reply, and no conditioned rate for this situation.

## Predicted reasoning (0.85)
The central claims were all borne out: denial; at least one more distribution, most likely for a late-Oct/early-Nov conference (it went to Nov 6); one to three additional distributions with a decision by January 2027 (one distribution, decided Nov 9); no CVSG; and a separate writing "possible but not expected" (none was noted). The hold-for-26-302 and substantive-relist paths were offered as alternatives and did not occur; that is a secondary miss. The grant-conditional ground and line-up forecast is unresolved and earns nothing either way. The document is specific, and its timing call landed. It falls just short of 1.0 because "deny" plus "no CVSG / no writing" is close to the default forecast for this kind of petition.

## Leakage
Forward cell. On Oct 6 the candidate fetched the live supremecourt.gov docket for this case and disclosed that the last entry was the Oct 2 reply. The next entry (the Oct 7 distribution) and the Nov 9 denial came later, so there was no outcome to retrieve. Its other web retrieval concerned related dockets, the amicus brief, the reply and a Rules suggestion, all of which is legitimate forward context. CourtListener calls returned 429. `not_applicable`; the candidate's disclosure counts in its favour.

## Big case
The evaluator's read is 0.4.
