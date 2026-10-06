# Rationale for the numbers (claude-baseline, run 20261006T142731Z)

**P(grant) = 0.08; predicted disposition `denied`.**

## What I read

- Snapshot `record/snapshots/2026-10-06.json` (the file `context.json` names). Mode `forward`; band `baseline` under `sal-v4`; `distribution_count` 1; no CVSG; Term 2026; paid docket from the Federal Circuit (No. 2024-1236, decided April 29, 2026, reported at 174 F.4th 910 per the petition).
- `record/documents/questions-presented.txt`, `petition.txt` (87 pp., full text), and `brief-in-opposition.txt` (Qualcomm's BIO, 23 pp., full text). `documents.json` shows none truncated and none `empty_text`.
- `metrics/statpack.md`: the sal-v4 segment table, the relist-count and CVSG cuts, and the originating-circuit cut.

## Anchor

The harness froze `band: baseline` under `sal-v4`, which matches the statpack table's version, so the anchor is the baseline band's bracketed `reached` rate pooled over the Terms the table renders strictly before 2026 (OT2017 through OT2025): 637.4 weighted grants over 12,720 weighted petitions, about **5.0%**. I did not substitute the relist-count cut's level, which buckets by terminal count.

## Adjustments up

1. **The Court called for a response after both respondents waived** (Aug 28, two days after the first distribution). A call for a response is the Court's own signal that at least one chambers wanted the other side heard, and it is not folded into `sal-v4`'s baseline band (which keys on relists and CVSGs). Among paid petitions, those with a requested response are granted at several times the undistinguished rate; my working figure for a CFR petition with no other signal is in the 10 to 15% range. This is the single largest adjustment and takes the number from 5% to the low teens.
2. **The hook is unusually clean.** The PTO Director conceded at the Federal Circuit that the Board should have resolved the RPI dispute (Pet. App. 8a n.5, confirmed by the BIO at its note 2), the Federal Circuit's decision is precedential, and the question is the scope of § 314(d), which the Court has taken three times (Cuozzo, SAS, Thryv) and which Justice Gorsuch in particular has written about. "The agency admits the statutory violation but no court may review it" is the kind of framing that draws attention.
3. The United States is a party, so the government's eventual brief will be read closely, and a repeat-player amicus (VLSI, which lost on an RPI question in its own litigation) is already on file.

## Adjustments down

1. **No split and no possible split.** The petition concedes the issue is "redressable only at the Federal Circuit"; the BIO says there is "admittedly no conflict among the circuits." The Court has taken § 314(d) questions without a split before, but only where the stakes were systemic.
2. **The Court just denied the neighboring petition.** Dolby Laboratories Licensing Corp. v. Unified Patents, No. 25-1011, asked in part "whether § 314(d) bars judicial review of a final decision regarding real parties in interest"; the Director (as a respondent, represented by the SG) and Unified filed BIOs in May 2026, the petition was distributed once for the June 18 conference, and it was denied June 22, 2026 without noted dissent. ESIP Series 2 v. Puzhen Life USA (2020) raised the RPI reviewability issue and was also denied. Those denials pre-date my snapshot and are legitimate forward signal. FedEx's framing is narrower and arguably better (the Board here refused to decide rather than deciding wrongly), but the Court has now twice passed on the family, and in Dolby with the government opposing.
3. **The policy has changed, which blunts recurrence.** The Director dedesignated the SharkNinja and Unified precedents during the appeal and now requires RPI determinations in every case, so the specific failure FedEx complains of should not recur. FedEx's answer ("nothing prevents a future Director from changing course") is the weaker side of that exchange.
4. **The government will oppose.** The Director maintained the § 314(d) position throughout the appeal and the SG opposed in Dolby. The SG's extension motion to Oct 28 is routine and not a signal either way. A confession of error is possible but I weight it under 10%.
5. **Narrow relief and a mixed posture.** FedEx won on some claims, the remaining unpatentability findings were remanded by consent, and FedEx did not seek review of the two companion Federal Circuit judgments (2024-1235 and 2024-1237) that rejected the same RPI argument, which the BIO uses as a vehicle point. The practical payoff of a grant is a remand for one RPI determination under a rescinded policy.
6. Petitioner's counsel is a patent litigation firm rather than a Supreme Court specialist, which modestly lowers the odds the Court sees the case as the best vehicle for the question.

Net: start near 5%, lift to the low teens for the call for a response and the concession hook, pull back for the Dolby denial, the government's opposition, the policy change, and the no-split posture. I land at **0.08**.

## The other claims

- **relist-increment 0.96.** Not a relist in the usual sense: the response deadline was extended past the Sept 28 conference the petition was distributed for, so the petition must be redistributed once the SG's BIO and a reply are in. Under the `dist-v2` count a redistribution adds a distribution entry. The residual is a dismissal or withdrawal before redistribution.
- **cvsg-increment 0.01.** The SG represents a party respondent and has been directed to respond; a CVSG to a party is not the Court's practice.
- **summary-disposition-route 0.30** (conditional on grant). The statpack's modern-cert split is roughly 577 GVRs to 655 plenary grants, but that pooled share is dominated by GVRs riding merits decisions, and no intervening decision bears on this question. A GVR here would run through a government confession of error, which I put well under even odds among the (already unlikely) grant scenarios; plenary review on the § 314(d) question is the modal grant.
- **dissent-from-denial 0.12** (conditional on denial). Dolby drew no writing. The "admitted error, unreviewable" framing plus a called-for response makes a short Gorsuch statement plausible but not expected.

## Uncertainty and where to discount me

- The size of the call-for-response lift is from general knowledge of the paid docket rather than from a statpack cut; the pack has no CFR cut, so a reader should treat the 5% to low-teens step as the least documented link.
- I could not read the Federal Circuit opinion itself or the Dolby BIOs: the CourtListener MCP sidecar returned HTTP 429 (daily limit exhausted, roughly 53 minutes to reset) on both calls, and I did not wait. The Dolby docket history came from a web fetch of the Supreme Court docket page; the Dolby outcome was already stated in Qualcomm's BIO.
- The one `fedcourts query` I ran (recent granted SCOTUS priors) returned no patent or § 314(d) neighbor and did not move the number; the corpus query surface has no text or topic filter for SCOTUS rows.
- I do not know this petition's outcome; the conference it was first set for has passed without a disposition because the response deadline was extended.
