# Rationale for P(grant) = 0.08

## What I read

- Provisioned snapshot `record/snapshots/2026-09-16.json` (the file `context.json` names; mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 1, no CVSG, Term 2025, paid docket, originating court Supreme Court of Minnesota).
- Provisioned `record/documents/questions-presented.txt` and `petition.txt` (379-page PDF, text truncated per `documents.json`; the truncation falls in the appendix and the full petition body was readable).
- The brief in opposition (filed Aug 26, 2026) and the petitioners' reply (Sep 4, 2026), which were **not** provisioned because the document fetch ran on 2026-07-17, before either existed. This is a forward cell, so I fetched both from the supremecourt.gov docket PDFs linked in the snapshot and extracted their text locally. The BIO is filed jointly for every respondent (the Minnesota Attorney General, Red Lake Nation, the guardian ad litem, the county, and the mother).
- `metrics/statpack.md`: the modern-cert disposition section, the relist-count and CVSG cuts, and the per-Term "Segment base rate by salience band (sal-v4)" table.

## Anchor

The context band is `baseline` and the statpack's band table is computed under `sal-v4`, matching `salience_version`, so the anchor is baseline's bracketed `reached` rate pooled over Terms strictly before 2025. Weighting each Term's rate by its risk-set `n` (OT2017 through OT2024: 4.7%, 4.6%, 4.6%, 4.5%, 5.6%, 5.8%, 5.9%, 5.7%) gives roughly **5.1%**. For shape only: the relist-0 terminal bucket in the paid scored segment shows a grant family of about 1.7%, and the no-CVSG bucket about 6.3%.

## Adjustments up

- **The Court called for a response.** The guardian ad litem waived, and the day after the first distribution the Court requested a response (June 25, 2026). That is an affirmative act by at least one chambers and moves a petition well above the band floor. The statpack carries no cut for it, so its size is judgment: in my experience a called-for response multiplies a paid petition's grant odds by a factor of two to three.
- **Three cert-stage amicus briefs** (Academy of Adoption & Assisted Reproduction Attorneys with the National Council for Adoption; foster parents with Pacific Legal Foundation; Christian Alliance for Indian Child Welfare), and counsel who are repeat players before the Court (Goldwater Institute, and the UVA Supreme Court Litigation Clinic joining on reply). Amicus interest at the cert stage correlates with grants.
- **Subject matter the Court has signalled interest in.** Brackeen (2023) expressly left the equal-protection challenge to ICWA open on standing grounds and, in footnote 10, said non-Indian would-be adoptive families could raise it in state court. Justice Kavanaugh's concurrence called the question "serious"; Justices Thomas and Alito have written skeptically of ICWA's classification. After Students for Fair Admissions, a race-classification challenge to a federal statute has a receptive audience.

## Adjustments down (decisive)

- **The question petitioners want decided was not decided below.** The Minnesota Supreme Court affirmed the denial of *permissive* intervention under the state best-interests rule (Minn. R. Juv. Prot. P. 34.02) for abuse of discretion, held that only a party may raise the constitutional challenge in a CHIPS proceeding, and vacated the Court of Appeals' equal-protection discussion. The BIO's adequate-and-independent-state-grounds argument is therefore strong on its face, and the reply concedes that "the most [Petitioners] would win is a remand to reconsider the intervention." The Court rarely grants to reach a question that sits several contingent steps behind a state-law threshold ruling.
- **The federal question actually decided is weak as a cert question.** The First Amendment / due-process theory (that weighing the foster parents' constitutional challenge as evidence of their "attitude toward the children's tribal identity" penalized protected petitioning) has no supporting appellate authority; the reply admits the state court's step "appears to be unprecedented." The state court found four independent disadvantages to intervention and said this one "was not the decisive factor," which is a Mt. Healthy-style alternative holding that would survive even if the theory were accepted.
- **Standing and redressability look genuinely contestable.** The twins are now enrolled Red Lake members, their mother is a member, placement is with their maternal grandmother (a relative preferred under ordinary Minnesota law too, and supported by the mother, the tribe, the county and the guardian ad litem), and the twins have not lived with petitioners for roughly three years. Brackeen shows this Court's caution about standing in exactly this area. Even Justices eager to reach the ICWA question have reason to wait for a cleaner vehicle, and the Goldwater/PLF litigation program is likely to supply one.
- **Equities and posture.** Four-and-a-half-year-old children in a settled kinship placement, a temporary CHIPS proceeding with a separate permanency track still available, and a unanimous state high court. The Court is disinclined to disturb this.
- **No split.** Respondents cite an unbroken line of state appellate decisions and the en banc Fifth Circuit rejecting equal-protection challenges to ICWA; petitioners' "existing Indian family doctrine" confusion was not raised or decided below.

Net: a called-for-response petition with amici on a salient topic would ordinarily sit around 12-15%; the vehicle defects here are unusually severe and cut that roughly in half. **0.08.**

## Claims

- `disposition` 0.08 (= P(grant), any form).
- `relist-increment` 0.30. The record shows one conference distribution (the September 9 redistribution is for the same September 28 conference), so no relist yet. The called-for response and amicus interest make a single relist plausible, whether for a closer look or to write separately; absent a CVSG I do not expect a second.
- `cvsg-increment` 0.08. No CVSG on the docket. ICWA is a federal statute and the United States is not a party, which is the classic CVSG shape, but the threshold problems make a plain denial likelier than an invitation.
- `summary-disposition-route` 0.12, conditional on a grant. Petitioners ask for summary reversal on Question 2 in the alternative; no intervening decision supplies a GVR hook and the Court seldom summarily reverses a unanimous state high court on a novel theory. Most grants here would be plenary.
- `dissent-from-denial` 0.22, conditional on denial. The petition is written to draw Justice Thomas and Justice Alito (it cites their statements in Parents Protecting Our Children and Lee v. Poudre about lower courts using threshold doctrines to avoid contentious questions); the poor vehicle cuts against a writing.

## Big-case score

0.65. The underlying equal-protection question about ICWA is nationally significant and would be closely watched if decided; but the case as postured would most likely produce a narrow ruling about intervention and state-ground adequacy, so I discount from what a clean ICWA merits case would score.

## Uncertainty and where to discount me

- The size of the called-for-response adjustment is judgment, not a statpack figure; the pack carries no response-requested cut.
- I cannot see the Minnesota Supreme Court opinion itself beyond the parties' characterizations (the appendix was in the truncated part of the petition text), so my read of the alternative-grounds holding relies on both briefs quoting the same passages (Pet. App. 34a-35a).
- I have no visibility into whether a cleaner ICWA vehicle is already pending or imminent, which would matter for whether the Court holds this petition rather than denying it; I did not find one, and the CourtListener searches I ran returned nothing.
- Corpus priors: two `fedcourts query` citation lookups (Brackeen and Adoptive Couple) returned no rows because the citation column is sparsely populated; the corpus contributed only the committed statpack base rates.
