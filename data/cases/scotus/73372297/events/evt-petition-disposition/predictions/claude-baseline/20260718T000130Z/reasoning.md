# Jane Doe v. Kennedy, Sec'y of HHS — No. 25-1300 (petition disposition)

## The case

A pro se, paid cert petition from the Federal Circuit (No. 2025-1769, decided
December 9, 2025) arising out of a National Vaccine Injury Compensation Program
(VICP) claim in the Court of Federal Claims. Petitioner received a damages award
under the Program (November 7, 2024 special-master decision, December 23, 2024
judgment) but contends she was owed far more: she alleges the special master
colluded with her former attorneys to delete her "causation" vaccine claim from
the case, struck her expert report, illegally obtained and published her
military/VA records, and miscalculated lost earning capacity. By the petition's
own account, the Federal Circuit affirmed on a procedural ground — her motion
for review/reconsideration in the Court of Federal Claims was untimely — without
reaching the merits.

## The legal question and the cert standard

The two questions presented (quoted in `questions-presented.txt`) are not
framed as legal questions at all: they are compound, fact-specific grievances
asking whether a judgment "rife with ... fraud, atty malpractice, atty/judge
collusion" can stand. Under Supreme Court Rule 10, certiorari turns on a
circuit conflict, a conflict with this Court's precedent, or an important
unsettled federal question. The petition identifies none:

- **No circuit split.** The Federal Circuit has exclusive jurisdiction over
  Vaccine Act appeals, so a split is structurally impossible on the Program
  questions, and none is alleged.
- **Fact-bound and case-specific.** The claims — onset timing under 42 U.S.C.
  § 300aa-13(b)(2), the earning-capacity calculation under § 300aa-15(a)(3A),
  attorney malpractice, alleged judicial misconduct — are all applications of
  settled standards (Althen) to one record. Rule 10 expressly disfavors review
  for "misapplication of a properly stated rule of law."
- **An independent procedural ground.** The decision below rests on
  untimeliness of the motion for review, which would prevent the Court from
  reaching the underlying merits even if it were interested — a classic
  vehicle defect.
- **Allegations of conspiracy without corroboration.** Petitions premised on
  judge–attorney collusion and bribery, supported by appendices consisting of
  an X post, a Brownstone Institute article, and a LinkedIn essay, are the
  profile of petitions the Court denies without comment.

## Docket signals

- **Respondent (the Solicitor General) waived the right to respond**
  (June 17, 2026). The Court virtually never grants a petition without at
  least calling for a response; no CFR has issued.
- **Distributed June 24, 2026 for the September 28, 2026 "long conference"** —
  the summer-list conference at which the overwhelming majority of petitions
  are denied. No relists (relist count 0), no CVSG, no amici.
- Paid (not IFP) filing, but pro se — the paid-class grant rate does not
  transfer to pro se filings, which are granted at rates well below even the
  IFP class.

## Base rates and adjustment

From the committed statpack (modern discretionary-cert slice,
denial-reweighted): overall grant rate ~2.5–3% per Term (OT2024 3.0%, OT2025
2.5%); Federal Circuit-originating petitions granted 3.0%; zero-relist
petitions granted 0.8%; paid class ~5.4–6.9% vs IFP ~0.9–1.1%. Starting from
the CAFC/paid anchor and adjusting sharply down for: pro se presentation,
frivolous-register questions presented, no split (structurally unavailable),
an untimeliness holding below as an independent ground, the SG's waiver with
no CFR, and long-conference distribution with no relist — each of which sits
in the far-left tail of grant likelihood — I put P(grant, including GVR)
at roughly **0.003**.

A GVR is also implausible: there is no intervening decision bearing on Vaccine
Act review timeliness, so the realistic non-denial mass is essentially only a
procedural dismissal. **Predicted disposition: denied**, granted = 0,
probability = 0.003, confidence 0.9.

## Big-case score

0.05. An individual compensation dispute, anonymized, pro se, with the
petitioner expressly asking to stay out of the media. The vaccine-policy
backdrop (HHS Secretary Kennedy's public criticism of the VICP, cited in the
petition itself) gives it faint topical adjacency, but a denial here will not
be news, and even a hypothetical grant would present no usable legal question.

## Inputs used

- Snapshot `record/snapshots/2026-07-17.json` (docket entries, parties, fee
  class, conference distribution).
- `record/documents/questions-presented.txt` and `record/documents/petition.txt`
  (19 pp., full text) — the QPs and the petition's own description of the
  proceedings below, weighed with no BIO on file because the response was
  waived.
- `metrics/statpack.md` / `statpack.json` base rates; one broad
  `fedcourts query` for recent SCOTUS priors; two CourtListener MCP lookups
  for the Federal Circuit decision (both returned nothing — see
  `retrieval.md`). Forward mode; no information about this petition's
  disposition exists or was sought.
