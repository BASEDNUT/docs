# 🌰 Based NUT FAQ

> ⚠️ **EXPERIMENTAL MEMEFI PROJECT — NOT FINANCIAL ADVICE.** BASED NUT is an experimental memefi project. All content is for educational and entertainment purposes only. Trade at your own risk.

Everything you need to know about the BASED NUT ecosystem. Playful, community-driven, and not investment advice.

## Basics

### What is BASED NUT?

Based NUT is a meme-themed DeFi experiment on the Base network (Coinbase L2). It features a unity token (NUT, supply=1), deflationary rewards (SNUT), a Balancer index basket (pNUT), and Mint Club bonding-curve tokens (SALT, NUTINO). No intrinsic value, no expectation of profit — pure peanut-powered DeFi.

### Is Based NUT intended as an investment?

No. The NUTpaper states that NUT tokens are meme coins without investment value. Treat it as entertainment and only risk what you can afford to lose.

### What chain is BASED NUT on?

Base (Coinbase L2). All contracts, pools, and tokens are on Base mainnet. Explorer: basescan.org.

### What are the ecosystem layers?

Three layers: (1) **BASED NUTs** — the foundation layer with NUT (unity token), SNUT (deflationary rewards), and pNUT (index basket). (2) **NESTED TOKENS** — Mint Club bonding-curve tokens like SALT and NUTINO, backed by locked NUT. (3) **NESTED NFTs** — War Generals and Soldiers minted with locked NUT, representing factions in the Great Nut War.

### What core tokens compose the ecosystem?

The base layer is NUT (`0xb8de15fb529d98c93c749de63c749d48d25a30df`, supply=1), deflationary layer SNUT (`0xAC130701aa31c284c36609E2489f150F419AD7AD`, supply=100,000), and Balancer index token pNUT (`0x2a5757b60987ff10385de1d4d923792f6fdcfff1`). Mint Club tokens SALT and NUTINO are backed by NUT.

### What is the MetaDEX / NUTDEX framework?

BASED NUT is described as a universal liquidity layer framework — a MetaDEX that combines protocol-owned liquidity (UniV3), community-driven pools (Aerodrome vAMM), and bonding-curve token minting into a single interconnected system. NUT sits at the root as the main liquidity anchor, with all nested tokens and NFTs deriving value from it.

## Tokens

### What is the difference between NUT, SNUT, and pNUT?

**NUT:** anchor token, supply=1, no tax. **SNUT:** deflationary reward-position token, supply=100,000, 1% tax, hold to earn NUT via non-escrow reward-position. **pNUT:** Balancer V2 index basket holding 25% each of cbETH, cbBTC, NUT, SNUT — inflationary counterbalance to SNUT.

### Why does NUT have a supply of 1?

NUT is a unity token — ERC-20 capped at 1 whole token, 18 decimals, so it is divisible down to 1e-18 NUT. TRUE Price = TRUE Market Cap. Standard APIs (CoinGecko, DexScreener) often miscalculate because they expect normal supply. Always check on-chain via Base RPC for accurate pricing.

### What is the SNUT transaction tax?

SNUT has a 1% tax on every transaction, split among liquidity, manager wallet, buyback/burn, and reward-position rewards (live per-stream rates on the SNUT page). Holding SNUT automatically earns NUT rewards via non-escrow reward-position — no locking required.

### What are SALT and NUTINO?

Mint Club bonding-curve tokens backed by NUT. SALT (`0x1EDe2AFC985F6D7aEb3F4c84B95A103c00D5dE81`): mint on Mint Club, sell on Aerodrome SALT/USDC. NUTINO (`0x30421e2d18dFF60B298eEF427cF868cA65f1476B`): mint on Mint Club, sell on Uniswap V2 NUTINO/cbBTC. Bonding curve price = NUT_locked / token_supply. 1% royalty on mint/burn.

### How are nested tokens created?

Nested tokens are minted on Mint Club using NUT as collateral. Price is determined by bonding-curve contracts: price = NUT_locked / token_supply. Buy price ≠ sell price (significant spread). 1% royalty on mint/burn. Users can arbitrage by minting when the curve price is lower than the market price, or burning when the curve price is higher.

### Which nested tokens exist?

SALT — two-venue arbitrage loop via Aerodrome SALT/USDC pool. NUTINO — arbitrage via Uniswap V2 NUTINO/cbBTC pool. Mint Club lists 14 NUT-backed tokens. SALT was airdropped to NUT Army NFT holders (200/NFT for Generals, 80/NFT for Soldiers). 7,420,420 SALT allocated to the Salt Forge vault.

### What role does Mint Club play?

Mint Club (mint.club) is the hub for NUT-backed child tokens. It lists existing tokens with prices and TVL and lets anyone deploy new NUT-collateralised tokens via bonding curves. The bonding curve buy/sell spread acts as protocol revenue.

## Mechanics

