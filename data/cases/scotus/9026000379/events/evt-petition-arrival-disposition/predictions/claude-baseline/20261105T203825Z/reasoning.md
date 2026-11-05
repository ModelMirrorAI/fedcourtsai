# Reasoning — Genalo v. D.C., No. 26-379 (arrival moment)

**P(any grant) = 0.80.**

## Inputs
- Snapshot `2026-09-21.json`: two entries, both from the docketing day. The petition is filed, a response is due Oct 21, 2026, and the Court ordered paper-only filing (Rule 34.6). The petitioner is the Solicitor General (D. John Sauer) on behalf of an ICE field office director. The case comes from the Second Circuit (No. 26-1396). The docket number is paid.
- `context.json`: forward mode, band `federal` (sal-v7), `distribution_count` 0, no CVSG, and `cert_anchor.rate` = 0.731 (10-Term lookback). `paper_only_filings: true`, so it is expected that no documents were provisioned. That is not a provisioning gap.
- `same-question.json`: `petitions: null` (no QP text to match on).

## Anchor
The federal caption-class floor is the frozen anchor, 0.731, pooled from prior Terms. The statpack's federal reached rates for 2017–2025 run from 48% to 96%, which matches the anchor. In the full federal band, GVRs make up a large share of grants (21% of resolved).

## Adjustments (forward retrieval, all public and predating today)
- The live docket shows that this is a **petition for certiorari before judgment**. According to SCOTUSblog's case page, it presents two questions. First, whether detention under 8 U.S.C. §1226(c) can become "unreasonably prolonged" so that due process requires a bond hearing. Second, if so, whether the government must justify detention by clear and convincing evidence.
- The Court **already granted this question** on June 15, 2026, in *Genalo v. Black* (G.M.), No. 25-886, and set argument for Oct 13, 2026. That case was dismissed by joint stipulation under Rule 46.1 on Sept 11, 2026, before argument. Ten days later the SG filed this petition. It is plainly the replacement vehicle. An ACLU letter of Sept 25 in *Putra v. Lopez-Campos*, No. 25-1415, describes D.C. as presenting "the same constitutional issues as those presented in G.M." That letter asks that any grant in D.C. be limited to the related statutory question. That request itself presumes a grant is live.
- A Court that has already voted to decide a question, then lost its vehicle to a stipulated dismissal, usually takes a clean replacement. This is my main reason for moving above the anchor.
- Risks pulling the number down:
  - (a) **Mootness or a second dismissal.** Detention cases moot readily through release, removal or settlement. G.M. itself ended that way, and a dismissal scores as ungranted.
  - (b) Before judgment, the Court may prefer to **wait for the Second Circuit**, or to take the question through another case. The related §1225 petitions (Putra, Rhoney, Buenrostro-Mendez) were distributed for the Sept 28 conference, and a grant there could absorb or defer this one.
  - (c) The respondent's time was extended only to Dec 8. The Court did not expedite, which mildly weakens the urgency.
- Net: 0.80. I put roughly 0.08 on a dismissal or mootness and roughly 0.12 on a denial.

## Other claims
- `relist-increment` 0.96: the record shows zero distributions. The petition will almost certainly be distributed at least once, unless it is dismissed first.
- `cvsg-increment` 0.01: the SG is the petitioner.
- `summary-disposition-route` 0.10: plenary review is expected. A GVR or hold is possible only if a related grant resolves the question first.
- `dissent-from-denial` 0.30: if the Court denied a federal petition on a question it had already granted, a writing is plausible. The likeliest writers are Alito or Thomas (favouring review), or Sotomayor or Jackson in a statement.

## Uncertainty
I did not read the petition text, because filings are paper-only. I did not confirm what happened to the related petitions at the Sept 28 conference; the docket pages I fetched showed entries only through Sept 25. Discount me if D.C. has already been released or removed.
