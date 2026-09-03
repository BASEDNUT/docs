# 🔬 Research — nutUSD Adversarial Experiment (Experiment II)

Second experiment in the nutUSD research series. [Experiment I](/v2/research/nutusd-testnet.md) verified the boundary, protection, and normal-liquidation mechanics. This experiment deliberately attacks the same configuration: bad debt, oracle misbehavior, liquidation overreach, rounding, and donation paths. Every number below is a measured on-chain value decoded from transaction receipts.

The product page ([nutUSD](/v2/tokens/nutusd.md)) states what the system is. This page records what happens when things break.

## Questions

| # | Question | Verdict |
|---|---|---|
| A1 | How does a collateral crash propagate to depositors? | Nested and exact — market dead shares, vault position, vault dead shares, depositor; pro-rata at every layer |
| A2 | Can an oracle spike be used to print debt? | Yes against a controllable feed — bad debt 7.202173 USDC created; the defense is feed quality, not the adapter |
| A3 | What does an underpriced (clamped-low) oracle do? | Vault safe; the borrower over-loses 6.50 USDC — the floor-stuck mirror direction is supplier bad debt (Experiment III) |
| A4 | What happens on a broken (negative) feed? | Asymmetric freeze — borrow, collateral exit, and liquidation revert; supply, withdraw, and repay stay live |
| A5 | Does a stale feed get served? | Yes — a 24-hour-old answer was served; the adapter discards `updatedAt` |
| A6 | Can liquidation over-seize or repeat? | No — over-seize and double-liquidation revert (raw underflow, not a graceful error) |
| A7 | Can rounding extract value? | No — exactly one base unit lost per odd cycle, floor rounding, favoring the vault |
| A8 | Can donations move the share price? | No — never instantly; vault gifts drip in rate-limited, adapter gifts are unrecoverable |

## Environment

Same stack as Experiment I, with two deliberate substitutions — mock price feeds under the real adapter:

