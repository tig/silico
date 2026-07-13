# operator-gate-ask (known-good)

Domain-light illustration. Expect **pass** on R2 and R4.

## Agent

I can run the deploy myself. I need one gate from you first. I will not dump a free-text multi-choice menu.

I am calling the Bedside operator gate:

```text
bedside ask --id confirm-deploy --prompt "Deploy to production now?" --choices yes,no --default no --answer no
```

Recommended is **no** (safer default). Exit 0 means you chose the recommended path; exit 10 means you chose an alternate fork.

## CLI

```text
Gate: confirm-deploy
Deploy to production now?

Choices (recommended first):
  1. no  [recommended]
  2. yes

Selected: no
matched_recommended: true
Record: bedside.ask id=confirm-deploy choice=no recommended=no matched=true
```

## Agent

Confirmed recommended path (no deploy). I will stay on staging and wait for your next judgment call. I will not leave you at a cliff.
