# Reasoning — 26-379, Genalo v. D. C. (arrival moment)

**P(grant) = 0.75.**

## Inputs
- Snapshot `record/snapshots/2026-09-21.json`: a paid petition docketed Sep 21, 2026, filed by the Solicitor General (D. John Sauer) for an ICE field office director, from the Second Circuit (No. 26-1396). There are two entries: the petition was filed (response due Oct 21), and a Rule 34.6 paper-only order. Distribution count is 0 and there is no CVSG, because no distribution exists yet at this moment.
- `context.json`: mode `forward`, band `federal` (sal-v7), `cert_anchor.rate` = 0.731 (reached rate pooled over 10 prior Terms). `paper_only_filings: true`, so no documents were provisioned. That is expected and not a flag matter. `same-question.json` has `petitions: null` because there was no QP to match on.

## Anchor
The federal caption-class floor is the arrival population's own base rate. The statpack's sal-v7 `federal` column, pooled over OT2017–OT2025, gives about 73% (the frozen `cert_anchor` is 0.731). I start there.

## Forward retrieval (allowed in a forward cell)
- The Court's live docket shows the filing is a **petition for certiorari before judgment**. Respondent asked to extend the response deadline to Dec 21; the Court **granted that only in part**, to Dec 8. Iowa and other states filed an amicus brief on Oct 20.
- Press coverage (Bloomberg Law and Fox News headlines/text) and docket 25-886 show the backstory. The Court **granted certiorari on this question** in *Genalo v. Black* (25-886) on June 15, 2026, and set argument for Oct 13, 2026. That case was dismissed under Rule 46.1 on Sep 11, 2026, after the respondent was pardoned. The SG offers D. C. as a stand-in vehicle on the same questions: whether a noncitizen detained under §1226(c) for a long time must get a bond hearing, and who bears the burden of proof. The petition describes a circuit split, with the Second Circuit putting the burden on the government.
- None of these sources says the petition has been decided. They post-date the snapshot, which is the ordinary forward shape and not leakage.

## Adjustments
- **Up:** The Court has already shown it wants this question; it voted to grant it four months ago. The SG is the petitioner, there is an acknowledged split, and states filed as amici. Granting the extension only in part looks like keeping the case decidable this Term (BIO Dec 8, a January conference, April argument).
- **Down:** Cert before judgment is extraordinary under Rule 11. The Court could wait for the Second Circuit, or for a vehicle from another circuit that already has a judgment, and deny or hold this one. D. C.'s own case could also go moot through release, removal or relief, as G.M.'s did. The earlier grant also asked a mootness question, which shows the Court watches vehicle problems closely. I have not read the petition or QP text myself because the filings are paper-only.
- Net: about the anchor, nudged up slightly by the prior grant and pulled back by the posture. 0.75.

## Other claims
- relist-increment 0.96: the petition will almost surely be distributed at least once after the BIO. The only exceptions are withdrawal or mootness first.
- cvsg-increment 0.005: the petitioner is the federal government.
- summary-disposition-route 0.05: if granted, plenary review is the point. A GVR of a petition for cert before judgment would be odd.
- dissent-from-denial 0.3: if the Court denies after having granted the question once, a statement from a Justice who favors review (Alito or Thomas) is plausible.

## Uncertainty
I have no petition text, so the QP wording comes from secondary reporting. I could not check whether competing vehicles from other circuits are pending.
