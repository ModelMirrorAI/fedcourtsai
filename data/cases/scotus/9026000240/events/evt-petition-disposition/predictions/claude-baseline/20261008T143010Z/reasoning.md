# Rationale for P(grant) = 0.36

## Anchor

Cert-stage cell, `moment: distribution`, mode `forward`. `record/context.json` freezes `band: baseline` under `sal-v4`, `distribution_count: 1`, no CVSG, Term 2026, so the anchor is the statpack's *Segment base rate by salience band (sal-v4)* table, `baseline` column, bracketed `reached` figure, pooled over the Term rows strictly before 2026 (OT2017–OT2025, every row the table renders). Pooled: about 637 grants over a weighted risk-set denominator of 12,720, or **5.0%**. The per-Term `reached` figures run 3.9% to 5.9%, so the anchor is stable. The relist cut (one distribution, bucket 0: granted 1.2%, gvr 0.5%) and the CVSG `none` cut (granted 4.0%, gvr 2.3%) sit beside it; the ca4 originating-circuit bucket (granted 1.3%, gvr 1.2%) is below the whole-docket average and I give it little weight against the case-specific signals.

## Adjustments up (large)

1. **The Court called for a response after a waiver** (Oct 5, after the Sept 23 waiver and the Sept 30 distribution). The statpack carries no cut for a Court-requested response, so this is judgment rather than a table lookup. The Court cannot grant without a response, and a request after a waiver means at least one chambers wants the option. Historically this multiplies a paid petition's grant odds severalfold relative to the unrequested population.
2. **Amicus support at the cert stage**: eight briefs, including 22 states, a Notre Dame religious-liberty clinic, and the Council for Christian Colleges & Universities. Cert-stage amicus volume at this level is rare and strongly associated with grants.
3. **Doctrinal posture.** The petition asks the Court to confine or overrule Locke v. Davey, the one remaining "play in the joints" precedent after Trinity Lutheran, Espinoza, Carson, Mahmoud, and Catholic Charities, all of which the Court granted when well presented. Three Justices have publicly questioned Locke; Carson confined it to clergy training. The Fourth Circuit's published Hall opinion applied Locke squarely, making this the cleanest overrule vehicle the Court has seen.
4. **Counsel and respondent.** Alliance Defending Freedom (Bursch, Campbell) is an elite Supreme Court practice; the respondent is a state, and the Court has taken every recent religious-funding case against a state in this line.
5. **The companion petition** Hall v. Fleming, No. 26-193 (forward, pre-snapshot public information, disclosed in `flags.json`): final judgment, published opinion, BIO due Oct 14 after an extension, thirteen amici. The Court's Nov 4 response deadline here lines the two up for the same conference, which is how the Court typically handles a cert-before-judgment companion.

## Adjustments down

1. **Cert before judgment is rarely granted on its own.** Rule 11's "imperative public importance" standard is almost never met by a private petitioner, and the Court grants CBJ companions mainly when it is already taking a lead case. This petition's fate is therefore mostly derivative of Hall's.
2. **Interlocutory posture.** The order under review denies a preliminary injunction and dismisses two plaintiffs' claims; pendent appellate jurisdiction over the dismissal is contestable, and the Court dislikes forecasting merits on a PI record.
3. **If the Court grants Hall, denying this petition as duplicative is a real path.** The Fourth Circuit would hold its own appeal pending Hall regardless.
4. **The baseline band.** The frozen band is the weakest, and the petition sits at one distribution; the scored baseline is 5.0%, so most of my number is adjustment.

## Decomposition

P(Hall granted) ≈ 0.5. Given Hall granted: plenary consolidation ≈ 0.35, hold ≈ 0.5 (then GVR, which counts as a grant on the binary axis, if the petitioner wins Hall, ≈ 0.7), outright denial ≈ 0.15, so P(grant here | Hall granted) ≈ 0.70. Given Hall denied: P(grant here) ≈ 0.05. Overall ≈ 0.5 × 0.70 + 0.5 × 0.05 ≈ 0.37, which I round to **0.36**. The most probable single outcome is still denial, so `granted` is 0 and `predicted_disposition` is `denied`; the probability expresses P(any grant), GVR included.

## Claims

- `disposition` 0.36, as above.
- `relist-increment` 0.94: the response request pulls the petition off the Oct 16 conference and the response (Nov 4) forces a redistribution; the residual is a withdrawal or a parse that does not register the new entry.
- `cvsg-increment` 0.04: no federal party or statute; the Court has not called for the SG in this line.
- `summary-disposition-route` 0.45, conditional on a grant: the hold-and-GVR path is roughly as likely as consolidated plenary review.
- `dissent-from-denial` 0.20, conditional on a denial: a denial most often comes either with Hall granted (no writing) or with both denied, where a Thomas/Alito/Gorsuch writing is plausible but would attach to Hall rather than to this docket.

## Big-case score

0.7: an overruling of Locke would reshape state tuition programs nationwide and the states' amicus brief shows the stakes; scored below the lead case because this is the companion. Not grant likelihood.

## What I read and where to discount me

Provisioned inputs: the 2026-10-08 snapshot, `context.json`, `questions-presented.txt`, and `petition.txt` (219 pages, `truncated: true`; I read the QPs, introduction, jurisdiction, statement, the vehicle and Rule 11 sections, and the start of the district court opinion). No brief in opposition exists; Virginia waived, so my read of the state's position is from the petition's account and the Fourth Circuit's published Hall opinion. Retrieval (forward mode, unrestricted): the Fourth Circuit docket for No. 26-1437 via CourtListener, the Supreme Court docket for No. 26-193 and its SCOTUSblog case page, two `fedcourts query` pulls for the era's grant/deny priors (which returned nothing closely analogous; used for shape only), and the statpack. The retrieval did not surface this petition's disposition; it is pending. Main uncertainties: whether the Court wants a CBJ companion at all when Hall is available, how Virginia's Oct 14 BIO in Hall frames vehicle problems (Hall's major changes, standing), and whether the Court's appetite extends to overruling Locke rather than distinguishing it. The response request is the single observation doing the most work; without it I would be near 0.15.
