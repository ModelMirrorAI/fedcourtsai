# In re: Angela DeBose — CA11 No. 24-10350 (mandamus disposition)

## The question

Will the Eleventh Circuit grant Angela W. DeBose's petition for a writ of
mandamus? The docket (snapshot `2026-07-11.json`) shows an **original
proceeding** docketed 2024-02-01 as "Original Proceeding, Fee not paid
Mandamus," arising out of the Northern District of Florida, No. 4:22-cv-00439.
The cell is `forward` mode: no disposition appears on the record and I predict
as if undecided.

## Governing standard

Mandamus is a "drastic and extraordinary" remedy reserved for "really
extraordinary causes" (Cheney v. U.S. Dist. Court for D.C., 542 U.S. 367, 380
(2004); Will v. United States, 389 U.S. 90 (1967)). The petitioner must show
(1) no other adequate means to attain the relief, (2) a right to issuance that
is "clear and indisputable," and (3) that the writ is appropriate under the
circumstances. The Eleventh Circuit applies this test strictly and routinely
denies mandamus where ordinary appeal is available (e.g., In re Lopez-Lukis,
113 F.3d 1187, 1188 (11th Cir. 1997)). Appellate mandamus against a district
court is granted in only a small fraction of petitions filed, and the rate is
lower still for pro se petitions.

## Facts from the snapshot that drive the outcome

- **Original mandamus proceeding, not a merits appeal.** The only entries are
  the petition itself (2024-02-01) and the petitioner's own IFP motion
  (2024-02-09). Nothing on the docket suggests the court has ordered a
  response or referred the petition to a merits panel — the usual first
  signals that a mandamus petition has any traction. Under Fed. R. App. P.
  21(b), a court may deny a petition without ever ordering an answer, and
  that is the routine path for petitions like this one.
- **Pro se / IFP posture.** The fee is unpaid and IFP is pending; the
  petitioner filed both papers herself. Pro se IFP mandamus petitions are the
  weakest-performing class of filings in the courts of appeals. There is also
  a realistic secondary path to **dismissal** rather than denial: if IFP is
  denied (e.g., under 28 U.S.C. § 1915(e)(2) for frivolousness, or for
  failure to pay after denial), the petition is dismissed without reaching
  the merits.
- **Nothing indicates an extraordinary claim.** The record before me contains
  no signal (no stay motion, no government response, no expedited briefing)
  of the kind that accompanies the rare granted mandamus (clear jurisdictional
  usurpation, refusal to rule, disqualification error). The petition appears
  to challenge some ruling or inaction in a pending N.D. Fla. civil case for
  which the ordinary remedy is end-of-case appeal — the classic ground for
  denial under the "no other adequate means" prong.

## Base rates

The committed statpack's ca11 cut is thin (45 resolved cases: other 95.6%,
denied 2.2%, granted 2.2%) and is dominated by merits appeals labeled `other`,
so it says little about original mandamus proceedings specifically. A
`fedcourts query --court ca11` pull of resolved priors was similarly dominated
by `other`-labeled merits dispositions (19 of 20 rows). General knowledge of
appellate practice is more informative here: courts of appeals grant a low
single-digit percentage of mandamus petitions overall, and materially less for
pro se IFP petitions.

## Prediction

- **P(granted) = 0.02.** A grant would require a clear and indisputable right
  with no adequate alternative remedy; nothing in the record hints at that,
  and the base rate for this posture is a percent or two at most.
- **Predicted disposition: denied** (~70% likely), with **dismissed** the main
  alternative (~25%, mostly via the IFP/frivolousness path — § 1915(e)(2) or
  failure to pay the fee); granted or granted-in-part ~2%; other ~3%. "Denied"
  is the modal outcome because the Eleventh Circuit typically denies weak
  mandamus petitions on the merits of the Cheney test rather than dismissing
  them, even when IFP is granted.
- **No panel votes predicted**: the docket lists no panel, and mandamus
  denials of this kind are near-uniformly unanimous, so per-judge votes would
  add noise, not signal.

## Caveats

- The CourtListener MCP server configured for this cell was down (every call
  returned a server-side `REDIS_URL is not set` error), so I could not examine
  the underlying N.D. Fla. docket 4:22-cv-00439 to characterize what the
  petition challenges. The prediction rests on the provisioned snapshot,
  corpus priors, the statpack, and the governing legal standard. Given the
  overwhelming base rate against mandamus grants in this posture, access to
  the underlying docket would be unlikely to move the probability materially.
- The snapshot was last indexed 2024-02-14; the docket may have moved since.
  I predict from the provisioned record as instructed.
- I did not search for, and do not know, this case's actual outcome.
