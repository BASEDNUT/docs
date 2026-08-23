# ⚙️ Machine-Readable Spec

***

This page is the **machine-readable reference** for the Arb Bot Builder: chain/RPC, tokens with addresses and decimals, liquidity pools, vaults, NFT collections, Sudoswap pools, function signatures, route IDs, and API endpoints — all straight from the site's `MACHINE_SPEC` section.

> **Traceability note:** the site interleaves token descriptions and addresses, and a few bindings in the source are ambiguous (noted inline). Addresses are snapshot-verified via Base RPC; **re-verify any contract against its latest state before executing against it.**

***

## Chain & RPC

| Field | Value |
|---|---|
| Chain | Base |
| Primary RPC | `https://mainnet.base.org` (rate-limits aggressively after ~5 requests) |
| Fallback RPC | `https://base.publicnode.com` |
| Fallback RPC 2 | `https://1rpc.io/base` |
| Retry | Yes — exponential backoff recommended |

*The numeric `chainId` is not stated in the source. All addresses, pools, and routes below are on Base.*

***

## Token Decimals (authoritative reference)

Source gives one complete reference for all ecosystem tokens. **Wrong decimals = wrong prices.**

| Token | Decimals | Trap? |
|---|---|---|
| NUT | 18 | — |
| SNUT | 9 | ⚠️ 9, NOT 18 |
| pNUT | 18 | — |
| SALT | 18 | — |
| NUTINO | 18 | — |
| WETH | 18 | — |
| AERO | 18 | — |
| cbBTC | 8 | ⚠️ 8, NOT 18 |
| cbETH | 18 | — |
| USDC | 6 | ⚠️ 6, NOT 18 |

***

## Tokens

| Token | Address (as paired in source) | Decimals | Role |
|---|---|---|---|
| NUT | `0xAC130701aa31c284c36609E2489f150F419AD7AD` | 18 | Root token. Anchor for all Mint Club curves. MCAP = price (supply = 1, unity token). |
| SNUT | *(no unambiguous address in source — the `0x2a5757…` shown beside it is the pNUT BPT)* | 9 | Liquid non-escrow NUT reward-position token. 1% tax (4-way: liquidity, manager, buyback/burn, NUT rewards). Recursive burn flywheel. |
| pNUT | `0x2a5757b60987ff10385de1d4d923792f6fdcfff1` | 18 | Balancer V2 WeightedPool BPT. 25% each: cbETH, cbBTC, NUT, SNUT. **The pool contract and token address are the same.** |
| SALT | `0x1EDe2AFC985F6D7aEb3F4c84B95A103c00D5dE81` | 18 | Mint Club bonding curve token backed by NUT. SALT/USDC on Aerodrome. |
| NUTINO | `0x30421e2d18dFF60B298eEF427cF868cA65f1476B` | 18 | Mint Club bonding curve token backed by NUT. NUTINO/cbBTC on Uniswap V2. |
| WETH | `0x940181a94A35A4569E4529A3CDfB74e38FD98631` | 18 | Wrapped ETH. Quote token for NUT/WETH and SNUT/WETH pools. |
| AERO | `0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf` | 18 | Aerodrome token. Quote for NUT/AERO pool. |
| cbBTC | `0x2Ae3F1Ec7F1f5012CFEab0185bfc7aa3cf0DEc22` | 8 | Coinbase Wrapped BTC. Quote for NUT/cbBTC and NUTINO/cbBTC. |
| cbETH | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | 18 | Coinbase Wrapped Staked ETH. 25% of pNUT basket. |
| USDC | *(address not present in the source token listing)* | 6 | USD stablecoin. Quote for SALT/USDC on Aerodrome. |
| PIPS | `0x3f2327221dd4f0bae660172606d6b288a1cf8ad9` | *(not stated in source)* | DevOps agent token. Trading fees fund its servers. 1%/1% transfer tax configured (official Virtuals pair only; external venues untaxed today). |

***

## Liquidity Pools

