# Evaluation — gemini-baseline

**Cell.** Cert stage, `moment: distribution`, forward. Outcome: petition **denied** on 2026-11-16 after five distributions, with a statement of Justice Thomas respecting the denial; no CVSG.

**Scores.** `predicted_disposition` denied vs. actual denied → `correct` 1. Probability 0.35 against `actual_granted` 0 → Brier 0.1225. No vote accuracy on a cert cell. Segment base rate, skill and basis are the harness's and left null; claim scores are computed in code.

## Reasoning (`reasoning.md`) — 0.30

Two short paragraphs. It starts from the right anchor (the elevated-band reached rate, about 17.5%) and then doubles it on one premise that the record contradicts: that the petition had been "relisted once" and so had "surviv[ed] the initial conference". The docket shows the first distribution was pulled as "Rescheduled" four days before the September 28 conference and redistributed for October 9, so the petition had not been considered at all. The main upward adjustment therefore rests on a misread signal.

The rest is assertion rather than analysis. It calls the case "a clean vehicle" without engaging the brief in opposition's points on percolation, the breadth of a single question covering eight location categories, or the Court's recent denials and partial grant on the same question. It does not mention *Wolford* or the petition's alternative GVR request, which were the live procedural questions. The one judgment that proved sound was the high weight on a separate writing if the petition were denied.

## Predicted reasoning — 0.55

The document's central claims are a further relist, a likely dissent from denial by Justice Thomas or Justice Alito, and no CVSG. All three were borne out, and the denial-writing call was the firmest of any candidate and named the right author as one of two. Against that, the document never commits to a disposition: it describes the Court "consider[ing] whether to grant" and handles grant and denial only as branches. It also repeats the "relisted once" misreading as its opening fact, and it is brief and generic on everything else. Specific secondary calls that held, with no committed call on the central question, sits a little above the middle anchor. The plenary-versus-summary content was conditional on a grant and is not graded.

## Leakage

Forward; `not_applicable`. The log captured no results, so it is graded on its queries. The one search on this case's caption ran six weeks before the disposition existed, and nothing in the prose reflects later material.
