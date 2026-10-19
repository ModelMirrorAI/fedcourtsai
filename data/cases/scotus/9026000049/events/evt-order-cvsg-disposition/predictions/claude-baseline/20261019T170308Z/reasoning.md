# Reasoning — P(grant) = 0.55

**Inputs read.** Snapshot `2026-10-19.json` (19 docket entries through the 10/19
CVSG order) and `record/context.json` (forward mode; band `high` under sal-v4;
distribution_count 3; cvsg_date 2026-10-19; term 2026). Provisioned documents: the
QP section, the petition (182 pp., truncated at the cap; I read the statement and
the reasons for granting), the BIO (48 pp.) and the cert reply (19 pp.). None had
`empty_text`.

**Anchors.**
- Salience band `high`: the sal-v4 table's column matches my context. Pooling the
  bracketed `reached` rates over Terms 2017–2025 (the 2026 row has no `high` entry)
  gives about 35.4% (weighted n≈971).
- The statpack's CVSG-status cut (paid scored segment, resolved CVSG petitions):
  granted 29.3% + GVR 5.5% ≈ 35% for any grant, n=164. The two anchors agree at
  about 0.35.

**Adjustments up.**
- The SG's likely answer. The United States already told the Eighth Circuit, as
  amicus supporting rehearing en banc, that SF2340 furthers the purposes of federal
  immigration law. It also abandoned its own challenge to the law. A grant
  recommendation is therefore much likelier than the usual CVSG mix. Historically,
  petitions with a grant recommendation are granted at well above the
  CVSG-population rate.
- Signals of importance. Judge Stras, joined in part by Judge Loken, dissented from
  denial of rehearing en banc and called QP 2 "about as important as it gets."
  Amicus briefs came from a state coalition (Oklahoma et al.), Senator Cruz et al.,
  and others. Several states have similar laws. The Fifth Circuit's Texas SB4
  litigation (en banc dismissal on standing; a stay of a later injunction) is
  leaving the states under different enforcement regimes, though the BIO is right
  that this is not a merits split.
- The Court rescheduled the petition twice before issuing the CVSG. That suggests
  at least one Justice was focused on it.

**Adjustments down.**
- No merits split: every court to reach the issue has found such laws preempted.
  The petition's standing split is contested and arguably factbound.
- Vehicle problems: a preliminary-injunction posture, plus a limited remand to
  consider narrowing the injunction under *Trump v. CASA*. The SG could recommend
  waiting for a final judgment, or for the Texas litigation, rather than granting
  now.
- Issuing a CVSG rather than granting means four votes were not yet there on
  10/16.

Net, I move from about 0.35 to 0.55. If the SG recommends a grant, my conditional
estimate is about 0.7. If the SG recommends denial or a hold, it is about 0.15. I
put roughly 70% on a grant recommendation.

**Increments.** relist-increment 0.9: a CVSG petition is almost always
redistributed after the SG files, and the residual covers withdrawal or mootness.
cvsg-increment 0.02: vacuous, since the CVSG is already on the docket.
summary-disposition-route 0.08: no intervening decision. dissent-from-denial 0.35,
conditional on denial: the issue is high-salience to several Justices, but a denial
after an SG recommendation against review often draws no writing.

**Uncertainties.** The biggest is the SG's position and its timing. A brief
recommending denial would move this a long way. I did no live retrieval, so I have
not checked for developments after the petition: the Texas litigation, any
amendment of SF2340, or the CASA remand. My knowledge of the SG's grant-recommendation
follow-through rate comes from general knowledge, not from a committed figure.
