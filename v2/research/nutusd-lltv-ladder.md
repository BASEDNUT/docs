# 🔬 Research — nutUSD LLTV Ladder (Experiment VII)

Seventh experiment in the nutUSD research series — the closing comparative-parameter experiment; the assurance program (multi-user ordering, emergency machinery, stateful invariants, mainnet fork) remains open. [Experiment I](/v2/research/nutusd-testnet.md) measured the boundary and the normal liquidation; [II](/v2/research/nutusd-adversarial.md) recorded the failure modes; [III](/v2/research/nutusd-liquidation-envelope.md) mapped the seizure branches and the oracle-zero states; [IV](/v2/research/nutusd-liquidity-rates.md) the rates and the utilization wall; [V](/v2/research/nutusd-vault-machinery.md) the vault machinery; [VI](/v2/research/nutusd-production-recipe.md) the production collateral shape. This one inverts the method: instead of studying the 38.5% market alone, it builds Morpho's eight nonzero standard LLTVs side by side — 38.5% through 98% — with everything else held constant. Same collateral, same oracle, same supply, same borrower shapes. Only the LLTV moves. Executed values below are receipt-measured, and the offline prediction from source matched at every rung and branch to the base unit; entries derived from the measured geometry rather than executed are labelled.

## Questions

| # | Question | Verdict |
|---|---|---|
| G1 | Is the borrowing-wall rule LLTV-dependent? | No — the rule is invariant: max = collateral × LLTV, one unit above reverts at all eight; the wall's height scales with LLTV |
| G2 | At equal utilization of each rung's own capacity, is the liquidation trigger LLTV-dependent? | No — LLTV cancels: exact-max borrowers flip under any downward move at all 8 rungs; half-max at exactly −50% |
| G3 | Where does static liquidation geometry diverge? | Three variables: liquidation incentive, crash absorption, and the covered/full branch — downstream quantities (max borrow, utilization at fixed supply) scale with LLTV as consequences of capacity |
| G4 | Is 38.5% unique among the standard rungs? | Yes — the only nonzero standard LLTV whose incentive is capped at 1.15×, and the only rung with zero bad debt at −50% |
| G5 | What happens beyond the 38.5% recovery boundary? | The boundary is −55.725%; at the sampled −60% crash: all collateral seized, ⌈800 ÷ 1.15⌉ repaid, 74.347826 USDC bad debt |

## Environment

