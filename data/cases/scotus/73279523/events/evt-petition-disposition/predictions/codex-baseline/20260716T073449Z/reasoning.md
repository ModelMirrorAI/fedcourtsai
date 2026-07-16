# Prediction

I predict that the petition will be dismissed, most plausibly after the parties resolve or materially narrow the underlying dispute. I assign an 18% probability to any grant (including a GVR), so the binary prediction is no grant. If the matter returns to an active conference rather than ending consensually, denial is the principal alternative to dismissal.

## Question and governing considerations

The petition asks whether a federal court may certify a damages class containing members whose only asserted injury is the intangible disparate impact of a race-neutral policy. It combines two questions: whether Rule 23 permits a damages class containing uninjured members, and whether an FHA disparate-impact violation itself supplies a concrete Article III injury.

Certiorari depends primarily on the importance and maturity of the conflict, the decision below's correctness, and whether this interlocutory case cleanly presents the questions. On the merits, *TransUnion LLC v. Ramirez* requires every class member to have Article III standing to recover damages but reserved whether every member must show standing at certification. *Laboratory Corp. of America Holdings v. Davis* granted review of the closely related Rule 23 question and then dismissed the writ as improvidently granted. Kavanaugh's solo dissent would have barred a damages class containing injured and uninjured members.

## Case-specific signals

The petition and questions-presented text provide real grant signals. The petition directly offers the Court another vehicle for the unresolved *LabCorp* issue, alleges a developed circuit conflict, comes from experienced Supreme Court counsel, attracted three amicus filings, and prompted the Court to request a response. The docket then shows three distributions associated with May conferences, although the first two were expressly rescheduled rather than recorded as post-conference relists. I therefore treat the repeated distributions as positive attention but do not mechanically apply the historical relist rates.

The brief in opposition supplies serious obstacles. It argues that every class member suffered two concrete harms—racial discrimination and an immediate property encumbrance from the lien—so the class contains no uninjured members. It also disputes the petition's factual premise that as much as 20% of the class lacked economic injury, notes that the Sixth Circuit expressly left the general class-member-standing question open, and emphasizes the interlocutory Rule 23(f) posture. Those issues could make this another poor vehicle even if four Justices still want the underlying question resolved.

The decisive docket signal is the May 29 joint motion to defer consideration, following the repeated reschedulings, with no later disposition in the July 16 snapshot. A joint request to defer ordinarily points to a party-driven development such as settlement rather than disagreement over the certworthiness of the petition. That makes a consensual dismissal more likely than it would be for an ordinary petition. The motion's text was not among the provisioned documents, so I do not assume its precise grounds; that uncertainty is reflected in the 0.65 confidence score.

## Calibration

The committed statpack places modern discretionary-cert grants at about 3.1% overall. For 2025 Term paid petitions, the estimated grant rate is 5.36%; Sixth Circuit petitions are about 3.5%, and petitions without a CVSG about 3.0%. This case deserves a large upward adjustment because of the response request, repeated distributions, amici, and its direct connection to a recently granted-and-DIG'd question. The vehicle disputes and, especially, the joint deferral motion then pull the forecast back toward a non-merits disposition. Balancing those considerations produces an 18% probability of a grant, with dismissal the single most likely label and denial next.

The 0.76 big-case score is independent of grant probability. A merits decision could affect damages-class certification nationwide, define the interaction between Article III and statutory disparate-impact injuries, and influence municipal and private defendants well beyond this water-lien dispute.

## Sources and limitations

I used the July 16 docket snapshot, `questions-presented.txt`, the complete petition, the complete brief in opposition, and `documents.json`. CourtListener confirmed the June 5, 2025 *LabCorp* disposition and Kavanaugh dissent. The ranged corpus-prior query was unavailable because the runner could not resolve the corpus endpoint, so no case-specific corpus priors were returned; I used the committed statpack for calibration instead.
