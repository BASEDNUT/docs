# 🔥 SNUT Mechanics — The Burn Flywheel

**Status: LIVE** — SNUT on Base mainnet. Supply = 100,000 (9 decimals). Liquid, non-escrow NUT reward-position token.

> Dead-held SNUT earns NUT. That NUT goes to dead too. **Burn feeds burn. The flywheel never stops.** 🔥

## The Recursive Burn Flywheel

1. Every SNUT trade pays a **tax** (current on-chain value: **1%**, cut from 6% — read live from the SNUT contract on the [SNUT page](https://orchard.basednut.com/token/snut))
2. That tax becomes ETH
3. ETH buys NUT rewards and SNUT buybacks
4. Buyback SNUT goes to the dead address
5. Dead-held SNUT keeps earning NUT rewards
6. Those NUT also go to dead

> Burn feeds burn. It never stops.

## The Swapback Engine

Tax SNUT is collected, sold for ETH, and routed to **4 destinations**: liquidity, manager wallet, buyback/burn, and reward-position rewards. Buyback fuel sits as ETH in the contract until triggered. Live per-stream rates are read directly from the SNUT smart contract.

## Where Is the SNUT?

SNUT lives in multiple compartments, each with a distinct economic purpose:

| Compartment | Meaning |
|---|---|
| 🔥 Burned | Sent to the dead address `0x000000000000000000000000000000000000dEaD` — permanently removed from circulation |
| 🌊 In Pools | Liquidity across the SNUT venue set |
| 🌿 Free Float | In wallets, earnable and transferable |

**Dead-held SNUT/ETH LP is permanently locked — it cannot be removed.**

## Pool Roles

SNUT lives in multiple pools. Each has a different job:

| Pool | Role |
|---|---|
| **SNUT/ETH** — MAIN LIQUIDITY | Primary market for SNUT. Price discovery happens here. LP token = claim on SNUT + ETH |
| **SNUT-LP/ETH** — META | Trade the LP token itself against ETH. Exit liquidity without removing it from the main pool |
| **SNUT/NUT** — REACTOR | Intentionally earns NUT rewards. Excess NUT creates arbitrage opportunities for keepers |
| **Balancer multi-asset** — REACTOR | Multi-asset arbitrage reactor |

### The Palm Grove Graft Market

The SNUT-LP meta-pool (`0x82bbadb9d6b2c0a59ed01809e30323f89f6faa1c`) is a specialized pool that holds SNUT liquidity pool tokens. It acts as a **Palm Grove Graft Market** — allowing SNUT LP tokens to be traded and valued independently. This creates an additional layer of liquidity for SNUT providers and opens new arbitrage vectors between SNUT spot price, SNUT LP value, and NUT.

## Reward Position — Hold to Earn, No Locking

Holding SNUT automatically earns NUT rewards via a **non-escrow reward position** — no locking required. SNUT is the liquid reward-position token for NUT: hold SNUT to earn NUT automatically.

> ⚠️ **Experimental Memefi.** Memetic assets with zero financial payload. All deployments fall under Operation: VIBES ONLY.
