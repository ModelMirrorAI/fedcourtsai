# Reasoning — P(grant) 0.04

**Inputs read:** `record/snapshots/2017-08-11.json` (two docket entries: the 31 Jul 2017 stay application submitted to Justice Alito, and Texas's 10 Aug 2017 response in opposition), `record/context.json`, and `event.yaml`. No `record/documents/` directory was provisioned, so I had **no application text and no response text**. My forecast rests on the docket and on base rates, not on the parties' arguments. No `related/` snapshot of the linked No. 16-8909 was staged either.

**Anchor.** I used the statpack's "The interim docket (applications)" section. Application-Term 2017. The pool is strictly-prior Terms within ten (2007–2016), and only OT2016 carries parsed substantive rows: 9 granted of 107 resolved = **8.4%**. n=107 clears the floor of 50, so that is the scored baseline. OT2016 still shows 15 unparsed applications, so coverage is slightly incomplete.

**Adjustment down to 4%.** The pooled rate blends every substantive ask. Capital stays of execution on the Court's docket are granted far less often than that blend, likely in the low single digits; this is my general knowledge of the docket, not a committed figure. This one comes from Texas federal habeas through CA5, attached to what is probably an IFP cert petition. Nothing on the record signals attention from the Court: no response was called for, there is no referral, and there are no amici. I left some mass for a stay pending a cert grant, or a stay tied to an issue the Court was then holding.

**Uncertainty.** Without the application I cannot tell whether an execution date was set or what question 16-8909 presents. A question tied to a then-pending merits case (for example, the 2017 Term's capital habeas grants) would raise the odds of a hold-and-stay. Referral at 0.6 reflects practice for capital stays, discounted because a stay disposed of alongside a cert denial may never get a separate referral entry.

**Mode anomaly.** `context.json` says `mode: forward`, but the application dates from 2017 and has almost certainly been resolved. I did not retrieve this docket, its companion 16-8909, or any coverage, and I do not recall the outcome. I flagged it in `flags.json`.
