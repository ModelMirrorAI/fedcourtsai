# Prediction: motion to proceed IFP — In re: Angela DeBose (ca11/68252091, No. 24-10350)

## The event

Docket entry 2 (filed 2024-02-09): "MOTION to proceed IFP filed by Petitioner
Angela W. DeBose." The question is whether the Eleventh Circuit will grant the
motion to proceed in forma pauperis in this **original proceeding** — a petition
for a writ of mandamus (entry 1, filed 2024-02-01) arising out of N.D. Fla. No.
4:22-cv-00439. The docket's appellate-case-type field reads "Original
Proceeding, Fee not paid Mandamus"; fee status is "IFP Pending." The cell is
`forward` mode.

## Governing standard

Leave to proceed IFP in the court of appeals is governed by 28 U.S.C. § 1915
and Fed. R. App. P. 24. Financial eligibility alone does not carry the motion:
the court denies IFP where the underlying appeal or petition is **frivolous** —
§ 1915(e)(2)(B)(i), and longstanding Eleventh Circuit practice (e.g., *Pace v.
Evans*, 709 F.2d 1428 (11th Cir. 1983)) that IFP is due to be denied when the
action "is frivolous and not brought in good faith." For an original mandamus
proceeding the merits screen effectively collapses into the IFP ruling: mandamus
is a drastic remedy available only when the petitioner shows a clear and
indisputable right to relief and no other adequate means (*Cheney v. U.S. Dist.
Court*, 542 U.S. 367 (2004)), so a facially meritless petition typically draws
an order denying IFP as frivolous, followed by dismissal for failure to pay.

## Facts that drive the outcome

1. **This is a pro se mandamus petition, not an ordinary appeal.** Pro se
   mandamus petitions are overwhelmingly denied; when the petition is facially
   meritless the Eleventh Circuit frequently resolves the case at the IFP stage
   by denying the motion as frivolous rather than granting IFP and reaching the
   merits. That alone pushes P(grant) well below the grant rate for ordinary
   indigent appeals.

2. **The petitioner's litigation history.** Angela W. DeBose is, to my general
   knowledge (which I could not verify this run — see the retrieval note
   below), a prolific pro se litigant in Florida's federal courts: a former
   university registrar whose employment case (M.D. Fla. No. 8:15-cv-2787)
   spawned years of post-judgment filings, follow-on suits against the
   university, its vendors, opposing counsel, and judicial officers, a
   vexatious-litigant filing injunction in the Middle District of Florida, and
   multiple Eleventh Circuit appeals dismissed as frivolous — including prior
   IFP denials on frivolousness grounds. A 2024 mandamus petition from a
   different Florida district (N.D. Fla.) fits that pattern, and a panel
   screening the petition will have that history in front of it. Courts are
   markedly less charitable at the § 1915 screen with serial litigants who have
   prior frivolousness findings.

3. **Nothing in the snapshot cuts the other way.** The docket shows only the
   petition and the IFP motion; there is no indication (counsel appearance,
   court-requested response, stay) that the petition raised a question the
   court found substantial.

4. **Financial eligibility is not the likely battleground.** Nothing suggests
   the affidavit of indigency would fail on its own terms; the predictable
   denial ground is frivolousness of the underlying petition.

## Probability

Ordinary indigent pro se appellants get IFP granted at high rates, but
conditioning on (a) an original mandamus proceeding, (b) pro se status, and
(c) a petitioner with prior frivolousness findings and a filing injunction,
the grant probability drops sharply. Some residual probability remains that a
screening judge takes the administratively cheaper path of granting IFP and
denying the mandamus petition on the merits — a real minority practice in the
circuit — and some that my recollection of the petitioner's history is wrong
or that this particular petition is substantial.

**Prediction: denied. P(granted) = 0.18.** Confidence 0.55 — moderate, because
motion-level base rates are not available from the corpus, the CourtListener
MCP server was down for this cell, and one meaningful driver (the petitioner's
litigation history) rests on unverified general knowledge, which I have
discounted accordingly.

## Caveats

- The provisioned snapshot is dated 2026-07-11 but its content was last
  indexed 2024-02-14; the underlying petition was filed 2024-02-01. Although
  the cell is marked `forward`, the motion has almost certainly been resolved
  in the real world by now. I deliberately did **not** query the live docket
  or any post-February-2024 material about this case, per the
  never-retrieve-the-outcome rule; the prediction rests on the pre-decision
  record and general legal context only. I do not know this case's actual
  outcome.
- The CourtListener MCP server failed on every call (server-side session-store
  error), so I could not verify the petitioner's litigation history or pull
  circuit IFP practice examples; flagged in `flags.json`.
