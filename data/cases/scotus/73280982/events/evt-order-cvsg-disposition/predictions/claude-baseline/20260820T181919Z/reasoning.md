# Rationale — claude-baseline, evt-order-cvsg-disposition, run 20260820T181919Z

**P(grant) 0.45.**

**Anchors (committed statpack, corpus vintage as committed in
`metrics/statpack.md`).** My cell's frozen context carries `band: high` under
`sal-v3`, matching the statpack's band table version. Pooling the high band's
bracketed `reached` rates over the Terms strictly before this case's own
(OT2017–OT2024, all rendered rows preceding 2025): weighted numerators sum to
≈439 grants over n=1,074 reached-band petitions, a pooled anchor of **≈0.41**.
That is the yardstick my skill is scored against. The CVSG cut — the anchor
this moment's prompt directs me to — shows resolved CVSG'd paid petitions at
**denied 62.0%, granted 29.4%, gvr 5.5%, dismissed 3.1%** (grant family
≈0.35). The two anchors bracket ≈0.35–0.41.

**Adjustments up from the anchor.** (1) The CVSG issued at the petition's
*first* conference — the Court flagged it immediately, not after relist churn.
(2) Petition-stage support is unusually strong: SIFMA + the Chamber of
Commerce, the Washington Legal Foundation, and Joseph Grundfest (former SEC
commissioner) as amici, with Jeffrey Wall (former acting SG) as counsel of
record. (3) The issue is recurrent and previously judged certworthy: the Court
granted *Leidos* (No. 16-581) on the Item 303 duty-to-disclose split and never
resolved it after settlement, and the petition ties QP1 to fresh tension with
*Macquarie* (2024). (4) A dissent below (Rawlinson, J.) and two claimed
circuit splits (First Circuit expressly disavowed on the misleading-omissions
prong; Fifth/Eleventh on Item 303's scope).

**Adjustments down.** (1) The BIO's vehicle objection is genuine: the Ninth
Circuit reversed a grant of a motion to dismiss and remanded — interlocutory
posture, no developed record, and the BIO argues the panel never actually
adopted the categorical rules the petition attacks. The SG frequently
recommends denial on exactly this ground, and the Court follows the SG's cert
recommendation most of the time. (2) Securities class actions settle; a
settlement before the SG files converts this cell to dismissed/withdrawn
(the CVSG cut's 3.1% dismissed is nonzero for this reason). Net: I land at
**0.45**, modestly above the pooled band anchor — the case-specific signals
(instant CVSG, elite support, pre-vetted issue) outweigh the vehicle risk, but
the interlocutory posture keeps me from going higher.

**Claims.** `disposition` restates 0.45. `relist-increment` 0.96: from the one
distribution shown, a further distribution is mechanical once the SG files;
the residual mass is pre-SG settlement/dismissal. `cvsg-increment` 0.01: the
CVSG is already on the docket, so the claim is vacuous for this cell and the
harness masks it. `summary-disposition-route` 0.08: the CVSG-cut's raw
GVR share of the grant family is ≈16%, but that pool is dominated by cases
where an intervening decision arrives during the CVSG's long pendency; here no
pending merits case bears on either QP, so I set it well below the cut.
`dissent-from-denial` 0.10 (banked, no published baseline): business-law
denials after an SG deny-recommendation are usually silent; a statement
respecting denial is the plausible tail.

**Uncertainty / discount guide.** The dominant unknown is the SG's
recommendation, many months out; my 0.45 is roughly a mixture over
SG-recommends-grant (grant very likely) and SG-recommends-deny-on-vehicle
(deny likely). I could not observe anything postdating 2026-06-02 and did not
seek this case's current status (forward-mode etiquette). Second discount: my
read of the "circuit split" strength comes from the petition and BIO
themselves, adversarial documents; I did not independently verify the cited
circuit authority beyond general knowledge of the *Leidos*/*Macquarie* line.
Third: the provisioned `questions-presented.txt` extract mis-cut the petition
(it carries a "reasons for granting" passage, not the QP section), so I took
the QPs from `petition.txt` directly — flagged in `flags.json`; no effect on
the forecast. The petition text is marked `truncated: true` in
`documents.json` (233 pages, appendix included), but the body I needed was
present; the BIO was complete (42 pages).
