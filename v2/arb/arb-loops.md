# ⚔️ Arbitrage Loops — Honest Assessment

***

Each loop below is a self-contained arbitrage strategy with a full breakdown: what it is, how to execute it, when to deploy it, difficulty level, expected frequency, capital requirements, prerequisites, profit condition, risks, and an honest verdict. Verdicts are **not** upgraded — the site's own words are preserved.

**How to use this page:** pick a loop that matches your skill level and capital. Read the What / How / When sections. The page's own guidance: start with beginner-friendly loops before attempting advanced ones.

***

## Summary Table

| # | Loop | Venues | Difficulty | Frequency | Capital | Verdict |
|---|---|---|---|---|---|---|
| 1 | Cross-Venue NUT | Uni V3, Uni V2, Aero (NUT/AERO), Aero (NUT/cbBTC) | Beginner-friendly | Event-driven | $500+ | VIABLE in principle |
| 2 | pNUT Index | Balancer V2 ↔ DEX | Advanced (most complex) | Rare — few per week | $2,000+ | THEORETICALLY VIABLE |
| 3 | SALT Loop | Mint Club → Aerodrome (SALT/USDC) | — | Sporadic | $200+ | CHALLENGING |
| 4 | NUTINO Loop | Mint Club → Uni V2 (NUTINO/cbBTC) | — | Sporadic | $200+ | CHALLENGING |
| 5 | SNUT Deflationary | Buyback contract → dead burn | Beginner (monitoring only) | Continuous | N/A (any SNUT to hold) | NOT AN ARB |
| 6 | NFT Fractionalization | Sudoswap ↔ NFT marketplaces | — | Very rare | $500+ per NFT | OPPORTUNISTIC |
| 7 | SNUT Cross-Venue | Uni V2 ↔ Aero ↔ pNUT basket | Advanced | Event-driven | $1,000+ | VIABLE WITH CAUTION |
| 8 | SNUT/NUT Keeper | Aero V2 (SNUT/NUT) reactor | Advanced Keeper | Regular (reward schedule) | $50+ gas | ADVANCED KEEPER ARB |
| 9 | SNUT/ETH-LP Meta-Pool | Uni V2 meta-pool ↔ main pool | Advanced | Low freq / high potential | $500+ | OPPORTUNISTIC |

*Difficulty marked "—" is not ranked in the page's suggested-start guidance; the page only labels loops 5 and 1 as beginner-friendly and loops 2, 7, 8, 9 as advanced.*

***

## Loop 1 — Cross-Venue NUT Arbitrage

* **Venues:** Uniswap V3 (NUT/WETH) ↔ Uniswap V2 (NUT/WETH) ↔ Aerodrome (NUT/AERO) ↔ Aerodrome (NUT/cbBTC)

### What it is

Classic cross-venue price arbitrage. NUT trades on 4 different DEXs with different quote tokens. When the same token has different prices on different venues, you buy low and sell high.

### How to use

1. Poll all 4 venues every block (Base block time ~2s).
2. Normalize all prices to USD using CoinGecko for quote tokens.
3. Calculate spread between every pair.
4. If spread > threshold, execute buy on cheap venue + sell on expensive venue in same block or next.
5. Use multicall or flashbots to atomic-execute both legs.

### When to use

After large directional trades on one venue. During volatility spikes. When new liquidity is added/removed from one pool. When AERO or cbBTC prices move sharply vs ETH.

### Frequency

Event-driven. Occurs when cross-venue prices diverge enough to clear fees + gas + route tax. No fixed cadence — poll venues, measure the live spread, execute only when positive after all costs.

### Capital needed

$500+ recommended. Gas is cheap on Base (~$0.10–0.20 per tx) but slippage on small sizes eats profit.

### Prerequisites

Base RPC access, USD price feeds for ETH/AERO/cbBTC, understanding of Uniswap V3 `slot0` vs V2 `getReserves`, wallet funded with ETH for gas.

### Profit condition

```
profit = NUT_price_venueB - NUT_price_venueA - 2 × gas - slippage
```

Spread between any 2 venues must exceed **2 × gas + slippage + quote token conversion cost**.

### Risks

Different quote tokens complicate comparison. Price moves during cross-venue execution. Liquidity depth varies. The V3 pool has deepest liquidity.

