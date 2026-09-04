🔬 Research — nutUSD Mainnet Fork (Experiment XI)

Eleventh experiment in the nutUSD research series — production equivalence. The preceding series ran on Sepolia against mock tokens and controlled feeds; this one moves to a fork of Base mainnet: the live cbBTC/USDC 38.5% market, the real Chainlink feeds, real USDC and cbBTC — and the 2-leg oracle candidate, cbBTC/USD ÷ USDC/USD, deployed through the real MorphoChainlinkOracleV2 factory. A funded whale walks the full roundtrip at the exact borrow maximum, and the market returns to zero. Fork receipts are fork-local by construction; the candidate’s deployment is proven by config readback and the factory’s registry flag — real mainnet carries zero code at the same address.

## Questions

| # | Question | Verdict |
|---|---|---|
| E1 | Does the 2-leg candidate price correctly? | Yes — cbBTC/USD ÷ USDC/USD at 1e34 scale predicts the adapter’s price exactly: 809257935592292554744145921111740273215, base-unit exact |
| E2 | How does it compare to the live market’s oracle? | 1.001104× — the candidate reads the Coinbase cbBTC/USD basis ($80,925.79/cbBTC) against the live V1’s BTC-composed price ($80,836.55), discounted by the USDC peg (0.99983065): both are real feed facts, not configuration error |
| E3 | What is the exact max on the live market? | 1,557.821525 USDC on 0.05 cbBTC — the double share-conversion floor; one unit above reverts `insufficient collateral` |
| E4 | Does the roundtrip close exactly? | Yes — borrow at max, repay, withdraw collateral, supplier exit: whale deltas zero, market back to zero shares |
| E5 | Does share math hold on real tokens? | Yes — first supply and borrow shares = assets × 1e6 exact; the full exit burns exact totals |

## Environment

