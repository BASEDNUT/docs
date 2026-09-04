# nutUSD Research Artifacts

Reproducible artifact bundle for the nutUSD research series (Experiments X and XI).
Published with the series pages under `v2/research/`.

## Contents

| Bundle | Experiment | What it contains |
|---|---|---|
| `exp10-invariants/` | X — invariant suite | Foundry stateful handler suite, vendored dependencies (forge-std MIT/APACHE-2.0, morpho-blue GPL-2.0), raw run logs, result JSON |
| `exp11-fork/` | XI — production fork | Fork pin (block/hash/addresses), deployment and roundtrip scripts, result JSONs, oracle/factory/adapter Solidity sources |

## Provenance

- All Morpho sources are unmodified upstream artifacts (morpho-org/morpho-blue, Morpho interfaces and oracle factory).
- All receipts are fork-local and deterministic under the pinned fork block.
- No private key material: fork runs use anvil impersonation of publicly-known accounts only.
- `foundry.lock` / dependency commits preserved inside the vendored trees.
