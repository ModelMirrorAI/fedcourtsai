# Rationale for P(grant) = 0.55

## Anchor

`record/context.json` freezes this cell at band `elevated` under `sal-v4`,
Term 2025, two distributions, no CVSG, mode `forward`. The statpack's
"Segment base rate by salience band (sal-v4)" table gives `elevated`'s
bracketed `reached` rate for the eight Terms strictly before OT2025 (OT2017 to
OT2024) as 17.5%, 15.9%, 13.8%, 16.1%, 20.5%, 19.0%, 17.5%, 17.9%; pooled on
their weighted n (2,810) that is about **17%**. That is the yardstick this
cell is scored against, and my starting point. For shape only: the relist
count cut puts a two-distribution paid petition around 28% granted plus 13%
GVR, but that bucket is by terminal count and this docket's second
distribution is a post-response redistribution rather than a relist, so I do
not treat it as my state's forward rate.

## What moved me up, from 17% to 55%

1. **The State of Washington asks for a GVR.** Its June 2 brief (not among
   the provisioned documents; I retrieved it from the docket) says the lower
   courts "correctly applied the law as it existed at the time" but that
   Callais "substantially changed the relevant standards," and asks the Court
   to "grant the petition, vacate the Ninth Circuit's opinion, and remand." A
   governmental respondent that administers the challenged map conceding a
   GVR is one of the strongest positive cert signals short of a Solicitor
   General recommendation. The State's Garcia v. Hobbs brief (No. 25-901)
   asks for the same disposition, expressly tied to its Trevino request.
2. **The Court's Callais GVR practice is broad.** On May 11 and May 18, 2026
   it GVR'd Allen v. Caster, Turtle Mountain Band v. Howe, and the Mississippi
   State Board of Election Commissioners case "for further consideration in
   light of Louisiana v. Callais," over Justice Jackson's dissent that those
   cases presented only private enforceability, which Callais did not
   address. A loose fit between Callais and the question decided below has
   not stopped a GVR this year.
3. **The docket pattern fits a hold-and-GVR.** Both respondents waived; the
   Court nonetheless called for a response on March 25, five weeks before
   Callais came down, in this case and in Garcia on the same day. Calling for
   a response is the Court's usual step before disposing of a paid petition
   by GVR, and the timing is consistent with the Court preparing both
   petitions for disposition once Callais issued.
4. **The petition itself flagged Callais** (note 2) and the reply asks for
   more than a GVR but accepts one.

## What holds me back from going higher

1. **The dispositive holding below is Article III standing.** The Ninth
   Circuit held, unanimously and in a published opinion, that permissive
   intervenors whom the State did not join on appeal lack standing to
   challenge the Section 2 liability judgment. Callais says nothing about
   intervenor standing. A GVR asks the lower court to reconsider in light of
   a decision that may not bear on the ground it decided; the Court sometimes
   denies rather than issue a futile GVR.
2. **The Soto Palmer respondents oppose with substance.** Their BIO (read in
   full from `record/documents/brief-in-opposition.txt`) argues the remedial
   map was drawn with racial and political data removed, that the district
   court chose it for traditional-criteria reasons, that Trevino forfeited
   the equal-protection theory, that Ybarra ran unopposed under the new map
   and does not live in the district, and that Callais's reaffirmation of
   the predominance requirement confirms the result below. Those are real
   vehicle defects for plenary review and give the Court a principled reason
   to deny.
3. **The Court has passed on this litigation before.** It denied certiorari
   before judgment (No. 23-484) and a stay application (No. 23A862) with no
   noted dissent, and denied the May 2026 motion to expedite. No Justice has
   shown appetite for this dispute on its own terms.
4. The State's request comes from a Democratic administration whose own
   expert conceded the Gingles preconditions; the majority may weigh a
   state's GVR request less heavily than the SG's, and the liberal Justices
   may resist. But a GVR needs only five votes and the Callais majority has
   supplied them three times.

## Decomposition

- P(GVR) about 0.50, P(plenary grant) about 0.05, P(denial) about 0.45. Hence
  `probability` 0.55, `predicted_disposition` `gvr` (the modal outcome), and
  `summary-disposition-route` 0.9 conditional on a grant.
- `relist-increment` 0.35: GVRs mostly issue off the conference; a denial
  with an internal disagreement or a separate writing would add relists.
- `cvsg-increment` 0.03: no federal interest, and the Court will not delay a
  petition it is holding for a Callais disposition.
- `dissent-from-denial` 0.15: the denial grounds are threshold and
  fact-bound, not the kind that draws a dissent.
- `big_case_score` 0.45: high doctrinal stakes if argued, but the likely
  dispositions are a GVR or a denial of a one-region state legislative
  district case.

## Inputs and their status

- Snapshot `record/snapshots/2026-09-16.json`, 19 docket entries through the
  June 17 distribution; `context.json` as above.
- Provisioned documents: `questions-presented.txt`, `petition.txt` (39 pages),
  and `brief-in-opposition.txt` (the Soto Palmer respondents' 87-page brief
  with appendix). All extracted cleanly (`empty_text: false`, not truncated).
  The pipeline did not fetch the State's June 2 brief or the June 10 reply;
  I retrieved both from supremecourt.gov (forward mode, unrestricted) and
  they are the decisive inputs. The fetch tool's own PDF summaries were
  unreliable (one described a different case), so I extracted the text
  locally and read it directly.
- Callais itself I know only through secondary sources and the parties'
  characterizations; the CRS summary was unreachable (HTTP 403). The parties
  agree on what matters here: the Court updated the Gingles preconditions and
  reaffirmed the predominance requirement, and the State reads it as a
  framework change warranting remand.
- No outcome for this petition surfaced anywhere. The docket shows no entry
  after June 17, 2026, and SCOTUSblog lists it as pending.

## Where to discount me

The number rests heavily on one inference: that the Court treats a state
respondent's GVR request the way it treats a Solicitor General's. If the
Court instead reads the standing holding as making any remand pointless, the
right number is nearer the 17% anchor. I have no corpus prior for "respondent
concedes GVR after an intervening decision," so that inference is from
general practice rather than a measured rate.
