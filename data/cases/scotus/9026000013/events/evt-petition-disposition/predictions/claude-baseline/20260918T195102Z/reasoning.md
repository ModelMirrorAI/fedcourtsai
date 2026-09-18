# Why P(grant) = 0.14

## Anchor

`record/context.json` freezes the cell as **forward** mode, Term 2026, `band: baseline` under `sal-v4`, one distribution, no CVSG. The statpack's *Segment base rate by salience band (sal-v4)* table matches the context's salience version, so the band is a valid anchor. Pooling the **bracketed `reached`** figure for `baseline` over every rendered Term strictly before OT2026 (OT2017 to OT2025, nine rows) gives:

| Term | reached rate | n |
| --- | --- | --- |
| 2025 | 3.9% | 1140 |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Pooled: about 5.0% over n = 12,720. That is the rate the evaluator scores my skill against, and it is my starting point.

## Adjustments up

- **Originating court.** The D.C. Circuit is the best-performing circuit in the statpack's circuit cut (granted 5.5%, gvr 2.3%, against 1 to 2.5% for the regional circuits).
- **Capital marking.** The petition's cover says CAPITAL CASE and the statpack's capital cut shows a grant rate near three times the unmarked rate (11.8% vs 4.2%). I discount this because the cut is dominated by state capital habeas petitions, not military-commission cases, and because the supremecourt.gov payload flag (`bCapitalCase`) is false for this docket, so the cut may not even count this petition as capital (see `flags.json`).
- **Cert-stage amici.** Three amicus briefs (Professor Vladeck, Professor Finkelstein, and a coalition of 9/11 victims' families) were filed before the response. Amicus support at the cert stage is one of the strongest observable grant predictors in the empirical literature, and Vladeck's brief frames a recurring D.C. Circuit mandamus problem rather than a one-off.
- **The Solicitor General filed a full brief in opposition,** taking two extensions to do it, rather than waiving. The government treats the petition as one that could be granted.
- **Dissent below and published opinion.** Judge Wilkins dissented in part and would have granted rehearing en banc; the majority opinion is long and published (143 F.4th 411). The petition and reply are by experienced Supreme Court advocates (ACLU's Cecillia Wang, Michel Paradis).
- **Companion petition.** Co-defendant bin 'Atash's petition (No. 25-1335) is distributed for the same conference against the same judgment, so the Court sees the question twice.
- **Genuine doctrinal hook.** Question 1 puts *Will v. United States* squarely in play: the D.C. Circuit itself acknowledged no interlocutory appeal exists and did not decide whether the government could appeal a final commission judgment, then issued a writ "in aid of" that uncertain jurisdiction. Justices attentive to statutory limits on jurisdiction could find that attractive.

## Adjustments down

- **The government's "no split" argument is credible.** The BIO shows that the First, Ninth, and Tenth Circuit cases the petition relies on (Kane, Dior, McVeigh) either affirmed mandamus jurisdiction and declined the writ on the merits, or expressly declined to rule out government mandamus. The Second Circuit cases assumed jurisdiction. The split as framed rests on decades-old dicta, and the Court rarely grants over an SG brief that plausibly denies a split.
- **Vehicle problems the SG will press hard and that the Court usually credits.** The military-commission appellate scheme (10 U.S.C. 950g) is sui generis; a ruling here would not cleanly resolve anything about 18 U.S.C. 3731 in civilian prosecutions. The petitioners barely briefed the jurisdictional point below (the reply's answer, that it was ventilated in stay briefing and incorporated by reference, is respectable but confirms the panel spent two paragraphs on it). The posture is interlocutory in a prosecution now scheduled for trial in 2028.
- **The Court's revealed preference on Guantanamo commission petitions.** Since *Boumediene* (2008) the Court has denied every military-commission cert petition presented to it (al-Nashiri, al Bahlul, Khadr, among others), preferring to let the D.C. Circuit run the system. This is a strong institutional prior against review.
- **Result valence.** The D.C. Circuit's writ leaves the death-penalty decision for the 9/11 defendants with the Secretary of Defense. A grant would reopen plea agreements sparing the alleged 9/11 plotters from execution. The current majority is unlikely to find that an appealing use of its docket, and the Justices most sympathetic to the *Will* argument face a defensive-denial calculus: a grant that ends in affirmance would entrench broad government mandamus power.
- **Kavanaugh recusal.** Justice Kavanaugh took no part in the sealing motion, and I assume he is recused from the case. Four votes out of eight are still needed to grant, and the recusal removes one potential vote and raises the prospect of a 4-4 merits split, both of which cut against a grant.

## Net

The feature profile (D.C. Circuit, amici, full SG BIO, dissent below, elite counsel, enormous stakes) would ordinarily push a `baseline` petition well into the teens or twenties. The institutional and vehicle factors pull hard the other way, and the SG's opposition is the single most reliable denial signal in the cert process. I land at **0.14**, roughly three times the pooled band anchor, with a `denied` modal disposition.

## The other claims

- **relist-increment 0.45.** From one distribution. High-profile petitions with SG opposition and amici are frequently carried over from the long conference once, either for a separate writing on denial or because a grant is being considered. I put P(at least one more distribution) a little under even.
- **cvsg-increment 0.01.** The United States is the respondent; a CVSG is structurally not available. The residual is only for coding oddities.
- **summary-disposition-route 0.03** (conditional on grant). No intervening decision supports a GVR; the government prevailed below on a published opinion, so a summary reversal against it is implausible.
- **dissent-from-denial 0.30** (conditional on denial). Salience is extreme, the petitioners' argument is respectable, and Justices Sotomayor and Jackson write separately on capital and detention matters with some regularity. But most high-profile denials are silent, and the political awkwardness of writing for KSM's position tempers the estimate.

## Big case score 0.9

Stakes, not grant odds: a grant would decide whether the 9/11 plea deals can be revived and would shape government mandamus in criminal cases. Newsworthiness is about as high as a cert petition gets.

## What I used and what to discount

- Provisioned inputs: the 2026-09-18 snapshot (`record/snapshots/2026-09-18.json`), `context.json`, `questions-presented.txt`, the full BIO (24 pages, complete text), and the petition (`petition.txt`, 336 pages including appendices, flagged `truncated: true`; I read the reasons-for-granting section, the importance section, and the front matter, all of which fell inside the extracted text).
- Retrieved: the reply brief (via supremecourt.gov, since it was not provisioned), the bin 'Atash docket (No. 25-1335), this docket's live page to confirm no entries after September 9, a Courthouse News article on the petition and amici, and a `fedcourts query` for recent granted SCOTUS priors (see `retrieval.md`). No search surfaced this petition's disposition; it is pending for the September 28 conference.
- I did not read the amicus briefs' text or the D.C. Circuit opinion beyond the BIO's and petition's accounts of them.
- Discount me most on the recusal inference (I am reading one "took no part" line on a motion as a case-wide recusal) and on the strength of the *Will* split, where I am weighting the SG's reading of the circuit cases over the petitioners' without having read those cases myself.
- I know this case from general background (the 2024 plea agreements, Secretary Austin's withdrawal, the D.C. Circuit's July 2025 ruling) but I hold no knowledge of the cert disposition, which had not occurred as of my snapshot.
