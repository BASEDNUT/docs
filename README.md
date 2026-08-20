# BASED NUT — Docs

The BASED NUT documentation.

## Layout

```
based-nut/   v1 — 19 pages from docs.basednut.com (GitBook originals, untouched reference)
v2/          v2 — 33 pages: v1 carried forward + portal content + agent layer
gate_v2.py   leak gate — diff-based scan of new content, runs before every push
llms.txt     v1 machine-readable index
```

## v2 = v1 + portal + agents

* All 19 v1 pages carried **verbatim** — tabs, figures, lore, formatting intact
* Portal content ported to docs form: Arb Bot Builder (3 pages), RWA (Environmental Balance Sheet, US Nut Economy), Great Nut War battlefield, staking, liquidity tree, FAQ, token catalog
* Orchard depth pages: NUT Doctrine, SNUT Mechanics, pNUT Mechanics — the site's own deep content, documented
* Corrections where on-chain truth has moved: SNUT fee 6% → 1% (2026-07-30, tx `0x7dc59b67…`)
* Smart Agents page fulfilled: Peanutoshi, x402 machine-payable data services, IRIS public data plane
* Entry index at `v2/index.md`

## Rules

- Public-safe content only. No secrets, no internal plans, no unreleased designs, no ops internals.
- Leak-check gate runs before every push (diff-based: new content only).
- v1 is the canonical base — v2 extends and corrects, never discards.
- Every v2 fact traces to the deployed portal (orchard.basednut.com) or v1 GitBook — no invented numbers.
