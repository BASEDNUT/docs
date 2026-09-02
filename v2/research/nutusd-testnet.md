# 🔬 Research — nutUSD Testnet Experiment (Experiment I)

This page records the controlled experiment behind the nutUSD credit layer's boundary and protection properties. The product page ([nutUSD](/v2/tokens/nutusd.md)) states what the system is; this page records how those properties were established, what was measured, and what remains untested. The follow-on [Adversarial Experiment](/v2/research/nutusd-adversarial.md) attacks the same configuration — bad debt, oracle misbehavior, and value-extraction paths.

All results were produced on Base Sepolia with live Chainlink price feeds and the canonical Morpho Blue deployment. nutUSD is not deployed on Base mainnet.

## Questions

| # | Question | Verdict |
|---|---|---|
| Q1 | Is the 38.5% LLTV a hard borrowing ceiling, and where does liquidation begin? | Hard ceiling; a position at the maximum stays healthy; crossing requires accrued interest or price movement |
| Q2 | Are protections bidirectional — healthy borrowers and standing lenders both covered? | Yes |
| Q3 | How is repayment settled, and what happens on overshoot? | Shares for exact full closure; an oversized asset-denominated repayment can fail — see F4 |
| Q4 | What does a real liquidation pay, and to whom? | 1.15× incentive, zero bad debt, independent liquidator |
| Q5 | What bounds a withdrawal — market liquidity or outstanding debt? | Both, separately enforced |
| Q6 | Does the vault hold idle capital? | None in the tested configuration |

## Environment

