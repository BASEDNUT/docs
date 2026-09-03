# 🔬 Research — nutUSD Emergency & Timelock Machinery (Experiment IX)

Ninth experiment in the nutUSD research series — the direct continuation of [Experiment V](/v2/research/nutusd-vault-machinery.md), which exercised the vault's role and timelock machinery at the fresh-vault zero default. This one runs the same machinery at the production shape: the 3-day timelock delay Morpho's listing guidance calls for, the permissionless `forceDeallocate` and its priced gate, the sentinel's emergency power, and the `max*` limit family a frontend integration sees. The market layer is deliberately a different rung — 98% LLTV — because none of this machinery lives in the market: it is vault-layer, LLTV-independent. Every number is a measured on-chain value.

## Questions

| # | Question | Verdict |
|---|---|---|
| E1 | Does the timelock enforce at the production delay? | Yes — 259,200 s (3 days) on `setIsAllocator`: pre-expiry execution reverts `TimelockNotExpired`, a duplicate submit reverts `DataAlreadyPending`, and `executableAt` = submit timestamp + 259,200 exactly |
| E2 | Can a raised wall be quickly undone? | No — the self-wall: a `decreaseTimelock` submit inherits the target selector's *current* delay, so lowering the 3-day wall itself waits 3 days |
| E3 | Does the full submit → execute cycle hold end-to-end? | Yes — at a 90 s delay: submit → pre-expiry revert → expiry execute, `executableAt` = submit timestamp + 90 exactly |
| E4 | Who can force-deallocate, and at what cost? | Three tiers: a stranger without allowance is blocked — the penalty's share-burn consumes the same allowance as a withdrawal (`Panic 0x11` underflow); the owner self-forcing pays 1% of the forced amount (20 USDC on 2,000) in burned shares; an approved caller forces and the owner's shares burn for the penalty |
| E5 | Is the penalty bounded? | Yes — capped at 2% per adapter: a 3% set reverts `PenaltyTooHigh`; the 1% penalty is itself set through the timelock |
| E6 | What can the sentinel do? | Emergency `deallocate` — pulled 2,000 USDC out of the market allocation without the allocator; set and removed by the owner directly, not timelocked; outsiders and the removed sentinel revert `Unauthorized` |
| E7 | Do the `max*` limits bind a frontend? | All four return 0 by design — a gross underestimation — while `previewDeposit` / `previewRedeem` return real values; integrations must quote `preview*`, never `max*` |

## Environment

