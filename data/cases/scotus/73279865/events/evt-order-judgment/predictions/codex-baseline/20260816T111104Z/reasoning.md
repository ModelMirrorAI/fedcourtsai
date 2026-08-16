# Prediction rationale

I assign a 0.70 probability that the Court disturbs the Eleventh Circuit's judgment and predict a reversal. This is a merits-stage, grant-moment forecast: certiorari is settled, the salience band and two pre-grant distributions are not evidence about the judgment.

## Information set

I used the event definition, `record/context.json`, the pre-grant entries in `record/snapshots/2026-08-16.json`, the questions presented, the petition, and the March 6, 2026 cert-stage response. The question is solely whether the Veterans' Judicial Review Act displaced the district-court jurisdiction recognized in *Johnson v. Robison* for constitutional challenges to Acts of Congress affecting veterans' benefits. It is not whether 38 U.S.C. § 5313 is constitutional.

The provisioned record is not cleanly frozen at the April 6 grant moment. The latest snapshot includes later merits-calendar entries, and `brief-in-opposition.txt` concatenates the March cert response with a July 13 post-grant merits brief; `documents.json` also marks that combined artifact truncated. I used the cert response only and excluded the later merits filing and post-grant docket developments. The record therefore supports a grant-moment forecast from the petition and cert opposition, not a briefing-informed forecast. This is recorded in `flags.json`.

## Baseline and adjustment

The committed merits section supplies the applicable ten-Term, strictly-prior anchor. For grant Term 2025, the 2015–2024 window has rendered rows for 2017–2024; Terms 2015 and 2016 are omitted because they contain no parsed judgment. Those eight rows contain 359 disturbed judgments among 515 parsed judgments, a 69.7% disturbed rate. They report 515 parsed cases against 557 grants and 57 pool-guard exclusions. The sample clears the 30-case floor, but the parsed slice has selection and coverage limits: the gap includes pendency and parser gaps, and the rates are raw rather than reweighted.

The case-specific arguments keep me close to that 69.7% anchor. Johnson's strongest point is textual and precedent-based: *Robison* treated a constitutional attack on a statute as a challenge to Congress's decision, not a decision of the VA Administrator made "under" a benefits law, and the VJRA retained the core "decision ... under" formulation. The ordinary presumption favoring judicial review, the reenactment principle, and the current Court's reluctance to force constitutional claims through agencies reinforce a narrow reversal. The government also conceded an actual circuit conflict and described the case as a suitable vehicle, reducing the chance of a DIG.

The principal downward pressure is *Elgin*. The VJRA created a comprehensive route through the Veterans Court and Federal Circuit, expressly authorizes constitutional adjudication, broadened Section 511, and eliminated *Robison*'s concern that no judicial forum would exist. Johnson's claim ultimately seeks to undo his individual benefit reduction, making it less collateral than the structural claims in *Axon*. The cert response also points to legislative history saying district courts would no longer hear constitutional challenges to matters affecting benefits. Those considerations leave affirmance a substantial alternative and prevent a larger upward adjustment from the historical rate.

## Judgment and votes

I expect a narrow reversed-and-remanded judgment allowing Johnson to substitute a proper executive defendant and litigate district-court jurisdiction. My central lineup is 7–2: Chief Justice Roberts and Justices Alito, Kagan, Gorsuch, Kavanaugh, Barrett, and Jackson in the majority; Justices Thomas and Sotomayor in dissent. That lineup is uncertain. *Elgin* strongly informs the dissent forecast, but the preserved statutory language and *Robison* permit Justices who favor channeling in other schemes to distinguish it here. A narrower majority or an affirmance under *Elgin* are the main alternatives; a DIG, equal division, or mixed judgment is much less likely.

The biggest uncertainty is how the Court characterizes the claim: a freestanding facial attack on Congress's enactment favors Johnson, while a legal question necessary to the Secretary's benefits decision favors Congress. No post-grant merits advocacy or argument reaction informed the forecast.
