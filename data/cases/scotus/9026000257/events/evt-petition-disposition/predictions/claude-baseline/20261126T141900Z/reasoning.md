# Reasoning: P(grant) = 0.40

## What I read
- Snapshot `2026-11-26.json`: paid petition, CA5 en banc, docketed Aug. 27, 2026; BIO Nov. 10; reply Nov. 20; distributed once for the Dec. 11, 2026 conference. Three cert-stage amicus briefs (Storslee/Laycock et al. on Sept. 28; Foundation for Moral Law and Barclay et al. on Nov. 10, the BIO's due date, which suggests those two support respondents; I did not read them).
- `questions-presented.txt`, the petition's reasons for granting, the BIO and the reply. The petition's appendix was cut at the text cap, so I did not read the en banc opinions themselves; `decision-below.txt` was not staged and `lower-court-docket.txt` records no panel or opinion. My account of the decision below (9–8 en banc, Judge Duncan writing, *Stone* held abrogated with *Lemon*, free-exercise claim rejected under *Mahmoud*) comes from the parties' briefs, which agree on it.
- `context.json`: band `baseline` (sal-v9), `cert_anchor.rate` 0.052, `cert_amicus_line.rate` 0.163 (`some` arm, n=2318). `same-question.json` lists no matching petitions.
- Statpack: relist-count and amicus-count cuts (paid scored segment). Amicus bucket 2+: granted 18.2% + gvr 4.5% (n=1459 resolved).
- Corpus lookup and the Court's docket page for No. 25-1360 (*Brumley v. Roake*), Louisiana's conditional petition from the companion en banc ruling. This docket's `Links` field names only the extension application, so *Roake* is not a `Vide` link; I found it through the petition and BIO.

## Why well above the anchor
The band anchor (5%) and the amicus line (16%) describe ordinary paid petitions. This one is far from ordinary:
1. A court of appeals sitting en banc, 9–8, held that a Supreme Court decision squarely on point (*Stone v. Graham*) is no longer good law. The BIO does not really dispute that *Stone* is on all fours; it argues *Stone* fell with *Lemon* and, in the alternative, asks the Court to overrule it. That is a concession the reply uses well, and lower courts overruling the Court by implication is something several Justices have objected to on institutional grounds.
2. The stakes are national: about 5.5 million Texas students, a parallel Louisiana law, and similar statutes in Arkansas and other States.
3. The Court has already shown interest in the companion. In *Roake* it called for a response after a waiver (July 28, 2026), and that petition was rescheduled off the Dec. 4 conference and redistributed for Dec. 11, the same conference as this one. That reads as deliberate pairing. It is evidence of attention, not of votes.

## Why not above 50%
1. No circuit split. The Fifth Circuit is the only court of appeals to rule after *Kennedy*. The Eighth Circuit argued the Arkansas case on Sept. 22, 2026; my one web search found no decision. The Court can wait a few months for it at little cost.
2. The vote arithmetic is awkward. The Justices likeliest to agree with the Fifth Circuit have no need to grant in order to preserve a result they like. The three Justices likeliest to disagree may prefer not to hand the majority a vehicle to overrule *Stone* nationally. That leaves the grant depending on some mix of Roberts, Kavanaugh and Barrett caring enough about vertical stare decisis, or on the conservative wing wanting to settle the question affirmatively.
3. Vehicle. The BIO says the incoming Texas Attorney General has said he will not defend S.B. 10, which threatens adversarial presentation. The reply answers that the respondents are school districts that can hire counsel and that the Court can appoint an amicus. I think this is a real but curable problem; it more likely delays than defeats review. The challenge is also facial and pre-enforcement, on appeal from a preliminary injunction (though the Fifth Circuit rendered judgment of dismissal, so it is effectively final).
4. The petition's lead request, summary reversal or GVR to apply *Stone*, is not something I can see a majority of this Court ordering.

Weighing these, I land at 0.40 for any grant on this petition. The single largest swing factor is the Eighth Circuit: a ruling for the Arkansas plaintiffs while this petition is pending would push me to roughly 0.75; a ruling for Arkansas would push me down toward 0.25.

## The other claims
- `relist-increment` 0.72. Grants at this Court are almost always preceded by a relist, and a denial here would likely carry a writing that takes time. A first-conference clean denial is the main way this resolves false.
- `cvsg-increment` 0.03. No federal party or federal statute.
- `summary-disposition-route` 0.15 given a grant. The petition asks for it, and a narrow per curiam vacatur on vertical stare decisis is conceivable, but I doubt the votes.
- `dissent-from-denial` 0.60 given a denial. A denial leaves a ruling that *Stone* is dead in place; I expect at least one of the three Justices appointed by Democratic presidents to say so in writing, though a strategic silence is possible.
- `order-writers`: Sotomayor 0.30 and Jackson 0.24 are consistent with a 0.6 chance of denial times a 0.6 chance of a writing, split between them with some overlap; the rest are small numbers for a statement from the other side or a concurrence.

## Where to discount me
- I did not read the en banc opinions or the amicus briefs.
- The reading of the *Roake* reschedule as pairing is an inference from dates.
- My vote arithmetic is judgement, not data. The base rates say 5–16%; I am far above them on case-specific grounds, and a reader who trusts the anchor more should shade down.
- I carry no knowledge of this petition's outcome, and nothing I retrieved claimed one. No one else's forecast of this case surfaced.
