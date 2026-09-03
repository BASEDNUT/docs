# 🔬 Research — nutUSD Rate Surface (Experiment XII)

Twelfth experiment in the nutUSD research series. [Experiment IV](/v2/research/nutusd-liquidity-rates.md) measured one accrual window at one utilization point; this one walks the whole surface: the AdaptiveCurveIRM's response across the utilization ladder, the `rateAtTarget` adaptation under saturation and repayment, the one breach that needs no oracle at all — interest alone crossing the health wall — and the full unwind at the end. Every executed value is receipt-measured; the offline model — source-derived constants proven against the canonical IRM fixture — predicted every rate update the suite gated on.

## Questions

| # | Question | Verdict |
|---|---|---|
| R1 | How does the borrow rate respond across utilization? | The AdaptiveCurve, measured 0 → 100%: gentle below target — ×(1 + 0.75·e), ≈1.0%/yr at 0% and ≈3.97%/yr at the 90% target — then steep above it, ×(1 + 3·e): ≈9.9%/yr at 95%, ≈14.7%/yr at 99%, 4× `rateAtTarget` at saturation |
| R2 | Does `rateAtTarget` adapt? | Yes — at sustained 100% utilization it rose ≈3.97%/yr → ≈4.37%/yr annualized, strictly monotone across four checkpoints; repayment below target turned it and it fell |
| R3 | Is accrual exact under saturation? | Yes — checkpoint interest 16,638 / 33,214 / 66,509 base units at 604 / 1,204 / 2,404 s: proportional to elapsed, matching the model |
| R4 | Can interest alone breach the health wall? | Yes — zero price move: an exact-max debt accrued 5,998 base units, crossed its own ceiling, and was liquidated at an unchanged feed — repaid in full, zero bad debt |
| R5 | Is the executable maximum state-dependent? | Yes — 770,000,000 at origination; 769,999,999 in the accrued market: the share-conversion pair (mint up, health-check up) rounds toward the protocol twice, so the passable maximum sits one base unit below the cap |
| R6 | Does the market unwind fully? | Yes — every borrower repaid, every collateral returned, the supplier redeemed 5,001.625340 USDC including 1.625340 USDC of interest; the market closed at 1 base unit of dust |

## Environment

