# In re: Angela DeBose — CA11 No. 24-10350 — petition for writ of mandamus

**Prediction: denied. P(granted) = 0.01.**

## The event

A pro se petition for a writ of mandamus, docketed in the Eleventh Circuit on
2024-02-01 as an original proceeding (No. 24-10350), with IFP status pending
(motion to proceed IFP filed 2024-02-09). The petition arises from N.D. Fla.
No. 4:22-cv-00439. The cell is `forward` mode; the snapshot
(`record/snapshots/2026-07-11.json`) contains only the two opening docket
entries and no disposition.

## The governing standard

Mandamus is a "drastic and extraordinary" remedy reserved for really
extraordinary causes (*Cheney v. U.S. Dist. Court*, 542 U.S. 367 (2004); *In re
BellSouth Corp.*, 334 F.3d 941 (11th Cir. 2003)). The petitioner must show (1) a
clear and indisputable right to the writ, (2) no other adequate means to obtain
the relief, and (3) that the writ is appropriate under the circumstances. Courts
of appeals grant a small percentage of mandamus petitions even from counseled
parties; pro se IFP petitions succeed at rates well under one percent.

## Facts driving the outcome

- **Posture.** Original proceeding, pro se, fee not paid, IFP pending. Nothing
  in the record suggests the petition presents the kind of exceptional
  circumstance (e.g., privilege-destroying discovery order, clear usurpation of
  judicial power) that draws a grant.
- **The underlying case.** One web search (see `retrieval.md`) identified
  N.D. Fla. 4:22-cv-00439 as *DeBose v. University of South Florida Board of
  Trustees*, filed December 2022. In that case the magistrate judge recommended
  dismissal under 28 U.S.C. § 1406(a) for improper venue, finding that DeBose
  filed in the Northern District to intentionally circumvent an injunction
  order. This is consistent with DeBose's long-running, repeatedly unsuccessful
  litigation against USF (originally in the Middle District of Florida, where a
  filing injunction issued). A mandamus petition growing out of an attempt to
  relitigate enjoined claims in a new venue is an exceptionally weak candidate
  for an extraordinary writ.
- **Petitioner's track record.** DeBose has filed multiple prior appeals and
  original proceedings in the Eleventh Circuit in the USF litigation; none of
  her prior mandamus attempts succeeded (background knowledge, corroborated by
  the vexatious-litigant posture in the district record). Repeat pro se
  mandamus filers essentially never obtain the writ.
- **Base rates.** The committed statpack's ca11 cut is tiny (45 resolved cases,
  95.6% labeled `other`) and mostly historical, so it carries little signal;
  the corpus priors returned by `fedcourts query --court ca11` were likewise
  generic. The operative prior is the well-established legal one: appellate
  mandamus grant rates are in the low single digits overall and far lower for
  pro se IFP petitions.

## Probability and disposition

P(granted) = 0.01. Modal disposition **denied** — the Eleventh Circuit's normal
course with a meritless mandamus petition is a short order denying it (often
denying IFP as frivolous along the way). The main alternative is **dismissed**
(if IFP is denied and the fee never paid, or for a procedural defect); I put
roughly 25–35% weight there, but denial remains the single most likely label.
Grant or grant-in-part is remote (~1%).

No panel is identified in the snapshot, so no per-judge votes are predicted.

## Degraded retrieval

The configured CourtListener MCP server was down for this cell — every call
returned a session-store configuration error (`REDIS_URL is not set`). I
proceeded on the provisioned snapshot, the committed statpack, one
`fedcourts query` corpus pull, and one web search scoped to the underlying
district case. I did not seek and did not encounter this petition's own
disposition; the search snippet described only the district-court proceedings.
