# Reasoning for my numbers

**Call: denied, P(relief granted in whole or in part | decided) = 0.02.**

## What I had
- The snapshot `2026-11-17.json` (arrival-position cut) carries a single entry: the stay application and sealing motion submitted to Justice Gorsuch on 16 Nov 2026. Applicant is a private individual with counsel; respondent is Oklahoma; the court below is the Oklahoma Court of Civil Appeals, Third Division (No. 123,076).
- **No application text was provisioned** (no `record/documents/`), and the application is filed under seal, so I could not read what order it seeks to stay or on what grounds. This forecast rests on the docket and base rates.
- Forward mode, so I read the Court's public docket for the linked petition, No. 26-502. It shows a paid cert petition filed 28 Aug 2026 with a sealed supplemental appendix (sealing motion granted 13 Oct), from a judgment of 9 Mar 2026 with discretionary review denied 1 Jun 2026, and a waiver of response filed by counsel for "Minor Child E.O.D." (a public defender's office). That shape (a parent against the State, a minor child as respondent, sealed filings, the civil appeals court) points to a juvenile deprived-child or parental-rights proceeding. That is my inference from the caption and parties, not something the record states.

## Base rates
- Scored pool: the statpack's interim section, finer reading, ten application-Terms before OT2026, gives 156/1337 = 11.7% (the applicant-class table's bottom-right cell; well above the floor of 50).
- Applicant-class cut: I read the `private` / `unmarked` (non-capital) cell, 7.0% (63/906). The caption rule's class (private) matches my own read.
- I go well below 7% because that cell includes well-resourced emergency applications on election, religious-liberty and regulatory disputes that draw responses and referrals. This one has none of those marks: a family-law matter from a state intermediate court, where the state's high court declined review, raising what will almost certainly be fact-bound due-process claims. The Court essentially never stays state child-welfare judgments, and domestic-relations matters are ones it leaves to state courts. The application was also filed more than five months after the state supreme court denied review and nearly three months after the cert petition, which undercuts urgency. The linked petition drew a waiver, not an opposition.
- I did one corpus query for recent denied SCOTUS rows including applications; it returned generic recent denials and added nothing case-specific.

## Ladder claims
- Response requested, 0.04: Circuit Justices rarely ask for a response on applications they intend to deny alone.
- Referral, 0.07: mostly the refile-to-another-Justice path after a single-Justice denial; counsel is on the case, which makes a refile less common than with pro se applicants but not rare.
- Amicus, 0.01: sealed family matter, no organised interest visible.
- Order writers: all near zero; slightly higher for Gorsuch as the Justice handling it and for the Justices who write most on orders.

## Where to discount me
- I have not seen the application. If it challenges something with a clean federal hook (for example, an Indian Child Welfare Act question, which is plausible in Oklahoma and within Justice Gorsuch's interests), the chance of a response request or referral is higher than I state. I kept a small allowance for that and nothing more, since nothing on the record indicates it.
- My reading of the case as a child-welfare matter is inferred.
