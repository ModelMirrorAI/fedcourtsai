# Predicted Court Action and Procedural Trajectory

## Disposition
The Court will **deny** the petition for a writ of certiorari (`predicted_disposition: "denied"`).

## Further Distributions and Relist Trajectory (`relist-increment`)
The provisioned docket snapshot (`2026-10-25.json`) currently shows **one** conference distribution (`distribution_count = 1`): on July 29, 2026, following respondent Central Contra Costa Transit Authority's initial July 24, 2026 waiver of the right to respond, the petition was distributed for the September 28, 2026 Long Conference. On August 13, 2026, the Court requested a response (`Response Requested`), pulling the petition from the Long Conference list, and after one 30-day extension, respondent filed its Brief in Opposition on October 14, 2026.

Because the October 25, 2026 snapshot falls 11 days after the Brief in Opposition was filed—inside the 14-day window under Supreme Court Rule 15.5 before the Clerk redistributes the case—the post-opposition conference distribution entry has not yet been posted to the docket. Barring a rare Rule 46 withdrawal before distribution, the Clerk will distribute the petition and Brief in Opposition (along with any reply brief) in late October or early November 2026 for a November 2026 conference, raising the docket's recorded `distribution_count` from 1 to at least 2 (`P(relist-increment) = 0.98`).

Once the petition reaches that first post-opposition conference, the Court will likely deny review at that conference without a true post-opposition relist (roughly 80% chance of denial at the first post-BIO conference, and roughly 20% chance of one or two post-BIO relists if a chambers takes time to consider or circulate a separate statement or dissent from denial).

## Call for the Views of the Solicitor General (`cvsg-increment`)
The Court will **not** call for the views of the Solicitor General (`P(cvsg-increment) = 0.005`). No CVSG appears on the docket, and none is warranted: this is a fact-bound municipal employment termination dispute under Title VII and California's FEHA involving no federal agency, federal program, or specialized regulatory scheme, and the Court's general approach to *McDonnell Douglas Corp. v. Green*, 411 U.S. 792 (1973), is a recurring judicial-administration question on which the views of the Solicitor General are unnecessary once the Brief in Opposition is on file.

## Question Presented and Conditional Merits Scope
If the Court were to grant certiorari, it would take the single Question Presented—whether applying the *McDonnell Douglas* burden-shifting framework to grant summary judgment under Federal Rule of Civil Procedure 56 in a Title VII disparate-treatment and retaliation case conflicts with Rule 56 and Title VII's text—and address whether *McDonnell Douglas* should be retired or confined to a non-mandatory analytical guide at the summary-judgment stage.

## Summary Disposition vs. Plenary Review (`summary-disposition-route`)
Conditional on the low-probability event of a grant, plenary review is markedly more likely than a summary disposition in the cert order itself (`P(summary-disposition-route | grant) = 0.20`). No intervening decision of this Court has been issued since the Ninth Circuit's January 13, 2026 memorandum disposition (*Ames v. Ohio Department of Youth Services*, 605 U.S. 303 (2025), was decided seven months before the Ninth Circuit ruled and was already briefed below), leaving no basis for a standard GVR unless the Court were to grant another *McDonnell Douglas* vehicle first and hold this petition for it, and the deeply contested factual record precludes a per curiam summary reversal.

## Dissent or Statement Respecting Denial (`dissent-from-denial`)
Conditional on denial, the most likely outcome is a routine summary denial without noted dissent, though there is a meaningful tail probability (`P(dissent-from-denial | denial) = 0.12`) that Justice Thomas and/or Justice Gorsuch—who dissented from the denial of certiorari on the same *McDonnell Douglas* question in *Hittle v. City of Stockton*, 145 S. Ct. 759 (2025), and concurred in *Ames v. Ohio Department of Youth Services*, 605 U.S. 303, 319–26 (2025), and whose chambers likely triggered the August 13, 2026 call for a response—notes a dissent from the denial of certiorari or issues a brief statement respecting denial.
