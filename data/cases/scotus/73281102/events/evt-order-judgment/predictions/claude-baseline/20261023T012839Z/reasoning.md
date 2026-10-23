# Why P(disturbed) = 0.84

**Inputs used.** I read the provisioned snapshot `2026-06-02.json` (date cut at 2026-06-02; forward mode). I
also read the provisioned cert-stage documents: the questions presented, the petition (pro se), the
government's brief in opposition, and the cert reply (by Davis Polk counsel). No merits briefs were
provisioned. That is correct for a `moment: grant` cell, so this forecast rests on the cert-stage record
plus general doctrine. I made no MCP or corpus-query retrieval.

**Anchor.** The statpack's "The merits docket (granted cases)" section publishes an `excluded` count, so it is
quotable. The grant was entered on 2026-06-01, which puts it in grant Term OT2025. The pool is grant Terms
2015–2024, strictly prior. The table renders only 2017–2024 for this window, since Terms with no parsed
judgment are omitted. Those Terms pool to 360 disturbed of 516 parsed, **≈ 69.8%**. Parsed coverage is near
complete across these Terms (e.g. 73/74, 75/77), and the pool is well above the 30-judgment floor. This is
the bar my skill is scored against.

**Adjustments up:**
- **The government half-concedes the merits.** The Solicitor General's BIO says that if the Fifth Circuit
  required accelerated release for §2241 cognizability, that "would be inconsistent with" *Jones v. Hendrix*.
  The BIO opposed only on vehicle grounds: unexhausted claims and intracircuit tension with *Cheek*. Nobody
  of consequence is defending the rule below on its merits.
- **A court-appointed amicus in support of the judgment below** appears in the snapshot's attorney list.
  The Court makes that appointment when the respondent will not defend the judgment, which is strong
  evidence that the Court expects to rule against it. The attorney list is not date-cut the way the
  proceedings are, so the appointment probably postdates my cutoff. Forward-mode retrieval permits
  post-cutoff material, but I weight it modestly for that reason. The government's BIO concession already
  points the same way.
- **A lopsided split.** The petition and reply cite a 9–1 alignment of circuits against the Fifth Circuit's
  *Melot* rule. The Court also granted after a response request and three distributions, and it rewrote the
  QP to a clean statutory question.
- Amici on the petitioner's side include the First Step Act's congressional sponsors, NACDL/NAFD, FAMM and
  habeas scholars.

**Adjustments down / uncertainty:**
- **Whether this is "core" habeas is a real question.** Transfer to a halfway house does not end custody.
  Some Justices (I'd guess Thomas and Alito) may accept the amicus's argument that this is a
  conditions-or-place claim outside §2241. That keeps me away from 0.9+.
- **Vehicle risk.** The exhaustion finding could support a DIG, which would count as undisturbed. I put it at
  roughly 3–5%.
- My judgment *label* (reversed vs vacated) is close to a coin flip. Both are disturbed, so the label
  does not affect the probability.

Net: about 0.70, raised to **0.84**. Votes and their 7–2 split are much lower-confidence than the
direction. big_case_score 0.45: important to a high-volume class of prisoner litigation, but a
remedial-vehicle question.
