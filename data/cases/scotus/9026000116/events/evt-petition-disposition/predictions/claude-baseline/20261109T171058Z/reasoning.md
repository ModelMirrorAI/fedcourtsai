# Reasoning — Allen v. Caster, No. 26-116 (cert before judgment), claude-baseline

**P(any grant) = 0.72; predicted disposition: `gvr`. That means a grant, vacate and remand, most likely a Munsingwear vacatur, with a summary reversal as the alternative.**

## Inputs read
- Snapshot `record/snapshots/2026-11-09.json`. The petition was filed 22 Jul 2026 and the BIO 18 Sep. Alabama filed the reply and a Rule 15.5 waiver 28–29 Sep. The petition was distributed for the 10/16 conference, again for 11/6 and again for 11/13, so the docket shows **3 distributions**. Nothing on the docket records the 10/16 conference acting on it: it was not redistributed until 2 Nov, so that first gap may be a reschedule rather than a true relist.
- `record/context.json`: forward mode, band `high` (sal-v8), `cert_anchor.rate` = 0.348 (10-Term lookback), no CVSG, Term 2026.
- `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt` (grepped for mootness, Munsingwear and summary-reversal passages; not read cover to cover), `lower-court-docket.txt`. The Eleventh Circuit stayed the Caster appeal pending this Court's disposition of Milligan and Singleton, so there is no CA11 opinion.
- `same-question.json` lists 26-117 (Milligan) and 26-118 (Singleton), the companion direct appeals with identical papers, both pending. The live docket for 26-117 shows the same distribution track (10/16, 11/6, 11/13) and a motion to dismiss or affirm.

## Anchor and adjustments
- Anchor: the band `high` reached-rate of 0.348. Cross-check: the statpack relist cut for the 3+ bucket shows granted 23.2% plus gvr 14.1%, about 37% grant family.
- **Up, strongly:**
  1. The companions are mandatory-jurisdiction appeals. The Court must dispose of them on the merits (affirm, reverse, or vacate as moot), and it has treated Caster in parallel throughout. Per the petition's appendix narrative, on 11 May 2026 it vacated and remanded all three in light of Callais.
  2. On 2 Jun 2026 the Court stayed the new preliminary injunction, finding Alabama likely to succeed (public reporting: SCOTUSblog, Alabama Reflector).
  3. Respondents' main argument is that the appeal is moot: the injunction covered only the 2026 elections, held 3 Nov 2026. Alabama's reply asks for summary reversal or, alternatively, Munsingwear vacatur. If the Court finds the case moot, Munsingwear vacatur is its standard practice where the mootness came from the passage of time rather than the losing party's own act. If it finds the case live, the stay signals a reversal. Both branches are grant-family outcomes.
  4. The relists line up with the election calendar (11/6, then 11/13 right after Election Day), which is consistent with the Court waiting for the mootness question to ripen or drafting a per curiam.
- **Down:** The Court could dismiss the appeals as moot without vacatur and deny cert before judgment, leaving the Eleventh Circuit to sort out Caster. Cert before judgment is also an extraordinary posture. I give these paths about 25–30%.

## Uncertainty
- Whether the Court vacates the Caster preliminary injunction through the cert-before-judgment petition, or simply denies it and lets the Eleventh Circuit apply Munsingwear itself. This is the main risk.
- I read the BIO and reply through targeted greps rather than in full.
- The order-writers numbers rest on the Court's ideological split in the earlier stay and Callais. That is judgment, not data.

No outcome information for this petition surfaced in retrieval. The SCOTUSblog relist-watch piece (Nov 2026) describes the case as pending.
