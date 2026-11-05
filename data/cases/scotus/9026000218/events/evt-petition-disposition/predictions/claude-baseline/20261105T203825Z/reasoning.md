# Why P(grant) = 0.12

**Anchor.** `context.json` freezes band `baseline` under sal-v7, with
`cert_anchor.rate` = 0.0515 (pooled over 10 prior Terms). This petition's facts
already sit well above the typical baseline-band petition:

- **Response requested after a waiver** (Sep 29, 2026, after Louisiana waived
  on Sep 16). This means some chambers took a closer look. No committed table
  conditions on it. In my judgement it roughly doubles the paid baseline, but
  most such petitions are still denied.
- **Four amicus briefs** were filed: Innocence Network, Orleans Public
  Defenders, Cato Institute, and fifteen Louisiana Brady exonerees. The
  statpack's amicus `2+` bucket (n=1446 resolved) shows granted 18.2% and gvr
  4.5%. That compares with 0-amicus at 2.0% / 1.8%. This is a marginal split
  that partly overlaps the response-requested signal, and Cato plus innocence
  groups file often.
- **Strong counsel** (Hogan Lovells and the Southern Center for Human Rights) and
  a **history in the subject area**: the Court has corrected Louisiana Brady
  rulings before (*Kyles*, *Smith v. Cain*, *Wearry v. Cain*, the last a
  summary reversal). The petition asks for summary reversal in the
  alternative.

**Adjustments down.**
- The relist-count cut shows that petitions with a single distribution and no
  relist rarely end up granted. I don't use the relist-0 bucket as the anchor,
  though, because a response request will produce another distribution.
- The question is fact-bound error correction. The claimed split (pet. Part
  II) is a disagreement over how a standard was applied, not a conflict over
  what the standard is. The Louisiana Fourth Circuit opinion (App. 3a–7a)
  explicitly recites Kyles/Bagley and "undermine confidence." Its use of
  "sufficiently strong" other evidence comes from *Smith v. Cain*'s own
  language. That gives the State a ready answer that the courts applied the
  correct test. A dissenting judge below (Jenkins, J.) and a Louisiana Supreme
  Court justice (Griffin, J., would grant) did see a sufficiency test.
- The suppressed evidence is less striking than in *Wearry*. None of it comes
  from someone who saw the shooting and identified a different person, and two
  other trial eyewitnesses identified Matthews. The current Court has shown
  less appetite for Brady summary reversals than the 2016 Court did. *Wearry*
  drew dissents from Justices Alito and Thomas.
- Collateral posture: a 1992 conviction with multiple earlier post-conviction
  rounds, and a prior cert petition was denied (No. 20-7311).

**Net.** Starting from about 5%, the response request, the amicus support and
Louisiana's history push me to about 15–20%. Fact-bound error correction and a
lower court that used the right words pull me back to **0.12**. That figure is
the whole grant family, including a GVR or summary reversal. Because of the
summary-reversal framing, I put P(summary disposition | grant) at 0.55.

**Other claims.** Relist-increment 0.96: a requested response essentially
guarantees another distribution once it is filed or the deadline passes. The
small residual covers withdrawal or a mootness event. CVSG 0.01: no federal
interest. Dissent-from-denial 0.30, because this kind of case often draws a
writing from Justice Sotomayor or Justice Jackson. Order-writers is consistent
with that figure, with small weights on Justices Alito and Thomas for a
possible dissent from a summary reversal.

**Inputs used.** Snapshot 2026-11-05.json, petition.txt (full), questions-
presented.txt, and appendix.txt (lower-court opinions, partly read; it is
truncated). No BIO exists yet, since the response is due Nov 30, 2026.
`same-question.json` lists no matching petitions. `metrics/statpack.md` sections
read: band table, relist, CVSG and amicus cuts. Corpus queries returned nothing
useful (sparse citation column; one era-flag usage error). I did not use the
CourtListener MCP server.

**Where to discount me.** The effect of a response request has no committed
base rate, so that step is judgement. I did not verify from the record any
recollection of particular Justices' writings in earlier Louisiana Brady
denials.
