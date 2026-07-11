# Prediction: denied

I assign a 29% probability that the Court grants the petition and predict denial. That is far above the ordinary cert-petition baseline, but still below even odds because the petition asks the Court to review a recent agency practice through a procedurally narrow mandamus vehicle, and the government's response is not yet available.

## Question and governing standard

Google asks (1) whether the PTO may deny inter partes review based on a patent owner's asserted “settled expectations” after the patent has been in force for six years and (2) whether courts may review a denial alleged to exceed the PTO's statutory authority. Certiorari ordinarily requires a square lower-court conflict, an important recurring federal question, or a serious departure from Supreme Court precedent, together with a clean vehicle. At least four Justices must vote to grant.

The petition frames the merits through 35 U.S.C. §§ 311, 314, and 315 and the reviewability question through 5 U.S.C. § 701(a)(2) and 35 U.S.C. § 314(d). Its strongest doctrinal hook is the Court's language in *Cuozzo*, *SAS Institute*, and *Thryv* preserving some judicial role when the PTO exceeds statutory bounds, reinforced by *Loper Bright*'s direction that courts police the boundaries of delegated authority. Its central obstacle is that § 314(d) makes institution decisions “final and nonappealable,” while § 314(a) gives the Director broad discretion not to institute.

## Record signals favoring review

The July 10 snapshot supplies a strong procedural signal. The PTO initially waived a response, the case was distributed for the June 25 conference, and the Court then requested a response on June 12. A requested response after waiver means at least one Justice considered the petition substantial enough not to deny summarily. Seven amicus briefs supporting the petition were filed on May 29, representing patent-law professors, the PTAB bar, pharmaceutical and technology interests, and other repeat participants. That unusually broad support makes the petition's claim of systemic importance plausible.

The provisioned questions-presented text and full petition also identify several vehicle strengths. The PTO reportedly relied only on the challenged patent's age and “settled expectations”; the Federal Circuit denied mandamus under its categorical precedent; and the petition presents a pure legal question rather than asking the Court to reassess the strength of an IPR petition. The asserted practice is recurring and potentially outcome-determinative across many IPRs. The Court has repeatedly taken patent-statute and administrative-review cases, and the petition ties both questions to recent Supreme Court decisions.

## Reasons denial remains more likely

The record lacks the respondents' merits arguments. `documents.json` lists only the petition and questions presented; no brief in opposition is provisioned. The snapshot shows that the United States, after waiving, had been ordered to respond and had submitted an extension request on July 10. The Solicitor General can therefore still expose vehicle defects, defend the policy as an ordinary exercise of institution discretion, report a policy change, or otherwise reduce the need for review.

The claimed circuit conflict is also imperfect. The petition cites other circuits' general APA decisions allowing review of statutory limits on agency discretion, but no other circuit can directly disagree about § 314(d)'s specialized IPR bar. The Federal Circuit's short mandamus disposition rests on recent precedent, so the issue has limited percolation. On the first question, Congress's omission of an age bar does not necessarily prohibit the Director from considering patent age when deciding whether to exercise discretion; the statute sets a prerequisite for institution without requiring institution whenever that prerequisite is met. On the second, *Thryv* reads § 314(d) broadly, and the petition depends heavily on “shenanigans” language whose precise reach remains uncertain.

## Calibration

The committed statpack reports only four grants among 296 resolved SCOTUS records (1.4%), but its disposition mix is not a clean modern paid-cert denominator and the modern discretionary-cert section described by the task prompt is absent. I therefore use it only as confirmation that grant is the rare outcome, not as a literal probability. The Court-requested response and seven supporting amici warrant a major upward adjustment, while the pending government response, non-square split, recent policy, and reviewability barrier keep the estimate at 29%.

No individual votes are predicted. Cert votes are not public, and the pre-response record does not support reliable Justice-by-Justice assignments.

## Retrieval limitation

The ranged corpus query failed before returning any priors because the corpus remote hostname could not be resolved. The configured CourtListener search likewise failed because its session store was unavailable. I proceeded from the provisioned event, snapshot, documents, and committed statpack; details are recorded in `retrieval.md`.