| Item | Value |
|---|---|
| Chain | Base Sepolia (84532) |
| Protocol | Morpho Blue, canonical deployment ([contract addresses](https://docs.morpho.org/developers/contracts/addresses/)) |
| Loan asset | USDC (testnet mock, 6 decimals) |
| Collateral | WETH, cbETH (testnet) |
| Price feeds | Live Chainlink Base feeds, wrapped by Morpho oracle adapters |
| Oracle adapters | WETH/USDC [0x0d9b096b904adaF33f3327052ab3D00A6EFf7e13](https://sepolia.basescan.org/address/0x0d9b096b904adaF33f3327052ab3D00A6EFf7e13) · cbETH/USDC [0x7762a74A02767F3369f5fA99D8E72237dD8041E2](https://sepolia.basescan.org/address/0x7762a74A02767F3369f5fA99D8E72237dD8041E2) — adapter price vs live feed drift measured 0.00000% |
| Credit markets | WETH/USDC and cbETH/USDC at 38.5% LLTV |
| Vault (ERC-4626) | [0x998C1a0aF0009d695A430521E97303f61ffb8928](https://sepolia.basescan.org/address/0x998C1a0aF0009d695A430521E97303f61ffb8928) |
| Liquidity adapter | [0x4eE61C2592a3B80A4324A7ce4F1be9541894b310](https://sepolia.basescan.org/address/0x4eE61C2592a3B80A4324A7ce4F1be9541894b310) |
| Closure market (fresh salt) | `0x32085c90…c2db7a` |
| Closure oracle | [0x32338F4e75E5f2a5C2AF3599aC5fbcdEa8248BA7](https://sepolia.basescan.org/address/0x32338F4e75E5f2a5C2AF3599aC5fbcdEa8248BA7) |
| Independent liquidator | [0x7b2198D66DD6de5c3b4323AD84C2446c88BDBD7C](https://sepolia.basescan.org/address/0x7b2198D66DD6de5c3b4323AD84C2446c88BDBD7C) — ephemeral, single-purpose wallet |

## Method

- **Unit-first.** 52 offline tests across two suites — 31 market-and-vault, 21 closure — cover calldata encoding, event decoding, and boundary math before any chain interaction.
- **Staged live gates.** 27 phases total (13 market-and-vault phases, 14 closure phases); every phase is gated by assertions on transaction receipts and on-chain reads.
- **Idempotent phases.** Each phase resumes from persisted state; a crash never re-broadcasts a settled transaction.
- **Chain-verified decoding.** The `Liquidate` event signature was derived offline, then corrected against the live receipt — the deployed contract emits the eight-argument form. A regression test pins the observed event topic.
- **Fresh-market isolation.** A fresh CREATE2 salt gives the closure oracle a distinct address; because the oracle address is a Morpho market parameter, the market ID is distinct — the closure run never touches the original market's state.

## Boundary

Sweep against a fixed collateral position (0.01 WETH):

| Borrow (fraction of maximum) | Outcome |
|---|---|
| 50% | Executed |
| 90% | Executed |
| 99.9% | Executed |
| 100% | Executed at the highest executable amount — floor rounding places it below the theoretical maximum |
| 101% | Rejected |

`Maximum Debt = Collateral Value × 0.385`

The 38.5% LLTV is a borrowing ceiling, not a liquidation trigger. A position at the computed maximum remains healthy — Morpho requires health after borrowing, and liquidation becomes possible only once accrued debt or collateral-price movement pushes the position past the ceiling. The measured crossing used interest accrual, not an oracle move (see Real liquidation).

Closure run: 0.02 WETH collateral · maximum debt 18.913388 USDC · borrowed 18.913386 USDC (two base units below the maximum) · market utilization at borrow 94.97%.

## Protections

| Probe | Outcome |
|---|---|
| Liquidate a healthy position | Rejected |
| Withdraw collateral while debt stands | Rejected — insufficient collateral |
| Withdraw beyond market liquidity | Rejected — insufficient liquidity |
| Zero-value borrow | Rejected |
| Zero-value repay | Rejected |

The two withdrawal bounds were probed as read-only revert calls at near-full utilization; the remainder were real transactions. The two bounds are distinct: liquidity bounds asset withdrawal, debt bounds collateral withdrawal.

## Real liquidation

The position was opened at the boundary; the protocol's own interest accrual moved it above 38.5%. No oracle manipulation was used — the feeds are live Chainlink. Eligibility was detected at block 46143144, and an independent wallet executed the liquidation.

| Measure | Value |
|---|---|
| Repaid | 4.271801 USDC |
| Seized | 0.002 WETH |
| Seized value at oracle price | 4.912568 USDC |
| Liquidation incentive | 1.1500× |
| Bad debt | 0 (assets and shares) |
| Gross liquidation bonus at oracle valuation | 0.640767 USDC (net profit not measured — gas and collateral-conversion costs excluded) |
| Transaction | [0x57a75a06…98d38f8](https://sepolia.basescan.org/tx/0x57a75a06ec563b79334c8723b56a64207116fa9c8a16849c9fe70668898d38f8) |

### Incentive formula

From the Morpho Blue source (`Morpho.sol`, `liquidate()`; `ConstantsLib.sol`):

`LIF = min(1.15, 1 / (1 − 0.3 × (1 − LLTV)))`

At LLTV = 0.385 the uncapped value is 1.2262; the protocol cap of 1.15 binds. The measured on-chain ratio (seized value ÷ repaid) was 1.14999…, matching the capped formula within share-conversion rounding. **The 38.5% choice therefore fixes the liquidation incentive at exactly 1.15× — the protocol maximum.** The cap binds below ≈56.52% LLTV; among Morpho's standard nonzero LLTVs (62.5% and up) none other reaches it. 38.5% pairs the lowest approved leverage ceiling with the maximum liquidation draw.

### After the liquidation

The partial liquidation pulled the position back under the boundary; protections returned. The position was then repaid in shares and closed — the remaining collateral (0.018 WETH) returned in full, the remaining supply withdrawn, the market left clean.

The experiment wallet held both roles, depositor and borrower. Its closing balance: +4.271802 net USDC and −0.002 WETH. At near-full utilization the liquidator's repayment is the supplier's exit liquidity — the withdrawn supply exceeded the remaining debt by the amount the liquidator had repaid, to one base unit. The economic cost of the liquidation was the seized 0.002 WETH (4.912568 USDC at the oracle price) against 4.271801 USDC of debt removed: the 0.640767 difference is the 1.15× incentive, borne by the borrower's collateral.

## Vault behavior

- **First shares.** Dead shares were seeded to the burn address in the vault and each credit market before user deposits — the first-depositor inflation window was closed before anyone deposited. This is a deliberate deployment step, following Morpho's vault guidance.
- **Deposit allocation.** Every USDC deposit is allocated to the credit market automatically; the idle balance measured zero throughout the tested configuration.
- **Redemption.** A full exit — every share in one transaction — returned USDC matching the expected value within one base unit.
- **Repayment arithmetic.** A repay call defined in assets does not clamp to outstanding debt; overshooting fails with an arithmetic error. Exact full closure was performed in shares; asset-denominated repayment remains valid for partial repayment.

## Findings

| # | Finding |
|---|---|
| F1 | The 38.5% LLTV forms a hard borrowing ceiling. The highest executable borrow sat one USDC base unit below the theoretical floor-rounded maximum; attempts beyond the ceiling reverted. A position at the maximum remains healthy; liquidation requires crossing via accrual or price movement. |
| F2 | Protections are bidirectional: healthy positions cannot be liquidated; indebted positions cannot withdraw collateral. |
| F3 | Two distinct withdrawal bounds, both enforced: market liquidity bounds asset withdrawal; debt bounds collateral withdrawal. |
| F4 | Asset-denominated repayment does not clamp to outstanding debt; an oversized repayment can revert when the computed shares exceed the position. Exact full closure uses the outstanding shares. |
| F5 | At 38.5% LLTV the liquidation incentive is exactly 1.15× — the protocol cap binds, measured on-chain. The cap binds below ≈56.52% LLTV; 38.5% is the only nonzero standard Morpho LLTV that receives the maximum. |
| F6 | A real liquidation executed by an independent party produced zero bad debt and a gross liquidation bonus of 0.640767 USDC at oracle valuation; net profit was not measured. |
| F7 | Before user deposits, the experiment seeded dead shares to the burn address in the vault and each credit market, closing the first-depositor inflation window. |
| F8 | The vault holds no idle capital in the tested configuration; deposits allocate automatically. |
| F9 | Full-exit redemption matched the expected value within one USDC base unit. |

## Limitations

- Single executor for the market and vault phases; the independent party executed only the liquidation.
- Testnet assets: mock USDC and testnet WETH/cbETH. Mainnet liquidity and behavior differ.
- Live Chainlink feeds cannot be crashed at will; the boundary crossing used interest accrual at an exact-boundary position rather than an oracle price move. Oracle failure modes were exercised in [Experiment II](/v2/research/nutusd-adversarial.md) against controlled feeds standing in for Chainlink.
- No multi-user concurrency and no adversarial flash-loan suite.
- Base Sepolia establishes mechanism behavior, not production performance.

## Best practices applied

- Conservative LLTV selection per Morpho's curation guidance ([docs.morpho.org/curate](https://docs.morpho.org/curate/)).
- Chainlink price feeds wrapped in Morpho oracle adapters, per the oracle requirements ([ecosystem/oracles](https://docs.morpho.org/developers/ecosystem/oracles/)).
- Dead-share initialization against first-depositor inflation ([vault-v2](https://github.com/morpho-org/vault-v2)).
- Share-based repayment for exact full closure — both asset- and share-denominated repayment exist; shares are the precise close path (measured; see F4).
- Liquidation economics verified against the reference bot ecosystem ([morpho-blue-liquidation-bot](https://github.com/morpho-org/morpho-blue-liquidation-bot), [Liquidator-Morpho](https://github.com/etherhood/Liquidator-Morpho), [morpho-liquidator-bot](https://github.com/zach030/morpho-liquidator-bot)).
- Interface listing policy reviewed for the future mainnet surface ([listing policy](https://docs.morpho.org/get-started/resources/interface-listing-policy/)).

## Artifacts

All state below is on-chain and immutable; the parameter set is sufficient to reproduce every scenario against the canonical deployment.

| Artifact | Value |
|---|---|
| Chain | Base Sepolia (84532), public RPC `https://sepolia.base.org` |
| Morpho Blue | [`0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb`](https://sepolia.basescan.org/address/0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb) — canonical per the [official addresses page](https://docs.morpho.org/developers/contracts/addresses/) |
| Oracle factory (V2) | [`0x2DC205F24BCb6B311E5cdf0745B0741648Aebd3d`](https://sepolia.basescan.org/address/0x2DC205F24BCb6B311E5cdf0745B0741648Aebd3d) |
| Vault V2 factory | [`0xE3a2CEbca662d99D0F279aF13a6bb8c9825D2ea0`](https://sepolia.basescan.org/address/0xE3a2CEbca662d99D0F279aF13a6bb8c9825D2ea0) |
| Adapter factory | [`0xa24674Cc2c603FBA8AE6b442E3dB05f3dDaAa3D5`](https://sepolia.basescan.org/address/0xa24674Cc2c603FBA8AE6b442E3dB05f3dDaAa3D5) |
| AdaptiveCurve IRM | [`0x46415998764C29aB2a25CbeA6254146D50D22687`](https://sepolia.basescan.org/address/0x46415998764C29aB2a25CbeA6254146D50D22687) |
| LLTV (raw) | 385000000000000000000000000 (38.5%) |
| Rehearsal market ID | `0x3988b77d…23aa02ba` |
| Closure market | ID `0x32085c90…c2db7a`, CREATE2 salt 1788054426 |
| Adversarial market ID | `0xf38bfb2a…d17057cc` (Experiment II) |
| Dead deposits | Burn address `0x…dEaD`, seeded before user deposits — 10^6 base units (1 USDC) in the closure and adversarial markets/vaults; 10^12 base units in the original market-and-vault rehearsal (larger seed, same purpose) |
| Run windows (UTC) | 2026-08-29 06:43–15:35 (market + vault) · 2026-08-30 01:47–01:56 (closure) · 2026-08-30 05:58–07:16 (adversarial) |
| Closure block range | 46143070–46143350 |
| Adversarial liquidation blocks | 46151903–46152400 |
| Offline tests | 76 across three suites (31 market-and-vault, 21 closure, 24 adversarial) |
| `Liquidate` event | 8-argument form; topic = keccak256 of `Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)`; pinned by regression test against the live receipt |

The measurement harness is internal tooling; the complete on-chain record — transactions, receipts, events — is public, and the parameter set above reproduces every scenario against the immutable deployment.

## References

**Protocol documentation**

- Morpho — Learn: <https://docs.morpho.org/learn/>
- Morpho — Developers: <https://docs.morpho.org/developers/>
- Morpho — Curate: <https://docs.morpho.org/curate/>
- Contract addresses: <https://docs.morpho.org/developers/contracts/addresses/>
- Oracles ecosystem: <https://docs.morpho.org/developers/ecosystem/oracles/>
- Liquidation bots: <https://docs.morpho.org/developers/ecosystem/liquidation-bots/>
- Public allocator: <https://docs.morpho.org/learn/concepts/public-allocator/>
- App ecosystem: <https://docs.morpho.org/get-started/resources/app-ecosystem/>
- Interface listing policy: <https://docs.morpho.org/get-started/resources/interface-listing-policy/>
- Vaults app: <https://app.morpho.org/vaults>

**SDKs and APIs**

- SDKs: <https://docs.morpho.org/developers/sdks/get-started/> · <https://github.com/morpho-org/sdks>
- API: <https://docs.morpho.org/developers/api/get-started/>

**Contracts and code**

- vault-v2: <https://github.com/morpho-org/vault-v2>
- vault-v2-adapter-registries: <https://github.com/morpho-org/vault-v2-adapter-registries>
- metamorpho: <https://github.com/morpho-org/metamorpho> · v1.1: <https://github.com/morpho-org/metamorpho-v1.1>
- morpho-lite-apps: <https://github.com/morpho-org/morpho-lite-apps/tree/main/apps/lite>
- ponder-for-morpho-v1: <https://github.com/morpho-org/ponder-for-morpho-v1>
- bundles: <https://github.com/morpho-org/bundles>
- morpho-bots: <https://github.com/morpho-org/morpho-bots>
- midnight: <https://github.com/morpho-org/midnight> · midnight-pocs: <https://github.com/morpho-org/midnight-pocs>
- viem-dlc: <https://github.com/morpho-org/viem-dlc>
- morpho-token: <https://github.com/morpho-org/morpho-token>

**Liquidation tooling**

- morpho-blue-liquidation-bot: <https://github.com/morpho-org/morpho-blue-liquidation-bot>
- Liquidator-Morpho (etherhood): <https://github.com/etherhood/Liquidator-Morpho>
- morpho-liquidator-bot (zach030): <https://github.com/zach030/morpho-liquidator-bot>

**Chainlink data feeds**

- Data feeds API reference: <https://docs.chain.link/data-feeds/api-reference>
- MVR feeds API reference: <https://docs.chain.link/data-feeds/mvr-feeds/api-reference>
- Chainlink for agents: <https://docs.chain.link/resources/chainlink-for-agents?parent=dataFeeds>
- Developer agent skills: <https://docs.chain.link/resources/chainlink-developer-agent-skills?parent=dataFeeds>

**Agent resources**

- Morpho agent skills: <https://docs.morpho.org/developers/agents/skills/>
- Morpho LLMs documentation: <https://docs.morpho.org/developers/agents/llms/>
- Agents get started: <https://docs.morpho.org/developers/agents/get-started/>
- morpho-skills: <https://github.com/morpho-org/morpho-skills>

## Appendix — closure transactions

| Purpose | Transaction |
|---|---|
| Oracle deployment (fresh salt) | [0x19468b0d…c4e4322](https://sepolia.basescan.org/tx/0x19468b0dd5392292f15fb9d244a77a0f90d9fcbfdb444ed2467ecc797c4e4322) |
| Market creation | [0x45c9ab5c…82eb13b8](https://sepolia.basescan.org/tx/0x45c9ab5c595c0b401dcd64bb1be502ac67f1af4dc47435360488869182eb13b8) |
| Dead deposit | [0x08a3f57b…06dc5c3](https://sepolia.basescan.org/tx/0x08a3f57b73d477314e852982c7d59d77d04fef0d97e396a4f3a76c78106dc5c3) |
| Supply (max-borrowable) | [0xf2122148…bc1fb2ad](https://sepolia.basescan.org/tx/0xf2122148af0419dc62c1cb3eca83e877ecb45c693b52ef69828857f7bc1fb2ad) |
| Collateral supply | [0x283d5a8a…30f3a89ce](https://sepolia.basescan.org/tx/0x283d5a8adc8b919606353d0e6acd748e1d335113f4d47093b7dede230f3a89ce) |
| Boundary borrow | [0x7fc1530d…8e0947498](https://sepolia.basescan.org/tx/0x7fc1530d59910bfe5a1b8cd58788ec585edd6abd9ea7ddd20f8869e8e0947498) |
| Liquidator gas funding | [0xd36528ed…6415c4098](https://sepolia.basescan.org/tx/0xd36528edfefa0c3305cf69f2cbd0984b574ddc6bc8165dc54cbb7046415c4098) |
| Liquidator USDC mint | [0x92eb821a…0a89b64b2](https://sepolia.basescan.org/tx/0x92eb821add77eb5e06def92c1af28524fbeef7b6c2f31b96aa0e2b30a89b64b2) |
| Liquidator approval | [0x9c448a38…25aa9172](https://sepolia.basescan.org/tx/0x9c448a386fc7e0422fcb21b477f408707c7fb5d7a578904aaa698c3e25aa9172) |
| Real liquidation | [0x57a75a06…898d38f8](https://sepolia.basescan.org/tx/0x57a75a06ec563b79334c8723b56a64207116fa9c8a16849c9fe70668898d38f8) |
| Repay by shares (cleanup) | [0x8d8025c6…de3a56a68](https://sepolia.basescan.org/tx/0x8d8025c6656850ef320c33958dd91461db13f7453c480225297b8d4de3a56a68) |
| Collateral withdrawal (cleanup) | [0xdc9d6e53…9640aaad8](https://sepolia.basescan.org/tx/0xdc9d6e5378e6181edc5e6e78afb30f32fe52422d74a263392b6dcbc9640aaad8) |
| Supply withdrawal (cleanup) | [0xd1eb3dd7…7b8c1a763d](https://sepolia.basescan.org/tx/0xd1eb3dd7dbc1a2a950a73f4fdc0ce5ec28921b387d6d4fd087e65b7b8c1a763d) |

> ⚠️ **Experimental Memefi.** No intrinsic value, no expectation of financial gain. Entertainment only — nut responsibly. 🌰
