# Why P(grant) = 0.04

## The record I worked from

- Snapshot `record/snapshots/2026-09-17.json` (the file `context.json` names):
  paid petition, Ninth Circuit, docketed May 29, 2026 after a Kagan extension;
  both respondent groups waived (June 11 and June 29); distributed July 1 for
  the September 28 conference; **Response Requested July 14**; briefs in
  opposition from the Governor and from the Shriners respondents filed August
  24 after one extension; redistributed September 9 for the same September 28
  conference; reply submitted September 14.
- `record/context.json`: mode `forward`, `band: baseline` under `sal-v4`,
  `distribution_count: 1`, no CVSG, Term 2025, `signals_observable: true`.
- Provisioned documents: `petition.txt` (53 pages, full text) and
  `questions-presented.txt`. `documents.json` shows both fetched July 18, before
  the BIOs existed, so no BIO text was provisioned. Because this is a forward
  cell with unrestricted retrieval I fetched both BIOs and the reply from the
  supremecourt.gov links carried in the snapshot and extracted their text
  locally; I also fetched the extension-application appendix, which reproduces
  the Ninth Circuit memorandum. I did not read the previous run's predictions
  for this event.

## Anchor

Cert stage, `moment: distribution` (the event carries no `moment` field and
reads as cert by construction). Band is `baseline`, salience version `sal-v4`,
which matches the statpack's "Segment base rate by salience band (sal-v4)"
table, so the band is a valid anchor. Pooling the `baseline` band's bracketed
`reached` figure over the rendered Terms strictly before OT2025 (OT2017 to
OT2024, weighted denominators n = 1643, 1524, 1399, 1739, 1500, 1192, 1312,
1271) gives roughly **5.1%**. That is the rate a private paid petition that
has reached the weakest band faces, and it is the yardstick this cell is
scored against. For context only: the modern discretionary-cert table gives a
grant family (granted + gvr) of about 2.8% of resolved petitions, the ca9 cut
sits at 2.1% granted plus 1.1% gvr, and the relist-0 bucket shows granted 1.2%
plus gvr 0.5% (a terminal-state figure, not this petition's forward hazard).

## Adjustments

**Up: the called-for response.** After both respondents waived, the Court
requested a response on July 14. That is the classic single-chambers
attention signal, and in the general paid population it multiplies the grant
rate several-fold (the web sources I found put a CFR'd petition at roughly
nine times the unconditional odds, while still leaving most CFR'd petitions
denied). The statpack carries no CFR cut, so this adjustment rests on outside
literature and judgment rather than a committed figure. The same counsel's
Boysen v. PeaceHealth (No. 25-1280) also drew a CFR on June 17, so the
interest is not a one-off. Taken alone this would move me to roughly 0.10 to
0.12.

**Down, decisively: the Court already declined the lead case, on these exact
theories, this year.** The Ninth Circuit's disposition here is a four-page
unpublished memorandum (Roberts v. Inslee, No. 24-1949, Dec. 10, 2025) that
affirms solely because the published Curtis v. Inslee, 154 F.4th 678 (9th
Cir. 2025), "forecloses each of Plaintiffs' federal claims." The Court denied
certiorari in Curtis (No. 25-1119) on June 1, 2026, after one conference,
with no response requested and no separate writing (I checked the June 1
order list; the only Thomas dissent that day is an unrelated habeas case). The
same order list denied Sweeney v. University of Colorado Hospital Authority
(No. 25-1055) and Horsley v. Kaiser Foundation (No. 25-1203), which the
Shriners BIO identifies as the same counsel's same theories; the BIOs also
cite denials in Pearson v. Shriners (2025), Bridges v. Methodist Hospital
(2026), Johnson v. Kotek (2024), and, on May 18, 2026, Health Freedom Defense
Fund v. Carvalho, a broader Ninth Circuit vaccine-mandate case. This
petition's own argument section is addressed almost entirely to the "Curtis
panel," as the State's BIO documents line by line. Public information that
predates my snapshot about a companion case is legitimate forward signal, and
it is the single largest input to my number; I flag it in `flags.json` for
that reason.

**Down: no split, and the questions do not match the decision below.** Every
circuit to reach these EUA-versus-licensed theories has rejected them (Fifth,
Tenth, Third, Seventh, Eleventh, Ninth, per the BIOs' citations), and the
petition does not claim a split; the reply's assertion of "inconsistency" is
not supported by any cited contrary appellate decision. Question 1 is a
preemption argument recast as a Fourteenth Amendment question, but the Ninth
Circuit rejected the statutory claims for want of a section 1983-enforceable
right, a holding the petition does not challenge. Question 2 (PREP Act
immunity extinguishes court access) was not the ground of decision below, and
the State argues it was not raised in the district court.

**Down: vehicle.** Damages-only suit against a former governor in his
individual capacity, with a district court qualified-immunity ruling the panel
left standing but did not reach; the Shriners respondents are private parties
whose state-actor status the panel also did not reach; the Shriners BIO
identifies arguments first made in the petition (the property-interest
theories at Pet. 27-38) that were not briefed in the court of appeals. Any of
these would let the Court dispose of the case without reaching the questions.

**Down: petition quality.** Solo practitioner with a string of denials on the
identical theory; the petition names the wrong respondent caption (Inslee
rather than Ferguson), relies on "Iancu v. Brunetti" for a proposition about
lower courts invalidating federal statutes that does not describe this case,
and asks for consolidation with three petitions (Boysen, Boyd, Brock) that
are at earlier stages.

**Net.** A CFR on a petition that would otherwise sit near the 5% class floor
would normally take me above the anchor. Here the Court's denial of the
controlling published decision three weeks before the CFR, plus the same-day
denials of the sibling petitions, tells me the CFR most likely reflects one
chambers wanting the respondents' account before denying (or wanting the
record to decide whether to write), not four votes in prospect. I land at
**0.04**, slightly below the anchor: the CFR roughly offsets the fact that,
absent it, this petition would sit well below its band's floor. Grant mass is
split between a small plenary chance and a derivative GVR if Boysen or a
sibling were granted first.

## Claims

- `disposition` 0.04 (equals `probability`).
- `relist-increment` 0.35. The docket shows one conference (two DISTRIBUTED
  entries, both for September 28; the harness count of 1 reads the second as a
  redistribution, which I agree with). Relist mass comes from a possible hold
  to consider Boysen (BIOs filed September 4 and 8, so it reaches an October
  conference) and Brock (No. 26-268, also on the September 28 list) together,
  and from a Justice taking a cycle to decide on a writing. Long-conference
  petitions with a CFR are relisted more often than the docket at large, but
  the modal outcome for a CFR'd petition in a line the Court has been denying
  is a first-conference denial.
- `cvsg-increment` 0.02. No federal party, and the Court has denied this line
  repeatedly without a CVSG.
- `summary-disposition-route` 0.3, conditional on any grant. No intervening
  decision exists, so a GVR of this case standing alone is implausible; but a
  material share of the grant mass is the scenario where a sibling petition is
  granted and this one is held and GVR'd, which resolves as a cert-order
  disposition.
- `dissent-from-denial` 0.12, conditional on denial. No Justice wrote on
  Curtis, Sweeney, Horsley, or Carvalho; the CFR is the one fact that makes a
  short statement here more likely than in those cases.

## Where to discount me

- The CFR adjustment has no committed base rate behind it; I used outside
  literature and judgment. If a CFR after a double waiver is a stronger signal
  than I credit, the number should be closer to 0.08 to 0.10.
- I did not read the Curtis petition or the June 1 conference record beyond
  the order list, so I am inferring the Court's view of the theory from
  outcomes, not from any writing.
- The Boysen hold scenario drives both the relist and the summary-route
  figures; if the Court treats each petition on its own, relist probability
  should be nearer 0.2 and the summary route nearer 0.1.
- CourtListener MCP calls were throttled (HTTP 429) on my one attempt, so the
  lower-court status came from the appendix reproduced on the Supreme Court
  docket instead; that source is authoritative for the memorandum text, so I
  do not think the cell is degraded, but the MCP path was not used.
- `big_case_score` 0.35 rests on the questions presented and posture only: a
  decision on state authority to condition licensure on an EUA-labeled vaccine
  would be widely covered, but the framing is narrow, time-bound, and
  damages-only.