| Item | Value |
|---|---|
| Chain | Base Sepolia (84532) |
| Market | The 38.5% rung, fresh for this experiment — `0x9b54c4e0…9fa71907` |
| Oracle | [`0x265FA7e0…aDfBd327`](https://sepolia.basescan.org/address/0x265FA7e0d48871Cf8bfE0Ac856C1151caDfBd327) over mock feeds: base 8-dec, controllable — [`0x0C5e0941…36238A05`](https://sepolia.basescan.org/address/0x0C5e0941910551c1B6709f14b487ea6836238A05); quote pinned at 1 — [`0x37968348…1F6862e4`](https://sepolia.basescan.org/address/0x379683481214aE5ab582ae782a4115781F6862e4) |
| Collateral | mockNUT, 18 decimals — [`0xd6f99071…0a14E55f`](https://sepolia.basescan.org/address/0xd6f990710b3A31C858737676DB354C8d0a14E55f) |
| IRM | AdaptiveCurveIRM, canonical — target utilization 90%, initial `rateAtTarget` 4%/yr, bounds 0.1%–200%/yr (source constants, proven against the fixture) |
| Supply | 5,000 USDC (mock, 6 decimals) |
| Borrowers | Seven wallets walking 25 / 50 / 75 / 90 / 95 / 99 / 100% of supply; one exact-max wallet for the wave; one independent liquidator |
| Price | 1 mockNUT = $2,000 throughout — the wave moved it zero |

## The ladder — the curve walked bottom-up

Seven borrows walked utilization to 100% of the 5,000 USDC supply. Each update receipts the governing rate at the utilization the market moved from — with `rateAtTarget` drifting under 0.005% during the ladder, the column reads as one curve:

| Utilization | Governing rate (per-second, WAD) | ≈ annualized | Receipt |
|---|---|---|---|
| 0% | 315,942,251 | 1.00%/yr | [`0xe1a38876…ca36941d`](https://sepolia.basescan.org/tx/0xe1a38876941d5e3d3cf507c9fada69d4959f3b4fbf122e26e0f88f47ca36941d) |
| 25% | 577,672,214 | 1.82%/yr | [`0xe6e4b826…01b3eafe`](https://sepolia.basescan.org/tx/0xe6e4b826f588a458640b405e3dd7bb5ca9bbc1c54d8d955abfe3937501b3eafe) |
| 50% | 840,233,620 | 2.65%/yr | [`0xeddc262f…4e6ad8b2`](https://sepolia.basescan.org/tx/0xeddc262fd452eac351a64641ae2634cb4680c94fd5b12631f85c97064e6ad8b2) |
| 75% | 1,102,796,426 | 3.48%/yr | [`0x179bfaa8…010c6a6f`](https://sepolia.basescan.org/tx/0x179bfaa80fd1870d048a8005203ef0badbe7e6b38a74dcaf331615b4010c6a6f) |
| 90% — target | 1,260,335,171 | 3.97%/yr | [`0x0724bf20…c03fb6ef`](https://sepolia.basescan.org/tx/0x0724bf209b563447116cdaeb464142530d891c7074661f6e97b60aa9c03fb6ef) |
| 95% | 3,150,860,295 | 9.94%/yr | [`0x6f1f00b5…1ba7003a`](https://sepolia.basescan.org/tx/0x6f1f00b53c60167e34583bb7a8c29fc3210b476aa368be60b7febfcc1ba7003a) |
| 99% | 4,663,386,308 | 14.70%/yr | [`0xf5d8f115…a6666ba2`](https://sepolia.basescan.org/tx/0xf5d8f115822e088a534f71ccb34910257f873809c12bd0ed238afb1da6666ba2) |
| 100% — saturation | 5,531,546,348 | ≈17.4%/yr | the cp600 accrual below |

Below target the curve scales gently — at 0% the debt prices at a quarter of `rateAtTarget`; at the target crossing it prices exactly at it. Above target the steepness takes over: one rung, 95 → 99%, near-tripled the rate; at saturation the debt prices at 4× `rateAtTarget` — the curve's ceiling multiplier at full error, measured in the saturation accruals.

## Saturation and recovery — the adaptation

Held at 100%, the market accrued across four checkpoints while `rateAtTarget` climbed:

| Checkpoint | Elapsed | Interest (base units) | `rateAtTarget` after |
|---|---|---|---|
| cp300 | 55,554 s | 1,464,326 | 1,376,301,485 |
| cp600 | 604 s | 16,638 | 1,377,620,111 |
| cp1200 | 1,204 s | 33,214 | 1,380,252,400 |
| cp2400 | 2,404 s | 66,509 | 1,385,523,281 |

Strictly rising across all four — and the checkpoint interest is proportional to elapsed at the governing rate, exactly. A repayment then walked utilization back below target — 1,150.363812 USDC repaid to 77.000000228% — and `rateAtTarget` turned and fell: 1,385,562,822 → 1,385,466,361. The adaptation is bidirectional, moving toward the curve's rest point from either side.

> 🥜 The curve is the gearstick, `rateAtTarget` the engine speed — saturation winds it up, repayment lets it back down.

## The wave — interest breaches the wall, price never moves

The failure mode no oracle defense covers: an exact-max borrower simply accruing. In the accrued market the executable maximum was 769,999,999 — one base unit below the 770,000,000 cap, the double share-conversion rounding (mint `toSharesUp`, health-check `toAssetsUp`, both toward the protocol; at origination the fresh market passes the full 770,000,000 — the state-dependence behind [Experiment VII](/v2/research/nutusd-lltv-ladder.md)'s origination-exact ladder). The borrower held the maximum; interest ran; the debt crossed its own ceiling.

| Step | Value |
|---|---|
| Debt after interest | 770.005997 USDC — 769.999999 borrowed, 5,998 base units accrued |
| Price | unchanged — 2×10²⁷ before and after |
| Liquidation | independent wallet — [`0x26244b27…3d7be91e`](https://sepolia.basescan.org/tx/0x26244b2701fbc851fa747835e72310c835ff8550e7b986cd6fe581ce3d7be91e) |
| Repaid | 770.005997 USDC — the full debt |
| Seized | 0.4427534475 mockNUT — the 1.15× incentive on the measured debt |
| Bad debt | 0 |

The offline model predicted the seizure from the snapshot state — repaid 770.005982, seized 0.442753439; execution carried 15 additional base units of interest accrued between snapshot and inclusion, and the seizure tracked the measured debt exactly, with one display-unit floor rounding recorded. Interest is a slow oracle made of time: it reprices the borrower's capacity without touching the feed.

## The sweep — full unwinding

Every borrower repaid — including wallets whose keys were wiped mid-experiment: repayment is permissionless, so fresh signers closed the recovered positions, the recovery law [Experiment II](/v2/research/nutusd-adversarial.md) established. Every collateral returned. The supplier redeemed the full balance — 5,001.625340 USDC, the 5,000 deposited plus 1.625340 USDC of interest earned across the window — [`0xe194afcc…0ae2e5a7`](https://sepolia.basescan.org/tx/0xe194afcc8699126ea4d2418a62ec455d19e0ce2a5d6c581df4e2bbcc0ae2e5a7) — and the market closed itself: total supply shares 0, assets 1 base unit of dust.

The 38.5% market was then spent — a 1-unit dust residue with zero shares — which is why [Experiment IX](/v2/research/nutusd-emergency-machinery.md) deployed its machinery stack on a fresh 98% rung rather than reuse it.

## Findings

| # | Finding |
|---|---|
| F1 | The AdaptiveCurve response measured end-to-end 0 → 100%: ≈1.0%/yr → 4× `rateAtTarget` at saturation, at near-constant `rateAtTarget` (≈4%/yr) — the error term does the work below saturation, the steepness above |
| F2 | `rateAtTarget` adapts: strictly monotone rise across the saturation checkpoints (≈3.97% → ≈4.37% annualized), reversing under repayment below target |
| F3 | Accrual under saturation is exact and proportional: 16,638 / 33,214 / 66,509 units at 604 / 1,204 / 2,404 s |
| F4 | Interest alone breaches the health wall: exact-max debt accrued 5,998 units, crossed its ceiling, and was liquidated at an unchanged feed — repaid in full, zero bad debt |
| F5 | The executable maximum is state-dependent: 770,000,000 at origination, 769,999,999 accrued — the share-conversion pair rounds toward the protocol twice, reconciling [Experiment VII](/v2/research/nutusd-lltv-ladder.md)'s origination-exact 770 |
| F6 | The market unwinds fully: permissionless repayment closed wiped-key positions, collateral returned, the supplier redeemed 5,001.625340 USDC, and the market closed at 1-unit dust |

## Limitations

- Mock feeds under the real adapter: the rate surface is IRM behavior, which the feeds never touch, but the liquidation pricing is controlled-feed geometry, not live-market data.
- One market, one supply size, one collateral; the curve's response at other depths follows the same formulas but is not receipted here.
- The wave is a single interest-driven breach at one accrual granularity; a compounding wave under repeated high-rate accruals is not separately receipted.
- Borrowers act in sequence — no concurrency; the multi-user program remains open.
- The sweep's 1-unit dust is the market's own floor rounding; negligible by construction, not economically measured.

## Artifacts

| Artifact | Value |
|---|---|
| Market id | `0x9b54c4e0…9fa71907` — 38.5% rung, fresh |
| Oracle | [`0x265FA7e0…aDfBd327`](https://sepolia.basescan.org/address/0x265FA7e0d48871Cf8bfE0Ac856C1151caDfBd327) · base feed [`0x0C5e0941…36238A05`](https://sepolia.basescan.org/address/0x0C5e0941910551c1B6709f14b487ea6836238A05) · quote feed [`0x37968348…1F6862e4`](https://sepolia.basescan.org/address/0x379683481214aE5ab582ae782a4115781F6862e4) |
| Collateral | [`0xd6f99071…0a14E55f`](https://sepolia.basescan.org/address/0xd6f990710b3A31C858737676DB354C8d0a14E55f) — 18 decimals |
| Ladder | b1–b7 receipts inline in the ladder table |
| Saturation | [`0x3ead36ae…caf97e65`](https://sepolia.basescan.org/tx/0x3ead36ae95e3509512940cce3db18f59c034ebe7cb5b44cf3f6d434ccaf97e65) · [`0xb2a0fe79…df90e398`](https://sepolia.basescan.org/tx/0xb2a0fe79769bc08d3b3c052ba6c8225971abd80de70b3f42198e5d14df90e398) · [`0xe678f9ff…6fc13d12`](https://sepolia.basescan.org/tx/0xe678f9ff09bda9301f87f02bd9e2589a63fa09b7434ec312c3dde2606fc13d12) · [`0x1056e4ab…4ba2d399`](https://sepolia.basescan.org/tx/0x1056e4ab821625feac460ff532974b1e6f899527a3c218328c1adf724ba2d399) |
| Recovery | [`0xa682427f…e5b1dbe5`](https://sepolia.basescan.org/tx/0xa682427f393c72c0b451a2619646e3532e8cdb993579e7cc3725d6c9e5b1dbe5) — repay to 77.000000228% |
| Wave | [`0x26244b27…3d7be91e`](https://sepolia.basescan.org/tx/0x26244b2701fbc851fa747835e72310c835ff8550e7b986cd6fe581ce3d7be91e) — interest-driven liquidation, price unchanged |
| Sweep | [`0xe194afcc…0ae2e5a7`](https://sepolia.basescan.org/tx/0xe194afcc8699126ea4d2418a62ec455d19e0ce2a5d6c581df4e2bbcc0ae2e5a7) — full redemption, market closed at 1-unit dust |
| Run window (UTC) | 2026-09-02 – 2026-09-03 |

## References

- Morpho AdaptiveCurveIRM — target, curve, adaptation, bounds
- [Experiment IV](/v2/research/nutusd-liquidity-rates.md) — the single-window accrual this one extends
- [Experiment VII](/v2/research/nutusd-lltv-ladder.md) — the zero-rate ladder; the origination-exact maximum
- [Experiment IX](/v2/research/nutusd-emergency-machinery.md) — the machinery stack this market's dust sent to a fresh rung
- [nutUSD](/v2/tokens/nutusd.md) — the credit layer

> 🥜 The feed never moved; the clock did. Eight rungs of rate, one wall breached by nothing but time — and the conservative rung paid it all back to the last base unit.

{% hint style="warning" %}
BASED NUT is an experimental memefi ecosystem. Nothing here is financial advice, no asset carries intrinsic value, and no figure on this page is a promise of performance. Measure twice, nut responsibly.
{% endhint %}
