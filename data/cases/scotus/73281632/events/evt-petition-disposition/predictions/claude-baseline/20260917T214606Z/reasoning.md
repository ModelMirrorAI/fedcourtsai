# Rationale for P(grant) = 0.07

## What I read

Provisioned inputs: `record/snapshots/2026-09-17.json` (the baseline; docket through the July 22 distribution for the 9/28 conference), `record/context.json` (mode `forward`, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, Term 2025), `questions-presented.txt`, the full `brief-in-opposition.txt` (14 pages, text intact), and the front matter, introduction, Reasons for Granting, and importance sections of `petition.txt` (117 pages, `truncated: true` per `documents.json`; the truncation falls in the appendix, so the argument was fully available). No merits briefs and no amicus filings appear on the docket.

Beyond the record I used the committed `metrics/statpack.md`, one corpus prior query, and four CourtListener MCP calls (listed in `retrieval.md`) to check for companion petitions and to read the Ninth Circuit panel opinion's opening pages. None surfaced this case's disposition; the petition is pending for the September 28 conference.

## Anchor

Context gives band `elevated` under `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" heading, so the band table is a valid anchor. Pooling the bracketed `reached` figure for `elevated` over the eight rendered Terms strictly before OT2025 (2017 through 2024) gives 484.4 / 2810 ≈ **17.2%** (grant family, denial-reweighted). That is the yardstick the evaluator scores against. For shape only: the relist-count cut shows relist-0 petitions at about 1.7% grant family and relist-1 at about 13%; the CVSG cut is irrelevant here because the SG is the respondent; the Ninth Circuit's modern rate is about 3.2% grant family, unremarkable.

## Adjustments from the anchor, and why I land well below it

I moved from 17% down to 7%. The reasons, in order of weight:

1. **The BIO says the theory is foreclosed, and I think it is right.** *CFPB v. CFSA* (2024) held that "an identified source and purpose are all that is required for a valid appropriation," and the SG quotes the Alito dissent conceding the majority imposes no upper-limit requirement. *FCC v. Consumers' Research* (2025) rejected the numeric-cap version of the nondelegation argument for a fee-funded program. The petition's "conflict with CFPB" is built from the majority's descriptive references to the CFPB cap and from the two dissents. A petition asking the Court to revisit a 7-2 and a 6-3 decision from the last two Terms, on a private investor's docket, is a hard sell for four votes; at most three Justices have shown sympathy for the cap theory.
2. **No split, and no other circuit has addressed it.** The petition invokes Rule 10(c) only. The SG notes that petitioners do not claim a conflict or even that another court of appeals has reached the question.
3. **Vehicle problems the SG preserved.** Standing (the panel rejected the argument, but the SG renews it and the Court would have to resolve it first), a claim-preclusion defense from petitioners' lost state-court quiet-title suits, and QP 2 mentioned in one sentence below and not addressed by the panel. Any one of these is a reason to wait for a cleaner vehicle, and the FHFA funding question will recur in other litigation if the Court wants it.
4. **Petitioner class and stakes signals.** The petitioners are Nevada HOA-foreclosure-sale investor trusts, a litigant genre the Court has repeatedly denied; counsel is a Las Vegas firm rather than a repeat Supreme Court advocate; and a petition proclaiming "exceptional importance" drew zero amicus briefs. The panel was unanimous and published, with no separate writing.

The one strong positive is that the Court **requested a response after the SG waived** (May 5). That is an affirmative signal that at least one chamber found the petition worth a look, and it is presumably what placed the petition in `elevated`. I weight it as roughly what keeps the number above the relist-0 floor rather than at it: response requests on colorable constitutional claims are common and most still end in denial once the SG answers, and here the SG's answer is short, direct, and grounded in two fresh precedents.

Netting these, 0.07 reflects a petition that is materially weaker than the typical `elevated` petition on the merits and the vehicle, but that carries one genuine attention signal and a subject a few Justices care about.

## The other claims

- **relist-increment 0.30.** The snapshot shows two distributions, but the first was displaced by the response request, so the petition has never been considered and relisted. From the long conference, most paid petitions are decided at once; I add for the response request and for the chance a Justice holds it to consider a statement, and subtract for the weak vehicle.
- **cvsg-increment 0.01.** Structurally near-impossible: the SG already represents the respondents.
- **summary-disposition-route 0.05.** Conditional on a grant, plenary review is the only realistic route; there is no intervening decision to GVR against.
- **dissent-from-denial 0.10.** Conditional on denial. Gorsuch or Alito might write on the Appropriations Clause, but they lost this argument recently and the vehicle is poor.
- **big_case_score 0.5.** If decided, invalidating or seriously questioning FHFA's funding would be a major separation-of-powers ruling with market consequences; but the realistic decided outcome is an affirmance restating *CFSA*, and a denial is a non-event.

## Uncertainties and where to discount me

- I did not read the Ninth Circuit opinion past its summary and background sections, nor the reply brief, nor the district court order. If the reply materially answers the standing and preclusion points, I have understated the vehicle.
- The `elevated` band's reached rate is a population anchor; I do not know how much of that population consists of response-requested petitions specifically, so the size of my downward adjustment rests on judgment about this petition rather than on a published conditional cut.
- `distribution_count` 2 in context counts the pre-response distribution; under the statpack's own caveat the stored count is an upper bound on true relists. My relist claim is stated from the two-distribution state the harness froze, as the contract requires.
- The corpus `query` surface has no topical filter, so the one prior query I ran returned recent grants and stay applications unrelated to this subject and did not inform the number.
