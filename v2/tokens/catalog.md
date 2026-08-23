# 🥜 Token Catalog — Every Asset in the Orchard

**Status: LIVE** — all on Base mainnet (chain ID 8453). Explorer: [basescan.org](https://basescan.org).

Every asset the portal documents, by layer. The root anchors; the branches and canopy build on it.

## The Root

| Token | Supply | Role |
|---|---|---|
| **NUT** | 1 whole token (18 decimals) | The root of all liquidity. TRUE Price = TRUE Market Cap. No mint, no burn, no governance |

## The Branches

| Token | Supply | Role |
|---|---|---|
| **SNUT** | 100,000 (9 decimals) | Liquid non-escrow NUT reward-position token. 1% tax funds NUT rewards, buyback/burn, and liquidity. Dead-held SNUT keeps earning NUT — recursive burn flywheel |
| **pNUT** | BPT | Balancer V2 index basket holding 25% each of cbETH, cbBTC, NUT, and SNUT. NAV drift from market price creates arbitrage |

## The Nested Tokens (Bonding Curves)

| Token | Role |
|---|---|
| **SALT** | Mint Club bonding curve token backed by NUT. Two-venue arb loop: mint with NUT → sell for USDC on Aerodrome |
| **NUTINO** | Mint Club bonding curve token backed by NUT. Two-venue arb loop: mint with NUT → sell for cbBTC on Uniswap V2 |
| **MT** | Stakable asset — the active Mint Club staking vault pays SALT rewards for staked MT |

## The NFTs (War Ranks)

| Collection | Count | Role |
|---|---|---|
| **P-NUTS** — Peanut War Generals | 251 officer NFTs | Bonded to NUT. Mint to enlist, burn to reclaim. 200 SALT airdropped per General. Whole-NFT trading on Sudoswap in USDC |
| **PEANUT ARMY (PNUTRMY)** — Peanut Soldiers | 5,013 infantry NFTs | Bonded to NUT. 80 SALT airdropped per Soldier. Backbone of the Orchard — no Sudoswap pool yet |
| **ALMONDS (ALMD)** — Almond War Generals | 424 officer NFTs | Bonded to NUT. Golden Salted Swarm. 200 SALT airdropped per General. Whole-NFT trading on Sudoswap in cbETH |
| **S-ALMONDS (SALMD)** — Almond Soldiers | 6,238 infantry NFTs | Bonded to NUT. Sky-Seasoned Crunch. 80 SALT airdropped per Soldier. Whole-NFT trading on Sudoswap in cbETH |

## The Soil (Base Assets)

| Token | Role in the Orchard |
|---|---|
| **wETH** | Primary quote token for NUT and SNUT — main price discovery venues (NUT/wETH UniV3+V2, SNUT/wETH V2) |
| **cbETH** | Coinbase Wrapped Staked ETH — 25% collateral in pNUT basket; quote asset for Sudoswap NFT pools (ALMD, SALMD) |
| **cbBTC** | Coinbase Wrapped BTC — 25% collateral in pNUT basket; quote token for NUTINO DEX pool |
| **USDC** | Primary stablecoin on Base — quote token for SALT DEX pool (arb loop exit venue) and Sudoswap NFT pools |
| **AERO** | Aerodrome governance token — quote token in NUT/AERO pool; gauge emissions may incentivize NUT liquidity |
| **PIPS** | Compute fuel for Pipshell (DevOps agent). Trade fees fund agent compute. Infrastructure token — not a consumer product |

## Nested Token Mechanics (shared)

- Curve price = NUT_locked ÷ token_supply
- Buy price ≠ sell price (significant spread) — the spread acts as protocol revenue
- 1% royalty on mint/burn
- Mint when curve price < market price; burn when curve price > market price — that is the arbitrage
- Mint Club lists 14 NUT-backed tokens; anyone can deploy new NUT-collateralised tokens via bonding curves

## PIPS Tax Detail

1%/1% transfer tax configured — fires only on pools registered via `isLiquidityPool()`. The official Virtuals pair is the only registered pool; NUT/PIPS + PIPS/USDC are unregistered → untaxed today. Risk: owner can register an external pool anytime.

## Key Addresses

| Token | Address |
|---|---|
| NUT | `0xb8de15fb529d98c93c749de63c749d48d25a30df` |
| SNUT | `0xAC130701aa31c284c36609E2489f150F419AD7AD` |
| pNUT | `0x2a5757b60987ff10385de1d4d923792f6fdcfff1` |
| SALT | `0x1EDe2AFC985F6D7aEb3F4c84B95A103c00D5dE81` |
| NUTINO | `0x30421e2d18dFF60B298eEF427cF868cA65f1476B` |
| P-NUTS | `0x794fcD89357C1CcF04a1a9A441ad4dB2Cd5EE387` |
| S-ALMONDS | `0x1E0f80529593185C021043ffcbfDcB8f4279C649` |
| ALMONDS | `0x1A160456005AED47994E1c13C9bc31F274413927` |
