# Reasoning — scotus/9026000267, evt-petition-disposition (distribution moment, forward)

## What I read
- Snapshot `record/snapshots/2026-11-13.json`: paid petition from CA9 (judgment 30 July 2026), filed 19 Aug 2026; respondent waived 16 Sep; petitioners' supplemental brief 18 Sep; distributed 23 Sep for the 10/9 conference; **response requested 1 Oct**; extension to 2 Dec 2026; one amicus brief (American Benefits Council, CIEBA, ERIC; Mayer Brown) filed 2 Nov.
- `questions-presented.txt`, `petition.txt` (QP, table of contents, split and vehicle sections), `supplemental-brief.txt`. `appendix.txt` was provisioned; I did not read the opinion below in full and relied on the petition's account of it.
- No brief in opposition exists yet. No `same-question.json`, no `related/`, no `decision-below.txt`.
- `context.json`: band `baseline`, `distribution_count` 1, no CVSG, `cert_anchor.rate` 0.0516.

## Anchor
The frozen anchor for a baseline-band paid petition is 5.2% (reached rate, prior ten Terms). Cross-checks from the statpack: CA9 petitions overall grant family ~3.3%; paid petitions with exactly one amicus brief at disposition 14.9% grant family (n=1159 resolved, read at disposition and a marginal cut).

## Adjustments up
- **Response requested after a waiver.** At least one chambers wanted to hear from the respondent. No committed table conditions on this; my own judgement is that it roughly doubles the rate for a paid petition, not more, because most called-for responses still end in denial.
- **Amicus support and counsel.** A trade-group amicus brief at the cert stage and an experienced Supreme Court practice for petitioners.
- **A split that respondent's own counsel has described as one.** The petition claims 1–7 (CA4 in *Trauernicht* against CA2, CA3, CA5, CA6, CA9, CA10, CA11), and the supplemental brief cites a Seventh Circuit brief by respondent's counsel calling *Trauernicht* at odds with the other circuits. The Ninth Circuit stayed its mandate with respondent's consent.
- **CVSG path.** ERISA remedial questions draw SG invitations at a higher rate than the docket generally.

## Adjustments down
- **The split is one case deep and months old.** *Trauernicht* was decided in March 2026. A web search confirmed it is a Rule 23(b)(1) class-certification decision, while this case arises from a denial of a motion to compel arbitration under the effective-vindication doctrine. The respondent will argue the conflict is in reasoning, not in holding, and that the Court should let it percolate.
- **Track record.** From memory, not from a committed table: the Court has repeatedly denied petitions from the majority-side ERISA arbitration decisions the petition lists (Tenth, Third, Second, Sixth Circuits), one of them after a CVSG. The new element is only the Fourth Circuit decision.
- **Posture.** Interlocutory: the case returns to district court for litigation on the merits regardless.
- Petitioner's reframing (from arbitration enforceability to the scope of § 502(a)(2) relief) is cleaner than the earlier petitions, but the decision below is an FAA decision first.

## Number
P(any grant) = 0.13: about two and a half times the band anchor, driven by the response request, amicus and the acknowledged conflict, held down by the shallowness of the split and the Court's past passes on this cluster. A CVSG would not itself resolve this claim; my 0.13 includes the path through one.

## Other claims
- `relist-increment` 0.97: the petition must be redistributed after the response arrives; the residual is dismissal by settlement or withdrawal before then.
- `cvsg-increment` 0.13: my judgement, well above the ~1% paid-segment share of petitions that draw one (180 of ~14,200), for the reasons above.
- `summary-disposition-route` 0.04: no pending case to hold for; summary reversal of a seven-circuit majority is implausible.
- `dissent-from-denial` 0.03, with `order-writers` kept small and consistent with it.
- `big_case_score` 0.45: large stakes for 401(k) litigation and plan sponsors, low public salience.

## Where to discount me
- I have not seen the opposition; a concession or a strong vehicle objection would move this a lot either way.
- The downward adjustment for past denials rests on recollection, which I did not verify by retrieval.
- I did not check the Court's live docket; the snapshot is dated today.
