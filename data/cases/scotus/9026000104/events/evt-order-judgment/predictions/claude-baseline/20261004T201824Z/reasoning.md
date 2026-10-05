# Why 0.55, and why `reversed`

## What I worked from

- The provisioned snapshot `record/snapshots/2026-10-02.json` (docket No.
  26-104, nine docket entries, petition granted October 1, 2026 at the
  September 28 conference, first distribution). `record/context.json`: mode
  `forward`, cutoff 2026-10-02, cut kind `date`, band `federal` (which I did
  not use, per the merits-stage rule), term 2026.
- **No provisioned documents.** There is no `record/documents/` directory and
  no `documents.json`, so no QP, petition, or BIO text came with the cell. This
  is a forward cell, so I retrieved the questions presented from the Court's
  QP page, the government's petition (with the Second Circuit opinion appended)
  from justice.gov, and the Second Circuit's September 25, 2026 order denying
  rehearing en banc with its separate opinions from the Second Circuit's site.
  No merits brief exists yet, so none was read; this is a `moment: grant` cell
  and the forecast is from the cert-stage record plus the opinions below.
- I did not read any `outcome.json`, anything under `data/qp-topics/`, or the
  cert-stage predictions already committed on this docket.

## The case

The question presented is whether § 1225(b)(2)(A) mandates detention pending
removal proceedings of noncitizens who are present in the United States
without having been admitted. The respondent is a Brazilian national who
entered without inspection around 2005, has an asylum application pending
since 2016 with work authorization, owns a home and a business in
Massachusetts, has no criminal record, and was arrested at a traffic stop in
September 2025 after ICE's July 2025 guidance reclassified all such
noncitizens as subject to mandatory detention. The district court granted
habeas; the Second Circuit (Bianco, J., joined by Cabranes and Nathan, with a
Cabranes concurrence) affirmed in a 68-page opinion holding that § 1226(a)
governs because the respondent is not "seeking admission." Rehearing en banc
was denied on September 25 with a six-judge concurrence (Bianco and Nathan,
joined by Lee, Robinson, Pérez, Merriam), a two-judge concurrence (Schwartz,
joined by Sullivan) that agreed with the dissent's statutory analysis but
voted to deny because Supreme Court review was inevitable, a dissent by
Menashi joined in part by Park, and a Cabranes statement.

The circuit split, as of Menashi's September 25 dissent: the Fifth
(Buenrostro-Mendez, 2-1, Douglas dissenting) and Eighth (Avila) Circuits read
the statute the government's way; the First, Second, Third, Sixth (over a
Murphy dissent), Seventh, Ninth, Tenth, and Eleventh Circuits read it the
respondent's way.

A fact that shaped the forecast: the government filed this as a **hold
petition**. Its petition asked the Court to hold No. 26-104 pending Raycraft
(now Putra) v. Lopez-Campos, No. 25-1415, from the Sixth Circuit, which it
called the better vehicle because it also squarely presents the due process
question. All three petitions (25-1415, 26-43, 26-104) were distributed for
the September 28 conference, and respondents' counsel filed letters in each on
September 14 and 25. The October 1 order granted only No. 26-104. The Court
therefore chose, over the Solicitor General's stated preference, the vehicle
that presents the statutory question alone.

## Anchor

The committed statpack's "The merits docket (granted cases)" section publishes
an `excluded` count (66), so it is quotable. This case's grant Term is OT2026
(grant date October 1, 2026, from `opened_at`), so the pool is grant Terms
2016 through 2025. The table renders Terms 2017 through 2025 (2016 holds no
parsed judgment and is omitted). Pooling `disturbed` over `parsed` across those
nine rows: 377 / 540 = **69.8%**, which clears the 30-judgment floor. The
nearest Term (2025: 24 parsed of 50 granted) is heavily censored, as the pack
warns; the pool is dominated by fully-resolved Terms. The pack-level figure
happens to coincide because the pack holds no other Terms.

## Adjustments

Starting from roughly 0.70, I moved **down** to 0.55 for these reasons:

1. **The respondent's textual case is unusually strong for the side that won
   below.** "Seeking admission" is a present participle that the deemed
   status does not obviously satisfy; the government's reading makes the
   phrase surplusage; § 1226(a) reaches "an alien" pending a removal decision
   without limitation to admitted aliens; and the Laken Riley Act of 2025
   added mandatory-detention categories to § 1226(c) for inadmissible
   noncitizens, which presupposes that such noncitizens otherwise sit in
   § 1226(a). Executive practice was uniform for thirty years under five
   administrations, announced in the 1997 regulatory preamble. These are the
   arguments that moved Justices Gorsuch and Barrett in Niz-Chavez.
