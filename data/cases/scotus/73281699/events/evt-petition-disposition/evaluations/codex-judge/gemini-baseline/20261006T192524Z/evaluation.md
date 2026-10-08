# Evaluation: gemini-baseline

## Outcome and numerical scores

This cert petition was denied on October 5, 2026, according to the supplied outcome, with `actual_granted = 0`. gemini-baseline predicted `denied` on September 17, so correctness is **1**. Its grant probability of 0.04 gives Brier **0.0016**.

The evaluation baseline is determined by the candidate's frozen context, not by the narrower baseline window its prose chose. That context carries Term 2025, `elevated`, and `sal-v4`; the committed table matches. All rendered strictly-prior reached-rate/denominator pairs are: 2024: 17.9%/336; 2023: 17.5%/354; 2022: 19.0%/300; 2021: 20.5%/342; 2020: 16.1%/397; 2019: 13.8%/334; 2018: 15.9%/347; 2017: 17.5%/400. Their resolved-weighted rate is **0.17237935943060498**, denominator **2,810**, on the `risk_set` basis. Exclude 2025 and 2026. The table displays 10 of 10 Terms, so its rendering hides no available earlier row. Rates are rounded denial-reweighted estimates, not exact grant counts or a refreshed corpus measurement.

Skill is `1 - 0.0016 / 0.17237935943060498^2 = 0.9461544946048972`. The low grant probability performs very well on this denial; one result cannot establish that the sharp discount was generally calibrated.

## Reasoning quality: 0.60

The document identifies the central tension between an asserted judicial-speech standards conflict and concrete vehicle objections. Its attention to the robe/title, multiple conduct rules, and the opposition's alternative strict-scrutiny argument is relevant. The provisioned opposition expressly advances those points. It also recognizes the requested response as an attention signal rather than treating this as an entirely routine petition.

The analysis is nevertheless substantially more confident than its evidentiary development supports. It relies on the opposition's split-deflation and judicial-prestige arguments without seriously testing the petitioner's account or acknowledging an unread reply. The conclusion that the robe supplies an independent basis satisfying strict scrutiny turns a disputed vehicle contention into something close to a settled answer. The supplied denial does not establish that answer.

Its quantitative anchor selects only 2021–2024 although the matching table supplies earlier eligible rows, does not show resolved-denominator weighting, and gives a rough 18% figure rather than an auditable pool. It then offers no quantitative bridge to 4%. It describes the elevated band through response requests without examining this docket's distribution sequence, and invokes a long-conference backlog discount without a comparable measured cohort. Those are weaknesses in reasoning, independent of the favorable realized Brier score.

Only `reasoning.md` contributes to this qualitative grade. Neither the forecast document nor the mechanical claims are independently graded or used to adjust it.

## Leakage and scope

The harness records `forward` and 34 calls, all marked `unobserved`; result-capture coverage is 0.0. That is a capture limitation, not evidence that calls failed or returned nothing, and not itself a predictor defect. Queries show local inputs and the statpack, without an external search for this case's disposition. The reasoning discusses a pending September 28 conference and does not presuppose the October 5 denial.

One late shell call attempts `git restore` of the labeling reference artifact named `qp-topic-reference.json`. This is out-of-scope restoration of a prohibited labeling artifact, and warrants the cell-level scope flag. The call's result is unobserved; the log does not show a subsequent content read or use of labeling information. I therefore do not convert restoration into a finding that outcome material was viewed. I have not accessed that artifact myself. On the available queries and prose there is no affirmative evidence of outcome retrieval; the genuinely forward timing supports `not_applicable` influence and no leakage exclusion. This is not a claim of complete observation.

No cert vote accuracy, semantic grades, or independent big-case assessment is supplied. Mechanical claims remain the harness's responsibility.
