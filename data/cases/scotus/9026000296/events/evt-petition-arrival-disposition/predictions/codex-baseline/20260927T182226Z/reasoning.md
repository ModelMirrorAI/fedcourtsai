# Rationale

## Record and conditioning

This is the cert-arrival event for Mike Singh Sethi, Supreme Court docket 26-296. I used `record/snapshots/2026-09-09.json`, the event definition, `record/context.json`, and the provisioned `documents/documents.json`, `questions-presented.txt`, and `petition.txt`. The snapshot is truncated at the September 9, 2026 date cutoff and records the September 1 petition filing, September 8 docketing, and an October 8 response deadline. Context specifies forward mode, Term 2026, sal-v4 baseline, zero distributions, and no CVSG. Those absent signals are normal at arrival, not adverse evidence about the Court's interest.

The document manifest describes the petition as 40 pages, untruncated, with nonempty extracted text. No brief in opposition or separately provisioned appendix is present. My account of the disciplinary orders and declaration therefore comes from the petition's descriptions and quotations, not an independent inspection of the complete underlying record. The absence of an opposition at this moment is not evidence of waiver or concession.

The petitioner is a private lawyer. Federal respondents and the Solicitor General's appearance do not turn him into a federal petitioner. I used the private caption-class floor, consistent with the frozen baseline band.

## Base rate and adjustment

The committed `metrics/statpack.md` sal-v4 table provides the appropriate arrival anchor: baseline's bracketed reached rates, not its terminal-band rates and not the terminal zero-relist bucket. Pooling every displayed prior Term, 2017 through 2025, gives approximately 5.01% on a weighted resolved denominator of 12,720. This calculation weights each rounded displayed percentage by its displayed denominator; it is approximate, not a reconstruction of unrounded grant counts. Term 2026 is excluded. The statpack is the committed copy available in this checkout; I did not refresh a corpus blob or establish its newest pull/snapshot timestamps, so these figures are not a claim about current remote-corpus freshness. The case-specific input vintage is September 9, 2026.

For context, the pack's modern-cert disposition table places the grant family at roughly 2.8% overall, and its Ninth Circuit cut is approximately 3.2%; those broader populations do not replace the private paid-arrival anchor. The paid-segment relist and CVSG cuts show substantially greater grant shares among repeatedly distributed and CVSG petitions. Those are terminal associations, not transition probabilities from this zero-distribution state. In particular, I did not use the terminal zero-relist rate of roughly 1.7% as the arrival prior or add a relist/CVSG premium before either signal exists.

I reduce the approximately 5% arrival anchor to **3% for any grant**. The case presents a genuine procedural concern, but the asserted conflict is principally an application of established notice principles to this disciplinary record rather than a well-aligned conflict on either question presented.

Factors supporting review:

- The first question is concretely linked to an existing Supreme Court notice precedent. The petition argues that the disciplinary response and later corrective filings became new grounds for suspension without supplemental charges (petition pp. 8–18). I independently checked the notice passages of *In re Ruffalo*, 390 U.S. 544, 550–552 (1968), through CourtListener opinion 107654. They support the general concern about charges emerging from a lawyer's defense; they do not establish that Sethi's record necessarily presents the same defect.
- The petition describes a published disciplinary decision, a six-month suspension, collateral reciprocal proceedings, and prospective firm-wide certification obligations (pp. 10–11, 22–25). Those features make the asserted problem more consequential than a minor monetary sanction.
- Question two isolates a potentially recurring boundary between ordinary candor duties and a specific requirement to disclose the technological source of erroneous citations (pp. 18–22). That supports modest institutional significance independently of grant likelihood.

Factors reducing review likelihood:

- The petition acknowledges defective verification and inaccurate authorities, an express show-cause notice warning of suspension or disbarment, and the failure to request a hearing on the original charges (pp. 3–8). These admissions make the vehicle less straightforward than a wholly unnotified disciplinary proceeding.
- Whether the later statements were genuinely new offenses, rather than evidence of ongoing dishonesty or aggravation of noticed conduct, requires close examination of the orders and record. Likewise, the claimed AI-source rule may be characterized as an application of existing candor duties rather than a freestanding new practice requirement. These are my anticipated counterarguments, not positions taken in an opposition I have read.
- The petition's discussion of differing disciplinary proof standards acknowledges that the cited authorities arise in different settings and do not constitute a perfectly aligned constitutional split (pp. 25–26). That issue also is not itself either question presented. I give it little cert weight.
- The publication and AI connection make the issue timely, but do not by themselves demonstrate that four Justices would choose this fact-intensive suspension dispute as the vehicle for a nationwide rule.

## Other probabilities and stakes

`relist-increment` is 0.97 because this arrival cell starts at zero distributions; an ordinary first distribution satisfies it. My modal procedural path is one initial distribution and no subsequent relist. `cvsg-increment` is 0.002 because the federal respondents already have the Solicitor General listed as counsel, and the identified questions do not obviously require a separate invitation for the government's views. These are judgmental forward probabilities, not estimates extracted from terminal signal buckets.

The 0.35 summary-route probability is conditional on a grant. The petition's reliance on existing notice precedent leaves room for summary correction, but disagreement about the scope of the original charges and the Rule 47(b) theory favors full briefing if the Court decides to intervene. No intervening decision supporting a routine GVR was identified. The 0.025 denial-writing probability is conditional on denial; the record does not supply a strong signal of a separate-writing campaign or a particular Justice's interest.

The significance score of 0.40 reflects the potential reach of a decision for federal discipline and AI-related correction practices, while recognizing the limited immediate subject: one lawyer's suspension. It is deliberately higher than the grant probability and is not a prediction that this will become a major constitutional merits case.

## Limitations and retrieval conduct

I did not retrieve this petition's current docket, disposition, subsequent history, or decision coverage, and I do not know its outcome. External retrieval was limited to general rules searches that returned no usable output and a historical Ruffalo precedent lookup. CourtListener's first citation-only search returned an unrelated case; I excluded it and used the named-case search and opinion-text excerpts instead. No individual corpus priors were queried. The largest substantive limitation is that the petition's characterization of the disciplinary record has not been tested against an opposition or the complete orders. The numerical forecast discounts that asymmetry rather than treating the petition's allegations as adjudicated facts.
