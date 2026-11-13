# Evaluation: codex-baseline

## Outcome and scoring

This is an **interim**, arrival-moment cell. The outcome records `interim_reading = denied` and `interim_granted = 0`; the staged November 12 docket snapshot attributes denial on November 10, 2026 to The Chief Justice. The denial call is correct: `correct = 1`; Brier is `(0.07 - 0)^2 = 0.0049`.

The baseline and skill are the harness's and are omitted. The committed interim section supports the OT2016–OT2025 finer-reading pool, 156 grants / 1,337 resolutions, with all pooled `finer_unread` zero and the 50-resolution floor satisfied. There is no evident refusal requiring a null baseline. No cert salience basis, vote accuracy, or semantic grade applies. The harness alone computes quantitative claim scores and writing-distribution scores.

## Reasoning quality: 0.92

The rationale is unusually disciplined about the information set. It identifies the arrival-position boundary, distinguishes submission from referral, and refuses to treat the absence of escalation at arrival as evidence of subsequent inattention. It correctly treats the blank application as unavailable content, the unsuccessful lower-court lookup as a coverage limit, and general-rules retrieval attempts as uninformative rather than support for a legal conclusion.

Its prior is reproducible: OT2016–OT2025 finer counts total 156/1,337, and the private/unmarked cut totals 63/906. These match both the current pack and the shared frozen digest `sha256:b122cc43052b1328321031e3615601101a1b85c7dcdc87d23e5436373b03f133`. I verified that digest through the reconstruction made for gemini-baseline, which froze the same build: `f0a8cabd41e643e9a1441db9518d722d427a1768`, landed November 7, 2026. The rationale appropriately identifies uneven parsing, selection, and right-censoring, and does not silently substitute its descriptive applicant-class cut for the scoring baseline.

Rounding the class prior to 7% is a defensible response to missing substantive content. It does not establish case-specific calibration, and the escalation estimates remain judgmental, but those limitations are explicit. The relatively larger realized Brier than the other candidates is not itself an analytical defect. This grade concerns `reasoning.md` alone, not the forecast or the numerical claims block.

The evaluator now has a November 11 OCR extraction; its opening and emergency-request sections reveal the bankruptcy/recusal preservation dispute. That later availability does not invalidate the candidate's documented inability to read the November 6 non-OCR extraction. I do not require the candidate to have known content supplied only later.

## Predicted reasoning

**Grade: 0.87.** The forecast correctly calls denial without a merits judgment, no response request, no full-Court referral, and zero new amici. Its November 9–23 horizon contains the November 10 disposition. Those procedural commitments are discriminating even though the document appropriately declines to manufacture a doctrinal ground from an unreadable application.

The forecast is less specific about the deciding actor than a firm Chief-Justice-only call. The staged docket records a terse denial, but there is no separately staged explanatory order proving a particular reason. The no-writing prediction is not conclusively testable: no writing is listed, yet `writing_roles` and noted dissent are null and there is no staged writing text. It therefore earns no separate confirmation. Conditional discussion of an unexpected grant is untested and earns neither credit nor penalty. These limits keep an otherwise strong procedural forecast below the top anchor.

## Leakage

`forward`; `retrieved_outcome_material = false`; influence `not_applicable`; no leakage exclusion. Of 30 logged calls, 27 are captured and three general-rules web attempts are unobserved. I do not turn those missing captures into proof that nothing returned: the queries themselves seek rules, not this application's disposition. The captured CourtListener query targets the Fourth Circuit docket and uses a pre-November 3 filing filter. The rationale discloses no live Supreme Court docket lookup. The calls occurred November 9, before the November 10 resolution, and nothing visible suggests a decided case was provisioned as forward.