### Verdict

**VIABLE in principle** — profitability depends on the LIVE spread clearing fees + gas + route tax. Past observed spreads are not guarantees; measure the current spread and execute only when it is positive after all costs. Requires fast execution and USD normalization across quote tokens.

***

## Loop 2 — pNUT Index Arbitrage

* **Venues:** Balancer V2 (mint/redeem BPT) ↔ DEX (buy/sell pNUT)

### What it is

pNUT is a Balancer WeightedPool token (BPT) holding 4 assets at 25% each: cbETH, cbBTC, NUT, SNUT. Its market price can drift from its Net Asset Value (NAV) when component prices move. You mint or redeem BPT against the basket to capture the premium/discount.

### How to use

1. Monitor pNUT BPT price on Balancer vs calculated NAV.
2. `NAV = sum(component_balance × component_price) / totalSupply`.
3. If BPT trades ABOVE NAV: deposit the 4-asset basket into Balancer to mint BPT, then sell BPT on secondary market.
4. If BPT trades BELOW NAV: buy BPT cheap, redeem for basket components, sell components.
5. Account for Balancer swap fees on join/exit.

### When to use

When NUT or SNUT makes a sharp move (they are the volatile components). When cbETH/cbBTC drift changes basket weights. After large pNUT mints or redeems that shift the pool. Low frequency but high value when triggered.

### Frequency

Rare — maybe a few times per week during volatile periods. Requires 4-component price divergence of >2%.

### Capital needed

$2,000+ recommended. Must hold or source all 4 basket components (cbETH, cbBTC, NUT, SNUT). Balancer join/exit has gas + fee overhead.

### Prerequisites

Balancer V2 SDK or API access, real-time price feeds for all 4 components, understanding of weighted pool math, ability to source and liquidate basket components.

### Profit condition

```
profit = |market_price - NAV| × pNUT_amount - gas - slippage - exit fees
```

`|market_price − NAV|` must exceed **gas + slippage + basket liquidation cost + Balancer exit fee**.

### Risks

NAV changes as basket components move. Redeeming requires selling 4 tokens. Balancer join/exit fees. Low pNUT trading volume.

### Verdict

**THEORETICALLY VIABLE** — most complex arb. Requires monitoring 4 component prices + pNUT market price. Best executed when NUT or SNUT makes a sharp move vs ETH/BTC, causing basket weight drift.

***

## Loop 3 — SALT Loop (Mint Club → Aerodrome)

* **Venues:** Mint Club (NUT→SALT) → Aerodrome (SALT→USDC)

### What it is

SALT is a Mint Club bonding curve token backed by NUT. It also trades on Aerodrome against USDC. The bonding curve price and DEX price can diverge, creating a loop: mint SALT cheap on Mint Club, sell on Aerodrome — or reverse.

**Forward:** Buy NUT → Mint SALT on Mint Club → Sell SALT on Aerodrome (SALT/USDC).
**Reverse:** Buy SALT on Aerodrome → Burn SALT on Mint Club for NUT → Sell NUT.

### How to use

1. Mint Club BUY price = `NUT_locked / supply` (from UI).
2. Mint Club SELL price is ALWAYS lower than BUY price (bonding curve spread).
3. 1% royalty on both mint and burn.
4. Execute forward when DEX price clears the buy side; reverse when MC sell clears the DEX side.

### When to use

When DEX price diverges >5–10% from the bonding curve fair value. During SALT liquidity events, market dumps, or when NUT price moves but SALT DEX lags. Most viable during high volatility windows.

### Frequency

Sporadic — the bonding curve spread captures most value. Windows open during volatility but close fast as arbitrageurs correct the divergence.

### Capital needed

$200+ for gas coverage, but profit margins are thin. Larger sizes get worse slippage on both MC curve and DEX.

### Prerequisites

Mint Club V2 SDK or browser automation for bonding curve prices, Aerodrome pool monitoring, understanding of bonding curve mechanics (buy ≠ sell), NUT price feed.

### Profit condition

* **Forward:** `SALT DEX price > MC buy price + 1% royalty + gas`.
* **Reverse:** `MC sell price > DEX price + 1% royalty + gas`.

### Risks

