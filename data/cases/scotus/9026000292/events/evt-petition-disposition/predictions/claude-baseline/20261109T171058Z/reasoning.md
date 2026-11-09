# Reasoning — Havlish v. Taliban, No. 26-292 (forward, cert, moment: distribution)

**P(any grant) = 0.22. Call: denied, eventually, with a good chance of a CVSG first.**

## What the record shows
- Snapshot `2026-11-09.json`, which matches the live supremecourt.gov docket I fetched today. The petition was filed on 8/31/2026. It was distributed for the 11/6 conference and then **distributed again for 11/13** after no action on the 11/9 order list. `distribution_count` = 2, so this is effectively a first relist (or a reschedule).
- **No respondent has appeared.** The docket lists no respondent counsel, no brief in opposition and no waiver. The respondents are the Taliban et al., and they defaulted below.
- Two amicus briefs: Iowa and 30 other States supporting the petitioners, and Afghanistan's UN mission (the Republic's chargé d'affaires) opposing. On 10/30 the petitioners moved for leave to file a supplemental brief replying to the Afghan mission's brief.
- The companion petitions Vide-linked to this one (`relation: Vide`): 26-293 (Ashton) and 26-294 (Owens) came from the same Second Circuit judgment. Each was distributed for 11/6 under its own cut. I see no hold or grant there.
- `same-question.json` lists no other petitions above the threshold.

## Documents used
- The questions presented and the petition text (truncated at the appendix). The petition asks whether TRIA §201(a) requires the assets' owner to have been a terrorist party or its agency or instrumentality **at the time of blocking**.
- The panel (Cabranes and Calabresi; Sullivan dissenting) adopted that blocking-date rule. Rehearing en banc was denied over dissents from five judges, including Chief Judge Livingston (Sullivan, joined by Livingston, Bianco and Park; Menashi separately).
- The petition claims a split with the Ninth and Eleventh Circuits (Stansell III and others). I read that split as somewhat soft. Those cases dealt with designation and turnover timing rather than a blocking-date rule, so the conflict is partly inferred.
- I skimmed the appendix only for structure. No BIO exists.

## Anchor and adjustments
- **Anchor:** `cert_anchor.rate` = 0.248, the reached rate for the `elevated` band (sal-v8) over the 10 prior Terms. Cross-checks:
  - Relist-count cut: bucket 1 has n≈2,532 with grant + GVR ≈ 13.5%; bucket 2 has n≈495 with ≈41%.
  - Amicus cut: the 2+ bucket has n≈1,446 with ≈23% grant family.
- **Up:**
  - A dissent from denial of rehearing en banc joined by the Chief Judge.
  - Billions of dollars and a nationally salient set of victims.
  - A 31-State amicus brief.
  - A clean statutory question with recurring importance for blocked-asset litigation (Iran, IRGC, FARC).
  - Elite counsel.
  - The relist itself.
- **Down:**
  - (a) **No adversary.** The Court almost never grants a paid petition without a response. With the respondents in default, the realistic routes to plenary review go through a CVSG or a called-for response (or an appointed amicus after a grant). That adds a step and a delay, and makes a deny-now outcome plausible if no Justice pushes for it.
  - (b) A foreign-affairs and recognition overlay: the Taliban is unrecognized, the Afghan Fund exists, and Executive Order 14064 is in play. The Court often waits for the Executive's view, and that view historically opposed turnover in this litigation (the 2022 statement of interest). The current Administration's position is unknown to me.
  - (c) The split is arguable, and there is a fact-bound component (when the Taliban took control of DAB).
  - (d) The FSIA holding below is not before the Court, which narrows what a grant could do.
- **Net:** a little below the anchor, at 0.22. The relist without a response looks to me most like a pause before a CVSG or a call for response. I put a CVSG at about 0.38. If a CVSG issues, I'd expect a grant at roughly the CVSG cut's ~35% grant family (n≈164), with the SG's view decisive.

## Increments
- **relist-increment, 0.58:** P(distributed after 11/13). A CVSG, a call for response, or another relist all produce a later distribution. Only a straight denial at 11/13 (or a grant there) does not, and a grant without a response is very unlikely.
- **cvsg-increment, 0.38.**
- **summary-disposition-route, 0.05:** no intervening decision supports a GVR, and a summary reversal without any respondent briefing is implausible.
- **dissent-from-denial, 0.25:** a five-judge en banc dissent and 9/11 victims make a written dissent from denial plausible, most likely from Gorsuch, Thomas or Alito.

## Uncertainty and caveats
- I have not read the supplemental brief or the Afghan mission's brief. I know of them only through docket text and a search snippet.
- I don't know the current Administration's position on the assets.
- Retrieval was limited: one live docket fetch, two web searches and one corpus query. The MCP server was not needed.