### What is the SNUT recursive burn flywheel?

Dead-held SNUT earns NUT. That NUT goes to dead too. Burn feeds burn — the flywheel never stops. See [SNUT Mechanics](/v2/the-orchard/snut-mechanics.md).

### What is the SNUT-LP meta-pool (Palm Grove)?

The SNUT-LP meta-pool (`0x82bbadb9d6b2c0a59ed01809e30323f89f6faa1c`) is a specialized pool that holds SNUT liquidity pool tokens. It acts as a Palm Grove Graft Market — allowing SNUT LP tokens to be traded and valued independently. This creates an additional layer of liquidity for SNUT providers and opens new arbitrage vectors between SNUT spot price, SNUT LP value, and NUT.

### How is pNUT NAV calculated?

pNUT NAV = totalLiquidity / totalShares. The Balancer V2 weighted pool holds 25% each of cbETH, cbBTC, NUT, and SNUT. totalLiquidity is the sum of all component values in USD. totalShares is the BPT token supply. When market price < NAV: buy pNUT and redeem basket for profit. When market price > NAV: mint pNUT and sell components. Data fetched from Balancer GraphQL API (labeled BAL).

### Are there transaction taxes?

NUT: no tax. SNUT: 1% fee split among liquidity, manager, buyback/burn, and reward-position. pNUT: no explicit tax but unwrapping triggers SNUT fee since SNUT is a component. Mint Club tokens: 1% royalty on mint/burn.

### What deflationary or inflationary forces exist?

NUT: supply fixed at 1, cannot expand. SNUT: deflationary — 1% transaction tax funds buyback/burn at dead address (`0x000000000000000000000000000000000000dEaD`), permanently reducing supply. pNUT: inflationary — can be freely minted, but growth tempered by NUT and SNUT deflation. This creates a balanced deflationary/inflationary system.

### Where are burned SNUT tokens sent?

Burned SNUT tokens are sent to the dead address `0x000000000000000000000000000000000000dEaD` — permanently removed from circulation. The SNUT buyback/burn mechanism (funded by a share of the 1% transaction tax) burns both SNUT and NUT at this address, reducing both supplies.

## Arbitrage

### What arbitrage opportunities exist?

Multiple loops: (1) SALT: mint on Mint Club → sell on Aerodrome SALT/USDC. (2) NUTINO: mint on Mint Club → sell on Uniswap V2 NUTINO/cbBTC. (3) pNUT drift: buy pNUT when market price < NAV, redeem basket; mint pNUT when market price > NAV, sell. (4) Cross-pool NUT arbitrage between Uniswap V3, V2, and Aerodrome. (5) NFT fractional: OpenSea vs Sudoswap vs intrinsic redeemable NUT.

### How does the SALT arbitrage loop work?

Forward: mint SALT on Mint Club (pay NUT) → sell on Aerodrome SALT/USDC pool (receive USDC). Reverse: buy SALT on Aerodrome → burn on Mint Club (receive NUT). Profit when price discrepancy exists between bonding curve and DEX, after accounting for 1% royalty, curve spread, and gas.

### What is pNUT drift arbitrage?

pNUT is a Balancer V2 weighted pool. When market price < NAV: buy pNUT and redeem basket (cbETH, cbBTC, NUT, SNUT). When market price > NAV: mint pNUT and sell. NAV = totalLiquidity / totalShares.

### How can I build an arbitrage bot?

Visit the Arb Bot Builder War Room for a complete guide including all arbitrage loops, machine-readable JSON spec with route IDs and contract addresses, execution doctrine, and getting started steps including Mint Club SDK installation. See [Arb Bot Builder](/v2/arb/index.md).

### What is the Mint Club SDK?

The Mint Club SDK (mint.club-v2-sdk) is an npm package for interacting with Mint Club bonding curves programmatically. Install with `npm i mint.club-v2-sdk`. Key methods: `getTotalSupply()` for current token supply, `buy()` for minting tokens via the bonding curve, `sell()` for burning tokens back to NUT. Requires viem and a wallet for transactions. Reference: sdk.mint.club.

## Liquidity

### Where is liquidity provided?

NUT: Uniswap V3 (NUT/WETH), Uniswap V2 (NUT/WETH), Aerodrome (NUT/AERO), Aerodrome (NUT/cbBTC). SNUT: Aerodrome (SNUT/NUT), Uniswap V2 (SNUT/WETH). pNUT: Balancer V2 weighted pool (cbETH/cbBTC/NUT/SNUT). SALT: Aerodrome (SALT/USDC). NUTINO: Uniswap V2 (NUTINO/cbBTC). Aerodrome pools have bribe incentives via gauge reward-position.

### How do I provide liquidity to NUT pools?

