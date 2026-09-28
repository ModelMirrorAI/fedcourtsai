# Rationale

## Record and limits

This is a forward, cert-stage arrival prediction for Beckie Boddie v. United
States District Court for the District of Maryland, No. 26-424. I read
`record/snapshots/2026-09-29.json`, the filename specified by `context.json`,
and the event definition. The September 29 date is the provisioned exclusive
date boundary, not a claim that I observed proceedings after September 28.
The snapshot records docketing on September 28, 2026, a petition filed July 6,
a response due October 28, and a Fourth Circuit decision dated April 9 in
No. 26-1130. It identifies a paid, noncapital petition. There are zero
distributions and no CVSG; that is the arrival moment, not missing trajectory.

No `record/documents/` directory was provisioned. I therefore read no petition,
questions presented, opposition, or lower-court opinion. A CourtListener MCP
opinion search restricted to the Fourth Circuit, No. 26-1130, before September
29 returned no results. That is a retrieval gap, not evidence that no opinion
exists. General web attempts concerning the Court's rules returned no usable
content. I did not retrieve this petition's disposition or subsequent history,
and I do not know its outcome.

## Anchor and adjustment

The frozen context is `baseline`, `sal-v4`, docket-number Term 2026. Boddie is
the private petitioner; the federal respondent and its Solicitor General
representation do not put this petition in the federal-petitioner class.
The matching anchor is the private class's bracketed `baseline` reached rate,
not the terminal baseline rate or a zero-relist bucket.

I used the committed `metrics/statpack.md` and the exact corresponding fields
in `metrics/statpack.json`, whose last commit is `808f812e9`, September 28,
2026 at 12:02:50 UTC. This identifies the artifact vintage, not a newly polled
corpus or a verified per-case pull date. Pooling every shown prior Term,
2017–2025, gives 638 estimated grants over 12,720 weighted resolved petitions:
**5.016%**. The calculation sums each baseline segment's
`prefix_weighted_resolved * prefix_est_grant_rate` and divides by the sum of
`prefix_weighted_resolved`. Term 2026 is excluded. The denominator is a
denial-reweighted estimate, not 12,720 individually inspected petitions.

My **1% probability of any grant** is a judgmental downward adjustment, not a
measured pro se subgroup rate. The petitioner is also the only listed attorney
on her side, suggesting self-representation. Naming the district court as
respondent suggests litigation about judicial action or procedure, but does
not establish mandamus, jurisdictional defects, or the underlying issue.
These limited clues make an individual procedural grievance my working
hypothesis rather than a demonstrated broadly recurring issue. The adjustment
is uncertain and should be discounted accordingly: unavailable questions
presented are not affirmative evidence that no conflict exists. I retain a
nonzero chance of a substantial issue or grant-and-remand route. Denial is the
categorical prediction; 99% nongrant is not a claim that every nongrant must
be a denial rather than a dismissal or withdrawal.

## Other elicited probabilities

The statpack's paid-segment relist and CVSG cuts describe terminal populations,
not forward transition hazards. I consulted their shape but did not use their
zero-relist rate as an arrival anchor. Most resolved petitions in that cut
end without a relist; CVSG cases are a small, selected group with much higher
grant rates. Neither table measures this petition's next-step probabilities.

- **Distribution increment, 97%:** the frozen count is zero, so the first
  distribution already satisfies this claim. This is not a prediction of a
  97% chance of a second conference. My modal path is one distribution total.
- **CVSG increment, 0.2%:** no CVSG is recorded, no substantive reason for a
  special invitation is available, and the snapshot already lists the
  Solicitor General for the respondent. This is a subjective low hazard,
  not the terminal no-CVSG bucket restated.
- **Summary route conditional on grant, 25%:** no intervening authority or
  clear error is established by the available record. Conditional on the
  rare grant, I favor plenary consideration, retaining a meaningful summary
  route because the actual legal question is unknown. This is not a rate
  inferred from historical `granted` versus `gvr` labels.
- **Separate writing conditional on denial, 0.3%:** no issue-specific signal
  suggests an exceptional public statement. I forecast none, without
  attributing an unobservable cert vote to any Justice.

The stakes score is null because the legal issue is unavailable, not because
a low grant probability makes the case unimportant. Timing and the conditional
grant route are especially uncertain on this docket-only record.
