# 🧺 pNUT Mechanics — The Basket Index

**Status: LIVE** — Balancer V2 Weighted Pool on Base mainnet.

> pNUT is a **basket index token** — a BPT (Balancer Pool Token) representing proportional ownership of a Balancer weighted pool holding **25% each of NUT, SNUT, cbETH, and cbBTC**.

| | |
|---|---|
| BPT contract | `0x2a5757b60987ff10385de1d4d923792f6fdcfff1` |
| Pool ID | `0x2a5757b60987ff10385de1d4d923792f6fdcfff100010000000000000019e` |
| Target weights | 25% NUT · 25% SNUT · 25% cbETH · 25% cbBTC |

pNUT converts NUT from a **singleton meme-root** into a **basketized liquidity index**, coupling it with blue-chip reserve assets (cbETH = Coinbase Wrapped Staked ETH, cbBTC = Coinbase Wrapped BTC).

## a. Constant-Mean AMM

Balancer's weighted pool uses a **constant-mean invariant** — the geometric weighted mean of token balances stays constant. This targets 25/25/25/25 but lets weights drift as prices move, creating natural rebalancing through trading activity.

## b. BPT Valuation

> **NAV = totalLiquidity ÷ totalShares**

- `totalLiquidity` = the sum of all component values in USD
- `totalShares` = the BPT token supply

Live weights of all 4 constituents are visible on the [pNUT page](https://orchard.basednut.com/token/pnut) — actual weights drift as prices change while the pool continuously targets 25% each.

## NAV Drift Arbitrage

| Condition | Action |
|---|---|
| Market price **< NAV** | Buy pNUT and redeem the basket (cbETH, cbBTC, NUT, SNUT) |
| Market price **> NAV** | Mint pNUT and sell components |

Weight drift creates further opportunities:

- If NUT weight drifts high → swap NUT into the pool, arbitrage against external NUT pools (Uniswap V3, Aerodrome)
- SNUT overweight → swap SNUT in, sell externally; underweight → buy externally, add to pool
- NUT in Balancer vs NUT in Uniswap V3 — the pNUT basket creates additional arbitrage pressure on NUT price

## An Endogenous State Sensor

The Balancer implied price is derived from the pool's internal balances and external price feeds. **This pool alone should not decide price** — it relies on its internal mechanics to force arbitrage. Treat it as an **endogenous state sensor** inside a reflexive AMM network, **not as an exogenous truth oracle**.

pNUT couples endogenous network assets (NUT, SNUT) with exogenous reserve assets (cbETH, cbBTC). The constant-mean invariant creates continuous rebalancing pressure that links the meme-root to blue-chip reserves with forced coherence.

## Research Questions pNUT Tests

- Can a basket index enforce topological monetary policy without governance?
- Do LPs in a weighted pool act as constitutional actors in the basket?
- Can TWAP in a weighted pool serve as memory for the basket index?
- Is there reflexivity between the NUT singleton and the pNUT basket index?
- Does forced coherence between meme-root and blue-chip reserves create stable pricing?

> ⚠️ **Experimental Memefi.** pNUT is a cryptoeconomic basket index experiment. The Balancer implied price is informational and manipulable — do not use it as a standalone price oracle. Not a utility token. Not a security. No guarantee of profit or value retention. Use at your own risk.
