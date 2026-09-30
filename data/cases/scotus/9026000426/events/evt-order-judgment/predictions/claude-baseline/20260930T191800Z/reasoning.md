# Rationale for P(disturbed) = 0.87, judgment = reversed

**Cell posture.** Forward-mode merits cell at `moment: grant`
(`evt-order-judgment`, opened 2026-09-29, the grant date). Snapshot read:
`record/snapshots/2026-09-29.json` (cut kind `date`, cutoff 2026-09-30, so it
carries the docket through the grant order itself). `context.json` carries
`band: federal` under sal-v4; that is the cert petition's construct and I
did not anchor on it, per the stage rule. The only provisioned document is
`application.txt`, the Government's 45-page stay application, which the
Court treated as the petition; there is no QP file, petition, or BIO because
none existed (see `flags.json`). No merits brief was on disk, as the moment
requires.

**The committed baseline.** The statpack's "The merits docket (granted
cases)" section publishes an `excluded` count, so it is quotable. The grant
date 2026-09-29 falls in **OT2025** under the tree's October-pivot Term
rule (a late-September grant lands in the outgoing Term's row). Pooling
`disturbed` over `parsed` across the ten grant Terms strictly before
(2015–2024; the table renders 2017–2024, Terms with no parsed judgment being
omitted): 360 / 516 = **69.8%**, far above the 30-parsed floor. That is the
rate my skill is scored against. Coverage: the nearest pooled Term (2024) is
well parsed (73 of 75 granted), so pendency censoring in this pool is mild;
the 2025 row (24 of 50 parsed) is outside the pool.

**Why I sit 17 points above the baseline.** Every strong signal points the
same way, and they compound:

1. **The Court has already found likelihood of success, twice, in this
   case.** A stay under Hollingsworth requires a fair prospect of reversal.
   Six Justices granted the stay of the preliminary injunction in June 2025
   (24A1153) and the same six granted this stay on 2026-09-29, treated the
   application as a petition, and granted it 40 minutes after the reply. The
   posture differs (final judgment, statutory grounds added), but the
   Government's brief argues the new grounds are weaker than the old, and a
   majority evidently agreed enough to act within five days.
2. **The Court framed the questions itself and added "such other questions
   that the Government determines are appropriate."** That is an unusual,
   one-sided invitation, and with the December expedition it signals a
   Court that intends to settle the policy's lawfulness rather than look for
   an off-ramp.
3. **Respondents must run the table.** To keep the judgment standing they
   must win (a) jurisdiction under 1252(g), (b)(9), and (a)(4)/FARRA,
   (b) the reserved 1252(f)(1) question for both classwide declaratory relief
   and universal vacatur, and (c) the merits under 1231(b)(3), FARRA/CAT, and
   due process. The Government needs one. On (b), Aleman Gonzalez read
   "restrain" broadly and the Court flagged the declaratory-relief question
   as open; on (c), 1231(h) and the lower courts' own admission that they read
   1231(b) "to mean more than what it plainly says" are the Government's best
   lines, and Munaf/Kiyemba (Kavanaugh concurring) supply the assurances
   deference. Any partial win is still "disturbed."
4. **The Solicitor General as petitioner after emergency-docket relief.** In
   this Court, a Government stay followed by plenary review has almost always
   ended in reversal (Trump v. Hawaii, Biden v. Texas after the denial
   ran the other way); Allen v. Milligan (stay, then affirmance) is the
   notable counterexample and caps how confident I can be.

**Why not higher.** (i) The First Circuit's unanimous opinion (Aframe, J.)
is careful, rests on statute rather than the due process theory the 2025
stay implicitly doubted, and the panel trimmed the sequencing declarations
for lack of standing, leaving a cleaner judgment. (ii) The 1252(f)(1)
textual argument for respondents is genuinely strong (caption; 1252(e)(1)(A)
contrast; AADC's "nothing more or less than a limit on injunctive relief";
Biden v. Texas proceeding on declaratory relief), and Barrett and Gorsuch
take text seriously, so the remedy route may not carry six. (iii) The SG's
own concession at the Riley v. Bondi argument that notice and an opportunity
to raise a fear are required before a third-country removal will be quoted
back at the Government; the Guidance's non-assurance track does provide
both, so the fight narrows to blanket assurances and the 24-hour window,
which makes an affirmance-in-part or a narrow remand more plausible than a
clean loss for respondents. (iv) An unexplained stay is not a merits
holding; respondents' brief lists cases the Court stayed and later affirmed.
Netting these, I land at 0.87 rather than the 0.92–0.95 the stay signals
alone would suggest.

**Judgment label.** "Reversed" is modal (Aleman Gonzalez-style remedy
holdings and merits holdings both read "reversed"); "vacated" is the label
if the Court stops at a jurisdictional holding and remands with
instructions; "affirmed in part" if some notice right survives. Roughly
0.55 / 0.25 / 0.07 of the disturbed mass, with the rest in odd forms. All
count as disturbed, so the label uncertainty does not move `probability`.

**Semantic claims.** I committed to the statutory-merits ground as the
majority's basis because the Court directed the lawfulness question
head-on and expedited; the 1252(f)(1) ground is my second most likely and
I named it as an additional holding. If the Court instead resolves only on
1252(f)(1) or only on jurisdiction, the `majority-ground` proposition is
wrong on its primary clause. Breadth: categorical, because a policy-level
ruling on a class judgment is the natural shape and QP4 invites it.

**Votes.** 6–3 along the stay lines. Alito as author and Sotomayor as
principal dissenter are guesses, stated because the block asks for them,
and unscored today.

**Claims coherence.** `judgment-disturbed` = 0.87 = top-level
`probability`; `granted` = 1 because "reversed" disturbs;
`predicted_disposition` = `other` per the merits contract.

**What I worked from.** The provisioned snapshot and application; the
committed statpack; and forward-mode retrieval: the First Circuit opinion
(CourtListener opinion 11444581, read in full), respondents' 2026-09-28
opposition to the stay (supremecourt.gov PDF, text extracted locally), one
commentary post on the grant order, and one corpus `query` that returned
recency-ranked rows of little use. I did not read the Government's reply to
the application. The `big_case_score` of 0.9 rests on the stakes: the
policy has been used for thousands of removals, the 1252(f)(1) remedy
question governs immigration class litigation generally, and the case has
been front-page news since 2025.

**Where to discount me.** My largest single input is the inference from two
emergency-docket stays to a merits outcome; if this Court treats the final
judgment's statutory grounds as genuinely new (as respondents urge), the
right number is nearer 0.75. I have no window into whether Roberts or
Barrett prefer a narrow remedy holding to a merits ruling, which is the
main risk to the semantic claims rather than to the number.
