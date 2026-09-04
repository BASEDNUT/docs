# Experiment XI — Base Mainnet Fork

Production-equivalence run: real USDC, real cbBTC, canonical Morpho, live Chainlink feeds,
and the 2-leg candidate oracle (cbBTC/USD / USDC/USD) deployed through the real V2 factory.

## Reproduce

1. Launch the fork exactly as pinned: `anvil --fork-url https://base.publicnode.com --port 8546 --chain-id 8453` at block 50852765 (see `fork-pin.json` for block hash).
2. `python3 exp11_oracle_candidate.py` — deploys the candidate oracle via the factory (CREATE2, deterministic address), writes `exp11_oracle_candidate.json`.
3. `python3 exp11_market_roundtrip.py` — creates the fork market, walks the full roundtrip at the exact borrow maximum, writes `exp11_market_roundtrip.json`.
4. `python3 exp11_o8.py` — cleanup + re-verified final zero-state roundtrip (idempotent).

Requires Python 3 with `web3` + `eth_abi`. All account access is anvil impersonation (whale + anvil default account) — no private keys.

## Fork pin

`fork-pin.json` carries the full determinism set: fork block + hash, chainId, endpoint, all contract addresses, feed proxies, market ids, creation tx hashes, and every roundtrip tx hash.

## Files

| File | Role |
|---|---|
| `fork-pin.json` | Determinism pin — everything needed to re-run identically |
| `exp11_oracle_candidate.py` | Candidate oracle deployment + formula proof |
| `exp11_market_roundtrip.py` | Market creation + exact-max roundtrip |
| `exp11_o8.py` | Idempotent cleanup + final verified roundtrip |
| `exp11_oracle_candidate.json` | Oracle deployment results (feed raws, scale factor, parity) |
| `exp11_market_roundtrip.json` | Roundtrip results (all tx hashes, exact-max math, final zero state) |
| `sources/` | Upstream Solidity sources (Morpho, V2 factory, oracle, adapters, VaultV2) |
