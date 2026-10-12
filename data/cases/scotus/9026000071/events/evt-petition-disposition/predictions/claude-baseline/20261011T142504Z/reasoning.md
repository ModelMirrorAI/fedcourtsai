# Rationale — P(any grant) = 0.27

**Anchor.** `record/context.json` puts this petition in band `elevated` under
`sal-v4`, which matches the statpack's band-table heading. I pooled the
bracketed `reached` rate for `elevated` over Terms 2017–2025, all strictly
before OT2026. The 2026 row adds only n=1. Pooled, the rate is about 17%
(n≈3,100). The relist-count cut over-states this petition's position: its
second distribution entry is a reschedule before the first conference, which
the statpack's own caption says inflates the count. A CVSG on *this* docket
(29% grant rate) does not apply either.

**Adjustments up.**
- The SG filed a brief in the companion Nwauzor petition (Sept 15, 2026),
  after a CVSG, recommending a grant on what it calls an "irreconcilable"
  split with the Third Circuit (*CoreCivic v. Governor of N.J.*). The reply
  says that brief refers to this case twice as a companion. I took this from
  the cert reply's characterization and did not read the SG brief itself.
- The Court rescheduled before the first conference. That usually means a
  Justice wants more time or wants to coordinate with a related matter.
- Counsel is Paul Clement, there is an amicus (FAIR), and similar state laws
  are pending in CA, NJ and CO.
- GVRs count as grants for this event. The most probable grant path is a hold
  followed by a GVR once Nwauzor is decided. My rough decomposition:
  - P(Nwauzor granted) ≈ 0.65.
  - Given that, this petition is granted outright ≈ 0.15, or held and later
    GVR'd ≈ 0.6 × 0.65 (Nwauzor reverses) × 0.7.
  - Plus a small path if Nwauzor is denied.
  - Total ≈ 0.28.

**Adjustments down.**
- The posture is interlocutory: a vacated preliminary injunction plus a remand
  on the comparator question.
- A second preliminary-injunction appeal is already pending in the Ninth
  Circuit, and GEO has a new ICE contract with different detention standards.
  The BIO presses these vehicle problems hard, and they are real.
- The BIO's "no split" argument is weaker: it is contradicted by the SG's own
  assessment in Nwauzor.

**Uncertainty.**
- The biggest is whether the Court holds this petition for Nwauzor (which
  helps a GVR) or simply denies it, given the interlocutory posture and the
  new appeal.
- I could not confirm Nwauzor's own conference date or status. A
  CourtListener docket search returned nothing, and the corpus `query` CLI
  takes no free-text search.
- The petition text is truncated in its appendix; the body was intact.

**Inputs read.** Snapshot `2026-10-11.json`, `context.json`,
`questions-presented.txt`, `petition.txt` (body), `brief-in-opposition.txt`
(QPs and vehicle/consolidation sections), `cert-reply.txt` (opening and
Nwauzor references), and `metrics/statpack.md` (band, relist and CVSG cuts).
