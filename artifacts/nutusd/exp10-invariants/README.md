# Experiment X — Foundry Invariant Suite

Stateful handler suite driving the canonical Morpho Blue source through randomized action sequences.

## Reproduce

1. Install Foundry 1.8.1 (`curl -L https://foundry.paradigm.xyz | sh && foundryup`).
2. `forge install` is NOT needed — dependencies are vendored under `lib/` (forge-std, morpho-blue).
3. Base run: `forge test --match-contract NutUSDInvariant` (64 runs x 100 depth).
4. Deep run: `FOUNDRY_PROFILE=deep forge test --match-contract NutUSDInvariant` (256 runs x 150 depth).

Seeds: Foundry's deterministic default per-run seeds (`--fuzz-seed` unset). With the same forge version, runs are reproducible; across versions, sequences may differ while invariants must still hold.

## Files

| File | Role |
|---|---|
| `test/NutUSDInvariant.t.sol` | Handler suite, 12 handlers, 4 actors, 7 invariants + 2 static proofs |
| `foundry.toml` / `remappings.txt` | Config incl. deep profile |
| `results/results_base.log` | Raw base-run log (6,400 calls, 161 reverts, 0 violations) |
| `results/results_deep.log` | Raw deep-run log (38,400 calls, 1,082 reverts, 0 violations) |
| `results/results_static.log` | Raw static-proof log |
| `exp10_invariant_results.json` | Structured results incl. per-handler call/revert matrix |
| `lib/forge-std` | Vendored forge-std (MIT OR APACHE-2.0) |
| `lib/morpho-blue` | Vendored canonical Morpho Blue source (GPL-2.0, unmodified) |