Bonding curve spread captures most value. Supply changes with each trade (price moves against you). DEX liquidity may be thin.

### Verdict

**CHALLENGING** — the Mint Club bonding curve has a massive BUY/SELL spread; BUY price is ALWAYS higher than SELL price. This is protocol revenue, not a bug. Forward: DEX price tends to be below MC buy price → squeezed. Reverse: MC sell price tends to be below DEX price → squeezed. The spread captures significant value from BOTH directions. However, during volatile conditions or external liquidity events, DEX price can diverge enough to create profitable windows. Monitor for 5–10%+ divergence.

***

## Loop 4 — NUTINO Loop (Mint Club → Uniswap V2)

* **Venues:** Mint Club (NUT→NUTINO) → Uniswap V2 (NUTINO→cbBTC)

### What it is

NUTINO is a Mint Club bonding curve token backed by NUT, trading on Uniswap V2 against cbBTC. Same loop concept as SALT but with BTC-denominated pricing adding a BTC volatility dimension that can create wider dislocations.

**Forward:** Buy NUT → Mint NUTINO on Mint Club → Sell NUTINO on UniV2 (NUTINO/cbBTC).
**Reverse:** Buy NUTINO on UniV2 → Burn NUTINO on Mint Club for NUT → Sell NUT.

### How to use

1. Get NUTINO mint price from Mint Club (`NUT_locked / supply`).
2. Get NUTINO DEX price from UniV2 (NUTINO/cbBTC reserves).
3. Forward: buy NUT → mint NUTINO on MC → sell NUTINO on UniV2 for cbBTC.
4. Reverse: buy NUTINO on UniV2 → burn on MC for NUT → sell NUT.
5. Subtract 1% royalty.
6. Convert cbBTC to USD for profit calc.

### When to use

During high BTC volatility (cbBTC price moves but NUTINO DEX lags). When NUT makes a sharp move and NUTINO bonding curve has not caught up. Same 5–10% divergence threshold as SALT.

### Frequency

Sporadic — similar to SALT but BTC volatility can create wider windows. Still squeezed by bonding curve spread on most attempts.

### Capital needed

$200+ for gas. cbBTC denomination means position sizes are effectively in BTC terms. Thin UniV2 liquidity limits size.

### Prerequisites

Mint Club V2 SDK, UniV2 pool monitoring, BTC price feed for cbBTC, understanding of bonding curve mechanics, NUT price feed.

### Profit condition

* **Forward:** `NUTINO DEX price in cbBTC > MC buy price + 1% royalty + gas`.
* **Reverse:** `MC sell price > DEX price + 1% royalty + gas`.

### Risks

cbBTC price volatility. Bonding curve spread. UniV2 slippage. Same fundamental issue as SALT loop.

### Verdict

**CHALLENGING** — same bonding-curve BUY/SELL spread capture as the SALT loop, plus a cbBTC-denominated pricing layer (8 decimals) and an additional BTC/USD conversion. Windows open during BTC volatility but are squeezed by the curve spread on most attempts.

***

## Loop 5 — SNUT Deflationary Pressure

* **Venues:** Aerodrome (SNUT/NUT, SNUT/WETH) ← Buyback contract → Dead address (burn)

### What it is

This is **NOT** an arbitrage loop. SNUT has a built-in deflationary mechanism: 1% tax on every trade routes through a swapback engine that buys back and burns SNUT. Dead-held SNUT keeps earning NUT rewards. This creates continuous price support and a recursive burn flywheel.

Key mechanics:
* `price_support = burn_rate / circulating_supply` (continuous, non-directional).
* 1% tax on every trade → swapback → ETH routing → NUT rewards + buyback fuel + liquidity injection.
* Buybacks send SNUT to dead address — dead-held SNUT keeps earning NUT rewards.
* NUT sent to dead is burned → recursive burn flywheel: burn feeds burn.
* 100,000 initial supply, supply decreases monotonically — no new SNUT minted.
* Tax breakdown: 1% total split 4 ways — liquidity, manager, buyback/burn, NUT rewards (live per-stream via RPC).

### How to use