Pick a venue (Uniswap V3/V2, Aerodrome, Balancer), fund both sides, and set your range. See [Pair With NUT](https://orchard.basednut.com/pair-your-token) for the interactive pairing tool.

### What are the pool roles in the ecosystem?

Each pool has a distinct economic purpose — main liquidity, meta-market for LP rights, keeper-arb reactor, multi-asset arbitrage reactor. See [SNUT Mechanics](/v2/the-orchard/snut-mechanics.md) for the SNUT venue set; see [Tokens](/v2/tokens.md) for the full catalog.

## Data

### Why do prices differ between sources?

NUT supply=1 causes standard APIs to miscalculate market cap and price. Different DEX venues (Uniswap V3, V2, Aerodrome) can have different prices for the same token. This is a feature, not a bug — these price differences ARE the arbitrage opportunities. The portal shows prices from GeckoTerminal (GT), DexScreener (DS), Base RPC (RPC), CoinGecko (CG), and Balancer (BAL) with source labels.

### What data sources does this site use?

Five free sources, no API keys needed: (1) GeckoTerminal (GT) — token prices, volume, market cap. (2) DexScreener (DS) — DEX pair prices, liquidity, volume. (3) Base RPC (RPC) — on-chain totalSupply and decimals. (4) CoinGecko (CG) — aggregated price data. (5) Balancer API (BAL) — pNUT pool data (totalLiquidity, APR, NAV, token balances). Each source is labeled in price displays.

## Agents & NFTs

### What is the Smart Agent System?

Peanutoshi Nutkamoto is the official BASED NUT AI agent — a DeFi Meme Oracle and Liquidity Warlord that provides market insights, arbitrage analysis, and ecosystem guidance. Peanutoshi uses the NUT Sentiment Index (NSI) to adapt strategy based on market conditions. You can chat with Peanutoshi on the portal.

### What is the NUT Sentiment Index (NSI)?

Peanutoshi NSI tracks market sentiment: green = bullish (rally the Nut Army), red = defensive (fortify liquidity positions), neutral = meme warfare mode. The NSI adapts strategy based on real-time market conditions.

### What NFT collections exist in the ecosystem?

P-NUTS (Peanut Generals, 251), PEANUT ARMY (Peanut Soldiers, 5,013), ALMONDS (Almond Generals, 424), S-ALMONDS (Almond Soldiers, 6,238). All bonded to NUT via Mint Club bonding curves — mint to enlist, burn to reclaim. Trade fractions on Sudoswap. See [Tokens](/v2/tokens.md).

### How does NFT fractionalization work?

War NFTs are minted by depositing NUT via bonding curves and burned to withdraw the NUT backing — the bonding curve sets a floor price. Sudoswap pools enable fractional NFT trading in USDC or cbETH.

### What is the "Great Nut War"?

A fictional narrative portraying a conflict between the Peanut Republic and Almond Empire over resources like Salt, Butter, Oil, Honey and Caramel. These resources are not active tokens; they are marked TBA.

### What is the War Machine page?

The War Machine page documents the faction abilities and protocol defensive infrastructure of the Great Nut War. Each faction (Peanuts, Almonds, Cashews, Pecans, Hazelnuts, Coconuts, Chestnuts) has unique abilities — from damage reduction to morale burn to resource stealing. The War Machine is a gamified representation of the ecosystem competitive dynamics.

## Project

### Are there plans for a DAO or governance?

No. There is no formal team, roadmap or governance mechanism. The project is community-driven.

### What risks should users consider?

The NUTpaper warns that the ecosystem complexity and multilayered smart-contract structure may introduce vulnerabilities. No audits exist. Regulatory uncertainty. Participants should treat the project as entertainment and only risk what they can afford to lose. This is an experimental memefi project — NOT financial advice.

### How does the community engage?

The culture emphasises memes and community interaction. Follow BASED NUT on Twitter, join the Liquidity Portal, and keep an eye on Mint Club for new tokens.

### What can I do on the portal?

Explore the ecosystem: view live token data on the All Tokens page, dive into individual token profiles (NUT, SNUT, pNUT, SALT, NUTINO, NFTs), study arbitrage loops in the Arb Bot War Room, visualize token relationships on the Nut Tree, learn the lore in the Great Nut War and War Machine pages, browse NUTINO memes, or chat with Peanutoshi AI for real-time insights.

### What is the Nut Tree?

The Nut Tree is a visual hierarchy page showing how all tokens in the ecosystem derive from NUT. NUT sits at the root, branching into SNUT (deflationary layer), pNUT (index basket), and Mint Club tokens (SALT, NUTINO). NFT collections (P-NUTS, ALMD, S-ALMD, PNUTRMY) are also shown as NUT-backed assets. The tree makes it easy to understand the relationships between tokens at a glance.

### What is NUTINO memes?

NUTINO memes is a community gallery page featuring user-submitted memes and creative content from the BASED NUT ecosystem. It showcases the culture and humor of the Nut Army. Submit and browse nut-themed memes, NUTINO art, and community creations.
