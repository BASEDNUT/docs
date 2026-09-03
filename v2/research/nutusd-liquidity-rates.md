# 🔬 Research — nutUSD Liquidity & Rates (Experiment IV)

Fourth experiment in the nutUSD research series. [Experiment I](/v2/research/nutusd-testnet.md) verified the boundary; [Experiment II](/v2/research/nutusd-adversarial.md) recorded the failure modes; [Experiment III](/v2/research/nutusd-liquidation-envelope.md) mapped the seizure branches and oracle-zero states. This experiment measures the market under the production interest-rate model: accrual exactness, the utilization wall, and liquidity recovery. Experiments II, III, and V–VII run a zero-rate IRM to isolate static geometry from accrual; Experiment I measured its boundary and liquidation through live-feed accrual; this market runs the canonical AdaptiveCurveIRM — the model the production vault will use.

## Questions

| # | Question | Verdict |
|---|---|---|
| R1 | Does the production IRM accrue exactly? | Yes — the source-derived Taylor 3-term prediction matched the on-chain accrual to the base unit |
| R2 | What stops a withdrawal at near-full utilization? | Market liquidity — `InsufficientLiquidity` the moment the request exceeds idle |
| R3 | How does liquidity come back? | Repayment — a repaid unit becomes withdrawable immediately; the repaid 1 USDC was withdrawn in the next transaction |

## Environment