| Item | Value |
|---|---|
| Chain | Base Sepolia (84532) |
| Protocol | Morpho Blue, canonical deployment |
| Collateral | mockNUT, 18 decimals, 1 unit per borrower — $2,000 at the origin feed |
| Oracle | One `MorphoChainlinkOracleV2` shared by all eight markets — [`0x265FA7e0…DfBd327`](https://sepolia.basescan.org/address/0x265FA7e0d48871Cf8bfE0Ac856C1151caDfBd327) |
| Base feed | Mock, 8 decimals, controllable — [`0x0C5e0941…238A05`](https://sepolia.basescan.org/address/0x0C5e0941910551c1B6709f14b487ea6836238A05) |
| Quote feed | Mock, 8 decimals, pinned at 1 — [`0x37968348…6862e4`](https://sepolia.basescan.org/address/0x379683481214aE5ab582ae782a4115781F6862e4) |
| IRM | Zero — debt is static between measurement points, so every prediction is exact integer math |
| Market supply | 5,001 USDC per market — 5,000 from the experiment wallet + 1 dead share |
| Borrowers | One exact-max wallet across all eight markets, one half-max wallet across all eight, two 38.5%-only extras, one independent liquidator |

The eight markets, differing only in LLTV:

| Rung | Market id |
|---|---|
| 38.5% | `0xfe8a66e3…fec5e5e9` |
| 62.5% | `0x164cb15f…647f0813` |
| 77.0% | `0xb9935485…6dcb4823` |
| 86.0% | `0xeb05719b…8179c4d7` |
| 91.5% | [`0x75eb4841…3c38dce`](https://sepolia.basescan.org/address/0x75eb4841b4603cfcd191d0575fe58901c0e7210699c089d2ede9037683c38dce) |
| 94.5% | [`0xbe2e2df3…005f000`](https://sepolia.basescan.org/address/0xbe2e2df3f4935c26a8b008604470750dc2931557362806573a40a9d31005f000) |
| 96.5% | [`0xff85f8fe…30bc58a`](https://sepolia.basescan.org/address/0xff85f8fefd7822d640fb568b4eb968b6ab04ec2b91095b02d87865e6d30bc58a) |
| 98.0% | [`0x5f57f3c2…9e895b6`](https://sepolia.basescan.org/address/0x5f57f3c2cd6e4e8ecd42a056de6b02ac2cab26694e26dc286261318079e895b6) |

## The invariants — identical at every rung

Three walls were probed at all eight rungs. None of them depends on the LLTV.

```
 $2000 ── origin price
    │
    ├── borrowing wall:   max = collateral × LLTV everywhere;
    │                      one unit above reverts at all 8 rungs
    ├── −10% trigger:      exact-max borrowers turn liquidatable
    │                      at ALL 8 rungs — LLTV cancels
    ├── −50% boundary:     half-max borrowers healthy at exactly
    │                      −50% at ALL 8 rungs
    └── one feed unit below −50%: all 8 flip liquidatable
```

- **Borrowing wall** — the exact executable maximum is 770 USDC at 38.5% up to 1,960 USDC at 98% (rung × 2 per $2,000 collateral). A borrow one base unit above the maximum reverts at every rung — 8 of 8 probes.
- **Liquidation trigger at −10%** — debt and ceiling scale with the same LLTV, so it cancels: an exact-max borrower at any rung is unhealthy under the same −10% price move. 8 of 8 rungs liquidatable.
- **Half-max boundary at −50%** — a borrower at exactly half the maximum is healthy at exactly half the origin price, at every rung. One feed unit lower — 999 instead of 1000 — flips all eight to liquidatable. The prudent wall is LLTV-invariant too.

> 🥜 The ladder's first finding is what it could not change: push the LLTV anywhere from 38.5% to 98%, and the *shape* of the walls does not move an inch. Only their height does.

## The variables — where the rungs diverge

| LLTV | Max borrow | Liquidation incentive | Capped | Crash absorption | Branch @ −10% | Branch @ −50% |
|---|---|---|---|---|---|---|
| 38.5% | 770 USDC | **1.15×** | yes | **55.725%** | covered | **covered** |
| 62.5% | 1,250 USDC | 1.1268× | no | 29.578% | covered | full |
| 77.0% | 1,540 USDC | 1.0741× | no | 17.293% | covered | full |
| 86.0% | 1,720 USDC | 1.0438× | no | 10.230% | covered | full |
| 91.5% | 1,830 USDC | 1.0262× | no | 6.106% | full | full |
| 94.5% | 1,890 USDC | 1.0168× | no | 3.915% | full | full |
| 96.5% | 1,930 USDC | 1.0106× | no | 2.476% | full | full |
| 98.0% | 1,960 USDC | 1.0060× | no | 1.408% | full | full |

Two formulas produce every entry:

- **Incentive** — min(1.15, 1 ÷ (1 − 0.3 × (1 − LLTV))). The cap begins binding below ≈56.52% LLTV, which makes 38.5% the *only* nonzero standard rung that receives the full 1.15×.
- **Absorption** — 1 − LLTV × incentive: how much of the collateral's value a crash can erase before an exact-max borrower slips past what a seizure can recover. 55.725% at 38.5%; 1.408% at 98%.

The incentive and absorption columns are formulas verified against the measured receipts; the −50% branch column is derived from them — only the 38.5% rung was executed at −50%.

## Crash at −10% — receipts

An independent wallet liquidated the exact-max borrower at every rung under the same corrected feed.

| Rung | Branch | Repaid | Seized | Bad debt | Tx |
|---|---|---|---|---|---|
| 38.5% | covered | 770 USDC — full debt | 0.491944 mockNUT | 0 | [`0x0e2950a4…f2a41019`](https://sepolia.basescan.org/tx/0x0e2950a4f228a4752a9238af5e590ff040e8285531559b0f08d01c88f2a41019) |
| 62.5% | covered | 1,250 USDC | 0.782473 mockNUT | 0 | [`0xb8bda86d…2296232e`](https://sepolia.basescan.org/tx/0xb8bda86d53bfe6bb2dceae90cc9b08c9a03fa320413e54c0b08d84122296232e) |
| 77.0% | covered | 1,540 USDC | 0.918964 mockNUT | 0 | [`0xbbc24b86…e991299f`](https://sepolia.basescan.org/tx/0xbbc24b86d25d5c19af1d424f6f8a9d78ecd8e31f60283dc090522f687e991299f) |
| 86.0% | covered | 1,720 USDC | 0.997448 mockNUT | 0 | [`0x21fb700a…7d5293c`](https://sepolia.basescan.org/tx/0x21fb700a646d56edf79fd88c954b5446928fce65d727f26f3d504119b7d5293c) |
| 91.5% | full | 1,754.100001 USDC | 1 mockNUT — all | 75.899999 | [`0x9895fe60…57c61a5`](https://sepolia.basescan.org/tx/0x9895fe60cc8b73e0b5aac7140d74f5b42f51128b6b80d68d39bc7a75957c61a5) |
| 94.5% | full | 1,770.300001 USDC | all | 119.699999 | [`0xa72d55c8…42d888f2`](https://sepolia.basescan.org/tx/0xa72d55c8b69db0ae901db747831d844dc64266a50e6a85c491441c2742d888f2) |
| 96.5% | full | 1,781.100001 USDC | all | 148.899999 | [`0xdec61f33…660492b`](https://sepolia.basescan.org/tx/0xdec61f339ea2649daa1448cf71ec0521d9982a43df0899d15600a4126660492b) |
| 98.0% | full | 1,789.200001 USDC | all | 170.799999 | [`0x392afb15…8417a881`](https://sepolia.basescan.org/tx/0x392afb1569f6716404c1c307435d358e013bee0dd488d06b78c7d3ae8417a881) |

- **Covered rungs (38.5–86%)** — the seizure is exactly debt × incentive ÷ price, the full debt is repaid, the borrower keeps the collateral remainder, and nothing reaches suppliers.
- **Full rungs (91.5–98%)** — the incentive-adjusted claim already exceeds all collateral at −10%. Everything is seized, repayment is ⌈collateral value ÷ incentive⌉, and the difference lands on suppliers as bad debt — 170.8 USDC per $2,000 collateral at 98%.

## Crash at −50% — 38.5% alone survives

A second 38.5% borrower, opened at the exact maximum, was liquidated at feed 1000 — [tx `0x7f36ebf2…e210a25b`](https://sepolia.basescan.org/tx/0x7f36ebf2a489191da141ee733de6e0283d7eeab36b716555d55d34dae210a25b): covered branch, the full 770 USDC debt repaid, 0.8855 mockNUT seized, zero bad debt. The seizure is exactly the absorption boundary — 885.5 is the floor feed for a covered seizure at 38.5%, and 1000 sits above it. Every higher rung is beyond its own recovery threshold at −50% — derived from the measured geometry, not separately executed; 38.5% is the only standard rung whose depositors take nothing at a halving of the collateral price.

## Crash at −60% — beyond the recovery boundary

At feed 800 — beyond the −55.725% recovery boundary — the 38.5% market takes its loss — [tx `0x456b9a0d…648b6a34`](https://sepolia.basescan.org/tx/0x456b9a0d277a32183a5920660bde3ca697b512da59fbf369dcf217ee648b6a34): all collateral seized, 695.652174 USDC repaid (⌈800 ÷ 1.15⌉), 74.347826 USDC bad debt. The borrower is wiped out; suppliers absorb the remainder. Even here the number is the exact integer the source math predicts.

## Limitations

- Borrowers are normalized to each rung's own borrowing capacity (exact-max and half-max); at the same absolute debt the liquidation price differs by LLTV — the LLTV-cancellation result holds at equal utilization, not absolutely.
- The zero-rate IRM removes the utilization/rate feedback: results characterize static liquidation geometry, not production rate dynamics.
- Price moves are instantaneous mock-feed repricings — no oracle latency, heartbeat, or deviation path.
- One liquidator, mock collateral, one collateral size; liquidation gas, slippage, and competing-liquidator economics are outside this experiment.
- The higher rungs at −50% are derived from the measured geometry, not separately executed.
- Testnet geometry, not production-loss prediction.

## Verdict — what 38.5% is

**Identical at every rung:** the borrowing wall's behavior, the −10% liquidation trigger, and the half-max boundary at exactly −50%. The LLTV sets the height of the walls, never their shape.

**Different at 38.5%:**

- the maximum 1.15× liquidation incentive — unique among nonzero standard rungs: the strongest protocol-defined economic reward available to a liquidator, exactly where bad debt is hardest to create;
- 55.725% crash absorption versus 29.6% at 62.5% and 1.4% at 98%;
- covered seizures down to a −55.725% feed, versus −1.4% at 98%;
- zero depositor loss at a −50% crash — alone in the set;
- bad debt begins beyond the −55.725% recovery boundary — the sampled −60% crash measured 74.35 USDC per $2,000 collateral.

**The trade, stated honestly:** 38.5% concedes capital efficiency — a borrower extracts 770 USDC per $2,000 collateral where a 98% borrower extracts 1,960, a 2.5× difference. 38.5% prioritizes solvency margin; 98% prioritizes capital efficiency. nutUSD picks the solvency margin — see [the credit layer](/v2/tokens/nutusd.md).

> 🥜 Eight ladders, one wall-shape. The conservative rung does not climb highest — it is the one still standing when the price halves.

{% hint style="warning" %}
BASED NUT is an experimental memefi ecosystem. Nothing here is financial advice, no asset carries intrinsic value, and no figure on this page is a promise of performance. Measure twice, nut responsibly.
{% endhint %}
