# Rationale

## Forecast and information set

I assign a **26% probability of any grant**, including a summary disposition, and predict **denial**. This is a forward cert-stage distribution cell, not the separate response-requested event. I used the case-level `record/snapshots/2026-11-05.json`, `context.json`, `documents/documents.json`, `documents/questions-presented.txt`, the petition, and the appendix. I did not retrieve this petition's outcome or subsequent history, and I do not independently know its disposition.

The snapshot shows **one distribution**, entered September 16 for the October 9, 2026 conference; a September 22 request for a response after respondents waived their response; and an October 13 extension of the response deadline to **November 23, 2026**. Thus the response is not yet due as of November 5. There is no provisioned opposition or reply, and I do not infer their arguments. The three provisioned document rows report nonempty, untruncated, non-OCR text. There is no CVSG. The three docketed supporting amicus briefs are from the Anglican Church in North America, former EEOC General Counsel and others, and the Roman Catholic Archbishop of Las Vegas. These are three briefs, not three procedural amicus orders. The empty `same-question.json` match list supplies no companion or hold signal and does not prove the absence of related litigation.

## Calibration

The authoritative frozen `context.cert_anchor.rate` is **0.051512996760685784**, approximately **5.15%**, for the `baseline` band under `sal-v7`, with a ten-Term lookback. I retain the supplied band, rather than promoting the case because the actual snapshot records a response request. The committed `metrics/statpack.md` uses the same salience version; its bracketed baseline reached rates for prior Terms 2017–2025 run approximately 4–6%. The frozen anchor, not the much lower terminal-baseline figure or the current incomplete Term, is my starting point.

The paid-segment signal cuts provide checks, not independent multipliers:

- Terminal relist bucket 0 has **n=10,204 resolved**, with 1.3% plain grants and 0.5% GVRs; bucket 1 has **n=2,532**, with 8.3% grants and 5.2% GVRs; bucket 2 has **n=495**, with 28.3% grants and 12.9% GVRs; bucket 3+ has **n=482**, with 23.0% grants and 14.1% GVRs. These describe where petitions ended, not the probability of progressing from this petition's current one-distribution state.
- The no-CVSG cut has **n=13,549 resolved**, with 4.1% grants and 2.3% GVRs, versus **n=164** with a CVSG, with 29.3% grants and 5.5% GVRs. This petition has not received that stronger signal.
- The 2+ amicus cut has **n=1,446 resolved**, with 18.2% grants and 4.5% GVRs. The zero-amicus cut has **n=11,109**, with 2.0% grants and 1.8% GVRs. Three supporting briefs make this petition more substantial than a routine private petition, but that marginal comparison overlaps with other selection signals and measures terminal counts.

The required broad corpus queries returned a few recent grants and denials. The grant sample included two cert petitions with two and three distributions, but also an emergency application; the denial sample consisted of emergency applications. These are neither topic-matched nor a random sample. I draw no numerical cert rate from them and do not substitute them for the statpack.

## Why move above the anchor?

**A squarely acknowledged disagreement.** The question asks whether neutral principles can support civil adjudication of internal religious-governance disputes outside property ownership. The Nevada opinion itself acknowledges disagreement and deliberately adopts the broader approach; this is not solely petitioners' characterization. See appendix **10a–13a**. The petition identifies contrasting circuits and state courts, including cases involving governance rather than merely commercial dealings. See petition **7–19**. That combination supports a substantial upward adjustment.

**A concrete constitutional setting and outside support.** The complaint challenges authority to create committees, the handling of membership records, and access to books; the governing documents impose religious qualifications. See appendix **3a–5a, 13a–15a**, and petition **4–6**. This places institutional governance near the center of the dispute. Multiple religious organizations' supporting briefs and a requested response reinforce the possibility of serious interest. A response request is nevertheless a low-threshold screening step, not evidence that four Justices favor review.

**The governing broad approach is real.** CourtListener located *Puri v. Khalsa*, 844 F.3d 1152 (9th Cir. 2017), opinion 4113720. Its discussion at 1165 expressly permits non-property disputes to be resolved by secular rules, subject to the ministerial exception and the bar on deciding religious controversies. This supports the Nevada opinion's account of that side of the disagreement. It does not establish that all of petitioners' contrasting cases present identical facts. A CourtListener search for the petition's newer *Lutheran Church* citation, 178 F.4th 193, returned no result; I therefore treat that asserted recent development as petition-sourced and do not give it a separate, independently verified boost.

## Why denial remains more likely

**The vehicle is less categorical than the question suggests.** The Nevada court specifically says religious qualifications for membership and management are uncontested and that the claims do not ask who should decide religious questions or whether the temple should be put into a trust. It views the action as enforcement of secular limits on corporate authority. See appendix **13a–15a**. A Justice could regard the case as an application of the religious/secular distinction, rather than a clean choice between competing constitutional rules. The property-transfer background also makes a rigid property/non-property line less tidy in practice.

**The underlying litigation is at an early stage.** The petition attacks a denial of dismissal followed by denial of an original writ of prohibition. Petitioners have substantial finality arguments: a separate original writ action under *Atlantic Richfield*, alternatively the *Cox Broadcasting* exception, and a stipulated stay. See petition **28–30** and appendix **5a–6a**. I do not treat lack of finality as established. Even so, the unfinished merits record and the possibility that discovery will avoid religious issues give the Court reasons to wait.

**The opposition is not yet available, and similar requests have failed.** The petition itself reports prior denials in *Belya* and *O'Connell*, while offering procedural distinctions. See petition **10–11, 29–30**. Those denials do not resolve the constitutional question, but they temper the assertion that recognizing the disagreement makes review probable. Without the requested opposition, neither the split's exact alignment nor the finality position has been tested here.

Putting these considerations together, 26% is a judgmental posterior, not a fitted estimate or a multiplication of overlapping signal cuts. It is slightly above the marginal 2+ amicus grant-family rate because the disagreement is expressly acknowledged and governance is central; it remains far below even odds because of the preliminary, fact-sensitive posture. I could move materially after a substantive opposition or a genuine post-consideration relist.

## Other elicited forecasts

The **98% redistribution probability** concerns at least one distribution beyond the currently recorded one. A requested response normally requires renewed distribution after filing or expiration of the response period; it does not mean a 98% chance of a genuine merits-driven relist. I give a **2%** chance of a new CVSG: the dispute is chiefly constitutional and private, without an identified federal-program or federal-party reason to solicit the government's views.

Conditional on a grant, I assign **7%** to disposition in the cert order and **93%** to plenary review. The record identifies no intervening controlling decision calling for a routine GVR, and an acknowledged doctrinal disagreement is more naturally resolved after briefing. Conditional on denial, I assign **16%** to a noted dissent or statement respecting denial. The per-Justice writer numbers are unconditional probabilities of authorship, not joining another Justice's writing; they place the largest small probabilities on Thomas, Alito, and Gorsuch. My modal prediction is an unsigned denial with no separate writing.

The **0.65 stakes score** reflects potentially nationwide consequences for religious organizational governance across faiths, not the likelihood of review or the value of this local property dispute.

## Retrieval limitations

No live Supreme Court docket refresh was needed. CourtListener was usable for the older authority but did not locate the newer citation. An attempted general-authority web search returned no usable result content. The default `uv` cache directory was read-only; setting `UV_CACHE_DIR=/tmp/uv-cache` and using `uv run --no-sync` resolved command execution without installing packages. None of these tooling limitations prevents a forecast from the provisioned record.
