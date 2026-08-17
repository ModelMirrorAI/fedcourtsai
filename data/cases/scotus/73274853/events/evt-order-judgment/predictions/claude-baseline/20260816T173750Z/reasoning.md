# Rationale for P(disturbed) = 0.45, judgment = affirmed

**Cell posture.** Forward-mode merits cell at `moment: grant` (event
`evt-order-judgment`, opened 2026-06-29, the grant date). Certiorari is settled;
the forecast is the judgment the Court enters. The context carries `band: high`,
but that is the cert petition's grant-likelihood band and I did not anchor on it,
per the stage rule.

**The committed baseline.** The statpack's "The merits docket (granted cases)"
section publishes an `excluded` count, so it is quotable. My case's grant Term
is OT2025 (granted 2026-06-29). Pooling disturbed over parsed across the ten
grant Terms strictly before (2015–2024; the table renders 2017–2024, and Terms
with no parsed judgment are omitted): 359 disturbed / 515 parsed = **69.7%**,
comfortably above the 30-parsed floor. That is the rate my skill is scored
against. Coverage caveat quoted per the contract: the nearest Term in the pool
(2024: 73 parsed of 75 granted; 2023: 55 of 56) is well-parsed, so pendency
censoring in this pool is mild.

**Why I sit 25 points below the baseline.** Four case-specific signals, all
predating the snapshot, push toward affirmance:

1. **The Solicitor General's invited brief endorsed the decision below.** The
   CVSG issued 2025-12-08; the SG filed 2026-05-22 urging grant while agreeing
   with the Eighth Circuit that the Fifth Amendment — not state law — supplies
   the compensation standard. The SG's merits position after a CVSG is
   historically one of the strongest single outcome predictors, and here it
   backs the respondent's side. (Caveat below on sourcing.)
2. **Petitioners must win a conjunction.** To disturb the judgment, the
   landowners need the Court to adopt state-law borrowing *and* to treat North
   Dakota's discretionary fee-shifting provision as riding along. The BIO's
   strongest point is that ND law itself does not define just compensation to
   include fees — so even a Court sympathetic to Kimbell Foods borrowing has a
   path to affirmance.
3. **Respondent holds a narrow, textualist path.** United States v. Bodcaw
   (fees are not constitutional just compensation) plus Alyeska's American Rule
   (no fees in a federal cause of action absent express authorization) let the
   Court affirm without much doctrinal invention, and PennEast's
   characterization of § 717f(h) as delegated *federal* power gives the
   federal-standard rule a recent, on-point anchor.
4. **The equities read differently than the headline.** The dispute as litigated
   is ~$383k in attorney's fees, not the land's value — less sympathetic than a
   compensation-floor case.

**Why not lower.** Real forces cut the other way and keep me near the middle:
the modern Court's hostility to federal common lawmaking (Rodriguez v. FDIC,
O'Melveny, Atherton) is precisely the petitioners' frame — adopt state law
unless Congress displaces it; four circuits and forty years of practice sit on
the petitioners' side, and the Court affirms outlier circuits less often than
it reverses them; the Court's recent property-rights run (Tyler, Cedar Point,
DeVillier) has been consistently pro-owner; and petitioners' counsel (Institute
for Justice) is an experienced Supreme Court advocate. The grant itself came
from the landowners' loss, which mechanically favors reversal. Netting the
strong SG signal and the conjunction structure against the anti-federal-common-law
instinct and the base rate, I land at 0.45 — affirmance slightly favored, far
from confident.

**Claims coherence.** `judgment-disturbed` = 0.45 = top-level `probability`;
`granted` = 0 because the judgment I name (affirmed) does not disturb;
`predicted_disposition` = `other` per the merits contract. A DIG (< 5%) and an
equally divided affirmance (no apparent recusal, ~1%) sit in the 0.55
complement, not as reasons to shade the number.

**What I worked from.** The provisioned snapshot (full docket through
2026-08-16, including the grant, the November 9 argument date, and petitioners'
merits brief filed 2026-08-13), the provisioned petition, BIO, and QP texts
(all fetched clean, no `empty_text`), the committed statpack, and forward-mode
web retrieval. The merits briefing content itself is *not* reflected here
beyond the docket's word that petitioners' opening brief was filed: I did not
obtain its text, so this is substantially a docket-skeleton-plus-cert-papers
forecast, informed by the cert-stage advocacy rather than the merits advocacy.

**Where to discount me.** My read of the SG's brief comes from secondary press
summaries surfaced by web search (Akin Gump's summary was 403-blocked;
SCOTUSblog's case page did not state the brief's position), not from the brief
text itself. If those summaries mischaracterized the SG's merits position, my
largest downward adjustment is built on sand and the right number is nearer the
0.70 baseline. The vote lineup and authorship are low-confidence throughout;
the choice-of-law question crosses the usual blocs.
