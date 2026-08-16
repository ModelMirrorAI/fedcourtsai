# Rationale for my numbers

**P(disturbed) = 0.86, against a committed baseline of 0.697.**

**The anchor.** The committed statpack's "The merits docket (granted cases)"
section publishes an `excluded` count, so its rates are quotable. This event's
`opened_at` is 2026-06-30, so the grant Term is OT2025 and the pool is grant
Terms 2015–2024, strictly before mine; the pack holds parsed rows for
2017–2024. Pooling `disturbed` over `parsed` across those eight Terms:
(50+34+49+46+57+42+50+31) / (73+55+72+65+69+54+75+52) = 359/515 = **69.7%**,
well past the 30-parsed floor. That is the baseline my Brier skill is scored
against. Coverage caveat quoted with it: the nearest Terms are the most
censored (OT2024 shows 73 parsed of 75 granted but 34 excluded; the parsed
slice skews toward quicker dispositions), so the pooled figure leans on the
older, more complete Terms.

**Adjustments up from 69.7% to 0.86:**

1. *Posture of the grant.* The BIO is correct that no circuit split favors
   petitioners — every circuit to decide has upheld assault-weapons bans
   (*Bevis* CA7, *Bianchi* CA4 en banc, *Capen* CA1, *NAGR v. Lamont* CA2).
   A grant over uniform circuit agreement is the classic
   reverse-the-consensus posture; the Court rarely takes a case in that
   shape to affirm.
2. *The Court's own signaling.* The Seventh Circuit affirmed summarily the
   same day certiorari was denied in *Snope v. Brown* (the petition recounts
   this), where the accompanying signals were that the question was being
   deferred, not declined on the merits. The Court then held this petition
   through twenty-two distributions and granted, consolidating it with the
   Second Circuit's Connecticut case and limiting 25-566 to this petition's
   QP — deliberate vehicle assembly to decide the AR-15 question nationally.
3. *Revealed doctrinal direction.* The majority's Second Amendment line
   (*Heller* common-use, *McDonald*, *Caetano*, *Bruen*) has disturbed
   pro-regulation judgments each time it reached one, and the *Bevis*
   "militaristic arms" textual carve-out sits awkwardly with *Heller*'s
   definition of "Arms" and *Caetano*'s treatment of common use. At least
   four sitting Justices have signaled skepticism of AWB constitutionality;
   the affirm path needs two of Roberts, Kavanaugh, and Barrett to break
   against their records.

**Adjustments holding me back from higher:** *Rahimi* and *VanDerStok* show
this Court willing to rule for the government in firearms cases when the
challenger's theory overreaches; the respondents' vehicle attack (expert
disclosure and summary-judgment record defects below) gives a DIG a real if
small foothold; and an affirmance theory that common use is necessary but not
sufficient exists in the academy and among some judges. I put affirmance ~8%,
DIG ~4%, equally divided ~1% — hence 0.86, a deliberate but bounded claim of
skill over the 69.7% base.

**Judgment label and votes.** `reversed` over `vacated` because the QP is
categorical and the record posture is final judgment after summary judgment —
the *Bruen* shape, which produced outright reversal — though I hold ~a
quarter of the disturbed mass on a framework-only vacatur. The 6–3 lineup
follows the *Bruen* bloc plus the three *Bruen* dissenters' successors in
interest; `confidence` 0.72 reflects that the lineup is firmer than the
authorship guesses riding on it. The vote block is banked, not scored, today;
I wrote it as if it graded.

**What I worked from.** This is a `forward` cell six weeks after the grant:
no merits brief exists yet (petitioners' is due 2026-08-28 per the extension
order on the docket), so there was no merits advocacy to retrieve — this
forecast is made from the docket skeleton plus the provisioned cert-stage
documents (petition, BIO, QP text, all with clean text; `documents.json`
shows no `empty_text`). The salience band in my context (`high`) is a
cert-stage construct whose question is settled; I did not anchor on it. My
one corpus `query` (citation lookup of the modern Second Amendment merits
line) returned nothing — the citation column covers only 161 of 590k SCOTUS
rows, a coverage gap, not absent precedent — so precedent context comes from
general legal knowledge, not corpus rows.

**Where to discount me.** The gap between 0.697 and 0.86 rests on a
qualitative read of grant posture and Justice-level signals, not on a
published conditional cut (the pack has no per-issue-area or
grant-over-consensus rate). If the consolidated argument surfaces a
standing or record problem that argument cannot cure, the DIG mass is
underweighted here.