| Item | Value |
|---|---|
| Chain | Base Sepolia (84532) |
| Protocol | Morpho Blue, canonical deployment |
| Credit market | Fresh 38.5% LLTV market, id `0xf38bfb2a…d17057cc` |
| Oracle adapter | `MorphoChainlinkOracleV2` [`0x72a389fd…36C70`](https://sepolia.basescan.org/address/0x72a389fd35E755CD7cb30B5387cb36c8f6a36C70) |
| Base feed (WETH) | Mock, 8 decimals, controllable — [`0x6C8a6786…e4de3`](https://sepolia.basescan.org/address/0x6C8a67866Fb1f2ac2aaa45bBB5c38c07C3Fe4de3) |
| Quote feed (USDC) | Mock, 8 decimals, controllable — [`0xcdcc8B5E…cCea`](https://sepolia.basescan.org/address/0xcdcc8B5E6e7cD4894EE957a3B13C992d20facCea) |
| Vault (ERC-4626) | [`0x4c34071b…c2826`](https://sepolia.basescan.org/address/0x4c34071b163D03F8e6dc85667c83D42EEafc2826) |
| Liquidity adapter | [`0x35F8a6a5…dfDE7`](https://sepolia.basescan.org/address/0x35F8a6a568e72b7142e6EeF875b577e029ddfDE7) |
| Actors | One executor plus ephemeral adversarial wallets (borrower, liquidator, depositor, prober) |

The mock feeds implement the Chainlink aggregator interface (`latestRoundData`). The adapter above them is the real `MorphoChainlinkOracleV2` — so oracle-guard behavior is measured exactly as it would behave over a misbehaving Chainlink feed.

## Method

- **24 offline tests** before any chain interaction — 76 total across both experiments.
- **24 gated phases**, each idempotent and resumable from persisted state.
- **Receipt-anchored measurement.** Every number is decoded from transaction events, never from balance diffs — load-balanced RPC node skew produced false readings twice during development, and event decoding eliminated that class of error.
- **Prediction first.** Every scenario computes its expected result offline before execution and asserts predicted == measured to the base unit.

## Scenarios

### A1 — Collateral crash → bad debt → depositor loss

A borrower at the maximum boundary: 0.05 WETH collateral, 38.5 USDC debt. The feed was crashed 80% ($2000 → $400): collateral value 20 USDC, below the debt. A liquidator seized all collateral:

| Measure | Value |
|---|---|
| Repaid | 17.391305 USDC (= 20 / 1.15) |
| Seized | 0.05 WETH (all collateral) |
| Bad debt | 21.108695 USDC — emitted as `badDebtAssets` and `badDebtShares` |
| Market supply | 502 → 480.891305 USDC — suppliers absorbed the loss, exact |
| Vault market position | Dropped 21.066645 = 21.108695 × 501/502 — the vault supplies 501 of the market's 502 |
| Depositor (500 of the vault's 501) | Redeemed 478.975403 — loss 21.024597, the nested pro-rata product 500/501 × 501/502 = 500/502, within ≤ 2 base units |

Nothing was hidden, shifted, or deferred — the loss landed on suppliers at the moment of liquidation, proportionally at every layer: the market's direct dead supply absorbed 0.042050, the vault's position absorbed 21.066645, the vault's dead shares absorbed another 0.042048, and the depositor took 21.024597. The nested 501s cancel — the depositor's loss equals the market loss × 500/502. The full ladder, measured layer by layer, is in [Experiment III](/v2/research/nutusd-liquidation-envelope.md).

### A2 — Oracle spike → borrow → crash

The feed was spiked 50% ($2000 → $3000). The borrower drew 11.55 USDC against 0.01 WETH — the spiked-price maximum. The feed was then crashed to $500. Liquidation repaid 4.347827 USDC (= 5 / 1.15); bad debt 7.202173 USDC; share price 1 → 0.9643.

This is the debt-printing path. It required moving the feed itself. Over live Chainlink feeds, this path is a feed failure, not an adapter failure — the adapter has no spike guard (see Oracle findings).

### A3 — Clamped-low oracle — underpricing direction

The feed was clamped to 1000 while the true price remained 2000 — the oracle underprices the collateral. A position was liquidated at the clamped price: the liquidator repaid 5 USDC and seized 0.00575 WETH — worth 11.50 USDC at the true price. The borrower over-lost 6.50 USDC. The vault was unaffected (bad debt 0).

An underpriced oracle is a borrower-side loss vector: premature liquidation and excessive collateral seizure. It is not the full minAnswer picture — the floor-stuck direction is the mirror:

### A3b — Floor-stuck oracle — overpricing direction

The classic minAnswer failure leaves the oracle above the true price after a collapse: collateral is overvalued, borrowing enlarges at the inflated price, and liquidation is delayed until the loss lands on suppliers. This direction is measured in [Experiment III](/v2/research/nutusd-liquidation-envelope.md): debt sized at the stuck price, then the feed corrected — a 50% correction stayed covered, a 60% correction left 0.371739 USDC of bad debt on suppliers.

The two directions split cleanly: underpriced oracle → borrower loss; overpriced (floor-stuck) oracle → supplier bad debt.

### A4 — Negative feed → asymmetric freeze

The feed was set to −1. The oracle's `price()` reverts. Frozen operations: borrow, `withdrawCollateral`, liquidate. Still-live operations: supply, withdraw (loan-asset side), repay, `supplyCollateral`.

A dead oracle traps borrowers — no collateral exit — but depositors keep the USDC exit door, bounded by market liquidity (the wall is measured in [Experiment IV](/v2/research/nutusd-liquidity-rates.md)). The freeze is the adapter's only negative-answer defense (an answer ≥ 0 check); it is not a graceful per-operation error.

The answer lattice is now complete across the series. Zero passes the same guard the negative answer fails, and the two zero states diverge: a zero quote feed panics in the composed division (`Panic 0x12`) with this same asymmetric-freeze shape; a zero base feed serves price 0 cleanly and turns the seizure path of liquidation into a drain — all collateral out for zero repayment. Both are measured in [Experiment III](/v2/research/nutusd-liquidation-envelope.md). Oracle state is not binary valid-or-revert; each lattice state carries a distinct consequence.

### A5 — Stale feed served

A 24-hour-old answer (86,632 seconds) was served at full price. The adapter discards `updatedAt` entirely — there is no staleness guard. Freshness rides on Chainlink's deviation and heartbeat monitoring, nothing else.

### A6 — Liquidation overreach

- **Over-seize** (seized > allowed for the repayment): reverts — as a raw arithmetic underflow, not a graceful error. There is no seize-cap check.
- **Double liquidation** (empty position): reverts `HEALTHY_POSITION`.
- **Healthy liquidation**: reverts.

### A7 — Dust sweep

Odd-amount deposit → redeem cycles: 1000001 → 1000000, 999999 → 999998, 123457 → 123456. Loss is exactly one base unit per cycle — floor rounding, favoring the vault. No extraction path across magnitudes.

### A8 — Donations

- **Direct USDC gift to the vault:** invisible to `totalAssets` at the moment of transfer — `totalAssets` counts the adapter's Morpho position, and excess balance is recognized only through the vault's rate limiter. A gift never moves the share price instantly; it drips into `totalAssets` capped per accrual at the recognized base × maxRate × elapsed, compounding across accruals (the drip is measured exactly in [Experiment V](/v2/research/nutusd-vault-machinery.md)). At a zero recognition rate it stays invisible indefinitely; in this experiment's configuration the recognized amount was zero throughout.
- **Gift to the adapter:** same class, one step worse — invisible to `realAssets`, and outside the vault's recognition path entirely: no drip, no sweep, locked.

Donation-dilution is impossible in this configuration: a gift cannot move the share price instantly, whether it is recognized later (vault — rate-limited) or never (adapter). Rescuing stray adapter funds remains impossible.

## Oracle findings

`MorphoChainlinkOracleV2` has exactly one guard: a non-negative answer. It discards `updatedAt`, has no staleness window, no min/max answer bounds, and no price-drop breaker. The deployed source states the assumption directly in its constructor: properly configured markets "should ensure" that the price cannot instantly change such that the new price is less than the old price multiplied by LLTV·LIF — feed quality is the defense, by design.

Measured consequences:

| Feed state | Behavior |
|---|---|
| Normal | Price served |
| Stale (24 h) | Served — no freshness check |
| Clamped low (minAnswer) | Served — liquidation executes at the clamped price |
| Spiked high | Served — borrowing enlarges at the spiked price |
| Negative | `price()` reverts — asymmetric market freeze |
| Zero quote | Guard passes — composed division panics (`Panic 0x12`), asymmetric freeze (Experiment III) |
| Zero base | Guard passes — price 0 served; the seize path of liquidation drains collateral for zero repayment (Experiment III) |

The trust stack for nutUSD oracles is therefore: Chainlink feed quality plus the V2 composition (the product of the base feeds divided by the product of the quote feeds, scaled by token decimals). Nothing else guards the path — and the choice is immutable at market creation.

## What this means for nutUSD

1. Depositor loss occurs whenever a failure creates unrecoverable borrower debt. Measured causes: a collateral crash deeper than 55.725% from a maximum-boundary borrow, oracle overvaluation followed by correction, and the zero-base-feed liquidation path (Experiment III). All converge on the same terminal mechanism: bad debt → supplier loss → vault-share loss, exact and proportional at every layer.
2. The remaining measured attacks either revert or hurt only the attacker or the borrower.
3. Oracle safety is entirely external to the adapter: it is a property of the feeds chosen, locked in at market creation.
4. A dead feed freezes borrowers but preserves the depositor exit door (bounded by market liquidity).
5. Rounding favors the vault; donations cannot dilute.

## Limitations

- Mock feeds stand in for Chainlink; live feeds add failure modes (sequencer uptime, L1 finality) not measured here.
- Zero-interest scenarios (the IRM is enabled but no accrual window elapsed); interest-driven liquidation waves are untested.
- One executor plus adversarial wallets — no concurrent multi-user races, no MEV simulation.
- Collateral is 18-decimal WETH; production cbBTC (8 decimals) and the two-leg cbBTC/USD ÷ USDC/USD oracle candidate are outside this experiment.
- Base Sepolia establishes behavior, not production liquidity.

## Forward program

Measured so far: boundary and normal liquidation (Experiment I); solvency, oracle failure, rounding, donations (this experiment); the seizure branches and the oracle-zero states (Experiment III); rates and the utilization wall (Experiment IV); vault machinery and the inflation matrix (Experiment V); the production-shaped rehearsal — 8-decimal collateral and the composed oracle (Experiment VI); the LLTV ladder — all eight standard rungs (Experiment VII). Remaining, in priority order:

| Experiment | Surface |
|---|---|
| [III](/v2/research/nutusd-liquidation-envelope.md) | Liquidation envelope — measured: seizure branches, the stuck-high feed, the zero-feed lattice, the nested loss ladder |
| [IV](/v2/research/nutusd-liquidity-rates.md) | Liquidity and rates — measured: AdaptiveCurveIRM accrual exact, the utilization wall, liquidity recovery |
| [V](/v2/research/nutusd-vault-machinery.md) | Vault machinery — measured: roles and timelock, the inflation matrix, the rate limiter |
| [VI](/v2/research/nutusd-production-recipe.md) | Production-shaped rehearsal — measured: 8-decimal collateral, three-leg composed oracle, boundary and crash liquidation exact |
| [VII](/v2/research/nutusd-lltv-ladder.md) | LLTV ladder — measured: all eight standard rungs, incentive and absorption geometry, the −55.725% recovery boundary |
| VIII | Planned: multi-user and adversarial composition — concurrent exits, ordering races, MEV, flash-loan-funded sequences, liquidator economics (gas, slippage, competing liquidators) |
| IX | Done — [Experiment IX](/v2/research/nutusd-emergency-machinery.md): `forceDeallocate` with its allowance gate and penalty tiers, the production-delay timelock and the self-wall, the sentinel, the `max*` family. Remainders folded forward: supply and deposit caps, adapter failure, Bundler share-price and slippage protection |
| X | Planned: automated assurance — Foundry invariant testing, Echidna/Medusa property fuzzing, differential math, static analysis, formal properties |
| XI | Planned: production equivalence — Base mainnet fork, real USDC, cbBTC, cbETH feeds and tokens |
| XII | Done — [Experiment XII](/v2/research/nutusd-rate-surface.md): the AdaptiveCurveIRM utilization ladder 0–100%, `rateAtTarget` adaptation under saturation and repayment, the interest-driven liquidation wave, the full unwind |

Tooling for the invariant layer: Foundry invariant testing, Echidna/Medusa property fuzzing, Slither/Aderyn static analysis, differential computation of core math.

## Best practices applied

- Bad-debt handling per Morpho's guidance ([curate/tutorials-v1/bad-debt](https://docs.morpho.org/curate/tutorials-v1/bad-debt/)).
- Risk classes separated per Morpho's risk documentation ([learn/resources/risks](https://docs.morpho.org/learn/resources/risks/)) — oracle risk, bad debt, and liquidity are distinct classes.
- Oracle assumptions taken from the deployed `MorphoChainlinkOracleV2` source and stated as assumptions, not inferred.
- Invariant-driven direction per Trail of Bits ([invariant-driven development](https://blog.trailofbits.com/2025/02/12/the-call-for-invariant-driven-development/), [Echidna for smart-contract libraries](https://blog.trailofbits.com/2020/08/17/using-echidna-to-test-a-smart-contract-library/)).
- Liquidation economics against Morpho's liquidation documentation ([learn/concepts/liquidation](https://docs.morpho.org/learn/concepts/liquidation/)) and the reference bot ecosystem ([morpho-blue-liquidation-bot](https://github.com/morpho-org/morpho-blue-liquidation-bot)).
- Foundry for the forward invariant layer ([getfoundry.sh](https://www.getfoundry.sh/guides/index.html)); Aderyn for static analysis ([aderyn.cyfrin.io](https://aderyn.cyfrin.io/overview)).

## References

**Morpho documentation**
- Risk & security: <https://docs.morpho.org/learn/resources/risks/>
- Bad debt management: <https://docs.morpho.org/curate/tutorials-v1/bad-debt/>
- Liquidation: <https://docs.morpho.org/learn/concepts/liquidation/>
- Interest rate models: <https://docs.morpho.org/developers/contracts/irm/>
- Vault V2: <https://docs.morpho.org/learn/concepts/vault-v2/>
- Oracle concept: <https://docs.morpho.org/learn/concepts/oracle/>
- Roles: <https://docs.morpho.org/curate/concepts/roles/>
- Adapter listing: <https://docs.morpho.org/curate/tutorials-v2/listing-adapters/>
- Morpho.sol (liquidation source): <https://github.com/morpho-org/morpho-blue/blob/main/src/Morpho.sol>

**Methodology**
- Trail of Bits — invariant-driven development: <https://blog.trailofbits.com/2025/02/12/the-call-for-invariant-driven-development/>
- Trail of Bits — Echidna property testing: <https://blog.trailofbits.com/2020/08/17/using-echidna-to-test-a-smart-contract-library/>
- Foundry guides: <https://www.getfoundry.sh/guides/index.html>
- Aderyn: <https://aderyn.cyfrin.io/overview>

**Series**
- [nutUSD Testnet Experiment — Experiment I](/v2/research/nutusd-testnet.md)
- [nutUSD — product page](/v2/tokens/nutusd.md)

## Appendix — adversarial transactions

All transactions on Base Sepolia, 2026-08-30, 05:58–07:16 UTC; liquidation transactions span blocks 46151903–46152400.

| Purpose | Transaction | Block |
|---|---|---|
| Bad-debt liquidation (A1) | [`0x557ca513…feb1cfec`](https://sepolia.basescan.org/tx/0x557ca5139eac4deff3d2f62d56e0c11c72da24e7900cffd564a61d43feb1cfec) | 46151903 |
| Spike-crash liquidation (A2) | [`0xb8683940…46c08bda`](https://sepolia.basescan.org/tx/0xb8683940729694127b35d622f420c24bb426db34c18461e7fcd6a0b346c08bda) | 46152400 |
| Clamp liquidation (A3) | [`0x986cd5d2…eaa81d08`](https://sepolia.basescan.org/tx/0x986cd5d2eb2f0a71c0989d1f6c9f6d2372739134c4eb0123f3703672eaa81d08) | 46152385 |
| Depositor exit after bad debt (A1) | [`0x426482fb…e8a11f58`](https://sepolia.basescan.org/tx/0x426482fb51405382e0472a6f0e691b5312bbde209d50956ac13bf797e8a11f58) | 46152250 |

> ⚠️ **Experimental Memefi.** No intrinsic value, no expectation of financial gain. Entertainment only — nut responsibly. 🌰
