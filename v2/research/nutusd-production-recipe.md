# 🔬 Research — nutUSD Production Recipe (Experiment VI)

Sixth experiment in the nutUSD research series. [Experiment I](/v2/research/nutusd-testnet.md) verified the boundary on the rehearsal shape; [Experiment II](/v2/research/nutusd-adversarial.md) recorded the failure modes; [Experiment III](/v2/research/nutusd-liquidation-envelope.md) mapped the seizure branches and oracle-zero states; [Experiment IV](/v2/research/nutusd-liquidity-rates.md) measured liquidity and rates; [Experiment V](/v2/research/nutusd-vault-machinery.md) exercised the vault machinery. This experiment runs the production-shaped decimal rehearsal on testnet: an 8-decimal collateral token with a composed oracle — two base legs and one quote leg — through market creation, the exact-maximum borrow, the boundary, and a crash liquidation. Every number is a measured on-chain value.

## Questions

| # | Question | Verdict |
|---|---|---|
| PR1 | Does 8-decimal collateral settle exactly? | Yes — max borrow, boundary, and liquidation all exact against an 8-dec collateral / 6-dec loan pairing |
| PR2 | Does the composed oracle price exactly? | Yes — mockBTC/BTC × BTC/USD over USDC/USD (two base legs + one quote leg), source-derived prediction == measured price |
| PR3 | Does the 38.5% boundary hold on the production shape? | Yes — the exact maximum executes; +1 base unit reverts |
| PR4 | Does a crash liquidation settle exactly across the decimal mix? | Yes — seize, repay, and bad debt match prediction to the base unit |

## Environment

