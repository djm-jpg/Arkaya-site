# Platform pilot

Page: https://arkayarisk.com/platform-pilot

Arkaya connects governance and cybersecurity platforms with the insurers, MGAs and lenders who price and set terms for AI and other governance risks.

For governance and cybersecurity platforms

# See what your records can show an insurer.
Before a loss, not after one.

## What you send, and what you get back

You send: one record type. Illustrative, synthetic data; not any insurer's requirement

```json
{
"label": "synthetic sample",
"record": "agent-action",
"agent": "Agent-Pebble-01",
"action": "submit-payment",
"amount": "GBP 50,000",
"recipient": "Supplier-Cobalt-22",
"model": { "name": "Model-A",
"provider": "Provider-X",
"version": null },
"approvalRef": "approval-demo-01",
"at": "2026-10-21T10:02:00Z"
}
```

You get: a one-page findings note. Illustrative, synthetic data; not any insurer's requirement

### What this record type carries

- Who acted, and what they did: Carried

- Who approved it: Referenced

- Which model, and which version: Version missing

- What the agent looked up first: Not in this record type

- When it happened: Declared, not anchored
Plus one example event rebuilt from your records.

## How it works

- You send: One record type and a sample. Synthetic is fine.

- We map: Your record format into the open schema.

- We rebuild: One example event from your records.

- You get: One page: what your records carry, and what they don't.

## What it is not

It is not a certification or an endorsement, and it does not say any insurer will accept your records.
We do not design your records or tell you what to change. We report what is there.
If we have only translated a platform's records into the open format, we read them for an insurer only after telling the insurer before appointment and having the translation checked, before it is relied on, by a competent checker with no involvement in the work and no interest in the finding. No such checker is in place yet, so we do not currently read records we have translated. Where we have designed evidence or advised on it, we do not read it.

## Questions
[Ask about a platform pilot](mailto:djm@arkayarisk.com?subject=Platform%20pilot)

### Is this a certification?
No. It reports what your records carry and what they do not. It does not certify or endorse your platform, and it does not say any insurer will accept your records.

### Do you design our records?
No. We map what you produce. Changes to your format are your decision.

### Can we use a synthetic sample?
Yes. A synthetic sample in your real format is enough to start.

Arkaya does not advise on or place insurance, score organisations or certify them. Arkaya Risk Limited, registered in England and Wales, no. 17380022.
