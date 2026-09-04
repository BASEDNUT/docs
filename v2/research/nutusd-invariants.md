🔬 Research — nutUSD Invariant Suite (Experiment X)

Tenth experiment in the nutUSD research series — a method shift from receipts to randomized sequences. A Foundry handler suite drives the canonical Morpho Blue source (morpho-org/morpho-blue, forge-installed, unmodified) through random valid action sequences — twelve handlers, four actors, a controllable oracle and IRM mock — checking seven invariants after every call, plus two static proofs. Two runs: 64 runs × 100 depth, then 256 runs × 150 — 38,400 calls, 983 reverts, no violation in either.

## Questions

| # | Question | Verdict |
|---|---|---|
| I1 | Can a random sequence break the aggregate accounting? | No — total supply assets ≥ total borrow assets after every call |
| I2 | Is a healthy position ever liquidatable? | No — a ghost ledger tracks health at every liquidation attempt; zero healthy seizures across all attempts |
| I3 | Does the 1.15× cap hold under fuzz? | Yes — every recorded seizure respects the cap at 38.5% |
| I4 | Are shares conserved on both sides? | Yes — supply and borrow share ledgers track mint and burn exactly |
| I5 | Is the collateral ledger exact? | Yes — the ledger equals the collateral token balance held by Morpho |
| I6 | Does idle cover the ledger? | Yes — the idle balance covers the withdrawable cushion at every step |
| I7 | Do the static proofs hold? | Yes — a healthy position is not liquidatable at the source level, and a covered full-debt close seizes exactly the incentive formula |

## Environment

| Item | Value |
|---|---|
| Harness | Foundry forge, invariant target-contract sequences |
| Source | morpho-org/morpho-blue canonical, forge-installed, unmodified |
| Market | 38.5% LLTV · 1.15× incentive cap · OracleMock controllable · IrmMock utilization-APR · ERC20Mock 18/18 |
| Actors | 4 rotating through borrower, supplier, liquidator, owner |
| Controls | price, fee, and time (warp) are handler actions |

## The suite — what the fuzzer drives

| Handler | Calls | Reverts |
|---|---|---|
| supply | 512 | 0 |
| supplyCollateral | 517 | 0 |
| borrow | 558 | 60 |
| repayAssets | 511 | 11 |
| repayShares | 534 | 0 |
| withdraw | 541 | 1 |
| withdrawCollateral | 562 | 18 |
| liquidateSeized | 513 | 16 |
| liquidateRepaid | 511 | 4 |
| setFee | 558 | 21 |
| setPrice | 553 | 0 |
| warp | 530 | 0 |

Base run: 6,400 calls, 131 reverts. Deep run: 38,400 calls, 983 reverts, 23.4 s. The reverts are the boundaries doing their work — health-wall hits on borrow, liquidity hits on withdraw — the same walls the receipted series measured.

## The invariants — what holds after every call

1. **Aggregate liquidity accounting** — total supply assets ≥ total borrow assets: the market never lends more than it holds. This is a liquidity invariant, not collateral recoverability — a borrower can be economically unrecoverable while the aggregate holds; the loss ladder is [Experiment II](/v2/research/nutusd-adversarial.md)’s.
2. **Healthy-never-liquidated** — a ghost ledger records whether a position was healthy at the moment of each liquidation attempt, read post-accrual the way the contract itself reads it; a seizure on a healthy-at-attempt position would fail the invariant. None did.
3. **LIF cap at 38.5%** — every recorded seizure stays within the 1.15× incentive bound.
4. **Supply share conservation** — shares minted minus shares burned equal the market’s total supply shares.
5. **Borrow share conservation** — the same on the debt side.
6. **Collateral ledger** — the sum of tracked collateral equals the token balance Morpho actually holds.
7. **Idle coverage** — the idle balance always covers the withdrawable cushion.

## The static proofs

Two source-level proofs anchor the fuzzed claims: a constructed healthy position is not liquidatable — the health check is the same `maxBorrow ≥ borrowed` comparison the boundary receipts of [Experiment I](/v2/research/nutusd-testnet.md) walked — and a covered full-debt close seizes exactly the incentive formula. The collateral-exhaustion branch — collateral caps the seizure below the formula — is outside this static fixture; the ladder of [Experiment VII](/v2/research/nutusd-lltv-ladder.md) measured it rung by rung.

## Findings

| # | Finding |
|---|---|
| F1 | Seven invariants and two static proofs hold across 44,800 total calls, zero violations |
| F2 | The 983 deep-run reverts are boundary hits — health wall, liquidity wall — not failures; invariants check after every call, reverted or not |
| F3 | The healthy-never-liquidated ghost survives randomized price moves and time jumps: accrual is forced before the health read, matching the contract’s own order |
| F4 | Every handler ran ≥ 500 calls in the base run — no cold paths |

## Limitations

- Mock tokens at 18/18 decimals: the production decimal mix (6-dec USDC loan, 8-dec cbBTC collateral) is receipted on-chain in [Experiment VI](/v2/research/nutusd-production-recipe.md) and [Experiment XI](/v2/research/nutusd-production-fork.md), not fuzzed here.
- IrmMock utilization-APR: the canonical AdaptiveCurveIRM is measured on-chain in [Experiment IV](/v2/research/nutusd-liquidity-rates.md) and [Experiment XII](/v2/research/nutusd-rate-surface.md).
- The suite fuzzes the market layer; VaultV2 machinery is [Experiment V](/v2/research/nutusd-vault-machinery.md) and [Experiment IX](/v2/research/nutusd-emergency-machinery.md).
- Randomized sequences are evidence of no violation found, not proof none exists — 44,800 calls is a deep sample, not exhaustiveness.
- Single market, plain mocks: no multi-market composition, no fee-recipient flows, no external-token quirks (fee-on-transfer, rebasing).

## Artifacts

| Artifact | Value |
|---|---|
| Suite | `agent-core/exp10_invariants/test/NutUSDInvariant.t.sol` |
| Source | morpho-org/morpho-blue, forge-installed canonical |
| Base run | 64 runs × 100 depth — 6,400 calls, 131 reverts, 7/7 invariants + 2/2 static |
| Deep run | 256 runs × 150 depth — 38,400 calls, 983 reverts, 7/7 + 2/2 |
| Result | `agent-core/exp10_invariant_results.json` |
| Run window (UTC) | 2026-09-03 – 2026-09-04 |

## References

- [Experiment I](/v2/research/nutusd-testnet.md) — the boundary the aggregate-accounting and health invariants formalize
- [Experiment II](/v2/research/nutusd-adversarial.md) — the failure modes the ghost ledger guards
- [Experiment VII](/v2/research/nutusd-lltv-ladder.md) — the incentive cap, measured rung by rung
- [Experiment XI](/v2/research/nutusd-production-fork.md) — the production decimal mix on a mainnet fork
- [nutUSD](/v2/tokens/nutusd.md) — the credit layer

> 🥜 Forty-four thousand eight hundred random hands reshuffled the ledger — every wall held, every share counted, not one peanut rolled loose.


{% hint style="warning" %}
BASED NUT is an experimental memefi ecosystem. Nothing here is financial advice, no asset carries intrinsic value, and no figure on this page is a promise of performance. Measure twice, nut responsibly.
{% endhint %}