| Item | Value |
|---|---|
| Chain | Base Sepolia (84532) |
| Protocol | Morpho Blue, canonical deployment; `VaultV2` via the canonical factory |
| Vault | [`0x90c40c02…270097f5`](https://sepolia.basescan.org/address/0x90c40c02D04cbC24E5b2Ba2095DD26C8270097f5) |
| Adapter | [`0x1581D059…6ba427F6`](https://sepolia.basescan.org/address/0x1581D059c4F8c47822819CD6aB02f6136ba427F6) — the vault's market adapter, penalty-capped at 2% |
| Market | Fresh 98% LLTV rung — `0x5eb03ad9…f66a6c2a`; the market layer is irrelevant to the machinery measured here |
| Loan asset | Mock USDC (6 decimals) — 10,000 USDC deposited |
| Oracle / collateral | The proven mock-feed stack of [Experiment XII](/v2/research/nutusd-rate-surface.md), reused — [`0x265FA7e0…aDfBd327`](https://sepolia.basescan.org/address/0x265FA7e0d48871Cf8bfE0Ac856C1151caDfBd327) over mockNUT |
| IRM | AdaptiveCurveIRM, canonical |
| Delays | `setIsAllocator` 259,200 s (production) · `setForceDeallocatePenalty` 90 s (the short dance) |
| Position owner | The experiment wallet — the `onBehalf` whose shares burn for penalties |

The opening deposit confirmed the vault-layer property at this stack: 10,000 USDC deposited arrived with zero idle — fully allocated to the market through the adapter.

## The timelock at the production wall

```
 curator ──submit(data)──▶ pending: executableAt = ts + delay
        │
        ├── execute before expiry ──✗── TimelockNotExpired
        ├── submit the same data again ──✗── DataAlreadyPending
        ├── execute at expiry ──▶ runs (the full cycle, at the 90 s delay)
        └── revoke ──▶ curator or sentinel, immediate, not timelocked
```

At the 3-day production delay: the submit was accepted, `executableAt` = submit timestamp + 259,200 exact, pre-expiry execution reverted `TimelockNotExpired`, and the duplicate submit reverted `DataAlreadyPending`. The full cycle through expiry execution ran end-to-end at the 90-second delay — submit, pre-expiry revert, expiry execute — with the same eta arithmetic exact. The machine is delay-parametric; both delays were measured, and both pendings were revoked after recording.

> 🥜 The wall is not one wall but two: the delay you must wait, and the delay you must wait to make the waiting shorter.

### The self-wall

`decreaseTimelock(setIsAllocator, …)` was submitted while `setIsAllocator` sat at 259,200 s. The decrease's own `executableAt` inherited the target's *current* delay — 259,200 s — not the delay of `decreaseTimelock` itself. A raised wall cannot be quickly undone: the shortening transaction waits behind the wall it wants to shorten.

## forceDeallocate — permissionless with a priced gate

`forceDeallocate` pulls assets out of a market allocation into idle without the allocator — the permissionless reclaim path for when vault liquidity runs short. The caller pays nothing; the position owner bears the penalty, in burned shares.

| Tier | Caller | Result |
|---|---|---|
| Stranger, no allowance | Independent wallet | Reverts — `Panic 0x11`, allowance underflow: the penalty's share-burn consumes the same allowance as a withdrawal, so the penalty *is* the stranger gate |
| Self-force | The position owner | Executes — 2,000 USDC forced out of the allocation; penalty 20 USDC (1%) burned from the owner's shares, 10,000 → 9,980 — [`0x04a91a75…354d8a3c`](https://sepolia.basescan.org/tx/0x04a91a752983814d5f4d9a2f47cdf7b55330aaa50a02c09066748b1d354d8a3c) |
| Approved caller | Wallet holding exact allowance | Executes — another 2,000 USDC forced; the owner's shares burn again, 9,980 → 9,960; the allowance is consumed to zero — [`0x6212c41b…620e28c7`](https://sepolia.basescan.org/tx/0x6212c41b884f322430d899fd9ca77754063f9ca738fe30db75d99391620e28c7) |

The penalty is bounded and itself governed: a set above the 2% cap reverts `PenaltyTooHigh` (a 3% probe), and the 1% penalty used throughout was set through the timelock — the 90 s dance above.

For contrast, the allocator's own path: a `reallocate` moved 1,000 USDC from idle back into the market allocation — idle 4,000 → 3,000, allocation 6,000 → 7,000 — [`0xd94f6a0d…f204cc02`](https://sepolia.basescan.org/tx/0xd94f6a0d4b921bc0fd04a29542891dff2c10f602850aec68c8605df8f204cc02).

## The sentinel — emergency without timelock

The owner sets and removes the sentinel directly, outside the timelock. The sentinel's power is `deallocate`: it pulled 2,000 USDC out of the market allocation (7,000 → 5,000) without the allocator — [`0x6694a3cf…09a95ac1`](https://sepolia.basescan.org/tx/0x6694a3cfb42cb476bfad56171bb52c4569e31f4c18686b9ff6dfbc5c09a95ac1). An outsider calling it reverts `Unauthorized`, and the removed sentinel reverting the same way proves the removal took effect immediately.

## The max* family — zero by design

| Call | Returns |
|---|---|
| `maxDeposit` / `maxMint` / `maxWithdraw` / `maxRedeem` | 0 — all four, by design: a gross underestimation |
| `previewDeposit(1 USDC)` | 1 share — 10¹⁸ share-wei at the 18-decimal share scale |
| `previewRedeem(all shares)` | 10,000 USDC — real |

A frontend that gates deposits on `max*` sees zero and blocks everything. The `preview*` family is the integration surface — quote previews, never limits. [Experiment XII](/v2/research/nutusd-rate-surface.md) measures the market-layer counterpart: a full supplier redemption executed to the base unit.

## Findings

| # | Finding |
|---|---|
| F1 | The timelock state machine holds at both delays: eta arithmetic exact (submit timestamp + delay), pre-expiry `TimelockNotExpired`, duplicate `DataAlreadyPending`, revoke immediate for curator or sentinel |
| F2 | The self-wall binds: `decreaseTimelock` inherits the target's current delay — a raised 3-day wall takes 3 days to lower |
| F3 | `forceDeallocate`'s penalty is the stranger gate: the share-burn consumes withdrawal allowance, so an unapproved caller underflows (`Panic 0x11`) rather than forces |
| F4 | The penalty is priced and bounded: 1% measured — 20 USDC on 2,000 forced, in burned owner shares — with the 2% cap enforced (`PenaltyTooHigh` at 3%) and penalty changes themselves timelocked |
| F5 | The sentinel holds emergency `deallocate` power — set and removed owner-direct, `Unauthorized` for outsiders and for the removed sentinel |
| F6 | `max*` returns 0 across the family while `preview*` returns real values — the integration law for anything building on the vault |

## Limitations

- The production-delay cycle was proven to its pre-expiry wall with eta exactness; the pendings were revoked rather than sat out — the expiry execution itself is receipted at the 90 s delay, and the machine is delay-parametric, but no 3-day expiry-execution receipt exists.
- The forced market held liquidity; `forceDeallocate` against an illiquid market — the withdraw reverting inside the adapter — is unmeasured.
- One vault, one adapter, one market; mock USDC at experiment scale.
- Allocator misuse — a compromised allocator reallocating across markets — is a design question for the product page, not a machinery measurement.
- No Bundler integration here; `max*` / `preview*` semantics for bundled flows are unmeasured.

## Artifacts

| Artifact | Value |
|---|---|
| Vault | [`0x90c40c02…270097f5`](https://sepolia.basescan.org/address/0x90c40c02D04cbC24E5b2Ba2095DD26C8270097f5) |
| Adapter | [`0x1581D059…6ba427F6`](https://sepolia.basescan.org/address/0x1581D059c4F8c47822819CD6aB02f6136ba427F6) |
| Market id | `0x5eb03ad9…f66a6c2a` — 98% rung, fresh |
| Deposit | 10,000 USDC → 0 idle, fully allocated |
| Delays | `setIsAllocator` 259,200 s · `setForceDeallocatePenalty` 90 s |
| Penalty | 1% measured · 2% cap enforced |
| Run window (UTC) | 2026-09-03 |

## References

- Morpho Vault V2 — timelock, roles, `forceDeallocate`, limits
- [Experiment V](/v2/research/nutusd-vault-machinery.md) — the same machinery at the fresh-vault default
- [Experiment XII](/v2/research/nutusd-rate-surface.md) — the shared stack; the market-layer full redemption
- [nutUSD](/v2/tokens/nutusd.md) — the credit layer

> 🥜 Three gates, one vault: time gates the controls, allowance gates the force, ownership gates the alarm. The shell does not crack — it schedules.

{% hint style="warning" %}
BASED NUT is an experimental memefi ecosystem. Nothing here is financial advice, no asset carries intrinsic value, and no figure on this page is a promise of performance. Measure twice, nut responsibly.
{% endhint %}