| Item | Value |
|---|---|
| Chain | Base mainnet fork — anvil, chainId 0x2105 |
| Morpho singleton | [`0xBBBBBbbB…37EEFFCb`](https://basescan.org/address/0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb) canonical |
| Market | Live cbBTC/USDC 38.5% — id `0x42b1be56…d5398e0f` · oracle V1 [`0x663BECd1…199639B9`](https://basescan.org/address/0x663BECd10daE6C4A3Dcd89F1d76c1174199639B9) · IRM [`0x46415998…50D22687`](https://basescan.org/address/0x46415998764C29aB2a25CbeA6254146D50D22687) AdaptiveCurve |
| Tokens | USDC [`0x833589fC…bdA02913`](https://basescan.org/address/0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913) 6-dec · cbBTC [`0xcbB7C000…0eed33Bf`](https://basescan.org/address/0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf) 8-dec |
| Candidate oracle | `0xe1cc5c35…6717660c` — cbBTC/USD base · USDC/USD quote · 1e34 scale · deployed via factory [`0x2DC205F2…48Aebd3d`](https://basescan.org/address/0x2DC205F24BCb6B311E5cdf0745B0741648Aebd3d) |
| Feeds at read | cbBTC/USD $80,912.09 (3,852 s old) · USDC/USD $0.99983065 (58,372 s) |
| Whale | fork-funded — supplies 10,000 USDC, collateralizes 0.05 cbBTC |

## The candidate — the 2-leg price

The production topology: one base leg (cbBTC/USD), one quote leg (USDC/USD), division at 1e34 scale. The prediction is exact —

```
cbBTC/USD 8091208877609 / USDC/USD 99983065 * 1e34
  = 809257935592292554744145921111740273215
```

— and the adapter returns exactly that. Against the live market’s V1 oracle the candidate reads 1.001104× higher: the Coinbase cbBTC/USD feed carries its own basis against the BTC-composed V1, and the USDC peg sits at 0.99983065 — both differences are real feed facts, not misconfiguration. At liquidation the candidate prices seizures at the Coinbase basis; choosing between the two oracles is a basis decision, not a correctness one.

## The market — live shape

The roundtrip ran on the market that already exists: cbBTC collateral, USDC loan, 38.5% LLTV, the real AdaptiveCurveIRM. The executable maximum on 0.05 cbBTC is 1,557.821525 USDC — the double share-conversion floor (mint up, health-check up), the same rounding pair [Experiment XII](/v2/research/nutusd-rate-surface.md) reconciled; one unit above reverts `insufficient collateral`.

## The roundtrip — at the exact max

| Step | Value |
|---|---|
| Supply | 10,000 USDC → 10,000,000,000,000,000 shares — assets × 1e6 exact |
| Collateral | 0.05 cbBTC (5,000,000 base units, 8-dec) |
| Max borrow | 1,557.821525 USDC — chain match to the double-floor prediction |
| Borrow | at max — 1,557,821,525 assets, 1,557,821,525,000,000 shares |
| Repay | full — borrow shares to zero |
| Withdraw collateral | 0.05 cbBTC home |
| Supplier exit | full redemption — market back to zero shares |
| Whale deltas | USDC 0 · cbBTC 0 |

Seven transactions, each receipted on the fork (below). The market ends where it began — zero shares, zero debt, zero dust beyond the ledger’s own floor.

## Findings

| # | Finding |
|---|---|
| F1 | The 2-leg candidate is formula-exact: cbBTC/USD ÷ USDC/USD at 1e34 scale, base-unit prediction match |
| F2 | Candidate vs live V1: 1.001104× — Coinbase-basis vs BTC-basis, discounted by the USDC peg; a basis choice, not a correctness question |
| F3 | The live market’s exact max on 0.05 cbBTC is 1,557.821525 USDC — the double share-conversion floor, one unit above reverting |
| F4 | The full roundtrip closes exactly: repay, collateral withdrawal, supplier exit — whale deltas zero, market to zero |
| F5 | Share math on real tokens matches the Sepolia receipts: first shares = assets × 1e6, full exit exact |

## Limitations

- Fork-local receipts: the seven transactions exist on the fork only; real mainnet carries zero code at the candidate’s address — itself the receipt that nothing was broadcast.
- One timestamp: feed ages 3,852 s and 58,372 s at read; the parity is a point-in-time measurement, not a tracked divergence series.
- No fork liquidation: the crash geometry is the Sepolia series’ controlled-feed work; this page prices the production path, it does not re-run the failure lattice on live feeds.
- The whale is the only actor: crowd-state economics — contention, races, waves — are [Experiment VIII](/v2/research/nutusd-mev-races.md).
- Accrual within the roundtrip window was minimal at the real IRM; the AdaptiveCurve response is [Experiment IV](/v2/research/nutusd-liquidity-rates.md) and [Experiment XII](/v2/research/nutusd-rate-surface.md).

## Artifacts

| Artifact | Value |
|---|---|
| Fork | anvil, Base mainnet state, chainId 0x2105 |
| Market id | `0x42b1be56…d5398e0f` — live cbBTC/USDC 38.5% |
| Candidate oracle | `0xe1cc5c35…6717660c` — fork-deployed via the real factory |
| Roundtrip txs (fork-local) | supply `0x22edd2a1…a3c29209` · collateral `0x2d5a0251…67db9cd4` · borrow `0xdd281084…69a23321` · repay `0x86c5806c…675a1f3d` · withdraw `0x8b9ed34c…8844311e` · supplier exit `0x282477e2…85922ce1` · pre-clean `0xf4a3dee5…9f3881c0` |
| Results | `agent-core/exp11_market_roundtrip.json` · `agent-core/exp11_oracle_candidate.json` |
| Run window (UTC) | 2026-09-03 – 2026-09-04 |

## References

- [Experiment VI](/v2/research/nutusd-production-recipe.md) — the production collateral shape this fork realizes
- [Experiment VII](/v2/research/nutusd-lltv-ladder.md) — the 38.5% choice, measured comparatively
- [Experiment X](/v2/research/nutusd-invariants.md) — the invariant suite over canonical source
- [Experiment XII](/v2/research/nutusd-rate-surface.md) — the real IRM’s response surface
- [nutUSD](/v2/tokens/nutusd.md) — the credit layer

> 🥜 The rehearsal stage came down and the real market stood up — the same math priced the true feed to the last base unit.


{% hint style="warning" %}
BASED NUT is an experimental memefi ecosystem. Nothing here is financial advice, no asset carries intrinsic value, and no figure on this page is a promise of performance. Measure twice, nut responsibly.
{% endhint %}
