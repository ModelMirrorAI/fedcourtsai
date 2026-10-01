# Rationale for the probabilities

## Target and evidence boundary

This is the interim arrival event for **Kenneth Nelsen, Warden v. Christa Gail Pike**, application 26A428. The forecast is P(an unqualified grant of the Warden's application to vacate the stay), not P(a stay for Pike), P(certiorari), or a merits judgment. I assign **0.82**, with `granted=1` and disposition `granted`.

I read the event definition, `record/snapshots/2026-09-30.json`, `record/context.json`, and the entire provisioned `record/documents/application.txt`, with its manifest. The manifest identifies a 15-page application fetched September 30, 2026, neither truncated nor text-empty. No respondent's filing, complete Sixth Circuit order, dissent, or underlying Rule 60(b) motion was provisioned separately. Their contents are known here only through the applicant's characterizations and excerpts; those are advocacy, not independent findings.

The context is forward, with an arrival-position cut at anchor index zero, snapshot date September 30, and cutoff October 1, 2026. The snapshot contains only the opening submission to Justice Kavanaugh. The frozen ladder is response requested false, referral false, amici zero. I do not infer any later docket action from the fact that the application's advertised September 30, 10 a.m. CDT execution time has passed by writing time. No current docket or target disposition was retrieved. I have no known outcome for this application.

The application at printed page 5 reports a September 29 denial in separate proceedings, 26A414 and 26-5696. That is provisioned pre-arrival history, not this event's resolution. I do not treat it as a denial of the Warden's application or as adjudication of the new Rule 60(b) issue.

## Published anchor and its limits

The committed `metrics/statpack.md`, section “The interim docket (applications),” supplies the comparison population. For application Term 2026, the eligible window is 2016–2025. Its nonzero resolved substantive counts are 226 resolved/17 granted in 2025 and 70 resolved/14 granted in 2024. Thus the strictly-prior pool is **31/296 = 0.10473**, above the 50-resolution floor. The earlier eligible Terms contribute no parsed substantive resolutions. I exclude the 2026 row and the all-Term rate. The null salience band is appropriate for this stage and provides no cert-rate anchor.

These are figures from the committed pack available in this checkout, not a freshly queried corpus. The pack exposes no build timestamp or newest-pull/newest-snapshot vintage in the inspected metadata, so its corpus-wide freshness is unverified. The case-specific input vintage is the September 30 snapshot and same-day document fetch; no separate case `last_pulled` was supplied.

Coverage sharply limits interpretation: the 2024 row has 972 unparsed applications out of 1,297, whereas 2025 has zero unparsed out of 1,467. The eligible 2016–2023 rows are entirely unparsed. Resolutions are machine-matched, and withdrawal/dismissal and mixed denial-first orders count as ungranted. The pack pools different substantive asks; it does not publish a state-requested capital-stay-vacatur rate. Its response/referral/amicus columns cover all substantive applications, pending ones included, and are not arrival-conditioned hazards. Nor is the pooled population identical to the signal-selected prediction cohort. I use the 10.47% rate as the declared unconditioned anchor, not as a measured frequency for this particular posture or evidence of forecast skill.

## Why the large upward adjustment

The adjustment is substantive and judgmental, not a fitted conditional rate. This applicant seeks to undo a lower-court stay, the opposite direction from a prisoner's application for a new stay. A low pooled relief rate cannot be transferred mechanically between those asks.

1. **A concrete successive-petition obstacle.** The application, printed pages 5–9, describes an attempt to reopen the rejection of a mitigation-related ineffective-assistance claim because state counsel recently acknowledged childhood abuse. I checked the general rule in *Gonzalez v. Crosby*, 545 U.S. 524, 531–33 (2005), through CourtListener's lead opinion, ID 9500020. The opinion distinguishes attacks on the merits resolution from defects in the integrity of the federal habeas proceeding, and addresses new evidence supporting a previously litigated claim. If the application's description is accurate, the former characterization fits appreciably better. That conditional assessment is the strongest reason for a high vacatur forecast.

2. **The alleged new fact may not alter the prior rationale.** Printed pages 3–4 and 9 describe earlier decisions as turning on cumulative mitigation and lack of prejudice in light of aggravation, rather than disbelief of the abuse reports. If accurate, a later acknowledgment of abuse does not directly undermine the ground on which relief was rejected. I did not independently retrieve those earlier Pike decisions.

3. **An unusually vulnerable rationale for the short stay.** Printed pages 6–8 report that the divided panel wanted time to analyze the remand issue, without making the usual likelihood-of-success findings. That favors vacatur, but the full order is missing and an administrative pause to determine jurisdiction is a meaningful counterargument. The State's assertion that Pike did not request a stay does not by itself establish that the panel lacked authority to preserve the status quo.

4. **Timing favors the State's equitable argument, with a qualification.** Printed pages 5 and 10–11 place the state-counsel statement on August 13 and the Rule 60(b) filing on September 29. This supports a delay objection. It does not independently prove intentional gamesmanship, and the intervening state proceeding may explain part of the chronology. I do not adopt the application's rhetoric about motive as fact. I also do not treat its cited *Price* concurrence as a majority holding.

The 0.18 complement reflects the missing adversarial record, the majority panel's actual willingness to preserve a short review opportunity, irreversible harm to Pike, the possibility that the motion identifies a genuine procedural-integrity defect, and the possibility of a procedural exit if the lower court acts first. These uncertainties keep me below near-certainty despite the seemingly strong successive-petition argument. No precise empirical state-vacatur success rate was available or invented.

## Other outputs

The **0.94 response-request** and **0.96 referral** probabilities reflect the capital execution-day posture and a state request to remove an existing appellate stay. They are predictions from a zero-rung arrival state, not observations of later activity. A requested response and an actual filed response are different events; this claim predicts the request. The **0.10 amicus increment** allows for a quick submission while recognizing an extremely short likely decision window and the narrow procedural issue. No published arrival-conditioned increment rates were used.

The **0.78 significance score** reflects immediate life-or-death consequences and the public importance of execution-day review, discounted from the highest tier because the apparent issue is a narrow application of existing habeas doctrine. It is not a second grant probability.

General-precedent web searches returned no usable results; CourtListener supplied the relevant *Gonzalez* text instead. Neither retrieval path was used to seek this application's outcome. The retrieval log records the unsuccessful searches as well as the successful precedent lookup.