You cannot arbitrage this directly. Instead:
1. Monitor burn rate (dead address SNUT balance growth).
2. Monitor buyback fuel (SNUT contract ETH balance).
3. Use burn rate as a price floor indicator — higher burn = stronger floor.
4. Hold SNUT to benefit from deflationary pressure.
5. Track NUT sent to dead (burned NUT) as a measure of flywheel intensity.

### When to use

Use as a HOLD signal, not a trade. When burn rate accelerates (high volume = more tax = more burns), the deflationary pressure increases. When dead-held LP percentage rises, the uncollapsable liquidity floor strengthens.

### Frequency

Continuous — every SNUT trade contributes to the burn. Monitor daily/weekly burn rates for trend analysis.

### Capital needed

N/A for monitoring. For holding: any amount of SNUT. No gas required to benefit from burns.

### Prerequisites

Base RPC for dead address balance queries, SNUT contract read for tax configuration, understanding of deflationary tokenomics.

### Profit condition

None — this is structural price support, not a tradeable spread.

### Risks

Tax reduces liquidity. Burn rate depends on volume. No arbitrage exit — long-term hold mechanic.

### Verdict

**NOT AN ARB** — this is a structural deflation mechanism. Cannot be arbitraged directly. Relevant for bots that monitor burn rate as a price floor indicator and hold signal.

***

## Loop 6 — NFT Fractionalization Arb

* **Venues:** Sudoswap AMM (fractional pools) ↔ OpenSea / NFT marketplaces

### What it is

NFT fractionalization arbitrage using Sudoswap AMM. Some BASED NUT NFT collections (PNUTS, ALMD, SALMD) have fractional pools on Sudoswap. When the sum of fraction prices diverges from the NFT floor price on marketplaces, you can arbitrage the gap.

### How to use

1. Identify collections with Sudoswap fractional pools.
2. Get fraction price from Sudoswap pool contract.
3. Get NFT floor price from OpenSea/marketplace.
4. If fractions cheap: buy fractions, assemble full NFT, sell on marketplace.
5. If NFT cheap: buy NFT, fractionalize on Sudoswap, sell fractions.
6. Account for 2.5% marketplace fee.

### When to use

When NFT floor prices move sharply (market dumps/hypes). When Sudoswap pool has stale pricing. After collection launches or events. Very opportunistic.

### Frequency

Very rare — NFT markets are illiquid and slow. Maybe once a week or less during active NFT periods.

### Capital needed

$500+ per NFT. NFT floor prices vary. Fractionalization and assembly have gas costs. Marketplace fees (2.5%) eat into profits.

### Prerequisites

Sudoswap SDK, NFT marketplace API (OpenSea), understanding of ERC721/ERC1155, fractionalization mechanics, NFT floor price tracking.

### Profit condition

```
profit = (fraction_price × total_fractions) - NFT_floor_price - gas
```

`|fraction_sum − floor_price|` must exceed **gas + Sudoswap fees + marketplace fees (2.5%)**.

### Risks

Illiquid NFT markets. Fractionalization may not be available for all collections. Marketplace fees. Slow execution.

### Verdict

**OPPORTUNISTIC** — low liquidity makes this sporadic. Monitor floor prices vs Sudoswap pool values. Best for bots with NFT marketplace integration.

***

## Loop 7 — SNUT Cross-Venue Arbitrage

* **Venues:** Uniswap V2 (SNUT/WETH) ↔ Aerodrome (SNUT/NUT) ↔ Balancer V2 (pNUT basket)

### What it is

SNUT trades on 3 venues: Uniswap V2 (SNUT/WETH), Aerodrome (SNUT/NUT), and indirectly via the Balancer pNUT basket. When SNUT prices diverge across these venues, you buy on the cheapest and sell on the most expensive.

### How to use

1. Get SNUT/WETH price from UniV2 (`getReserves`).
2. Get SNUT/NUT price from Aerodrome (`getReserves`).
3. Get SNUT implied price from pNUT basket (NAV component).
4. Normalize all to USD.
5. Buy low, sell high across venues.
6. CRITICAL: account for 1% SNUT transfer tax on non-exempt addresses.
7. Verify which addresses are tax-exempt (pool-to-pool may be exempt).

### When to use

During SNUT volatility. After large buys/sells on one venue. When NUT price moves but SNUT lags on one venue. The 1% tax matters only on taxable routes.

### Frequency

