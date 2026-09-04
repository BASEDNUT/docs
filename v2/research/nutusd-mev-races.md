🔬 Research — nutUSD MEV Races (Experiment VIII)

Eighth experiment in the nutUSD research series — the multi-user composition the single-actor experiments deferred. A field of wallets moves at once: seven debtors drain the pool near-max, a racer takes what remains, a reinforcement refills it, and after the feed crashes, a field of liquidators — EOAs and one contract — competes for every unhealthy position. Ordering is the variable: the same repay succeeds or panics depending on whether a liquidator landed first. Key material was wiped twice mid-run; positions were recovered and races reconstructed from on-chain events, per the recovery law of [Experiment II](/v2/research/nutusd-adversarial.md). Every executed value is receipt-measured.

## Questions

| # | Question | Verdict |
|---|---|---|
| M1 | Who wins a liquidity race? | One borrower: seven near-max borrows (760 USDC each) drained the pool to 680 USDC idle; the racer’s 400 USDC included and the losing borrow reverted `insufficient liquidity` — pool arithmetic is the arbiter |
| M2 | Who wins a liquidation duel? | Exactly one: the winner’s full close seized 0.993181818181818181 mockNUT; the loser’s attempt on the closed position reverted `position is healthy` |
| M3 | Does a split close reconcile? | Yes: part A repaid 382.608696 / seized 0.5, part B repaid 377.391304 / seized 0.493181817045454545 — totals exact, 1,136,363,636 wei rounding loss at the seam |
| M4 | Does ordering decide? | Yes: one debtor repaid and withdrew ahead of the crash-closure, untouched; the other was liquidated first and the identical repay then reverted `Panic 0x11` — share underflow on a closed position |
| M5 | Does a crash wave propagate bad debt? | No: the whole field went unhealthy at 880; closures proceeded position by position, re-attempts reverted `position is healthy`, zero bad debt |
| M6 | Can a contract liquidate? | Yes — same seizure, same profit, 152,023 gas vs 130,749 EOA; the contract shape costs gas and changes nothing else |
| M7 | Are wiped-key positions recoverable? | Yes — fresh signers closed three of them by address: repay and collateral claim are permissionless |
| M8 | Is liquidation profitable? | Yes at every measured shape — 113.999999 USDC quoted profit per full close, 59.999999 partial, 113.999998 split |

## Environment

