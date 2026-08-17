# Reasoning — why P(disturbed) = 0.93

**Cell and inputs.** Forward-mode merits cell at `moment: grant`
(evt-order-judgment), opened on the June 22, 2026 cert grant in Nielsen v.
Watanabe, No. 25-417 (CA9, Watanabe v. Derr, 115 F.4th 1034; rehearing en
banc denied over eleven dissents, 139 F.4th 1056). I worked from the
provisioned snapshot (2026-08-16), the provisioned cert-stage documents
(petition, brief in opposition, questions presented — all with extracted
text), and the committed statpack. This is a docket-skeleton-plus-cert-papers
forecast: the only merits filing on the docket is petitioner's opening brief
(filed August 14, 2026), and I could not retrieve its text — the
CourtListener MCP sidecar returned a daily rate-limit error (HTTP 429) on my
first call, so live retrieval was unavailable for this cell. No merits
briefing from respondent, no amicus briefs, and no argument exist yet
(argument is set for November 9, 2026). The salience band in
`record/context.json` (`high`) scores the now-settled grant question, so per
the stage rule I did not anchor on it.

**Anchor.** The statpack's "The merits docket (granted cases)" section
publishes an `excluded` count (67), so its pooled rate is quotable and is the
committed baseline my Brier skill is scored against. My grant Term is 2025
(grant date June 22, 2026). Pooling `disturbed` over `parsed` across grant
Terms 2015–2024 — the ten-Term window strictly before mine; the table carries
rows only for 2017–2024, so those eight rows are the pool — gives
359/515 ≈ **0.697** (well above the 30-parsed floor). Coverage beside that
figure: the pooled Terms' parsed counts run 52–75 against granted counts
56–85, so coverage is high for these older Terms and pendency-censoring is
modest in the pool itself.

**Adjustments, all upward from 0.697 to 0.93:**

1. *The modern Bivens track record is one-directional.* Since Ziglar v.
   Abbasi (2017), every Supreme Court merits disposition of a lower-court
   decision recognizing or extending a Bivens remedy has disturbed it —
   Ziglar (reversing CA2), Hernandez v. Mesa (affirming CA5's *denial* of a
   remedy), Egbert v. Boule (reversing CA9), and Goldey v. Fields (2025)
   (summarily reversing CA4). The Court has not affirmed a decision
   recognizing a Bivens claim in over four decades. Conversely, it has denied
   cert where the officer won below (Sargeant, Causey, Noe, Snowden — all
   noted as cert-denied in the petition), which is strong evidence about what
   this grant is *for*.
2. *Selection.* The petitioner is the federal officer; the decision below
   recognized the Bivens action over a panel dissent and eleven dissents from
   denial of rehearing en banc, in the circuit the en banc dissenters
   themselves described as "famous for repeatedly ignoring the Supreme Court
   on Bivens questions." A Court that agreed with the Ninth Circuit had an
   easy path: deny, as it did in the mirror-image cases. Granting here, after
   holding the petition through multiple reschedules and two rounds of
   supplemental briefing, is hard to read as anything but an intent to
   disturb.
3. *Doctrinal fit.* Under Egbert's "any rational reason" formulation the
   petition's argument is close to self-executing: the ARP/PLRA are remedial
   structures Carlson did not consider, Ziglar itself treated unconsidered
   alternative remedies as making a context new, and Watanabe conceded below
   that a new-context finding is fatal at step two. The BIO's best arguments
   (Carlson considered the FTCA; the ARP predates Carlson's decision date;
   Westfall Act ratification) engage the history but not Egbert's test, which
   five-plus current Justices have signed onto repeatedly.

**Why not higher.** The residual ~0.07 covers: (a) a genuine, if small,
chance of affirmance — three likely votes exist for Watanabe's position, and
the Westfall-Act ratification argument is the kind of textual-reliance point
that occasionally peels off a textualist vote; (b) a DIG if merits briefing
surfaces a vehicle problem I cannot see from the cert papers (the case comes
up on the pleadings, so this is small); (c) an equally divided affirmance
(no recusal is apparent; negligible). Vacatur rather than reversal would
still count as disturbed, so label risk between `reversed` and `vacated` does
not bite the probability — I chose `reversed` because the step-two concession
makes the new-context holding case-dispositive, as in Egbert.

**Judgment label and votes.** `reversed` over `vacated` per the above.
The 6–3 lineup copies Egbert's alignment on what is essentially Egbert's
question one step further; my main vote uncertainty is on the high side
(a narrower opinion could draw 8–1 or 9–0, as Goldey's summary reversal drew
no recorded dissent), not the low side. The vote block is banked, not yet
scored, and I have committed it as if it graded today. Writing forecasts
(Gorsuch concurrence, Sotomayor principal dissent) are unscored context.

**Where to discount me.** I could not read the merits briefs or any
post-grant commentary (MCP throttled; corpus citation lookup empty — see
`retrieval.md`), so this forecast leans on the cert-stage papers and the
publicly settled shape of the Court's Bivens doctrine as of the snapshot
date. The supplemental briefs of February and May 2026 are on the docket but
unprovisioned and unread; if they disclosed an intervening development that
changed the complexion of the grant (e.g., a companion case or an intervening
decision the parties fought over), I have not seen it. My 0.93 is also close
to the practical ceiling for this stage; if the reader thinks the
grant-selection argument is double-counting the base rate's own selection
(the 0.697 pool already consists of granted cases), the honest floor for this
case's profile is still around 0.85.
