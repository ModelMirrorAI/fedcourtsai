# Rationale for the numbers (claude-baseline, 20260816T111104Z)

**P(disturbed) = 0.82.**

**Anchor.** The committed statpack's "The merits docket (granted cases)"
section publishes an `excluded` count (67 pool-guard exclusions), so its rates
are quotable. This case's grant date is 2026-06-30 (the event's `opened_at`),
so the grant Term is OT2025 and the pool is grant Terms 2015–2024. The pack
holds parsed rows for 2017–2024 within that window; pooling `disturbed` over
`parsed` across those Terms gives 359/515 ≈ **69.7%**, comfortably above the
30-judgment floor — this is the committed baseline my Brier skill is scored
against. Coverage caution quoted per the section's caption: the nearest Terms
are pendency-censored (2024: 73 parsed of 75 granted, but 34 excluded; 2023:
55 of 56), so the pooled figure leans on quicker dispositions in recent Terms.

**Adjustments up from 0.70.** (1) The grant is limited to Question 1, the
contempt-standard question, where the Ninth Circuit's "spirit of the
injunction" doctrine (Sea Shepherd) is the outlier against the First, Second,
Third, and Fifth Circuits' clear-and-unambiguous requirement, and sits in
visible tension with Taggart v. Lorenzen (2019, unanimous), Rule 65(d), and
ILA v. Philadelphia Marine. The Court rarely takes an outlier-circuit
standards case to bless the outlier. (2) The panel itself conceded (App. 34a
n.9, quoted in the petition) that the injunction's text "does not address
commissions at all" — an unusually clean admission for the petitioner's frame.
(3) The grant came fast — distributed twice, granted June 30 at the end of the
Term, no CVSG — a cleanup-shaped grant. (4) The forum is the Ninth Circuit and
the Court's recent equity line (Taggart, Trump v. CASA, Starbucks v. McKinney)
runs consistently toward cabining loose equitable power.

**Adjustments down.** (1) Epic's strongest point: the contempt finding did not
rest on "spirit" alone — the district court found Apple "violated the literal
text" as well, and the panel held the commission's "prohibitive effect"
violated the injunction's text under McComb's no-evasion principle. That gives
the Court a path to announce Apple's standard yet affirm, or the briefing
could convince it the QP is not squarely presented (a small DIG tail). (2) The
compliance record is terrible for Apple — bad-faith findings, a commission
engineered to nullify the injunction, a "manufactured" justification study —
which makes an affirmance-in-result more palatable to some Justices and makes
a clean reversal harder to write. Net of both directions: **0.82**.

**Judgment label `vacated` over `reversed`.** Taggart's own pattern:
announce the standard, vacate, remand for application. Because the panel
embraced an alternative text-based rationale, outright reversal (contempt
unsustainable, full stop) is less likely than vacatur with a remand that
leaves the text theory open.

**Votes (7–2).** Per-Justice modal calls. The seven-member majority holds with
high confidence for Roberts, Thomas, Alito, Gorsuch, Kavanaugh, and Barrett
(each joined Taggart's rule or the CASA equity line); Kagan joined Taggart and
denied Apple's stay only on equities, which I read as weak-to-no merits
signal (an administrative-stay denial by a Circuit Justice without referral).
Sotomayor and Jackson are near coin flips — the clear-statement contempt rule
has cross-ideological appeal (it protects unions and civil-rights defendants
too), but McComb plus Apple's willfulness findings give a natural dissent —
and I call them dissent at roughly 0.55 each. A 9–0 is the most likely
alternative lineup, which is why `confidence` is only 0.55.

**What I worked from.** Forward-mode cell; the judgment does not exist yet.
Inputs: the provisioned 2026-08-16 snapshot (docket through the Aug 13 stay
denial), the provisioned cert-stage documents — questions-presented.txt,
petition.txt (213 pages, marked truncated, but including the Ninth Circuit
opinion appendix through the CASA discussion), and the 43-page BIO, all with
extracted text — and the committed statpack. No merits briefs exist yet
(petitioner's is due 2026-09-14), so this is a grant-moment forecast from the
cert-stage papers plus the docket skeleton, which is exactly what this moment
is for. One corpus lookup (Taggart by citation) returned empty on a stated
coverage gap; I did not retry sparse filters, and no CourtListener retrieval
was needed beyond the rich provisioned record.

**Where to discount me.** The 0.14 affirmance mass rides on how squarely the
panel's text-violation rationale stands independent of the spirit doctrine —
I read that only through the parties' adversarial framings and the appendix
excerpts, not the full opinion. The petition text is marked truncated, so the
appendix may omit passages that would sharpen the affirmance path. And the
salience band in my context (`elevated`) is a cert construct for a settled
grant; per the stage rule I did not anchor on it.