| Item | Value |
|---|---|
| Chain | Base Sepolia (84532) |
| Market | Fresh 38.5% rung — `0x1b976738…344b7409`, zero-IRM (the rate surface is [Experiment XII](/v2/research/nutusd-rate-surface.md)) |
| Oracle | V1 adapter over mock feeds — base [`0x7fD83AA2…8b1517B5`](https://sepolia.basescan.org/address/0x7fD83AA2a59429e12696A9619A1bb3D58b1517B5) controllable, 8-dec · quote [`0xf60B6CD8…b1DfaC4b`](https://sepolia.basescan.org/address/0xf60B6CD8Cac165E71FB1669C03fD7383b1DfaC4b) pinned at 1 |
| Collateral | mockNUT, 18 decimals |
| Loan | mock USDC, 6 decimals |
| Supply | 6,000 USDC initial · +1,600 reinforced mid-run |
| Field | r1–r7 debtors × 760 USDC · racer × 400 · r8–r9 × 760 after reinforcement |
| Liquidators | EOAs and one contract — [`0x2b5477B0…58B1E163`](https://sepolia.basescan.org/address/0x2b5477B040e618aDEEdC67F5b1137d7158B1E163) |
| Price | 2,000 → 880 at the crash |

## The contention — draining the pool

Seven borrowers each took 760 USDC — the near-max of their collateral at the 2,000 price — leaving 680 USDC idle. Two racers fired at what remained: the winner’s 400 USDC borrow included, [`0x3f9c781c…ab4407e2`](https://sepolia.basescan.org/tx/0x3f9c781c8498ed3f17293d70ab0bbdbd2df4685cb0ef256a1087630bab4407e2); the loser reverted `insufficient liquidity`, [`0x6658fb9e…c6270b22`](https://sepolia.basescan.org/tx/0x6658fb9eb6c81c3ee45c0a076bb287c52a9a6f9285294e05202d25edc6270b22). The pool, not a queue or a policy, is the arbiter: liquidity is first-come, and the second spend of the same base units cannot include.

## The duel — exactly one winner

After the crash, two liquidators raced the same full close. One seized the whole incentive — 0.993181818181818181 mockNUT for repaying 760 USDC, [`0x71b028ab…84e92038`](https://sepolia.basescan.org/tx/0x71b028ab70bd180a35fcf1829b68003922fba80bdb987a5bd887097984e92038); the loser’s attempt landed on the closed position and reverted `position is healthy`, [`0xbce88c8c…07fc6c37`](https://sepolia.basescan.org/tx/0xbce88c8cee61fb47b58ebd85664bb620d9c749c520e5a1c15b48ac5107fc6c37). There is no shared prize: the closure re-prices the position instantly, and every later attempt reads it healthy-side.

## The relay — a close in two parts

One position, two liquidators, one split: part A repaid 382.608696 USDC and seized 0.5 mockNUT; part B repaid the remaining 377.391304 USDC and seized 0.493181817045454545 — [`0xe78b6e95…97b117f4`](https://sepolia.basescan.org/tx/0xe78b6e95174fb94e30af319ba9c0734005e3cacb70b83e0f7246907097b117f4). The parts sum exactly to the single-winner shape — 760 repaid, 0.993181817045454545 seized — with 1,136,363,636 wei of rounding loss at the seam and 0.006818182954545455 mockNUT of residual collateral claimable by the borrower. Splitting a close is composition, not a new shape.

## The sandwich — order decides

Two debtors, one crash, the same escape available to both — repay and withdraw. One made it: debt 0, collateral home, untouched. The other was liquidated first, [`0xc2908927…8862f8fb`](https://sepolia.basescan.org/tx/0xc2908927727a1638c29e242b74b4659750514cc61ee7a4d987bdf75f8862f8fb), and the identical repay then reverted `Panic 0x11`, [`0x77beec09…6b2ef2f4`](https://sepolia.basescan.org/tx/0x77beec09b8304dbd8e41c0aacf443ece68ffc8395b950473abf446746b2ef2f4) — the share underflow of repaying a closed position, the same arithmetic wall [Experiment II](/v2/research/nutusd-adversarial.md) recorded. The contract enforces whichever transaction lands first; there is no fairness layer between them.

## The wave — one crash, many closures

At 880 every debtor in the field went unhealthy — the executable maximum per unit of collateral fell to 338.8 USDC. A representative full close repaid 760 USDC and seized 0.993181818181818181 mockNUT, zero bad debt, [`0xcaf89986…dd542c67`](https://sepolia.basescan.org/tx/0xcaf899869c4eaab945139bff4de7311d5475f1a01a4e862f74ee7434dd542c67); a re-attempt on the closed position reverted `position is healthy`, probe [`0x4a0aa7b3…68378dee`](https://sepolia.basescan.org/tx/0x4a0aa7b3dd6376e9b8c0593f6d0079a745c0767243496871dbc871ca68378dee). The wave is the duel repeated: each closure is atomic, and each later attempt reads the position healthy-side.

## The contract liquidator

A liquidating contract, [`0x2b5477B0…58B1E163`](https://sepolia.basescan.org/address/0x2b5477B040e618aDEEdC67F5b1137d7158B1E163), closed the same shape an EOA closes: repaid 760 USDC, seized 0.993181818181818181 mockNUT, profit identical — [`0x86cca187…8756b263`](https://sepolia.basescan.org/tx/0x86cca187275794d7c4fbf6b5bcaa5d70f8a3552334f1e775ce7ffd468756b263). The cost is gas: 152,023 vs 130,749 for the EOA full close. Nothing else differs — the protocol does not distinguish the caller’s shape.

## The unstuck — permissionless recovery

Key material was wiped twice mid-run. The orphaned positions — unhealthy since the crash — were closed by fresh signers acting by address: repayment and liquidation are permissionless, so no key material is needed to act on a position. Three recoveries, each a full close at the standard shape — r3 [`0x771937b1…ec6b5e06`](https://sepolia.basescan.org/tx/0x771937b1b6beeeee09e0de1b0eb86293c76d491ef4f98f009a00158aec6b5e06), r4 [`0xb0a95c4a…4ec77594`](https://sepolia.basescan.org/tx/0xb0a95c4ae29a0c1a05a61ef168a1fe39c3c02f90a767ebadd0129dda4ec77594), r7 [`0x9f4d3eea…d2278a7b`](https://sepolia.basescan.org/tx/0x9f4d3eea559551a855a325278b56a47913c06221797a20de2ca7f9edd2278a7b). The closer earns the incentive; the borrower’s residual collateral remains claimable by address.

## The economics

| Shape | Repaid (USDC) | Seized quoted (USDC) | Gas used | Profit (USDC) |
|---|---|---|---|---|
| EOA full close | 760.000000 | 873.999999 | 130,749 | 113.999999 |
| Duel winner | 760.000000 | 873.999999 | 130,749 | 113.999999 |
| Contract close | 760.000000 | 873.999999 | 152,023 | 113.999999 |
| Split relay (A+B) | 760.000000 | 873.999998 | 244,690 | 113.999998 |
| Partial close | 400.000000 | 459.999999 | 113,637 | 59.999999 |
| Recovery close | 760.000000 | 873.999999 | 130,749 | 113.999999 |

Gas price 0.016 gwei throughout — the testnet floor; the ETH leg of a full close is 0.000002092 ETH, six orders below the quoted profit. Every shape is profitable: the 1.15× incentive outpaces repayment by 15% of the debt value, and no measured execution came close to inverting it.

## Findings

| # | Finding |
|---|---|
| F1 | Liquidity races have exactly one winner — the losing borrow reverts `insufficient liquidity`; pool arithmetic, not policy, is the arbiter |
| F2 | Liquidation duels have exactly one winner — the closure re-prices the position instantly; the loser reverts `position is healthy` |
| F3 | Split closes reconcile to the single-winner shape exactly, with a 1,136,363,636 wei rounding seam |
| F4 | Ordering decides escape: repay-then-withdraw succeeds ahead of a liquidator; behind one, the same repay reverts `Panic 0x11` |
| F5 | The crash wave closes position by position — atomic closures, healthy-side re-reads, zero bad debt |
| F6 | A contract liquidator is an EOA plus gas: same seizure, same profit, +21,274 gas |
| F7 | Wiped-key positions remain actionable — permissionless closes recovered three of them by address |
| F8 | Every measured liquidation shape is profitable — 113.999999 USDC per full close at the 0.016 gwei floor |

## Limitations

- Sequencer-ordered, not mempool-raced: the orderings here are receipt reconstructions — no bundle competition, no priority-fee warfare, no real MEV adversary; flash-loan-funded sequences were not exercised.
- Testnet gas floor (0.016 gwei): the quoted profit is receipted; the mainnet gas leg is inference, not receipt.
- Zero-IRM market: the wave’s debts are static — the interest-driven breach is [Experiment XII](/v2/research/nutusd-rate-surface.md).
- Mock feeds under the real adapter: controlled-crash geometry — live-feed pricing is [Experiment XI](/v2/research/nutusd-production-fork.md).
- Post-sweep, 1.531818182954545461 mockNUT of collateral remains in the market — unclaimed remains claimable by their owners; actor-side balances were swept where key material allowed.

## Artifacts

| Artifact | Value |
|---|---|
| Market id | `0x1b976738…344b7409` — 38.5% rung, fresh, zero-IRM |
| Oracle / feeds | adapter over base [`0x7fD83AA2…8b1517B5`](https://sepolia.basescan.org/address/0x7fD83AA2a59429e12696A9619A1bb3D58b1517B5) · quote [`0xf60B6CD8…b1DfaC4b`](https://sepolia.basescan.org/address/0xf60B6CD8Cac165E71FB1669C03fD7383b1DfaC4b) |
| Contract liquidator | [`0x2b5477B0…58B1E163`](https://sepolia.basescan.org/address/0x2b5477B040e618aDEEdC67F5b1137d7158B1E163) |
| Race | win [`0x3f9c781c…ab4407e2`](https://sepolia.basescan.org/tx/0x3f9c781c8498ed3f17293d70ab0bbdbd2df4685cb0ef256a1087630bab4407e2) · lose [`0x6658fb9e…c6270b22`](https://sepolia.basescan.org/tx/0x6658fb9eb6c81c3ee45c0a076bb287c52a9a6f9285294e05202d25edc6270b22) |
| Duel | win [`0x71b028ab…84e92038`](https://sepolia.basescan.org/tx/0x71b028ab70bd180a35fcf1829b68003922fba80bdb987a5bd887097984e92038) · lose [`0xbce88c8c…07fc6c37`](https://sepolia.basescan.org/tx/0xbce88c8cee61fb47b58ebd85664bb620d9c749c520e5a1c15b48ac5107fc6c37) |
| Relay | [`0xe78b6e95…97b117f4`](https://sepolia.basescan.org/tx/0xe78b6e95174fb94e30af319ba9c0734005e3cacb70b83e0f7246907097b117f4) — A+B split close |
| Sandwich | liquidation [`0xc2908927…8862f8fb`](https://sepolia.basescan.org/tx/0xc2908927727a1638c29e242b74b4659750514cc61ee7a4d987bdf75f8862f8fb) · post-close repay panic [`0x77beec09…6b2ef2f4`](https://sepolia.basescan.org/tx/0x77beec09b8304dbd8e41c0aacf443ece68ffc8395b950473abf446746b2ef2f4) |
| Wave | close [`0xcaf89986…dd542c67`](https://sepolia.basescan.org/tx/0xcaf899869c4eaab945139bff4de7311d5475f1a01a4e862f74ee7434dd542c67) · re-attempt probe [`0x4a0aa7b3…68378dee`](https://sepolia.basescan.org/tx/0x4a0aa7b3dd6376e9b8c0593f6d0079a745c0767243496871dbc871ca68378dee) |
| Contract close | [`0x86cca187…8756b263`](https://sepolia.basescan.org/tx/0x86cca187275794d7c4fbf6b5bcaa5d70f8a3552334f1e775ce7ffd468756b263) |
| Recovery | r3 [`0x771937b1…ec6b5e06`](https://sepolia.basescan.org/tx/0x771937b1b6beeeee09e0de1b0eb86293c76d491ef4f98f009a00158aec6b5e06) · r4 [`0xb0a95c4a…4ec77594`](https://sepolia.basescan.org/tx/0xb0a95c4ae29a0c1a05a61ef168a1fe39c3c02f90a767ebadd0129dda4ec77594) · r7 [`0x9f4d3eea…d2278a7b`](https://sepolia.basescan.org/tx/0x9f4d3eea559551a855a325278b56a47913c06221797a20de2ca7f9edd2278a7b) |
| Racer partial close | [`0x94caddc0…357a7429`](https://sepolia.basescan.org/tx/0x94caddc033aa32d945de60e369e18f509303fdf35f1ee34221fbf99d357a7429) |
| Run window (UTC) | 2026-09-03 – 2026-09-04 |

## References

- [Experiment II](/v2/research/nutusd-adversarial.md) — the failure modes and the permissionless-recovery law
- [Experiment VII](/v2/research/nutusd-lltv-ladder.md) — the crash geometry this field ran on
- [Experiment XI](/v2/research/nutusd-production-fork.md) — live-feed pricing on a mainnet fork
- [Experiment XII](/v2/research/nutusd-rate-surface.md) — the rate surface behind the zero-IRM choice
- [nutUSD](/v2/tokens/nutusd.md) — the credit layer

> 🥜 Ten borrowers, one jar, one crash — the chain chose its winners in base units, and not a single debt went bad.


{% hint style="warning" %}
BASED NUT is an experimental memefi ecosystem. Nothing here is financial advice, no asset carries intrinsic value, and no figure on this page is a promise of performance. Measure twice, nut responsibly.
{% endhint %}