| Item | Value |
|---|---|
| Chain | Base Sepolia (84532) |
| Protocol | Morpho Blue, canonical deployment |
| Credit market | Fresh 38.5% LLTV market, id `0x1efd4ca2…05a923a9` |
| Collateral | mockBTC — 8 decimals, 1:1 stand-in for cbBTC — [`0x1D5bA143…64DeBbce`](https://sepolia.basescan.org/address/0x1D5bA143625843226F93BA536CCCC51a64DeBbce) |
| Oracle | `MorphoChainlinkOracleV2` [`0xF6Fd5307…3342aafB`](https://sepolia.basescan.org/address/0xF6Fd5307791461b21148e825aa5fab5E3342aafB) — composed |
| Base feed 1 | mockBTC/BTC = 1.0 — [`0x42413E54…088b6f44`](https://sepolia.basescan.org/address/0x42413E54BBba9696Fa646a718982c4cD088b6f44) |
| Base feed 2 | BTC/USD = 100,000 — [`0x239008a8…E133CFe8`](https://sepolia.basescan.org/address/0x239008a84b8181Bd07bcd8f8BA3815f7E133CFe8) |
| Quote feed | USDC/USD = 1.0 — [`0x648969d2…3FEb5b6c3`](https://sepolia.basescan.org/address/0x648969d24E04f5a6264cc4f68C264933FEb5b6c3) |
| Market supply | 500 USDC + 1 USDC dead |
| Borrower | 0.01 mockBTC collateral — 1,000 USDC quoted value at the composed price |

The oracle is composed: the collateral price is the product of the base feeds divided by the quote feeds, each answer scaled by its feed decimals and the token decimals — not a single direct feed. This experiment's three-leg shape rehearses decimal composition; it is not the final mainnet topology. A direct cbBTC/USD Chainlink feed is live on Base ([`0x07DA0E54…59f9D`](https://basescan.org/address/0x07DA0E54543a844a80ABE69c8A12F22B3aA59f9D)), and no Base cbBTC/BTC feed exists — so the production candidate is the simpler two-leg route: cbBTC/USD ÷ USDC/USD. Fewer oracle legs, fewer heartbeat and deviation interactions, fewer asynchronous-update states.

## Boundary

The borrower opened at the exact maximum: 385 USDC of debt against 0.01 mockBTC (1,000 USDC quoted × 38.5%). The chain matched the source-derived prediction to the base unit — the maximum borrow on 8-decimal collateral settles with zero rounding residue. A borrow of maximum + 1 base unit reverts; the boundary holds identically to the 18-decimal rehearsal shape of Experiment I.

## Crash liquidation

BTC/USD was corrected from 100,000 to 40,000 — collateral value 1,000 → 400 USDC, below the incentive-adjusted claim (385 × 1.15 = 442.75):

| Measure | Value |
|---|---|
| Seized | 0.01 mockBTC — all collateral |
| Repaid | 347.826087 USDC — ⌈400 ÷ 1.15⌉ |
| Bad debt | 37.173913 USDC — on suppliers |
| Prediction | Matched all three to the base unit |
| Transaction | [`0xb8a1cb38…a2cc28a`](https://sepolia.basescan.org/tx/0xb8a1cb3893c3ce2ce71abb3e3afae2c5dd4e0dc4efc79914dd75735b1a2cc28a) |

The liquidation settled exactly across the full decimal mix: 8-decimal collateral quoted through a composed oracle into 6-decimal debt. Cross-decimal precision is a documented failure class in lending integrations; on the canonical deployment with this recipe it is exact.

## What the production design inherits

| Property | Status |
|---|---|
| 8-decimal collateral settlement | Measured exact — boundary, borrow, liquidation |
| Composed oracle (3 legs: 2 base + 1 quote) | Measured exact — price, boundary, liquidation; the production candidate drops to 2 legs |
| 38.5% boundary | Measured exact — same wall as Experiment I |
| Crash liquidation accounting | Measured exact — seize/repay/bad-debt to the base unit |
| Feed failure states | Measured in Experiment III on the single-feed shape — the composed shape inherits the same adapter guard structure |

The production mainnet step swaps mockBTC for cbBTC and the mock feeds for the real cbBTC/USD and USDC/USD Chainlink feeds — the direct two-leg topology. The adapter structure, market parameters, and cross-decimal integration math are this experiment's; the two-leg oracle itself is unmeasured and belongs to the mainnet-fork step. If a BTC/USD leg is ever retained, the exact proxy must be specified: Chainlink enabled SVR by default on the Base BTC/USD feed on 2026-08-26, and both Standard and SVR proxies exist.

## Limitations

- Mock feeds stand in for Chainlink — real aggregator heartbeats, deviation tolerance, and answer lifecycle are external to this measurement.
- One borrower at one collateral size; the boundary sweep (50/90/99.9/100/101%) was measured on the rehearsal shape, not repeated here.
- The composed oracle's failure lattice (zero quote, zero base) was measured on the single-feed shape in Experiment III; the composed division structure is identical, but the two-leg base-feed product was not separately zeroed.
- The measured oracle is the three-leg composed shape; the production candidate (cbBTC/USD ÷ USDC/USD, two legs) is structurally simpler and unmeasured here.

## Artifacts

| Artifact | Value |
|---|---|
| Market id | `0x1efd4ca2…05a923a9` |
| Oracle | [`0xF6Fd5307791461b21148e825aa5fab5E3342aafB`](https://sepolia.basescan.org/address/0xF6Fd5307791461b21148e825aa5fab5E3342aafB) |
| mockBTC | [`0x1D5bA143625843226F93BA536CCCC51a64DeBbce`](https://sepolia.basescan.org/address/0x1D5bA143625843226F93BA536CCCC51a64DeBbce) — 8 decimals |
| Base feed 1 | [`0x42413E54BBba9696Fa646a718982c4cD088b6f44`](https://sepolia.basescan.org/address/0x42413E54BBba9696Fa646a718982c4cD088b6f44) — 1.0 |
| Base feed 2 | [`0x239008a84b8181Bd07bcd8f8BA3815f7E133CFe8`](https://sepolia.basescan.org/address/0x239008a84b8181Bd07bcd8f8BA3815f7E133CFe8) — 100,000 |
| Quote feed | [`0x648969d24E04f5a6264cc4f68C264933FEb5b6c3`](https://sepolia.basescan.org/address/0x648969d24E04f5a6264cc4f68C264933FEb5b6c3) — 1.0 |
| Crash liquidation | [`0xb8a1cb38…1a2cc28a`](https://sepolia.basescan.org/tx/0xb8a1cb3893c3ce2ce71abb3e3afae2c5dd4e0dc4efc79914dd75735b1a2cc28a) |
| Run window (UTC) | 2026-08-30 – 2026-08-31 |

## References

**Series**
- [nutUSD Testnet Experiment — Experiment I](/v2/research/nutusd-testnet.md)
- [nutUSD Adversarial Experiment — Experiment II](/v2/research/nutusd-adversarial.md)
- [nutUSD Liquidation Envelope — Experiment III](/v2/research/nutusd-liquidation-envelope.md)
- [nutUSD Liquidity & Rates — Experiment IV](/v2/research/nutusd-liquidity-rates.md)
- [nutUSD Vault Machinery — Experiment V](/v2/research/nutusd-vault-machinery.md)
- [nutUSD — product page](/v2/tokens/nutusd.md)

**Protocol documentation**
- Oracle concepts: <https://docs.morpho.org/learn/concepts/oracle/>
- morpho-blue-oracles (adapter source): <https://github.com/morpho-org/morpho-blue-oracles>
- Morpho.sol: <https://github.com/morpho-org/morpho-blue/blob/main/src/Morpho.sol>

> ⚠️ **Experimental Memefi.** No intrinsic value, no expectation of financial gain. Entertainment only — nut responsibly. 🌰
