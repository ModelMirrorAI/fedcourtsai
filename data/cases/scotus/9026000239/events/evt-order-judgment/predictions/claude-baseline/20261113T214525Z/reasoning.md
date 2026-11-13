# Reasoning — scotus/9026000239, evt-order-judgment (merits, moment: grant)

**Call:** P(judgment below disturbed) = 0.83; predicted judgment `reversed`; predicted lineup 6–3.

## What I worked from

- Snapshot `2026-11-13.json`: paid petition by the Solicitor General (No. 26-239), four cert-stage amicus briefs supporting the government (including Iowa and 21 other States), brief in opposition 23 Sep 2026, reply 6 Oct 2026, distributed for the 6 Nov and 13 Nov conferences, and on 13 Nov 2026 "Petition GRANTED limited to Questions 1 and 2".
- Provisioned documents: `questions-presented.txt`, `petition.txt` (body read in full; appendix not read), `brief-in-opposition.txt` (introduction and the §1252(f)(1) section), `cert-reply.txt` (first half), `lower-court-docket.txt`. I did not read `decision-below.txt` directly; my account of the D.C. Circuit's reasoning comes from the two sides' descriptions of it, which agree on the essentials.
- No merits briefs or argument exist yet, and none was on disk. This is a forecast on the cert-stage papers and the docket.
- The cert band in `context.json` (`federal`) is not used: it prices a grant that has already happened.

## Base rate

Statpack "The merits docket (granted cases)" section, which publishes an `excluded` count. Grant Term is OT2026 (grant order dated 13 Nov 2026). Pooling the grant Terms the table shows before it (OT2017–OT2025; the ten-Term window would also admit OT2016, which the table does not carry): 395 disturbed of 560 parsed = **70.5%**. Coverage: 560 parsed of 612 granted; OT2025 is the thinnest row (26 parsed of 53 granted) and the most censored.

## Adjustments up from 70.5%

1. **Petitioner is the United States, on a flagship policy, with no circuit split.** The Court took the case because the lower courts set aside a presidential border proclamation, not to resolve a conflict. Grants of that kind lean toward reversal more than the average grant.
2. **Two independent routes to disturbing the judgment.** The grant covers both the legality of the proclamation (Q1) and whether 8 U.S.C. 1252(f)(1) bars the classwide injunction (Q2). A government win on either changes the judgment. Even a Court unpersuaded on asylum could vacate the injunction under *Garland v. Aleman Gonzalez*, where the government's "either the removal provisions apply or they don't" argument has real force.
3. **Lower-court judges split in the government's favour on asylum.** Per the petition, the stay panel (Millett, Katsas, with Pillard dissenting) stayed the asylum portion of the injunction, and Judge Walker dissented from the merits panel on asylum, class scope and §1252(f)(1). The "categorical pre-denial makes applications futile" theory has therefore already persuaded judges across the usual lines.
4. **Recent direction of the Court in this area.** *Mullin v. Al Otro Lado* (decided 25 June 2026; retrieved via CourtListener) reversed the Ninth Circuit 6–3 on a neighbouring asylum-access question, Alito writing, Sotomayor, Kagan and Jackson dissenting. It predates my snapshot and is general context, not information about this case's outcome.

## Adjustments down

1. **The respondents' textual case is serious.** Section 1158(a)(1) says any alien physically present "may apply" for asylum "whether or not at a designated port of arrival"; §1158(b)(2)(C) lets the Attorney General add limits "by regulation" and "consistent with" the section. A proclamation that pre-denies everyone looks like an eligibility bar adopted outside that channel. The brief in opposition also invokes decades of contrary executive-branch positions and *Learning Resources, Inc. v. Trump* (2026), where the Court ruled against a broad presidential reading of a statute. Roberts, Gorsuch or Barrett could be drawn to that.
2. **The government has narrowed its own defence.** The brief in opposition says the government no longer defends the elimination of withholding or the CAT restrictions. So a full, clean reversal of everything is not on offer; the question is whether *anything* is disturbed, which is what the probability measures.
3. **Limiting the grant to Q1 and Q2** drops the class-definition question, removing one of the government's three routes.

Net: 0.83. I would not go above roughly 0.88 without merits briefing; the statutory text is a real obstacle, and the Court has shown this year that it will rule against the President on statutory-authority questions.

## Judgment label

`reversed` is my single most likely label (about 0.45), with `vacated` (about 0.2) and `affirmed-in-part-reversed-in-part` (about 0.18) splitting the rest of the disturbed mass, `affirmed` about 0.15, and a DIG or an equally divided Court about 0.02 together. The mixed label is a real risk because the withholding and CAT rulings are effectively unchallenged, but the Court usually writes "reversed and remanded" when it reverses on the questions it took, so I kept the plain label.

## Votes

Statpack per-Justice section, Terms before the grant Term (OT2025 and earlier), shows disturb rates clustered between about 51% and 75% for every Justice, so it does not separate them; I used it only as a check that no Justice is a reflexive affirmer. The lineup rests on the subject matter: the six-Justice majority in *Al Otro Lado* and in the Court's other recent immigration-enforcement cases, with Sotomayor, Kagan and Jackson in dissent. Least certain votes: Barrett and Gorsuch (textual objections on Q1), and Kagan (could join a narrow §1252(f)(1) holding). Chance the exact 6–3 lineup is right: about 0.4.

## Authorship

Majority author: I moved off the flat historical shares toward Roberts (he wrote *Trump v. Hawaii*, the leading §1182(f) case, and tends to keep major presidential-power cases), with Alito (*Aleman Gonzalez*, *Al Otro Lado*), Kavanaugh and Barrett next. The argument sitting is unknown, so I kept the distribution wide. Separate writings: Sotomayor and Jackson as likely dissent authors (both wrote in *Al Otro Lado*), Thomas as a likely concurrence on inherent executive power.

## Where to discount me

- I did not read the D.C. Circuit opinion itself, only the parties' accounts of it.
- No merits briefs. The government's argument may shift, as it already did between the proclamation and the petition.
- The 0.83 leans on a judgment about ideological alignment that a statutory-text case can upset.

## Retrieval and conduct

Forward cell. Retrieval beyond the provisioned record was limited to corpus queries and a CourtListener lookup of *Mullin v. Al Otro Lado* (see `retrieval.md`). I did not look for any forecast of this case and none surfaced. I did not read any outcome file or another cell's output.
