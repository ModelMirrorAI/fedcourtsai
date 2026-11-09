# Reasoning — Rivera-Perez v. Flowers, No. 26-396 (P(grant) = 0.30)

## Inputs used
- Snapshot `record/snapshots/2026-11-09.json` (forward mode, `cutoff: null`, so the docket is as it stood when last stored).
- `record/context.json`: band `baseline` (sal-v8), `distribution_count` 1, no CVSG, `cert_anchor.rate` 0.0516.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (138 pp., truncated in the appendix) and `party-letter.txt`. The party letter's extracted text is only the Federal Defenders' letterhead (1 page), so I cannot tell what it asked for. It came two days after distribution and four days before the Court called for a response, so it may well have asked the Court to call for one. That is inference, not something the text shows.
- No BIO exists yet. No `decision-below.txt`, `same-question.json` or `related/` was staged.

## Docket posture
The petition was filed 9/17/2026 by a paid petitioner. Counsel are the Federal Public & Community Defenders Supreme Court Project, with Haynes Boone. The SG (federal respondents) waived a response on 9/30. The petition was distributed for the 11/6 conference on 10/7. On **10/13 the Court called for a response**, and the SG got an extension to 12/14/2026. So the petition will go to a January 2027 conference at the earliest, once the BIO and any reply are in.

## Anchor and adjustments
- Anchor: the baseline band's pooled reached rate, **5.2%** (`cert_anchor`). This is the scoring yardstick. The statpack's relist-1 bucket (8.3% granted plus 5.2% GVR) points in the same direction.
- **Up, strongly.** This is a real, acknowledged split on a pure question of statutory text. The 9th Circuit (Gonzalez v. Herrera, published) says credits can reduce supervised release. The 2nd Circuit (below: published, with a concurrence and Judge Nathan dissenting) and the 6th Circuit (Hargrove, published, with a dissent) say no, and so do unpublished 4th and 11th Circuit decisions. The petition reports that in the Hargrove BIO the SG conceded a "circuit conflict" and asked the Court to wait for "percolation", citing this very case. The 2nd Circuit has now ruled. The government did not seek rehearing in Gonzalez, so the split will not resolve on its own. The Court has repeatedly granted First Step Act interpretation questions (Terry, Concepcion, Pulsifer, Hewitt, and Maxwell v. Dinis this Term). The Court's own call for a response is a modest additional signal. Eligibility is undisputed here: BOP already applied 365 days of credit. The five-year supervised-release term, which started around 2024–25, keeps the dispute live.
- **Down.** The Court denied Hargrove (25-818) at its first conference on 4/20/2026. The corpus row shows one distribution and an amicus coalition (Cato, NACDL and others) supporting the petition. So the Court passed on this split very recently, although the SG's main reason there was a vehicle problem (eligibility) that this case does not have. The 2nd Circuit's judgment directs dismissal *as moot*. Mootness turns on the merits question, but the SG may still use it to call this a poor vehicle. The SG will likely oppose, perhaps arguing that the 9th Circuit is an outlier or that the practical stakes are small.
- **Hold/GVR channel.** Maxwell v. Dinis (25-5930; argued 11/2/2026 per the petition; the corpus row shows court-appointed amicus defending the judgment below) asks whether a First Step Act time-credit claim seeking transfer to prerelease custody can be brought under § 2241. This petitioner's claim began as exactly that kind of § 2241 petition. A hold for Maxwell, followed by a GVR, is plausible. Roughly 0.06–0.08 of my grant mass is that GVR route.

Overall: about 0.22 for a plenary grant plus about 0.07 for a GVR, giving **0.30**. I call it denied because that remains slightly more likely than not. This is a high number for the baseline band, and my main uncertainty is how much weight the recent Hargrove denial deserves. If the Court simply does not want this question, the true rate is nearer 0.1. If Hargrove was purely about the vehicle, it is nearer 0.5.

## Claims
- relist-increment 0.96: the petition must be distributed again once the BIO is in (after 12/14). The only routes without another distribution are a voluntary dismissal or withdrawal.
- cvsg-increment 0.01: the United States is the respondent, so a CVSG is essentially impossible.
- summary-disposition-route 0.22 | grant: the Maxwell GVR route is the main summary channel.
- dissent-from-denial 0.12 | denial: Hargrove's denial apparently drew no noted writing. A deepened split with a dissent below gives Justices Jackson, Sotomayor or Gorsuch some chance of writing.

## Retrieval
Two corpus docket lookups (Hargrove 25-818 and Maxwell 25-5930) and statpack reads. No MCP or web calls. Details are in `retrieval.md`.
