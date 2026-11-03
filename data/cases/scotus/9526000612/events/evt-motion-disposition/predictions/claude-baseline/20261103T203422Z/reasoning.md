# Reasoning — scotus/9526000612 (26A612), evt-motion-disposition (interim, arrival)

**P(relief granted in whole or in part) = 0.02. Predicted disposition: denied.**

## Record
- Snapshot `2026-10-21.json` (arrival-position cut, anchor index 0). It holds one entry: "Application (26A612) for an injunction, submitted to The Chief Justice" (Oct 20, 2026). The lower court is the D.C. Circuit (No. 26-5131). Martin Akerman is the applicant and represents himself. The respondents are the Merit Systems Protection Board et al., represented by the Solicitor General.
- `context.json`: forward mode, `band: null` (the normal interim case), no response requested, no referral, 0 amicus briefs. The ladder has not moved.
- The application text (`application.txt`, 20 pages) was fetched with `empty_text: true`. I could not read its content, so I don't know the specific relief requested or the grounds. I treat it as content-unavailable rather than absent, and I forecast from the docket and base rates.
- The live supremecourt.gov docket adds only the Oct 30, 2026 docketing entry. There is no response request, no referral and no disposition.

## Base rate
- Statpack, "The interim docket (applications)": my application Term is 2026, so the pool would be Terms 2016–2025 using `finer_granted`/`finer_resolved`. `statpack.json` shows `finer_resolved = 0`, and `finer_unread` is non-zero (equal to the substantive resolved count) in every pooled Term. The pool fails the every-Term-unread-zero condition and does not reach the 50-resolved floor, so **the pack publishes no interim baseline for this cell**, and I anchored without one. For shape only: the older `substantive_granted/resolved` reading pools to about 10–12% across 2016–2025 (e.g., 2025: 17/226; 2024: 16/194). That population is dominated by counseled government and institutional applications.

## Adjustments
- The applicant is self-represented, asks for an injunction (the most demanding interim relief: under the All Writs Act standard, the legal rights must be "indisputably clear"), and opposes a federal agency in what appears to be a personal employment/MSPB dispute. Pro se injunction applications against the government are granted extremely rarely; they are typically denied by the Circuit Justice in chambers. Corpus priors (other pro se substantive applications from this period, e.g. 26A613, 26A617, 26A618) are in the denied set.
- The application was submitted to the Chief Justice, who is the Circuit Justice for the D.C. Circuit. If he denies it, a pro se applicant often renews it to another Justice, who usually refers it to the full Court, which then denies it. That is why I put referral-increment at 0.25 rather than near zero.
- Response requested: the government rarely is asked to respond to a pro se injunction application, so 0.03. Amicus: essentially none, so 0.02.
- Order-writers: a written opinion on such a denial is very unlikely, so every Justice gets ≤0.4%.

## Uncertainty
I could not read the application. If it raised an unusual structural question (for example, MSPB quorum or removal issues), the stakes would be higher, but injunctive relief would still be very unlikely. I chose 0.02 instead of something lower to leave room for that uncertainty.