| Pair | Platform | Type | Address | Price Call |
|---|---|---|---|---|
| NUT/WETH | Uniswap V3 | Concentrated (1% fee tier, `fee=10000`) | `0xe3ce00e2ed742b142c15eedc208657dd22aa987e` | `slot0()` — **DEX Screener cannot see this pool** |
| NUT/WETH | Uniswap V2 | Constant product | `0x997bad8e9f5c34d5e9784caaa8a554a5e6192f53` | `getReserves()` |
| NUT/AERO | Aerodrome | Constant product (token0=AERO, token1=NUT) | `0x38630fede5e2032652640d98b2d3f9c6296eea5d` | `getReserves()` + `token0()` |
| NUT/cbBTC | Aerodrome | Constant product (token0=NUT, token1=cbBTC, 8d) | `0x15385c9281bc12d2e9bf5c081621944b0ee2acca` | `getReserves()` |
| SNUT/NUT | Aerodrome | Constant product — **dividend-eligible reactor** | `0x893faaa7baf7a8247fc7142afb28e13d51a5aae8` | `getReserves()` (SNUT 9 decimals) |
| SNUT/WETH | Uniswap V2 | Constant product | `0xB228…` *(truncated in source)* | `getReserves()` |
| NUTINO/cbBTC | Uniswap V2 | Constant product | `0xeafde67d470480d14139e3d91164c158b82b38e2` | `getReserves()` (cbBTC 8d) |
| SALT/USDC | Aerodrome | Constant product | `0x64ca0b147f625007b6f082abbb3ba217930eccb2` | `getReserves()` (USDC 6d) |
| PIPS/NUT | — | Concentrated liquidity (token0=PIPS, token1=NUT, 1% fee) | `0x7f8e532cf1be9ed688adb9e6585bc69f017201b5` | `slot0()` |
| PIPS/USDC | Balancer V3 | reCLAMM (1% fee) | `0xb19e3af68BB307369e8772A9E157431FcFE9Dd44` | — |
| SNUT/ETH-LP / ETH | Uniswap V2 | Meta-pool (LP tokens of SNUT/ETH main pool) | `0x82bbadb9d6b2c0a59ed01809e30323f89f6faa1c` | `getReserves()` |
| pNUT | Balancer V2 | WeightedPool (25% ×4) | `0x2a5757b60987ff10385de1d4d923792f6fdcfff1` | `getPoolTokens(poolId)` |

*Source's own count: "10 pools total: 4 NUT, 3 SNUT, 1 NUTINO, 1 SALT, 1 pNUT. Plus 3 NFT Sudoswap pools."*

### Critical pool quirks

* **Balancer V2 uses a singleton Vault.** All pNUT pool tokens (cbETH, cbBTC, NUT, SNUT) are held in the Balancer Vault, NOT in the pNUT pool contract. `balanceOf(pNUT_address)` returns **ALL ZEROS**. Use `balanceOf(BALANCER_VAULT)` or `getPoolTokens(poolId)` instead.
* **Uniswap V3 NUT/WETH = 1% fee tier** (`fee=10000`). Every swap costs 1% — factor into profitability. Query `fee()` with selector `0xddca3f43`.
* **Aerodrome pools (proxy pattern, `code_len=92`) do NOT implement `token1()`** (`0xd21220a7`) — it REVERTS. Use `token0()` + pool name semantics to infer token1.
* **Always verify token0/token1 ordering** before deriving prices from reserves.

***

## Vaults & Infrastructure

| Contract | Address | Role |
|---|---|---|
| Mint Club Lock | `0xc5a076cad94176c2996b32d8466be1ce757faa27` | Holds NUT reserves backing all Mint Club bonding curves (SALT, NUTINO). |
| Balancer Vault | `0xBA12222222228d8Ba445958a75a0704d566BF2C8` | Global vault for all Balancer V2 pools. Use `getPoolTokens(poolId)`. |
| Dead address | `0x000000000000000000000000000000000000dEaD` | Recursive burn sink. Dead-held SNUT earns NUT rewards. NUT sent to dead = burned. LP burned here cannot be removed. |

***

## NFT Collections

| Collection | Contract | Minted Supply |
|---|---|---|
| PNUTS | `0x794fcD89357C1CcF04a1a9A441ad4dB2Cd5EE387` | 251 |
| ALMD | `0x1A160456005AED47994E1c13C9bc31F274413927` | 424 |
| SALMD | `0x1E0f80529593185C021043ffcbfDcB8f4279C649` | 6,238 |
| PNUTRMY | `0xF07530…` *(truncated in source)* | 5,013 |

*Source: "PNUTS: 0x794fcD… (251 minted). ALMD: 0x1A1604… (424). SALMD: 0x1E0f80… (6238). PNUTRMY: 0xF07530… (5013)."*

