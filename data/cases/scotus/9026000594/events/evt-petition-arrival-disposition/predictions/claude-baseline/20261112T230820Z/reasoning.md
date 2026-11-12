# Reasoning — Citibank, N.A. v. Climate United Fund (No. 26-594), arrival moment

**P(any grant) = 0.62.**

## What I read
- Snapshot `2026-11-06.json`: paid petition, docketed 5 Nov 2026, one entry (petition filed 2 Nov), no distribution, no CVSG. Linked `Vide` to No. 26-589.
- `record/related/26-589.json` (relation `Vide`): *Zeldin v. Climate United Fund*, the Solicitor General's petition from the same D.C. Circuit en banc judgment, filed the same day.
- `questions-presented.txt`, `petition.txt`, `decision-below.txt` (the en banc per curiam judgment of 4 Aug 2026 — it matches the judgment the petition describes) and `lower-court-docket.txt`. I skimmed `appendix.txt` only through the petition's description of it.
- Forward-mode retrieval: the Court's live docket page for 26-589 and the government's petition (see `retrieval.md`).

## Anchor
`context.json` freezes band `baseline` (sal-v8) with `cert_anchor.rate` = 0.052, the private-petitioner class floor. That is the yardstick. I depart from it a long way, for one reason: this petition is not an independent draw from the private-petitioner population. It is an explicit tag-along to a Solicitor General petition, and its fate is almost entirely determined by that petition's.

## Why far above the anchor
1. **The companion is a federal-petitioner petition.** The statpack's `federal` band reached rate over OT2017–OT2025 runs roughly 48%–96% per Term (pooled around 70%; n per Term 12–43). The government's petition is stronger than the typical one: it comes from a fractured en banc D.C. Circuit (6–4 on one paragraph, equally divided on the rest, after a panel had gone the other way), involves about $16 billion, raises the Tucker Act channelling question on which the Court has already acted twice on the emergency docket (*Department of Education v. California*, *NIH v. APHA*), and alleges a conflict with the Fourth Circuit (*Solutions in Hometown Connections*, *Sustainability Institute*). The live docket shows the SG opposing a response extension and the Court granting only part of it (to 15 Dec 2026), consistent with the government pressing for a decision this Term. I put P(26-589 granted in some form) at about 0.82.
2. **Citibank asks only to ride along.** The petition takes no position on the government–grantee dispute and says that if the Court grants the government's petition it should grant this one too. The injunction against Citibank is derivative of the one against EPA (the panel said so; the en banc court affirmed that part by an equally divided vote without reasons). Given a grant in 26-589, I see three paths: grant and consolidate (about 0.5); hold, then GVR if the government prevails or deny if it does not (about 0.4, with the government favoured at roughly 0.75 on the merits); deny outright because Citibank is already a Rule 12.6 respondent in 26-589 and its question is fact-bound (about 0.1). That gives roughly 0.80 conditional on a grant in 26-589.
3. If 26-589 is denied, this petition is denied with near certainty (the QP alone is a fact-bound, splitless request for error correction on an interlocutory order).

0.82 × 0.80 ≈ 0.66; I shade to 0.62 for the possibility that I overrate the government petition (interlocutory posture; one question turns on a now-repealed statute; an equally divided, unreasoned judgment is a poor vehicle on some issues) and for the outright-denial path.

## Other claims
- `relist-increment` 0.97: the frozen count is zero, so any distribution for conference satisfies it; only a withdrawal or Rule 46 dismissal before distribution would not.
- `cvsg-increment` 0.01: the United States is a party.
- `summary-disposition-route` 0.35 (conditional on grant): the hold-then-GVR path's share of the grant paths, plus a small chance the Court disposes of both petitions summarily.
- `dissent-from-denial` 0.08 (conditional on denial): most denial paths are quiet (denial after a hold, or denial alongside a grant in 26-589); a noted dissent is plausible mainly if the government's petition is itself denied.
- `order-writers`: low single digits each, consistent with the above.

## Where to discount me
- The conditional (what the Court does with a tag-along co-defendant petition) rests on my judgement of practice, not on a committed table.
- The same-question list was empty and the corpus query returned nothing bearing on this question beyond the companion's row (still pending, zero distributions).
- No BIO exists yet; respondents have argued below that the Citibank injunction should survive even if the government's is vacated, which could persuade the Court to leave Citibank's question for remand rather than grant it.
- Big-case score 0.65 reflects the underlying dispute; Citibank's own question is narrow.
