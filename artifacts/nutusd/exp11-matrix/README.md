# Experiment XI — Oracle Failure Matrix (M1–M10)

Production-shaped oracle failure lattice on a pinned Base mainnet fork: the real
Morpho singleton, real USDC and cbBTC, the real MorphoChainlinkOracleV2 factory —
with two fork-deployed controllable aggregators seeded to the Experiment XI
captured live raws. The oracle path is production-shaped end to end; only the
feed answers are controllable.

## Reproduce

1. Build the mock: `forge build` (Foundry; `foundry.toml` included — produces `out/MockAggregator.sol/MockAggregator.json`).
2. Launch the fork: `anvil --fork-url https://base.publicnode.com --fork-block-number 50889452 --port 8547 --chain-id 8453` (see `fork-pin.json` for the block hash).
3. `python3 exp11_matrix.py` — deploys the two mocks, creates the factory oracle, creates the cbBTC/USDC 38.5% market, walks the max-borrow position, then executes M1–M10; writes `exp11_matrix_results_repro.json`.

Requires Python 3 with `web3` + `eth_abi`. All account access is anvil impersonation (whale + anvil default account) — no private keys. No storage edits were needed in the recorded run: the pinned whale balances covered the position directly.

## Fork pin

`fork-pin.json` carries the full determinism set: fork block + hash, chainId, endpoint, contract addresses, mock feed addresses and seeded raws, creation salt, market id and params, position sizing, and account roles. The pin is subject to the endpoint's state-serving window — see the `pinNote` there: re-take the pin from the chain tip before re-running.

## Scenario registry

| # | Scenario | Verdict class |
|---|---|---|
| M1 | baseline — live-captured raws through the real factory oracle | `baseline_serves` |
| M2 | base answer → 0 | `base_zero_zero_price` |
| M3 | quote answer → 0 | `quote_zero_panic_freeze` |
| M4 | base answer → −1 | `base_negative_string_freeze` |
| M5 | updatedAt pushed back 24 h | `stale_serves_unchanged` |
| M6 | quote depeg to 0.90 USD | `quote_depeg_price_up` |
| M7 | base dislocation to 0.70× | `base_dislocation_price_down` |
| M8 | base answer restored | `recovery_baseline_exact` |
| M9 | base 0.80× + quote 0.90× combined | `combined_shift` |
| M10 | latestRoundData reverts | `broken_feed_call_freeze` |

## Files

| File | Role |
|---|---|
| `fork-pin.json` | Determinism pin — everything needed to re-run identically |
| `exp11_matrix.py` | Matrix driver (this bundle's copy; writes `exp11_matrix_results_repro.json`) |
| `exp11_matrix_results.json` | Recorded results — all 10 scenario verdicts, 29 fork-local tx hashes, position and market records |
| `results/exp11_matrix_run9.log` | Full driver console log of the recorded run |
| `src/MockAggregator.sol` | Controllable Chainlink-style aggregator (serve / broken modes, settable answer and updatedAt) |
| `out/MockAggregator.sol/MockAggregator.json` | Foundry build artifact the driver deploys |
| `foundry.toml` | Foundry profile for the mock build |

## Notes

- The mock matches the exact call surface `MorphoChainlinkOracleV2` uses via `ChainlinkDataFeedLib`: `latestRoundData()` and `decimals()`. Mode 0 serves; mode 1 makes `latestRoundData` revert (broken feed).
- All mutating steps (feed edits, market ops) are receipted transactions; health-gate probes are `eth_call` simulations — no hidden state changes.
- Fork receipts are fork-local by construction; real mainnet carries zero code at the mock, oracle, and market addresses.
- The balance-adaptive whale top-up guard remains in the driver (probe-then-setStorageAt via a verified slot) but was dormant in the recorded run — whale balances at the pin covered the position with no cheat.