| Item | Value |
|---|---|
| Chain | Base Sepolia (84532) |
| Protocol | Morpho Blue, canonical deployment |
| Credit market | Fresh 38.5% LLTV market, id `0x7b976f12…e0a79fb3` |
| Oracle | `MorphoChainlinkOracleV2` [`0x067d1BcF…39dF34aA`](https://sepolia.basescan.org/address/0x067d1BcF9aF5E60E57e090F4feB996Ac39dF34aA) — WETH base feed at 2000, USDC quote at 1 |
| IRM | AdaptiveCurveIRM [`0x46415998764C29aB2a25CbeA6254146D50D22687`](https://sepolia.basescan.org/address/0x46415998764C29aB2a25CbeA6254146D50D22687) — canonical deployment |
| Borrower | 0.05 WETH collateral at the exact maximum — 38.5 USDC debt |
| Market supply | 500 USDC + 1 USDC dead; utilization at open 7.7% |

## Interest accrual

| Measure | Value |
|---|---|
| Elapsed | 1236 s (block timestamps) |
| Borrow rate before | 396,840,627 — wad per second, ≈ 1.25%/yr at 7.7% utilization |
| Borrow assets | 38,500,000 → 38,500,018 |
| Interest accrued | 18 base units |
| Prediction (Taylor 3-term, source-derived, contract rounding) | 18 — exact |
| Transaction | [`0xa6c0bd6d…a80993`](https://sepolia.basescan.org/tx/0xa6c0bd6d0c587350737258be83de9e142f2f8eb8b05668d13427e12634a80993) |

The IRM sets the borrow rate through exponential adaptation (`wExp`); Morpho's accrual then compounds the debt with the three-term Taylor approximation (`wTaylorCompounded`). The offline model — the same approximation and the same share-conversion rounding as the contract — predicted 18; the chain accrued 18. Accrual is deterministic and reproducible offline to the base unit.

## The utilization wall

Idle liquidity was drawn down to 1.000018 USDC (1 USDC plus the accrued interest) — utilization 97%:

| Step | Result |
|---|---|
| Withdraw 2 USDC at 1.000018 USDC idle | Reverts — `InsufficientLiquidity` |
| Repay 1 USDC | Borrow 38.500018 → 37.500018; idle 1.000018 → 2.000018 USDC |
| Withdraw the freed 1 USDC | Executes |

Final state: supply 38.500018 USDC, borrow 37.500018 — utilization 97%. The wall is exact: asset withdrawal is bounded by idle supply exactly, and repayment is the recovery path — a repaid unit is withdrawable immediately. Collateral withdrawal for the indebted borrower remains bounded by health (Experiment I).

At full utilization the depositors' USDC exit is the borrowers' repayment stream — the same coupling measured from the liquidator side in Experiment I, where the liquidator's repayment funded the supplier's exit to the base unit. The vault's `forceDeallocate` — a permissionless path that reclaims market allocation when vault liquidity runs short — is measured, with its allowance gate, penalty tiers, and sentinel counterpart, in [Experiment IX](/v2/research/nutusd-emergency-machinery.md).

## Findings

| # | Finding |
|---|---|
| F1 | The canonical AdaptiveCurveIRM accrues exactly: source-derived Taylor 3-term prediction == on-chain accrual — 18 base units over 1236 s at rate 396,840,627 (≈ 1.25%/yr at 7.7% utilization). |
| F2 | The utilization wall is exact: withdrawal reverts the moment it exceeds idle supply; at 1.000018 USDC idle, a 2 USDC withdrawal reverts `InsufficientLiquidity`. |
| F3 | Liquidity recovery is immediate: the repaid 1 USDC became withdrawable at once — no unlock delay, no queue. |
| F4 | Rate dynamics and boundary mechanics compose cleanly: the exact-max borrower of the Experiment I shape accrues interest deterministically under the production IRM. |

## Limitations

- One accrual window at one utilization point (7.7%); the full curve response — utilization ladder, saturation, adaptation, interest-driven liquidation waves — is measured in [Experiment XII](/v2/research/nutusd-rate-surface.md).
- Testnet liquidity: the wall is a mechanism property, not a market-depth statement.
- Single borrower, single supplier of record; concurrent exit races belong to the multi-user program.

## Artifacts

| Artifact | Value |
|---|---|
| Market id | `0x7b976f12…e0a79fb3` |
| Oracle | [`0x067d1BcF9aF5E60E57e090F4feB996Ac39dF34aA`](https://sepolia.basescan.org/address/0x067d1BcF9aF5E60E57e090F4feB996Ac39dF34aA) |
| Base feed (WETH) | [`0xFC5A3C6f…071D3DE`](https://sepolia.basescan.org/address/0xFC5A3C6fA34eaA8ed00E51E056F92D2e5071D3DE) — 2000.00 |
| Quote feed (USDC) | [`0x4879b280…2AbBbcEA`](https://sepolia.basescan.org/address/0x4879b280a317b584694c2C618f7704332AbBbcEA) — 1.00 |
| IRM | AdaptiveCurveIRM [`0x46415998764C29aB2a25CbeA6254146D50D22687`](https://sepolia.basescan.org/address/0x46415998764C29aB2a25CbeA6254146D50D22687) |
| Accrual transaction | [`0xa6c0bd6d…34a80993`](https://sepolia.basescan.org/tx/0xa6c0bd6d0c587350737258be83de9e142f2f8eb8b05668d13427e12634a80993) |
| Run window (UTC) | 2026-08-30 – 2026-08-31 |

## References

**Series**
- [nutUSD Testnet Experiment — Experiment I](/v2/research/nutusd-testnet.md)
- [nutUSD Adversarial Experiment — Experiment II](/v2/research/nutusd-adversarial.md)
- [nutUSD Liquidation Envelope — Experiment III](/v2/research/nutusd-liquidation-envelope.md)
- [nutUSD Production Recipe — Experiment VI](/v2/research/nutusd-production-recipe.md)
- [nutUSD — product page](/v2/tokens/nutusd.md)

**Protocol documentation**
- Interest rate models: <https://docs.morpho.org/developers/contracts/irm/>
- AdaptiveCurveIRM source: <https://github.com/morpho-org/morpho-blue-irm>
- Morpho.sol (accrual source): <https://github.com/morpho-org/morpho-blue/blob/main/src/Morpho.sol>

> ⚠️ **Experimental Memefi.** No intrinsic value, no expectation of financial gain. Entertainment only — nut responsibly. 🌰
