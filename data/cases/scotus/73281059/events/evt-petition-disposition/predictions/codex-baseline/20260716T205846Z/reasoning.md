# Prediction

I predict a plenary grant, with a 0.64 probability of any grant. The most likely grant-side disposition is `granted`, not a GVR: the petition presents unresolved statutory and structural questions rather than asking for reconsideration in light of an intervening authority.

## Questions and governing standard

The petition asks whether the National Voter Registration Act or a 2018 consent decree prevents Arizona from requiring documentary proof of citizenship and residence from applicants using Arizona's state form; whether the NVRA preempts Arizona's restriction on mail voting by federal-only registrants; and whether the Ninth Circuit properly disturbed the district court's finding that H.B. 2243 lacked discriminatory intent.

At the certiorari stage, the main considerations are whether the decision conflicts with Supreme Court precedent, presents an important recurring federal question, and offers a suitable vehicle. The petition relies especially on *Arizona v. Inter Tribal Council of Arizona, Inc.*, 570 U.S. 1 (2013), which described the Federal Form as a backstop while recognizing room for state-developed forms. The parties dispute whether that language permits Arizona's documentary requirements and whether the NVRA reaches post-registration voting methods.

## Record signals favoring review

The strongest signal is procedural. The July 16 snapshot records distribution for the June 18 conference and redistribution for the June 25 conference. That is one recorded relist. The snapshot still contains no terminal entry after the second conference, suggesting continued consideration across the summer, though I do not count the carry-over as an additional formal relist without another distribution entry. Historical statpack data put ordinary paid petitions at roughly a 5.4% grant rate in the 2025 Term, one-relist petitions at 7.6%, and two-relist petitions at 33.6%; this petition has unusually strong case-specific signals beyond those broad buckets.

Most important, the petition recounts that the Court previously stayed the injunction against Arizona's state-form proof-of-citizenship requirement, while three Justices would have granted broader relief covering the presidential- and mail-voting restrictions. The opposition identifies four Justices who would have denied all interim relief. Thus, the prior emergency ruling supplies evidence that a majority saw sufficient merit and urgency in at least the central proof-of-citizenship issue, and that at least three Justices were receptive to the broader claims. Four votes are needed for certiorari.

The case also drew eleven dissenting votes from denial of rehearing en banc. It concerns election administration, federalism, the reach of the NVRA, and the continuing force of a federal consent decree against later state legislation. Multiple related petitions and VIDED filings show that the Court can choose among or coordinate companion vehicles. Those features make the dispute nationally salient even without a circuit split.

## Counterweights

The respondents' opposition presents substantial vehicle objections. It characterizes the state-form and mail-voting rules as Arizona-specific, identifies no circuit conflict, and stresses that the discriminatory-intent claim was remanded. The consent-decree issue also carries a procedural complication: the legislative petitioners did not seek modification in the court that entered the decree. The third question is fact-bound, and the Ninth Circuit described its action as a remand for application of the ordinary *Arlington Heights* framework rather than a final finding of discriminatory intent.

There is also docket-specific uncertainty. The same lower-court litigation generated companion petitions, so the Court could grant a different petition and deny or hold this one. That possibility is the principal reason not to place the probability closer to the apparent strength of the underlying grant signal.

## Calibration and disposition

The committed statpack's modern discretionary-cert baseline is about 3% overall, about 5.4% for paid 2025-Term petitions, and 3% for petitions from the Ninth Circuit. Those unconditional rates are heavily outweighed here by the recorded relist, post-conference pendency, the earlier partial stay, the divided Ninth Circuit, and the coordinated companion cases. Balancing those signals against the interlocutory and vehicle objections yields 0.64 for any grant.

If review is granted, plenary treatment of one or more NVRA questions is more likely than summary reversal. I do not predict individual votes because certiorari votes ordinarily are not disclosed and the public emergency-order alignment does not map cleanly onto the final choice among companion petitions.

## Inputs and retrieval limitations

I used the July 16 docket snapshot, `questions-presented.txt`, the petition, and the provisioned brief in opposition. The opposition PDF was marked truncated in `documents.json`, but its complete merits-and-certiorari argument through the conclusion was present; truncation affected the lengthy appended trial material and did not prevent evaluation of the opposition's principal arguments.

The ranged corpus-prior lookup failed before returning a row or read-count line because the remote endpoint could not resolve. I therefore used the committed statpack for calibration and the provisioned filings for case-specific analysis. CourtListener MCP search confirmed the *Inter Tribal Council* citation but did not add outcome information about this petition.