Event-driven. Occurs when SNUT diverges across its 3 venues enough to clear fees + gas + tax. No fixed cadence — measure the live spread across venues and execute only when positive after all costs. Tax-exempt routes are the key to profitability.

### Capital needed

$1,000+ recommended. Tax-exempt routes need less capital but require verification.

### Prerequisites

Base RPC for 3-venue price monitoring, SNUT tax-exempt address list, understanding of 9 decimals (NOT 18), NUT price feed for USD normalization, Balancer API for pNUT component.

### Profit condition

```
profit = SNUT_price_venueB - SNUT_price_venueA - 2 × gas - slippage - 1% tax (if applicable)
```

Spread between any 2 venues must exceed **2 × gas + slippage + 1% tax (if applicable)**. Tax-exempt routes (pool-to-pool) only need **spread > gas + slippage**.

### Risks

SNUT 1% transfer tax erodes profits on taxable transfers. SNUT uses 9 decimals (NOT 18). Thin liquidity on SNUT/WETH UniV2. pNUT basket price is implied, not directly tradeable. Tax-exempt status of pool addresses must be verified.

### Verdict

**VIABLE WITH CAUTION** — SNUT has multiple venues creating real cross-venue spread opportunities. The 1% transfer tax is one cost factor — verify which addresses are tax-exempt before executing. Spreads between SNUT/WETH and SNUT/NUT can exceed 2% during volatility. The pNUT basket provides an additional price reference and indirect arb via basket composition. Monitor all three venues simultaneously.

***

## Loop 8 — SNUT/NUT Reactor Keeper Game

* **Venues:** Aerodrome V2 (SNUT/NUT) — dividend-eligible pair

### What it is

The SNUT/NUT Aerodrome pool is dividend-eligible by design. NUT rewards flow into the pair, creating excess balance above recorded reserves. Keepers monitor this excess and extract it via `skim()` or `sync()`+`swap()`. This is an intentional reactor surface — a keeper competition game.

### How to use

1. SNUT/NUT pair is dividend-eligible BY DESIGN — NUT rewards sent to pair create excess balance above recorded reserves.
2. Monitor: actual NUT balance vs `getReserves()` NUT reserve. Excess = actual − recorded.
3. When excess > gas cost: call `skim()` to extract excess NUT to yourself, OR call `sync()` to absorb excess into reserves then swap.
4. Alternatively: burn LP tokens to claim pro-rata share of actual balances (including excess NUT).

This is a keeper game — fastest bot wins the excess. Low float + thin liquidity = forced arb surface.

### When to use

Continuously monitor. NUT rewards flow on a schedule — excess accumulates predictably. Best executed right after reward distributions. Gas wars during high-excess events.

### Frequency

Regular — depends on NUT reward distribution schedule. Excess accumulates every reward cycle. Competition is the main barrier, not opportunity.

### Capital needed

$50+ for gas. No capital needed for `skim()` — you extract value directly. For LP burn strategy, you need LP tokens (requires providing liquidity first).

### Prerequisites

Mempool monitoring for competing keepers, gas optimization (priority fee bidding), understanding of skim/sync mechanics, Aerodrome dividend system knowledge, fast RPC endpoint.

### Profit condition

```
profit = excess_NUT_balance - gas (skim or sync + swap)
```

`excess_NUT_value > gas + slippage`. Must be faster than competing keepers.

### Risks

Competition from other keepers. Gas wars during high excess events. NUT is low-float, thin liquidity — exit may be difficult. Must understand skim/sync mechanics. Not a passive yield position — active keeper role only.

### Verdict

**ADVANCED KEEPER ARB** — this is an intentional reactor surface, not a bug. The SNUT/NUT pair is dividend-eligible by design. NUT reward inflows create excess-balance opportunities. Keepers who monitor and act fastest extract value. Best for sophisticated bots with mempool monitoring and gas optimization.

***

## Loop 9 — SNUT/ETH-LP Meta-Pool Arbitrage

* **Venues:** Uniswap V2 (SNUT/ETH-LP/ETH meta-pool) ↔ Uniswap V2 (SNUT/WETH main pool)

### What it is

