# 🥜 Arb Bot Builder

***

## What This Is

The **Arb Bot Builder Helper** is a public read-path tool on the BASED NUT site. It gives agents and developers instant build context for trading the BASED NUT ecosystem on Base — how to think about the tokens and what to do, without doing the research yourself.

All code shown on the page is copy-pasteable Python. Addresses are **snapshot-verified** on-chain via Base RPC; the registry evolves as venues are added (newer pools are listed too). **Re-verify any contract against its latest state before executing against it.**

This is a technical reference — **not** a solicitation to trade.

***

## 📌 Build Order

The page is structured as an ordered build sequence. Each section gives you one piece of the trading machine:

| # | Section | What It Gives You |
|---|---|---|
| 1 | 📍 Addresses | Which contracts to call |
| 2 | 🔧 Sigs | The read calls to price them (a subset, not the full ABI) |
| 3 | 🐍 RPC Code | Working Python to copy |
| 4 | ⚔️ Arb Loops | Which trades exist and when they work |
| 5 | 🏭 Mint Club | Bonding-curve pricing quirks (buy ≠ sell) |
| 6 | 🧺 pNUT | How to price the index basket |
| 7 | 🏠 Venues | Where each token trades + which API |
| 8 | 🖼️ NFT | Sudoswap whole-NFT AMM venues |
| 9 | ⚙️ Spec | One machine-readable JSON of everything |
| 10 | 🚀 Start | The order to build |

**Suggested start:** pick a loop that matches your skill level and capital. Read the What / How / When sections. Start with beginner-friendly loops before attempting advanced ones.

***

## ⚠️ Risk Disclosure

This is **NOT financial advice**. BASED NUT is an experimental memefi project.

* Arbitrage is a **risky** business. You CAN and WILL lose money. Markets move instantly — a profitable spread can vanish in milliseconds.
* **Smart contract risk:** bugs, exploits, and rug pulls exist. Token taxes can change. Pool configurations can shift. Nothing is guaranteed.
* **Liquidity risk:** low-liquidity pools mean slippage will eat profits. Exit liquidity is never guaranteed. You may get stuck holding bags.
* **Competition risk:** other bots are faster than you. Gas wars are real. MEV extractors WILL front-run your transactions.
* **Technical risk:** incorrect decimals, wrong token ordering, misconfigured tax — a single mistake can drain your wallet.

**TRADE AT YOUR OWN RISK. USE AT YOUR OWN RISK.**
Nothing here constitutes financial, investment, or trading advice. Always do your own research and never risk more than you can afford to lose.

***

## ⚠️ Honest Verdicts

Every loop on this page is assessed honestly. Verdicts are **not** upgraded to look better than they are:

* **VIABLE** — the opportunity is real, but profitability depends on the live spread clearing fees + gas + route tax. Past spreads are not guarantees.
* **THEORETICALLY VIABLE** — sound in principle, but complex and rarely triggered.
* **CHALLENGING** — the market structure captures most of the value; windows open only during volatility.
* **NOT AN ARB** — structural mechanic, not directly tradeable.

Some loops carry additional honest tags (e.g. **OPPORTUNISTIC**, **ADVANCED KEEPER ARB**, **VIABLE WITH CAUTION**) — these are kept verbatim, never softened.

The full breakdown of all eight loops lives in [arb-loops.md](arb-loops.md). The machine-readable contract/address/signature reference is in [machine-spec.md](machine-spec.md).

***

## Key Getting-Started Truths

* **NUT Supply = 1 (UNITY TOKEN).** Standard APIs cannot calculate price or MCAP correctly. TRUE Price = TRUE MCAP.
* **DEX Screener is BLIND to the Uniswap V3 Genesis pool.** Query on-chain via Base RPC for accurate NUT price.
* **Wrong decimals = wrong prices.** The 3 traps: SNUT (9, NOT 18), cbBTC (8, NOT 18), USDC (6, NOT 18).
* **Always verify token0/token1 ordering** before deriving prices from reserves. Wrong ordering = inverted price.

***

*References: the deployed site's Arb Bot Builder Helper page. All addresses and numbers in this guide are traceable to that public page — re-verify live before executing.*
