# Why P(grant) = 0.25

**Anchor.** `record/context.json` freezes the band as `state` (sal-v4), with
distribution_count 2, no CVSG, Term 2026. The statpack's sal-v4 band table matches
that version. Pooling the bracketed `reached` figures for `state` over the Terms
before 2026 (2017–2025, as rendered) gives about 99 grants out of 421 weighted
petitions, or **~23.5%**. The relist-count cut (paid scored segment) agrees: bucket
2 shows 27.7% granted plus 13.3% GVR, and much of that GVR mass is
intervening-decision holds that do not fit this case.

**Adjustments.**
- Up: the petition has a genuine relist after its first conference (10/9 → 10/16).
  In current practice the Court relists before nearly every grant. A state AG is
  the petitioner, 16 States filed as amici, and the decision below strikes down a
  state statute on First Amendment grounds. Several Justices have shown interest
  in where compelled speech ends and disclosure begins (*NIFLA*, *303 Creative*).
- Down: there is no real split. The BIO (read in full in its key sections) shows
  that *McClendon* (CA11) agrees with the decision below, and *Arnold* (CA5) is a
  pro se SORNA registration case. The practical stakes are small, one statute
  enforced one night a year. The injunction has been narrowed on remand to this
  respondent alone. The district court held in the alternative that the mandate
  fails lesser scrutiny too, on a trial record, which weakens the claim that this is
  a clean vehicle. A relist is also consistent with a dissent from denial being
  prepared.

These roughly offset, so I stay near the anchor at 0.25.

**Other claims.** relist-increment 0.5: a grant at the 10/16 conference or a clean
denial both end the distributions, while a dissent from denial or a hold for a
second look adds more. cvsg-increment 0.03: there is no federal party, and a CVSG
after a relist is rare. summary-disposition-route 0.10 given a grant. Dissent from
denial 0.40 given a denial, because a relist followed by a denial often produces
a writing.

**Inputs used.** Snapshot `2026-10-13.json`, `questions-presented.txt`, the
petition's introduction and reasons, the BIO's split and vehicle sections, and
`metrics/statpack.md`. I did not read the provisioned cert reply
(cert-reply.txt). I did no live retrieval and did not check whether the 10/16 conference
has produced anything (it has not yet occurred as of the snapshot).

**Where to discount me.** I cannot tell from the docket whether the relist reflects
grant interest or a writing, and that is the main driver of the uncertainty.
