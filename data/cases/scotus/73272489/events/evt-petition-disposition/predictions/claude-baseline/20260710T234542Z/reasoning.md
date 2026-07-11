# Sanders v. City of Long Beach, No. 25-1235 — cert petition disposition

**Prediction: denied. P(granted) = 0.002.**

## The case

Leslie Sanders, proceeding pro se, sued the City of Long Beach over flood
damage to his home on February 2, 2019, alleging premises liability, public
nuisance, negligence, and failure to warn of a dangerous condition at storm
water "Pump 13" (Los Angeles County Superior Court No. 19STCV43406). After a
bench trial, Judge Kim found for the City. The California Court of Appeal
(Second District, Division Seven) affirmed in an unpublished opinion on
August 18, 2025, denied rehearing September 3, 2025, and the California
Supreme Court denied review November 19, 2025 (No. S293138). The petition
was filed February 9, 2026, docketed April 30, 2026 as a paid case, and
distributed June 17, 2026 for the Conference of September 28, 2026 — the
Term-opening "long conference."

## The question presented and why it cannot carry a grant

The QP (from the provisioned `questions-presented.txt`) is a single run-on
narrative of case-specific grievances: the trial judge excluded the
plaintiffs' 2005 Storm Water Report and deposition evidence, barred
impeachment of the City's witness (Arthur Cox) with prior inconsistent
statements, admitted the City's assertedly hearsay-based testimony, and
displayed bias — all said to violate the Fifth, Sixth, and Fourteenth
Amendments. Under the Rule 10 criteria this is about as weak as a petition
can be:

- **Fact-bound error correction.** Every claim is an evidentiary ruling in
  one bench trial. Rule 10 expressly disfavors review of "erroneous factual
  findings or the misapplication of a properly stated rule of law," and the
  Court does not sit to review state evidentiary rulings for error.
- **No split, no unsettled federal question.** The petition invokes the
  Federal Rules of Evidence and Federal Rules of Civil Procedure, but those
  do not govern California state-court trials at all — the premise of the
  "uniformity" argument is legally mistaken. The Sixth Amendment
  Confrontation Clause claim fails at the threshold because this is a civil
  case (the petition itself concedes the Amendment "applies explicitly only
  in criminal cases"). What remains is a generic due-process complaint about
  evidence exclusion, which presents no question the Court has left open.
- **Vehicle defects throughout.** Unpublished intermediate state-court
  opinion; discretionary review denied without comment below; underlying
  claims turn on California Government Code §§ 835/835.2 and state evidence
  law (independent and adequate state grounds for most of the rulings);
  the QP is not framed as a certworthy legal question.
- **Pro se drafting signals.** The petition mislabels the state Court of
  Appeal as a "U.S. Court of Appeal," cites cases with garbled names and
  reporters ("AT&T Mobility v. Conception," "Muskopf v. Coming Hospital
  District" — attributed to the U.S. Supreme Court though it is a California
  case), and asks the Court to reweigh witness credibility. None of this is
  disqualifying by itself, but it marks the petition as a member of the
  large class of pro se error-correction petitions that are denied
  essentially without exception.
- **No respondent engagement.** The docket shows no brief in opposition
  (response was due June 1, 2026) and the case was distributed for
  conference anyway — consistent with a waiver by the City and no call for
  a response, the standard posture of a petition headed for a one-line
  denial. No amicus support, no CVSG plausibility.

## Base rates

The corpus statpack puts the resolved-SCOTUS grant rate at 1.4% (296
resolved), and the prompt notes the modern discretionary-cert grant rate is
a few percent of *all* petitions — but that pool is dominated by
counseled petitions raising genuine splits. Paid pro se petitions from
state-court civil judgments are granted at a rate conventionally estimated
well below 0.1%. A `fedcourts query` over 2020s-era resolved SCOTUS priors
returned ten cases: the sole grant was a counseled, SG-opposed immigration
case (Montoya Palacios, 25-1223); every pro se petition in the sample —
including a closely analogous pro se state-court civil petition (Kama v.
Greenridge Place Apartments, 25-1222) — was denied at its first or second
conference.

## Calibration

Starting from a sub-0.1% base rate for pro se state-civil petitions, nothing
in this record moves the needle upward: no federal question the Court could
plausibly want, no split, no respondent, no amici, a long-conference
distribution. I set P(granted) = 0.002 rather than lower only to leave room
for tail events (a relist, an unexpected CVSG). The realistic alternative
dispositions are all forms of denial; outright dismissal is unlikely since
the petition was accepted, docketed, and distributed. **Predicted
disposition: denied**, most likely in the order list following the
September 28, 2026 conference (October 2026).

No outcome for this case was known to me or encountered during retrieval;
the case is pending (`forward` mode) and the snapshot is current as of
today (2026-07-10).
