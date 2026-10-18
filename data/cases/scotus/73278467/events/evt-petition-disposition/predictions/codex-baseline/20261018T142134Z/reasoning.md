# Basis for the prediction

## Record and information boundary

This is a forward cert-stage cell, not a merits forecast. I used the case-level `record/snapshots/2026-10-18.json`, `context.json`, and the unresolved petition event definition. The frozen context supplies sal-v4 **high**, docket Term **2025**, three distributions, and the June 30, 2026 CVSG. I retained those values rather than reclassifying the caption or treating three distributions as three completed relists. The null cutoff permits use of the provisioned September 25 invited brief.

I read the questions presented and relevant portions of `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, `sg-invited-brief.txt`, and `appendix.txt`, with `documents.json` for provenance. The petition, opposition, reply, and invited brief are marked nonempty and untruncated. The 268-page appendix is truncated; I used the retained discussion of party presentation at appendix pages 36a–37a, not omitted material. The most consequential input is the invited brief's express recommendation of a GVR, coupled with its opposition to plenary review (pp. 1, 8–9, 17–23).

I neither sought nor encountered this petition's disposition and do not independently know its outcome. The SG brief's description of B.P.J. is pre-snapshot context about a different case, not this petition's outcome. I treat that description as the government's advocacy, not as an independently verified holding covering all of Griffith's claims.

## Base-rate anchor

The committed `metrics/statpack.md` sal-v4 table matches the context. Pooling every rendered Term strictly before 2025, namely 2017–2024, using the JSON's bracketed reached-rate numerators and weighted denominators gives **314 / 898 = 34.97%**. The eight denominators are 127, 99, 98, 111, 140, 105, 102, and 116. This is the starting probability for a high-band petition, not the much lower whole-docket probability. I exclude Terms 2025 and 2026 despite this being a forward cell.

The modern-cert section's displayed counts imply roughly 2.8% for the grant family overall; the Tenth Circuit cut is roughly 3.7%. Neither is an appropriate substitute for the selected high-band anchor. The paid-segment terminal cuts show roughly 40.6% any-grant at two relists and 34.8% following a CVSG. These overlapping cuts describe population shape, not independent likelihood ratios or a forward relist hazard. In particular, the long gap and CVSG account for much of this docket's distribution history.

These are figures from the committed pack, whose last modifying commit is `cf9ae960e`, dated October 13, 2026. I did not access the live corpus service, and the pack does not establish current corpus-wide pull freshness. Case facts here are from the October 18 provisioned snapshot, not a claim about a separately refreshed live docket.

## Why 0.90 for any grant

The large upward adjustment is for the **substance of the returned SG recommendation**, not merely the fact of a CVSG already reflected in the band. The invited brief recommends a specific, administratively simple grant-family outcome: reconsideration under intervening Supreme Court decisions. The petition itself requests similar relief in the alternative, and the reply develops why an appellate mandate may keep the challenged reasoning operative without vacatur (reply pp. 8–11).

The opposition supplies substantial reasons against plenary review: the panel did not decide the claimed Turner-versus-heightened-scrutiny conflict because the petitioners had not presented that argument; the search claim lacks an asserted circuit conflict; and the case comes from a dismissal-stage decision rather than a developed merits record (BIO pp. 9–13, 23–27). The retained appellate opinion confirms that party presentation controlled its treatment of Turner. The SG largely accepts these vehicle concerns while arguing they favor GVR rather than denial. Thus, evidence that lowers plenary-review probability need not lower the probability of the grant family to the same extent.

The principal contrary consideration is the opposition's argument that lower courts can incorporate intervening law during the remand already ordered, making Supreme Court vacatur unnecessary. The relationship between the newer decisions and the separate privacy/search allegations also leaves room for disagreement. I do not assume the SG's assertion that every claim fails is correct. These uncertainties, plus the Court's discretion to deny despite the government's recommendation, keep the forecast below certainty.

For general procedural context only, I checked Lawrence v. Chater, 516 U.S. 163, 167–168 (1996), through CourtListener's lead-opinion excerpt. It recognizes GVR as potentially appropriate when intervening developments could alter the lower court's premise and the litigation's outcome, subject to equitable considerations. This supports the availability of the proposed route, not a measured 90% empirical success rate. The numeric adjustment remains a judgment based on this record.

## Other probabilities and stakes

The **0.96 conditional summary-route** probability reflects the SG's preference for GVR and its rejection of plenary review; it is not multiplied by 0.90 in the claims block. The **0.35 additional-distribution** probability leaves room for disagreement over the scope of a remand or a separate writing, while recognizing that a straightforward GVR could follow the already-scheduled conference. The **0.30 conditional denial-writing** probability reflects the salience of the issues and the express recommendation for intervention, but I have no published conditioned baseline for that estimate. The CVSG increment is already vacuous.

The **0.80 stakes score** concerns the potential reach of rules governing transgender detainees' equality, privacy, searches, and institutional safety across correctional systems. It is not grant likelihood and does not imply that the most likely, narrow procedural disposition will itself settle those rules. I omit cert votes because this record does not support a reliable individual lineup.
