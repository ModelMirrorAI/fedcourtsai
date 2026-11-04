# Reasoning — scotus/9026000589 (No. 26-589), arrival moment

**P(grant family) = 0.85.**

## What I had
- Snapshot `2026-11-05.json`: a single entry, "Petition for a writ of certiorari filed" on Nov 2, 2026 (response due Dec 4). Paid docket. The counsel of record is the Solicitor General (D. John Sauer). No distributions, no CVSG. That is what an arrival cell is supposed to look like.
- `context.json`: forward mode, band `federal` (sal-v6), `distribution_count` 0, and a `cert_anchor.rate` of **0.734** (the federal reached rate pooled over 10 prior Terms).
- `questions-presented.txt`: (1) whether the Tucker Act bars a district-court challenge to EPA's grant terminations; (2) whether a claim under the now-repealed Greenhouse Gas Reduction Fund statute (42 U.S.C. 7434) can support the injunction.
- `petition.txt` (truncated at the cap, appendix cut): I read the introduction, the statement and the table of contents and authorities. The petition says this is the same Tucker Act question that the Court's stays in *Department of Education v. California* and *NIH v. APHA* treated as likely certworthy. It claims a persistent lower-court divide, with the Fourth Circuit (*Sustainability Institute*) against the D.C. Circuit. It says $16B is at stake, and that respondents agreed to keep the administrative stay in place pending this Court's disposition. The petition's caption page reads "No. 24-101", which looks like a drafting leftover. The Court's docket number is 26-589.
- `decision-below.txt`: the D.C. Circuit's en banc per curiam judgment of Aug 4, 2026, which matches petition App. A. It affirms paragraph two of the PI 6-4, on the IRA §60103 ground. The rest of the PI is affirmed by an equally divided court (5-5, Henderson not participating). The Chief Judge joined the four votes to vacate because of the OBBBA repeal. `lower-court-docket.txt` reads no further rehearing petition, which is expected after an en banc judgment.
- `same-question.json`: an empty list, so nothing scored above the 0.5 threshold.

## Anchor and adjustments
I anchored on the federal floor/`cert_anchor` of 0.73. The federal column's Terms range from 48% to 96%, and their n values are modest (12–41).

Reasons I moved up:
- The SG is petitioning on a question the Court has already flagged twice on the emergency docket.
- The court below was a fractured en banc court with much of its judgment equally divided, which gives the Court no reasoned circuit precedent to defer to.
- A circuit conflict is claimed.
- The money at stake is very large, and the case is a template for many other grant-termination suits.
- The current Court has granted SG petitions in administrative-power cases at a high rate.
- Respondents' agreement to keep the stay in place shows that both sides expect the Court to act.

Reasons I discounted:
- The case is interlocutory: it reviews a preliminary injunction.
- QP2 involves a repealed statute, which could create vehicle or mootness complications.
- The corpus shows *Trump v. Thakur* (No. 26-210, CA9, also an SG grant-termination petition) distributed for the Nov 13, 2026 conference. If the Court takes Thakur, it might hold this petition and later GVR it. A GVR still counts in the grant family, so that path mostly lowers plenary review rather than the grant number. An outright denial after Thakur is decided is possible but unlikely given the $16B.

## Claims
- relist-increment 0.97: the petition will almost certainly be distributed at least once from zero.
- cvsg-increment 0.01: the SG is the petitioner.
- summary-disposition-route 0.20: this is mainly the hold-then-GVR path behind Thakur or another lead case.
- dissent-from-denial 0.55: if the Court denied a $16B SG petition, some Justice would likely write.

## Uncertainty
I have not seen the BIO, which is not yet filed. I also did not verify the claimed split beyond the petition's own description. The petition's opinion citations are as the petition gives them.