### Sudoswap pools

The source states **"Sudoswap pools for 3 of 4"** collections. Three Sudoswap pool addresses appear in the source's interleaved registry:

| Sudoswap Pool Address |
|---|
| `0x262bEaa785a0eF65f5D9C1b8BA5c41980D087ff3` |
| `0x308C9BC0546723d6e4905c971cd34feBF1f94031` |
| `0xeE7243F0E02e5890c6415B5CbAe58e0D0fb758a5` |

*One collection has no Sudoswap pool. The source does not bind each pool address to a specific collection name — re-verify against the live registry before executing.*

***

## Function Signatures (Hex Selectors)

These are a **subset** of the read ABI, not the full ABI.

| Function | Selector | Scope | Notes |
|---|---|---|---|
| `slot0()` | `0x3850c7bd` | Uniswap V3 | Returns `sqrtPriceX96`, `tick`, `protocolFee`. |
| `getReserves()` | `0x0902f1ac` | Uniswap V2 / Aerodrome | Returns `reserve0`, `reserve1`, `blockTimestampLast`. |
| `token0()` | `0x0dfe1681` | Pool | CRITICAL for price direction. |
| `token1()` | `0xd21220a7` | Pool | REVERTS on Aerodrome pools. |
| `balanceOf()` | *(not stated)* | ERC20/ERC721 | Pool TVL and basket composition. |
| `totalSupply()` | `0x18160ddd` | ERC20/ERC721 | MCAP, NAV per share, NFT minted count. |
| `decimals()` | *(not stated)* | ERC20 | SNUT=9, cbBTC=8, USDC=6, others=18. |
| `name()` | *(not stated)* | ERC20 | Verification. |
| `liquidity()` | `0x1a686502` | Uniswap V3 | Do NOT use `getReserves()` for V3 pools. Alternative selector exists on some deployments. |
| `fee()` | `0xddca3f43` | Uniswap V3 | NUT/WETH V3 = 10000 (1%). |
| `getPoolTokens(poolId)` | *(not stated)* | Balancer V2 Vault | Returns `tokens[]`, `balances[]`, `lastChangeBlock`. |

***

## Route IDs

| Route | Value |
|---|---|
| pNUT poolId (Balancer V2) | `0x2a5757b60987ff10385de1d4d923792f6fdcfff100010000000000000000019e` |

*Used with `getPoolTokens(poolId)` on the Balancer Vault to read the pNUT basket composition. Basket weights: `[25, 25, 25, 25]` — cbETH, cbBTC, NUT, SNUT.*

***

## APIs

| Source | Use | Limitation |
|---|---|---|
| Base RPC (`eth_call`) | Core on-chain pricing (`slot0`, `getReserves`) | Rate-limits; use fallbacks + backoff. |
| CoinGecko | USD normalization for quote tokens (ETH, BTC, cbETH, AERO) | Do NOT use for NUT/SNUT/pNUT prices directly. |
| DexScreener | Secondary for V2/Aerodrome prices + TVL | CANNOT handle UniV3 NUT/WETH (returns NULL or wrong data). |
| GeckoTerminal | Alternative pool data / cross-verification | — |
| Mint Club V2 SDK (`npm i mint.club-v2-sdk`) or browser automation (Playwright) | Bonding curve prices for SALT/NUTINO | RPC unreliable for minimal-proxy Mint Club contracts. |
| Balancer API / `getPoolTokens` | pNUT basket composition + NAV | Needed because `balanceOf(pNUT)` returns zeros. |
| OpenSea API | NFT floor prices | For NFT venue arb (marketplace vs Sudoswap). |

### Data source hierarchy

* **V2 / Aerodrome pools:** Base RPC `getReserves()`; DexScreener/GeckoTerminal as secondary.
* **UniV3 NUT/WETH:** Base RPC `slot0()` only — DexScreener blind to it (returns NULL or wrong data).
* **Mint Club (SALT/NUTINO):** SDK or browser automation — never direct RPC on the minimal-proxy contract.
* **pNUT:** Balancer `getPoolTokens(poolId)` — not DEX APIs, not `balanceOf(pNUT)`.

***

*Reference: the deployed site's Arb Bot Builder Helper page, MACHINE_SPEC section. All addresses, decimals, selectors, pool IDs, and counts are verbatim from that page; ambiguous or truncated bindings are marked inline. Re-verify before executing.*