The SNUT/ETH-LP meta-pool is a Uniswap V2 pool where LP tokens of the main SNUT/ETH pool are traded against ETH. This creates a secondary market for LP token claims. When the meta-pool LP price diverges from the fair Net Asset Value (NAV) of the underlying LP position, you can arbitrage the gap.

Three paths exist:
* **Path 1 — LP Premium:** Acquire SNUT + ETH → add liquidity to SNUT/ETH main pool → receive LP tokens → sell LP tokens on meta-pool for ETH. Profit when meta-pool LP price > fair NAV.
* **Path 2 — LP Discount:** Buy LP tokens on meta-pool for ETH → remove liquidity from SNUT/ETH main pool (unwrap LP) → receive SNUT + ETH → sell SNUT for ETH. Profit when meta-pool LP price < fair NAV.
* **Path 3 — Synthetic Short:** If SNUT price dropping on main pool but LP tokens lag on meta-pool → buy LP on meta-pool, unwrap, dump SNUT. LP price is sticky to NAV but reacts slower than spot.

### How to use

1. Calculate LP fair NAV: `LP_NAV = (SNUT_reserve × SNUT_price + ETH_reserve × ETH_price) / LP_total_supply`.
2. Compare meta-pool LP token price vs fair NAV — identify discount or premium.
3. Monitor both pools simultaneously — meta-pool price should track NAV but may drift during volatility.

### When to use

When meta-pool LP price diverges >1% from fair NAV. During SNUT volatility (LP price is sticky, spot moves fast). After large liquidity adds/removes on the main pool. When SNUT tax events create imbalances.

### Frequency

Low frequency but high potential. Opportunities arise during SNUT price volatility. LP token prices are inherently sticky, creating predictable lag-based windows.

### Capital needed

$500+ recommended. LP addition/removal requires both SNUT and ETH. Meta-pool liquidity may be thin — slippage on large sizes.

### Prerequisites

Real-time LP NAV calculation (`SNUT_reserve × price + ETH_reserve × price) / LP_supply`), monitoring both pools simultaneously, understanding of LP token mechanics, SNUT 1% tax awareness on LP transfers.

### Profit condition

```
profit = LP_NAV_premium - gas - slippage
```

`|meta_pool_LP_price − LP_fair_NAV|` must exceed **gas + slippage + LP removal/addition fees**.

### Risks

LP token liquidity on meta-pool may be thin. Removing liquidity from SNUT/ETH main pool affects SNUT price. SNUT 1% tax may apply on LP token transfers. Complex multi-step execution. Must account for pending fees accrued in LP position.

### Verdict

**OPPORTUNISTIC** — unique meta-market arb. The LP-token/ETH pool creates a secondary market for SNUT/ETH liquidity claims. Best executed when meta-pool LP price diverges significantly from fair NAV. Requires monitoring both pools and calculating LP NAV in real-time. Low frequency but high potential when triggered.

***

## Mint Club Bonding Curve Mechanics (shared context for Loops 3–4)

Critical for understanding why the Mint Club loops are challenging:

* Mint Club tokens are minimal proxy contracts (45 bytes). Direct RPC price queries are unreliable. Use browser automation (Playwright) or the V2 SDK for accurate prices.
* Mint/burn (NOT AMM swap). New tokens are minted when buying, burned when selling. No LP deposits needed — the curve IS the liquidity.
* Bonding curve price = `NUT_locked / token_supply`. Price increases as supply mints, decreases as supply burns.
* BUY (mint) price is ALWAYS higher than SELL (burn) price. The spread is protocol revenue. Can be 10x to 18,000,000x depending on curve position.
* 1% creator royalty on BOTH mint and burn transactions, deducted from the base asset (NUT).
* Curve types: Exponential (most common, price increases at constant rate), Linear, Logarithmic, Flat. Mint Club uses a Discrete Bonding Curve (DBC) with step arrays.
* Parameters: Max Minting Supply, Initial Minting Price, Final Minting Price, Price Intervals (steps). More steps = smoother price curve.
* NUT is the base/reserve asset for all BASED NUT bonding curves. SALT and NUTINO are both backed by NUT.

***

*Reference: the deployed site's Arb Bot Builder Helper page, "Arbitrage Loops — Honest Assessment" section. All verdicts, addresses, costs, and thresholds are verbatim from that page.*
