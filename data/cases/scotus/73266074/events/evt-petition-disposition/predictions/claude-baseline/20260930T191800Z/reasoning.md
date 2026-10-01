# Reasoning — why 0.08 and not another number

## What I read

Provisioned inputs only, plus three retrievals logged in `retrieval.md`. Snapshot `record/snapshots/2026-09-30.json` (as-stored, no cutoff; forward mode). `record/context.json`: band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, Term 2025, paid docket. Documents: `questions-presented.txt`, `petition.txt` (46 pages), and `brief-in-opposition.txt`, which concatenates both briefs in opposition (the State of California's, filed by the California Solicitor General's office, and the College respondents', filed by Cooley). None was empty or truncated. I did not read the earlier predictions under this event and forecast from this record alone.

## Anchor

Cert-stage cell with a frozen band, so the anchor is the `elevated` band's bracketed `reached` grant rate pooled over Term rows strictly before 2025 in the statpack's sal-v4 segment table. Pooling OT2017 through OT2024 (weighted n = 2810) gives about 17%. Sanity checks beside it: the relist-count cut's bucket 1 (two distributions) shows a grant family of roughly 13% (8.2% granted plus 5.1% GVR); the state-court originating-court rows in the pack run at or near zero grants, though those are small buckets.

## Adjustments down (the bulk of the move)

- **No conflict alleged.** The petition seeks error correction of a published California intermediate appellate decision that the California Supreme Court declined to review. Both BIOs lead with this and the petition does not answer it.
- **Vehicle problems.** The Court of Appeal deemed the damages theory forfeited and the petitioners raised it squarely only on rehearing; the College BIO also disputes standing of the "purported descendants." The case arrives on a demurrer, so the record is thin. The BIOs make a plausible case that the 1878 Act contains no covenanting language, giving the Court a narrow state-law-flavored reason to stay out.
- **No amicus support at all**, despite the petition's claim that public-private partnerships nationwide are threatened. For an "exceptionally important" case with a politically salient renaming story, the silence is telling.
- **Doctrinal shape.** The reserved-powers holding below rests on East Hartford, Newton, Stone, and Winstar; the Court would have to narrow century-old precedent to reach for the petitioners. The Bill of Attainder theory concerning a person dead since 1893 is novel, and the Court has not taken a merits attainder case in over forty years.
- **Two distributions overstate relist interest.** The first distribution ended in a call for response after both respondents waived; the October 16 conference is the first at which the Court will consider the petition fully briefed. So the bucket-1 figure is optimistic for this docket.

## Adjustments up (why not lower)

- The call for response after a double waiver means at least one chamber found the petition worth a closer look; that is the signal that put the docket in the `elevated` band, and it distinguishes this from the ordinary paid petition.
- The Contract Clause and Bill of Attainder Clause are constitutional provisions some Justices have expressed interest in revisiting, and the underlying facts (a state statute declaring a historical figure a financier of massacres, then stripping a hereditary board seat) have an unusual shape that could attract a vote or two.
- Petitioners are represented by counsel with Supreme Court experience, and the Center for American Liberty backs the litigation, so the petition will be pressed competently.

Net: 0.08, well under the band anchor, above the bare paid-petition rate.

## Claims

- `disposition` 0.08, the top-level number.
- `relist-increment` 0.30: from a two-distribution state, the next conference is the first fully briefed one. Most petitions denied after a call for response are denied at that conference, but a relist for a statement or a further look is a real minority outcome.
- `cvsg-increment` 0.02: no federal interest.
- `summary-disposition-route` 0.08 conditional on grant: no intervening decision, questions too novel for a per curiam.
- `dissent-from-denial` 0.15 conditional on denial: a short statement from a Contract Clause-minded Justice is possible, but the forfeiture and no-amicus posture cut against it.

## Uncertainty and where to discount me

The main uncertainty is what prompted the call for response. If it came from a Justice with a real interest in the attainder question rather than a clerk-level flag, the grant probability is meaningfully higher than I have it. I also could not test the relevant conditional base rate: the statpack has no cut for petitions where a response was called after a waiver, and the corpus query surface has no subject-matter filter for SCOTUS rows, so the comparison class is my judgment rather than a table. The corpus statpack was read as committed; I did not refresh it and quote no corpus vintage beyond what `metrics/statpack.md` carries.

I know of no disposition of this petition and none surfaced in retrieval; the web search results were the docket page, the state-court opinions, and older news about the state-court proceedings.
