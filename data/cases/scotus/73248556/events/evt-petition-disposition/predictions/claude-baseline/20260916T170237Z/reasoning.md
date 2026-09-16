# Rationale for the numbers

**P(any grant) = 0.07; predicted disposition: denied.**

## What the record shows

The snapshot (`record/snapshots/2026-09-16.json`, docketed April 27, 2026, paid, Term 2025, from the Fifth Circuit, No. 24-60436) shows: petition filed April 24, 2026; two response extensions; brief in opposition and IFP motion filed June 29, 2026; distributed July 15, 2026 for the Conference of 9/28/2026. One distribution, no relist, no CVSG, no reply or supplemental brief from the Solicitor General. `context.json`: mode `forward`, band `federal` (sal-v4), `distribution_count` 1, `cvsg_date` null, `signals_observable` true.

Provisioned documents (all with extractable text, none truncated): `questions-presented.txt`, `petition.txt` (43 pages), `brief-in-opposition.txt` (12 pages).

- **The petition** (Solicitor General Sauer) asks for exactly one thing: hold the petition pending *United States v. Hemani*, No. 24-1234 (the §922(g)(3) case argued March 2, 2026), and then grant, vacate, and remand in light of Hemani. The government does not ask for plenary review and does not argue the Fifth Circuit's as-applied holding is wrong on its own terms; its theory is that the panel drew on *Connelly* (the Fifth Circuit's §922(g)(3) decision) and on a rejection of the "dangerous persons" theory, both of which the government was contesting in Hemani. Respondent's single predicate is a 2018 Mississippi conviction for simple possession of methamphetamine; the panel (Higginson, J., with Willett, J., concurring) held the government did not carry its burden to show a historical tradition supporting disarmament for that predicate.
- **The brief in opposition** (Federal Public Defender) says Hemani was decided June 18, 2026 against the government, that the Court expressly declined to address §922(g)(1), that Hemani did not disturb *Connelly* and rejected the government's dangerousness analogues, and that the Court has already denied the government's identical hold-and-GVR requests in *Mitchell* (No. 25-935, June 29, 2026), *Doucet* (No. 25-1001, April 27, 2026) and *Cockerham* (No. 25-1029, June 8, 2026), as well as defendant-side §922(g)(1) petitions (*Diaz*, *Duarte*, *Vincent*).

## What I verified beyond the record (forward mode, all predating the snapshot)

- **Hemani outcome.** Confirmed by web sources (LII opinion page, SCOTUSblog case page, Wikipedia, ACLU): decided June 18, 2026, judgment for Hemani; Gorsuch majority joined by Roberts, Thomas, Sotomayor, Kavanaugh, Barrett, Jackson; Alito, joined by Kagan, concurring in the judgment. The majority says it does not address §922(g)(1) and that nothing in the opinion casts doubt on felon-disarmament provisions; it also rejects a "broad power to designate any group as dangerous." So the decision the petition asked the Court to wait for went against the petitioner and disclaimed the very provision at issue here. There is no intervening decision favoring the government for a GVR to rest on.
- **Mitchell, No. 25-935** (supremecourt.gov docket): the government asked for precisely the same relief as here (hold for Hemani, then GVR), on a §922(g)(1) reversal with a §922(g)(3) predicate, a case where Hemani was far more directly relevant than it is to Hembree. The Court distributed it April 22 for the May 14 conference, held it through Hemani, redistributed June 22 for the June 25 conference, and denied it June 29, 2026 with no GVR and no noted dissent. This is the closest possible comparator, and it resolved against the government after Hemani.
- **Doucet, No. 25-1001** (supremecourt.gov docket; The Reload and lisa-legalinfo coverage): distributed once (no BIO), denied April 27, 2026, before Hemani, i.e. the Court would not even hold it.
- **Cockerham, No. 25-1029** (SCOTUSblog case page, The Reload): BIO April 29, distributed May 19 for June 4, denied June 8, 2026, before Hemani, no noted dissent.
- **No §922(g)(1) case granted for plenary review** as of the sources I could reach (CRS Legal Sidebar LSB11108 as of March 2026; web search in September 2026 surfaced no grant). The Court has denied every as-applied §922(g)(1) petition presented, from both sides, through the end of OT2025.

