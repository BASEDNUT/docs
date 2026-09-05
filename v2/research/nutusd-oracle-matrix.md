# Research — nutUSD Oracle Failure Matrix (Experiment XI, second instrument)

Companion instrument to the [mainnet fork](/v2/research/nutusd-production-fork.md): the same production shape — the canonical Morpho singleton, real USDC and cbBTC, the real MorphoChainlinkOracleV2 factory, the real AdaptiveCurveIRM at 38.5% — with the two feed answers placed under direct control. Two fork-deployed Chainlink-style aggregators are seeded to the mainnet fork's captured live raws (cbBTC/USD 8,091,208,877,609 · USDC/USD 99,983,065, both 8-dec) and wired through the real factory into a fork-created cbBTC/USDC market. The oracle path is production-shaped end to end; only the answers move. Ten feed-failure states are then driven one at a time — zero base, zero quote, negative base, day-old staleness, quote depeg, base dislocation, recovery, a combined shift, and a broken feed — each against the live market machinery: the price view, the borrow gate, and the liquidation gate.

## Questions

| # | Question | Verdict |
|---|---|---|
| Q1 | What does each failure state do to the price? | Four distinct behaviors: zero base serves a zero price; zero quote panics (0x12) in the division; negative base reverts `negative answer`; staleness serves the same integer unchanged |
| Q2 | Which failures freeze the market? | Two: zero quote (panic propagates to every price-dependent call) and a broken feed (the adapter's own call reverts — `mock: broken feed` — and every dependent call reverts with it) |
| Q3 | Which failures move the price without freezing? | Depeg and dislocation: quote at 0.90 USD raises the price by exactly 1/0.9; base at 0.70x lowers it floor-exact to 0.70x; combined 0.80x/0.90x lands at 0.8/0.9 of baseline — each floor-of-exact-rational |
| Q4 | Does the health gate follow the price? | Yes — at 0.70x the borrow ceiling collapses and the same position that was healthy at baseline becomes liquidatable end to end |
| Q5 | Does the system return to baseline when the feed heals? | Yes — the restored base answer prices back to the baseline integer exactly; a healed broken feed serves the baseline again |

## Environment

| Item | Value |
|---|---|
| Chain | Base mainnet fork — anvil at block 50889452, chainId 8453 |
| Morpho singleton | [`0xBBBBBbbB…37EEFFCb`](https://basescan.org/address/0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb) canonical |
| Tokens | USDC [`0x833589fC…bdA02913`](https://basescan.org/address/0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913) 6-dec · cbBTC [`0xcbB7C000…0eed33Bf`](https://basescan.org/address/0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf) 8-dec |
| Factory | [`0x2DC205F2…48Aebd3d`](https://basescan.org/address/0x2DC205F24BCb6B311E5cdf0745B0741648Aebd3d) MorphoChainlinkOracleV2Factory — real, fork-read |
| Controllable feeds | base mock `0x30a5b95c…6045ffd5` (cbBTC/USD role, 8-dec) · quote mock `0xdc4fcc80…0ac90d66` (USDC/USD role, 8-dec) — seeded to the captured raws, fork-deployed |
| Matrix oracle | `0x8b346150…ca60822e` — 2-leg cbBTC/USD ÷ USDC/USD at 1e34 scale, factory-registered |
| Market (fork-created) | cbBTC/USDC 38.5% — id `0x707d922a…44877fff` · IRM [`0x46415998…50D22687`](https://basescan.org/address/0x46415998764C29aB2a25CbeA6254146D50D22687) AdaptiveCurve |
| Position | whale supplies 10,000 USDC · borrower collateralizes 0.05 cbBTC · borrows the executable maximum 1,557.821525 USDC |
| Whale | [`0xfBB6Eed8…E1e43ef`](https://basescan.org/address/0xfBB6Eed8e7aa03B138556eeDaF5D271A5E1e43ef) — fork-impersonated, balances covered the position at the pin (no storage edits) |

## The lattice — ten states, four behaviors

The baseline is the mainnet fork's own captured raws: the factory oracle prices cbBTC/USDC at exactly 809257935592292554744145921111740273215 — floor(SCALE x BASE / QUOTE) at 1e34 scale, base-unit exact. Every scenario is that same arithmetic under a moved answer.

```
BASE 8,091,208,877,609 / QUOTE 99,983,065 * 1e34
  = 809,257,935,592,292,554,744,145,921,111,740,273,215   (M1 baseline)

base -> 0        price = 0                    (served, no revert)
quote -> 0       panic 0x12 in the division   (market freezes)
base -> -1       revert: negative answer      (market freezes)
updatedAt -24h   price unchanged              (served, same integer)
quote -> 0.90    price * 10/9, floor-exact    (depeg raises it)
base -> 0.70x    price * 0.70, floor-exact    (gate flips)
base restored    baseline integer, exact      (recovery)
0.80x + 0.90x    price * 0.8/0.9, floor-exact (combined)
latestRoundData  revert: mock: broken feed    (market freezes)
      reverts
```

## The zero pair - asymmetric by construction

Zero base and zero quote are not symmetric. A zero base answer serves a zero price without reverting - and the market machinery follows it down honestly: the borrow gate reverts `insufficient collateral` for any amount, and a 1-sat collateral seizure quotes a zero repayment. Nobody can extract value from a zero base; the position simply becomes unborrowable and unliquidatable at that valuation. A zero quote is the opposite: the adapter's division by zero panics (0x12) inside `price()`, and the panic propagates - every price-dependent market call freezes. The asymmetry is structural: the base enters the numerator, the quote enters the denominator.

## Staleness - no guard in the adapter

The adapter carries no staleness guard: `updatedAt` pushed back a full day leaves the served price the same integer, byte-identical. Feed freshness is the caller's problem in this topology - the market will happily price a day-old answer. The sequencer-uptime and heartbeat question belongs to the feed layer, not the adapter.

## Depeg and dislocation - the moving pair

A quote depeg to 0.90 USD raises the price by exactly 10/9 - floor-exact at 899023208623222222222222222222222222222 - because the devalued denominator inflates the ratio. A base dislocation to 0.70x lowers it floor-exact to 566480554914574783239541616372732722286 - and the gates follow: the max-borrow ceiling collapses with the price, the health gate flips, and a liquidation that reverts `position is healthy` at baseline executes end to end at the dislocated feed. Combined 0.80x/0.90x lands at 719340391190139112226095001555707912222 - exactly 0.8/0.9 of baseline, floor-exact. Restoration returns the price to the baseline integer exactly - the arithmetic is stateless, so recovery is exact by construction.

## The broken feed - freeze by refusal

When `latestRoundData` itself reverts, the adapter reverts with the feed's own message - `mock: broken feed` - and every price-dependent market call reverts with it. The freeze persists exactly as long as the feed stays broken, and heals the moment it serves again - the post-heal price returns to the baseline integer.

## Findings

| # | Finding |
|---|---|
| F1 | The four failure behaviors are distinct and structural: zero base serves zero (no revert); zero quote panics 0x12; negative base reverts `negative answer`; a broken feed reverts with the feed's message - three freezes, one silent degradation |
| F2 | The zero-base path degrades safely: price 0 served, borrow gated off (`insufficient collateral`), 1-sat seizure quotes 0 repayment - no extraction surface at zero valuation |
| F3 | The adapter carries no staleness guard: a 24-hour-old answer serves the identical integer |
| F4 | Price moves are floor-exact: 1/0.9 depeg, 0.70x dislocation, 0.8/0.9 combined - each floor-of-exact-rational, and recovery returns the baseline integer exactly |
| F5 | The health gate tracks the price: at 0.70x the same position crosses from healthy (`position is healthy` reverts) to liquidatable end to end |
| F6 | Freezes lift only at the feed: zero quote and broken feed hold the market frozen until the feed itself recovers; the adapter adds no guard, retry, or fallback of its own |
| F7 | The matrix oracle is factory-registered with SCALE_FACTOR 1e34 and the market is the standard cbBTC/USDC 38.5% shape - the production oracle path, only the answers controlled |

## Limitations

- Mock aggregators stand in for the live proxies: they match the exact call surface the adapter uses (`latestRoundData()`, `decimals()`) but are not the live Chainlink contracts; live-feed failure modes beyond the answer (sequencer uptime, L1 finality, proxy upgrade) are outside this lattice.
- One position, one market: the lattice reads the borrow gate and the liquidation gate on a single max-borrow position; crowd-state behavior under oracle failure is [Experiment VIII](/v2/research/nutusd-mev-races.md)'s surface.
- Feed edits are fork-local transactions on the mock contracts; the market itself is fork-created, and real mainnet carries zero code at the mock, oracle, and market addresses.
- The broken-feed message is the mock's own revert string (`mock: broken feed`); a live feed's revert would carry its own message, with the same propagation shape.
- Single-block probes: each scenario is read at one state point; no time-series of divergence is tracked.

## Artifacts

| Artifact | Value |
|---|---|
| Fork | anvil, Base mainnet state at block 50889452 - hash `0x3415eab4...e2091`, endpoint base.publicnode.com, chainId 8453 |
| Matrix oracle | `0x8b346150...ca60822e` - fork-deployed via the real V2 factory, salt `0x6e7574555344...02` |
| Mocks | base `0x30a5b95c...6045ffd5` - quote `0xdc4fcc80...0ac90d66` - fork-deployed, seeded to the captured raws |
| Market id | `0x707d922a...44877fff` - keccak of the market params, recomputable offline |
| Receipted txs (fork-local) | 29 - mock deploys, factory create, createMarket, supply/collateral/borrow, and every scenario edit and restore |
| Results | `artifacts/nutusd/exp11-matrix/exp11_matrix_results.json` - all ten verdicts, probes, and tx hashes |
| Driver + mock | `artifacts/nutusd/exp11-matrix/exp11_matrix.py` - `src/MockAggregator.sol` - anvil impersonation only, no key material |
| Run window (UTC) | 2026-09-04 |

## References

- [Experiment XI - Mainnet Fork](/v2/research/nutusd-production-fork.md) - the production shape this matrix controls
- [Experiment II - Adversarial](/v2/research/nutusd-adversarial.md) - the failure-mode record this matrix extends to the production shape
- [Experiment III - Liquidation Envelope](/v2/research/nutusd-liquidation-envelope.md) - the seizure branches under oracle-zero states
- [Experiment VII - LLTV Ladder](/v2/research/nutusd-lltv-ladder.md) - why 38.5% holds the failure lattice
- [nutUSD](/v2/tokens/nutusd.md) - the credit layer

> The ten faces of a lying feed, catalogued in their own tongue - three freeze, one whispers zero, and the arithmetic never blinks.

{% hint style="warning" %}
BASED NUT is an experimental memefi ecosystem. Nothing here is financial advice, no asset carries intrinsic value, and no figure on this page is a promise of performance. Measure twice, nut responsibly.
{% endhint %}
