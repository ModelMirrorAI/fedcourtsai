# Evaluation: codex-baseline

## Outcome and quantitative score

The event is cert-stage. The authoritative outcome records **denied** on October 5, 2026, with `actual_granted = 0`. The September 17 forecast's label is `denied`, giving **correct = 1**. Its **0.14** grant probability gives **Brier = 0.0196**.

The prediction's own frozen context specifies **elevated**, **sal-v4**, and **Term 2025**. The statpack table uses the same salience version, so the appropriate basis is **risk_set**, using bracketed reached rates. I pool every rendered Term before OT2025: OT2017–OT2024. Their printed rate/denominator pairs, in ascending order, are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336. This produces an approximate weighted numerator **484.386**, denominator **2,810**, and baseline **0.17237935943060498**. The table shows 10 of 10 Terms, with no rendered-window shortfall; own-Term and later-Term rows are excluded.

Brier skill is **1 - 0.0196 / 0.17237935943060498^2 = 0.3403925589099902**. The candidate reports a slightly different 17.2242% from unrounded JSON counts; my score follows the evaluator's rendered-table contract, so the small rounding difference is not a substantive analytical defect. The baseline is a denial-reweighted estimate from the committed pack, not a live census. No corpus freshness claim or aggregate-performance claim is made.

## Reasoning quality: 0.90

The analysis is careful about both the legal issue and the evidentiary status of its inputs. It identifies the general-fund donor/earmarking question rather than resting on a generic campaign-finance label. It separates substantive concern about compelled disclosure from the threshold reasons this petition might be a poor vehicle. In particular, it discusses the state's limiting-construction, alternative-provision, preservation, and record objections while expressly treating them as advocacy positions rather than established cert-stage findings. These arguments are identifiable in the provisioned briefs.

The treatment of the missing reply and unread appellate appendix is appropriately qualified. The candidate regards a square circuit split as unestablished rather than conclusively disproved. It avoids treating two distributions separated by a response request as two substantive conference examinations, recognizes the risk of double-counting attention signals, and distinguishes a terminal-state table from a forward transition probability. Its treatment of AFPF distinguishes narrow tailoring from a least-restrictive-means requirement on the briefs' account and candidly withdraws any claim of successful independent retrieval. It does not give the unverified NRSC characterization a separate decisive adjustment.

The remaining weaknesses are the subjective size of the move from the matched anchor to 14%, incomplete access to the appellate materials and reply, and the absence of a measured response-request/amicus adjustment. The denial is consistent with the analysis but does not establish why the Court denied review or vindicate the respondent's merits position. The high quality grade rewards source discipline and balanced case-specific reasoning, not hindsight correctness alone.

Only `reasoning.md` supplies the quality grade. The separately read forecast and structured quantitative claims are not graded here; the latter remain for the harness. No cert vote score, semantic-grade block, or independent big-case score is supplied.

## Leakage assessment

The captured log says **forward**. The September 17 prediction and tool activity precede the October 5 denial. Its coverage is **28/32 captured calls (0.875)**. Four web calls are **unobserved** and target the 2021 Bonta precedent or its official opinion URL. I assess their queries, not the candidate's assertion that nothing usable returned: an unobserved result is unknown, not empty. These queries do not target this petition's disposition.

The recorded shell search that mentions the labeling directory explicitly excludes it; that is not evidence of reading its contents. Local record reads, statpack inspection, and general-precedent queries reveal no already-decided fact for this petition. The reasoning remains prospective and attributes NRSC to pre-decision briefing. I therefore record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`, with the capture limitation stated rather than silently treating missing results as evidence of cleanliness.
