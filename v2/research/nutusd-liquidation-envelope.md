# 🔬 Research — nutUSD Liquidation Envelope (Experiment III)

Third experiment in the nutUSD research series. [Experiment I](/v2/research/nutusd-testnet.md) verified the boundary and the normal liquidation; [Experiment II](/v2/research/nutusd-adversarial.md) recorded the failure modes. This experiment completes the liquidation envelope across the oracle-state lattice — partial and full seizure branches, a feed stuck above the true price, both zero-feed states, and the nested ladder a market loss climbs from market to depositor. Every number is a measured on-chain value decoded from transaction receipts.

## Questions

| # | Question | Verdict |
|---|---|---|
| L1 | Does a partial seizure settle exactly when collateral still covers the claim? | Yes — seize exactly debt × LIF ÷ price, repay the full debt, zero bad debt |
| L2 | What does a feed stuck above the true price do? | Enlarges borrowing at the inflated price; the correction depth decides covered seizure vs bad debt |
| L3 | What does a zero quote feed do? | The guard passes; the composed division panics — the same asymmetric freeze as a negative answer |
| L4 | What does a zero base feed do? | The guard passes; price 0 is served cleanly — and the seizure path of liquidation takes all collateral for zero repayment |
| L5 | How does a market loss reach an individual depositor? | Nested, exact, pro-rata at every layer — market dead shares, vault position, vault dead shares, depositor |

## Environment