2. **Eight of ten circuits**, with panels including many Republican
   appointees (the Second Circuit opinion was written by a Trump appointee),
   have rejected the government's reading. The split's lopsidedness does not
   predict the Court's answer well, but it does mean the government's reading
   has lost nearly every time an Article III court has examined it de novo.
3. **The Court picked the statutory-only vehicle** over the government's
   preferred case. That is consistent with wanting to decide only the statute,
   which is slightly more natural if the Court expects to affirm (the
   constitutional question then never arises) than if it expects to reverse
   (the due process question would then flood the lower courts, which the
   government itself warned about). I weight this modestly; vehicle choice
   also reflects that the respondent did not oppose review and that the
   Second Circuit record is a clean single-petitioner habeas case.
4. **Stakes.** The government's reading mandates detention of a population in
   the millions. The Chief Justice and Justice Kavanaugh are not immune to the
   "no one noticed for thirty years" argument.

I moved **up** from where those considerations alone would leave me (around
0.45) for these reasons:

1. **The Court's record in detention-statute cases** heavily favors the
   government: Demore, Jennings, Preap, Thuraissigiam, Guzman Chavez,
   Arteaga-Martinez, Aleman Gonzalez. Jennings in particular called
   § 1225(b)(2) "a catchall provision that applies to all applicants for
   admission not covered by § 1225(b)(1)," which the government will quote on
   every page, and the Second Circuit had to treat it as dicta.
2. **The deeming clause** is a real textual argument, not a purposivist one.
   Congress said such noncitizens "shall be deemed for purposes of this
   chapter an applicant for admission," and a textualist can read "an alien
   seeking admission" as describing that same person. The 1996 Act's stated
   aim was to eliminate the advantage of entering without inspection.
3. **Grant-to-reverse and the Solicitor General as petitioner.** The Court
   granted the government's petition rather than the noncitizens' petition
   from the Fifth Circuit (No. 26-43), which would have been the natural
   vehicle for a Court inclined to affirm the majority view. The SG's reversal
   rate as petitioner runs above the general argued-case rate.
4. **Disturbed-without-a-government-win routes.** Mootness is live: the
   respondent is released on bond with an asylum application pending since
   2016; if his proceedings terminate or asylum is granted before June 2027,
   the likely result is a Munsingwear vacatur, which counts as disturbed. I put
   this and other non-merits vacatur paths at roughly 0.04 combined. A DIG
   (undisturbed) I put at about 0.02.

Net: P(disturbed) = 0.55. P(government wins on the merits) is about 0.51 of
that; the remainder is the vacatur paths.

## Votes

The vote block is my best guess at the modal 5-4 lineup, not a confident call.
Thomas and Alito for the government and Sotomayor, Kagan, and Jackson for the
respondent are each near-certain. Roberts and Kavanaugh lean government (both
joined the Niz-Chavez dissent and the Jennings and Preap majorities). Gorsuch
and Barrett are the swing votes; I split them, placing Barrett in the majority
and Gorsuch in dissent, because Gorsuch has more often broken with the
conservative bloc on textual grounds in immigration cases (Dimaya, Davis,
Niz-Chavez). I would not be surprised by 6-3 either way. Writing roles are
stated only for Alito (majority author, by subject-matter history) and
Sotomayor (principal dissent); the rest are left unstated.

## Where to discount me

- The forecast rests on the docket skeleton, the petition, the opinion below,
  and the en banc separate opinions. I did not read the brief in opposition
  (the respondent acquiesced in review) and there are no merits briefs yet.
- I have no information about Court composition changes after mid-2026; the
  lineup assumes the nine Justices sitting in June 2026.
- The salience band in `context.json` is `federal`; I did not use it, per the
  stage rule.
- The semantic claims are written on the reversal branch to match the
  judgment. If the Court affirms, both will grade poorly by construction.
- `big_case_score` 0.92 reflects stakes only: the policy governs detention of
  every noncitizen present without admission and has produced thousands of
  habeas petitions; it is the Term's leading immigration case regardless of
  how it comes out.
