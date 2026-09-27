# Why 0.22

## Inputs read

- Snapshot `record/snapshots/2026-09-23.json` (date cut, cutoff 2026-09-24): two
  entries, the September 17 submission to Justice Sotomayor and the September 23
  call for a response due September 28. No amicus, no referral.
- `record/context.json`: forward mode, interim stage, `band: null`,
  `response_requested: true`, `referred_to_court: false`, `amicus_briefs: 0`,
  Term 2026. No band, so no cert anchor applies, as the stage rules require.
- `record/documents/application.txt`: the full 38-page application, text
  extracted cleanly. No response or amicus text was provisioned.
- Event: `moment: response-requested`, opened 2026-09-23.

## The base rate

The statpack's interim section says its rows ground the interim stage's scored
base rate, so I read the pooled rule rather than the descriptive-only caption.
Pooling the substantive resolved rows for application-Terms strictly before
2026 within the ten-Term window (2016 to 2025), only Terms 2024 and 2025 carry
parsed rows:

| Term | resolved (subst.) | granted | unparsed |
| --- | --: | --: | --: |
| 2025 | 226 | 17 | 0 |
| 2024 | 70 | 14 | 972 |
| pooled | 296 | 31 | |

Pooled grant rate 31/296 = 10.5%, well above the 50-resolved floor. Term 2024 is
mostly unparsed, so the pool leans on one fully covered Term. The pack's
escalation-signal counts (64 of 367 substantive applications with a requested
response) are right-censored and unconditioned, so I read them as shape only.

## Adjustments up from 10.5%

- **The rung reached.** A Circuit Justice's call for a response is the strongest
  rung of the ladder; applications that are summarily denied never get one. The
  pack publishes no conditioned rate, but the recent corpus rows I pulled show
  the two September grants (26A308, 26A388) both carrying a requested response
  and a referral, while the denials in the same window carry neither.
- **Malliotakis v. Williams (March 2, 2026).** The Court granted a stay of a New
  York trial-court order pending the state appeal and a certiorari petition,
  6-3, presented to Justice Sotomayor and referred. It shows the Court will
  reach into pending New York proceedings when the federal claim is strong.
- **Doctrinal appeal.** The order's second directive, compelling the applicant
  to petition his rabbis to withdraw a censure he agrees with, is a
  compelled-speech and church-autonomy problem the current majority takes
  seriously; the Yeshiva dissenters (Alito, Thomas, Gorsuch, Barrett) signalled
  they would grant relief against a New York court in a comparable posture.
- **Counsel and support.** Dechert (McGinley, Engel) and the Notre Dame
  Religious Liberty Clinic, with the Becket Fund already filing as amicus.

## Adjustments down

- **Exhaustion and jurisdiction.** In Malliotakis both the Appellate Division
  and the Court of Appeals had refused stays, so section 1257 jurisdiction
  attached to a highest-court order under Skokie. Here no state appellate court
  has ruled on the stay motion; only a single Appellate Division justice denied
  interim relief, and the applicants did not go to the Court of Appeals. The
  Yeshiva majority (Roberts and Kavanaugh with the three liberal Justices)
  denied in 2022 precisely because New York's expedited-review and interim
  avenues had not been pressed, and told the applicants to return only if they
  sought and received neither. A four-month-old undecided motion is a strong
  fact, but the application does not say the appeal itself was expedited, and
  the swing Justices can plausibly say the state courts have not yet refused.
- **Private commercial dispute, no deadline.** Unlike an election map, nothing
  becomes irreversible on a date certain; the trial court found no violation
  of the TRO and denied sanctions, so contempt is a prospect, not a pending
  order.
- **Partial relief resolves as denial.** The seruv-withdrawal directive is far
  more vulnerable than the bar on furthering the beis din proceeding, so a
  stay of one provision only is a real path, and the interim resolver reads a
  mixed order as denied. This shaves a few points off the unqualified-grant
  number.
- **Mootness.** A Second Department ruling on the stay motion before the Court
  acts would lead to withdrawal or a denial as moot.

Netting these, I moved from 10.5% to 22%. The rung reached and the Malliotakis
precedent carry most of the upward weight; the exhaustion problem, judged
against the Yeshiva majority's stated rule, is the main reason I stay well
under even odds.

## The increment claims

- `response-requested-increment` 0.03: the rung has fired; the harness will
  mask it. A second call is rare.
- `referral-increment` 0.80: a referral almost always follows a requested
  response on a well-lawyered application, with withdrawal or mootness the
  main alternative.
- `amicus-increment` 0.96: forward-mode retrieval of the live docket shows a
  Becket Fund amicus brief filed September 25, after my snapshot's cutoff, so
  the rise from the frozen count of zero has already happened. Disclosed in
  `flags.json`; it is ordinary forward-mode signal, not leakage.

## Uncertainty and discounts

- I could not see the response (not yet due) or the Becket brief's content.
- The corpus pool rests essentially on one fully parsed Term.
- I did not verify whether the Appellate Division has acted since September 17;
  the live Supreme Court docket showed no withdrawal or letter as of retrieval.
- I read the Malliotakis order text from the concurrence's account of the
  procedural history; the per curiam order itself gives no reasoning.