| Item | Value |
|---|---|
| Chain | Base Sepolia (84532) |
| Protocol | Morpho Blue, canonical deployment |
| Credit market | Fresh 38.5% LLTV market, id [`0xc54c7a99…f305ebc`](https://sepolia.basescan.org/address/0xc54c7a998cf9f38abcc60049f21532a744f71f11d1ade3b332292a0bbf305ebc) |
| Oracle adapter | `MorphoChainlinkOracleV2` [`0x0577410f…36f9Ba`](https://sepolia.basescan.org/address/0x0577410feAB091718C1E7FecaFe67bfa0836f9Ba) |
| Base feed (WETH) | Mock, 8 decimals, controllable — [`0x53ebD058…7C96D5`](https://sepolia.basescan.org/address/0x53ebD05880442f45160B7f72175d1dD7547C96D5) |
| Quote feed (USDC) | Mock, 8 decimals, controllable — [`0x77D30fc5…D03bEeD`](https://sepolia.basescan.org/address/0x77D30fc564e3066Cc48c5AB35b4d082D8D03bEeD) |
| Borrowers | Four ephemeral wallets, each 0.01 WETH collateral, each at the exact maximum borrow for the stuck price |
| Market supply | 500 USDC from the experiment wallet + 1 USDC dead supply |

Method, as throughout the series: a prediction computed offline from source before every execution, then the on-chain measurement — receipt-anchored events with block-pinned state reads. Predicted equals measured to the base unit in every scenario below.

## Seizure branches

The base feed was held at 1000 while the borrowers sized their debt: the exact maximum at that price is 3.85 USDC per 0.01 WETH. The feed was then corrected to the true price and an independent wallet liquidated.

| Correction | True price | Seizure | Repaid | Bad debt | Borrower keeps |
|---|---|---|---|---|---|
| −50% | 500 | 0.008855 WETH — partial | 3.85 USDC — the full debt | 0 | 0.001145 WETH |
| −60% | 400 | 0.01 WETH — all collateral | 3.478261 USDC | 0.371739 USDC | 0 |

- **Covered branch** — [tx `0xfae38d8a…292fc071`](https://sepolia.basescan.org/tx/0xfae38d8a029efe2db9f1a5e837a594050713f5ece7b652fa7f347623292fc071): at the true price the collateral value (5 USDC) still covers debt × LIF (4.4275 USDC). The seizure is exactly ⌈debt × LIF ÷ price⌉, the full debt is repaid, the borrower keeps the remainder, and no loss reaches suppliers.
- **Bad-debt branch** — [tx `0xc3aa3db6…c142599f`](https://sepolia.basescan.org/tx/0xc3aa3db6c0cf449b3801f5f35dd6291b7c90d1e3d6935948af8a6931c142599f): at 4 USDC the incentive-adjusted claim exceeds all collateral. Everything is seized, repayment is ⌈4 ÷ 1.15⌉, and the 0.371739 USDC difference lands on suppliers.

A feed stuck above the true price is the supplier-side failure direction: it enlarges borrowing, and the correction depth decides who pays. The underpricing direction (Experiment II, A3) takes from the borrower instead. Both directions are now measured.

## Zero quote feed

The quote (USDC) feed was set to 0. The adapter's only guard — answer ≥ 0 — passes, and the composed price division hits the zero denominator: `price()` panics with `Panic(0x12)`.

| Operation | Behavior at quote = 0 |
|---|---|
| Borrow | Reverts |
| Withdraw collateral (indebted) | Reverts |
| Liquidate | Reverts |
| Supply | Live |
| Withdraw (loan asset) | Live |
| Repay | Live |

The freeze matches the negative-answer case (Experiment II, A4) in shape — borrowers are trapped, depositors keep the USDC exit door — but the failure is an arithmetic panic, not the guard. The exit door is still bounded by market liquidity (the wall is measured in [Experiment IV](/v2/research/nutusd-liquidity-rates.md)).

## Zero base feed — free seizure

The base (WETH) feed was set to 0. The guard passes and the adapter serves price 0 cleanly — no revert on `price()` itself. The consequences, measured on the canonical deployment:

- **Borrowing and indebted collateral exit revert** — the computed maximum borrow is zero.
- **The repayment path of `liquidate` panics** — debt recomputation divides by the price (`Panic(0x12)`).
- **The seizure path of `liquidate` executes with zero repayment.** The quoted value of any seizure is `seized × 0` = 0, the repaid shares are 0, and the requested collateral is subtracted regardless. Every indebted position can be emptied for nothing, and each emptied position socializes its full debt.

Measured: two borrowers, each 0.01 WETH seized for 0 repaid, each emitting 3.85 USDC of bad debt — [tx `0xfd4275ec…0bc6c3fa`](https://sepolia.basescan.org/tx/0xfd4275ec68e65c4aef893701d0a8377813d1cef42233aea4cf006c3c0bc6c3fa) and [tx `0xfd9a6c1c…d2c45dc1`](https://sepolia.basescan.org/tx/0xfd9a6c1cda81d9a92601aa301909644d5a56eb35bedf608720e4cb7bd2c45dc1). The final market state matched the offline prediction exactly: supply 492.928261 USDC, borrow 0.

**A zero base price is the most severe oracle state in the series: it does not freeze the market — it turns liquidation into a drain.** The defense is unchanged and external to the adapter: feed quality. Zero passes the only guard the adapter has.

A borrower's own exit stays open at price 0: repayment reads no price, and after a full repay-by-shares the position is healthy and collateral withdrawal succeeds — measured with a fresh wallet at price 0 (repay by shares, then full collateral exit). The exit door for borrowers is self-repayment, not liquidation.

## Nested loss ladder

The collateral-crash loss of Experiment II (A1) propagates through two share structures — the market's suppliers, then the vault's suppliers. The ladder, exact at every layer:

| Layer | Loss (USDC) | Share |
|---|---|---|
| Market bad debt | 21.108695 | — |
| → Market dead shares | 0.042050 | 1/502 of the market loss |
| → Vault position | 21.066645 | 501/502 of the market loss |
| → Vault dead shares | 0.042048 | 1/501 of the vault loss |
| → Depositor (500 of 501 vault supply) | 21.024597 | 500/501 of the vault loss |

The recorded redemption confirms the ladder end-to-end: the depositor redeemed 478.975403 USDC — a loss of 21.024597, matching 500/501 × 21.066645 within share-conversion rounding (≤ 2 base units). Losses do not skip layers and do not concentrate: the dead shares absorb their pro-rata slice at each level, and the depositor's loss is the product of the two pro-rata factors — 500/501 × 501/502 of the market loss — not the market total.

## Findings

| # | Finding |
|---|---|
| F1 | Partial seizure is exact: seize ⌈debt × LIF ÷ price⌉, repay the full debt, zero bad debt, the borrower keeps the remainder. |
| F2 | A stuck-high feed enlarges borrowing at the inflated price; a 50% correction stays covered, a 60% correction leaves 0.371739 USDC of bad debt on suppliers — the supplier-side failure direction, counterpart to underpricing (Experiment II, A3). |
| F3 | A zero quote feed passes the guard and panics in the composed division — asymmetric freeze, depositor exit preserved, bounded by liquidity. |
| F4 | A zero base feed passes the guard and serves price 0: the seizure path of liquidation takes all collateral for zero repayment and socializes the full debt — free seizure, measured on the canonical deployment. |
| F5 | The repayment path of liquidate divides by the price and panics at zero; a borrower's self-exit — repay by shares, then withdraw collateral — needs no price and stays open. |
| F6 | Loss propagation is nested and exact: market → vault → depositor, pro-rata at every layer, dead shares absorbing their slice. |

## Limitations

- Mock feeds stand in for Chainlink. A real aggregator serving zero has not been observed; the state is constructed, the contract behavior at that state is measured.
- One executor plus ephemeral wallets — no competing liquidators, no ordering races, no MEV.
- The stuck-high scenarios correct the feed before liquidation; a feed that stays stuck through liquidation is the Experiment II A3 configuration.

## Artifacts

All state is on-chain and immutable; the parameter set reproduces every scenario against the canonical deployment.

| Artifact | Value |
|---|---|
| Market id | `0xc54c7a998cf9f38abcc60049f21532a744f71f11d1ade3b332292a0bbf305ebc` |
| Oracle | [`0x0577410feAB091718C1E7FecaFe67bfa0836f9Ba`](https://sepolia.basescan.org/address/0x0577410feAB091718C1E7FecaFe67bfa0836f9Ba) |
| Base feed | [`0x53ebD05880442f45160B7f72175d1dD7547C96D5`](https://sepolia.basescan.org/address/0x53ebD05880442f45160B7f72175d1dD7547C96D5) — 8 decimals, `latestRoundData` controllable |
| Quote feed | [`0x77D30fc564e3066Cc48c5AB35b4d082D8D03bEeD`](https://sepolia.basescan.org/address/0x77D30fc564e3066Cc48c5AB35b4d082D8D03bEeD) |
| Covered partial seizure | [`0xfae38d8a…292fc071`](https://sepolia.basescan.org/tx/0xfae38d8a029efe2db9f1a5e837a594050713f5ece7b652fa7f347623292fc071) |
| Bad-debt full seizure | [`0xc3aa3db6…c142599f`](https://sepolia.basescan.org/tx/0xc3aa3db6c0cf449b3801f5f35dd6291b7c90d1e3d6935948af8a6931c142599f) |
| Free seizure 1 | [`0xfd4275ec…0bc6c3fa`](https://sepolia.basescan.org/tx/0xfd4275ec68e65c4aef893701d0a8377813d1cef42233aea4cf006c3c0bc6c3fa) — 0.01 WETH seized, 0 repaid, 3.85 USDC bad debt |
| Free seizure 2 | [`0xfd9a6c1c…d2c45dc1`](https://sepolia.basescan.org/tx/0xfd9a6c1cda81d9a92601aa301909644d5a56eb35bedf608720e4cb7bd2c45dc1) — same shape |
| Zero-base final market state | Supply 492,928,261 · borrow 0 — matched the offline prediction exactly |
| Run window (UTC) | 2026-08-30 – 2026-08-31 |

## References

**Series**
- [nutUSD Testnet Experiment — Experiment I](/v2/research/nutusd-testnet.md)
- [nutUSD Adversarial Experiment — Experiment II](/v2/research/nutusd-adversarial.md)
- [nutUSD Liquidity & Rates — Experiment IV](/v2/research/nutusd-liquidity-rates.md)
- [nutUSD Vault Machinery — Experiment V](/v2/research/nutusd-vault-machinery.md)
- [nutUSD Production Recipe — Experiment VI](/v2/research/nutusd-production-recipe.md)
- [nutUSD — product page](/v2/tokens/nutusd.md)

**Protocol documentation**
- Liquidation: <https://docs.morpho.org/learn/concepts/liquidation/>
- Risk & security: <https://docs.morpho.org/learn/resources/risks/>
- Morpho.sol (liquidation source): <https://github.com/morpho-org/morpho-blue/blob/main/src/Morpho.sol>
- morpho-blue-oracles (adapter source): <https://github.com/morpho-org/morpho-blue-oracles>

> ⚠️ **Experimental Memefi.** No intrinsic value, no expectation of financial gain. Entertainment only — nut responsibly. 🌰