## Anchor and adjustments

- **Band anchor.** `band` = `federal` under sal-v4, matching the table's version. Pooling the bracketed `reached` figures for `federal` across the shown prior Terms (2017–2024, n=181 weighted) gives a grant-family rate around 73% (132 weighted grants over 181; per-Term 43.5%–89.5%; OT2025 itself is 52.4%, n=21, and is this case's own Term so I do not pool it). That is the evaluator's yardstick and the population this cell was placed in.
- **Why I move so far below it.** The federal band's high rate is carried by SG petitions that either seek plenary review on a question the government wants decided, or seek a GVR in light of a decision the government won. This petition is neither. Its only requested relief is a GVR in light of a case the government then lost 9–0 on the judgment, in an opinion that expressly declined to reach §922(g)(1). The SG has filed nothing since Hemani (no supplemental brief, no reply) to supply a new basis. And the Court has already denied the identical request in *Mitchell* after Hemani, and declined even to hold *Doucet* and *Cockerham* before it. Conditioning on those facts, this is a federal petition in name but a spent hold petition in substance.
- **Residual grant mass (~7%).** (a) The Court could grant plenary review on §922(g)(1) in some other vehicle at the long conference or later this Term and hold Hembree for it, GVRing later if the government prevails; the Court has shown no appetite for the question so far, and even on a grant the government would have to win, so I put this path at roughly 4–5%. (b) An unexpected GVR "in light of Hemani" so the Fifth Circuit can reconsider under Hemani's reasoning: foreclosed in practice by *Mitchell*, ~1–2%. (c) Plenary grant in Hembree itself without the SG asking: ~1%.
- **Cross-checks against the other cuts.** Relist-0 paid segment: grant family ~1.7%; CA5 origin: ~3.7% grant family; no-CVSG paid segment: ~6.3%. My 7% sits at the top of those unconditioned cuts, which is where a government petition with a dead theory should sit: above an ordinary private petition because the SG is the petitioner and the issue is live, far below the federal band because the specific request has already been rejected on identical facts.

## Claims

- `disposition` 0.07 (equals `probability`).
- `relist-increment` 0.18: one distribution shown; no hold reason remains, and the three comparators show straight denials at the first conference after ripeness (Mitchell's extra distribution was purely the Hemani hold). Some mass for a routine one-conference carry or a reschedule.
- `cvsg-increment` 0.01: the SG is the petitioner.
- `summary-disposition-route` 0.6 (conditional on a grant): the grant paths I can see are mostly GVRs (hold-then-GVR after another vehicle, or a GVR in light of Hemani); the plenary path is the smallest.
- `dissent-from-denial` 0.06 (conditional on denial): none in Doucet, Cockerham or Mitchell; a Thomas or Alito statement on §922(g)(1) is conceivable but has not materialized on any of this year's denials.

## Uncertainty and where to discount me

- I did not read the Hemani opinion in full, only its key passages via LII; if it contains language the Fifth Circuit's felony-by-felony method contradicts more directly than the excerpts suggest, a GVR becomes somewhat more plausible. *Mitchell*'s denial after Hemani is my main protection against that error.
- I could not confirm whether any §922(g)(1) petition is set for the long conference in a posture the Court might grant; a grant of a different vehicle with a hold of Hembree is the scenario that would most move this number.
- The band anchor is thin (n≈15–41 per Term) and this cell is an unusual member of its band; the skill score will be measured against a yardstick that does not condition on the petition's collapsed theory.
- CourtListener's MCP server was rate-limited (429) on several calls and held no entries for the comparator dockets; the comparator docket histories come from supremecourt.gov via web fetch instead, and web-fetched PDFs of a CRS report and the Mitchell petition were text-extracted locally.
