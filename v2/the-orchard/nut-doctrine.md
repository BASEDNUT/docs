# 🌰 NUT Doctrine — The Root of All Liquidity

**Status: LIVE** — NUT on Base mainnet. Supply = **1**, forever.

> One whole token split into 1 quintillion atomic units (10^18 attoNUTs) — a conserved ledger with no mint, no burn, and no admin on the root contract. Every swap relocates a fraction of the same supply; whole-token price equals FDV because total supply is one. Specified child assets use NUT as collateral, reward asset, constituent, or reference input.

## The Master Question

> How many economically distinct systems can coordinate around the same monetary root?

One token, quantity frozen forever. Everything in this ecosystem is the economic structure that can still expand around it.

NUT is the **root asset** of the BASED NUT ecosystem. Because supply is 1, the whole-token price equals the FDV. Every other token in the ecosystem is built on top of NUT:

- **Bonding curve tokens** (NUTINO, SALT) are minted by locking NUT as collateral
- **SNUT** is a reward-position token that earns NUT for holders
- **pNUT** is an index basket that includes NUT at 25% weight

This makes NUT the **reference coordinate** — child assets use NUT as collateral, reward asset, constituent, or reference input.

## Why Layers Exist

A flat token forces incompatible economic pressures onto one instrument: if spending, rewards, collateral, and index value all ride the same balance, changing any one destabilizes the others. The layered system separates those pressures into distinct instruments **while keeping them all anchored to the same conserved root** — separation of monetary labor without splitting the monetary whole.

## A Conserved Measure of Allocation

Supply is 1 — forever. But that 1 NUT is split across pools and wallets. This is a **conservation problem**: how is the single NUT distributed across the ecosystem?

Formally: μ(C) = the fraction of total NUT residing in compartment C, and μ(𝒞) = 1 across every compartment. "Where is the NUT?" is not just token distribution — it is the observable map of a **conserved measure** over the economic system.

### Normalized by Construction

A 10,000-supply token also holds quintillions of atomic units — so what is really different about NUT? Other supplies can be normalized too. What is different is that NUT **begins normalized**: because total supply is exactly one, every balance is numerically identical to its share of the whole. 0.01 NUT is 1% of every NUT that will ever exist — no secondary math needed.

## The Four Rules

### 1 — Conservation

One whole NUT is 10^18 atomic units, minted once, never again. Total supply is verified on-chain as exactly 1 NUT; the root contract has no mint, no burn, no admin. Every swap, pool move, mint, or index change only relocates a fraction of the same total. **State changes address; amount never changes.**

*Why it matters:* supply can never drift or dilute.

### 2 — Whole Price Equals FDV

Because total supply is exactly one, FDV = price × 1 = price — no circulating-supply estimate needed, no unlock schedule, no inflation curve. A separate fact: quantity is invariant, but **effective float** — how much of the one NUT is accessible to trade — is endogenous to pools, locks, indexes, and inactive balances.

*Why it matters:* whole-token price equals FDV by construction.

### 3 — State Transition

Each venue couples fractions of the same conserved NUT root to different counter-assets and state variables under different transition rules — NUT/wETH, NUT/AERO, NUT/cbBTC, an index basket. The same one NUT can carry different prices at the same moment. Deterministic rules make discrepancies observable; arbitrage creates pressure toward executable consistency within a band set by fees + gas + slippage.

*Why it matters:* venue rules are deterministic; whether and how fast markets converge is an open question, not a guarantee.

### 4 — Denomination

NUT uses strict SI units: the attoNUT is the monetary quantum of the ledger — its smallest representable transfer unit. 1 NUT = 10^18 monetary quanta. picoNUT, microNUT, and NUT are the same quantity at larger scales.

*Why it matters:* one unit, one grammar, one conserved root at every zoom.

## The Four Jobs — Allocation Pressure

| Job | What it does |
|---|---|
| **Collateral** | Commits NUT to mint child tokens (NUTINO, SALT) on bonding curves — locked and stable |
| **Reward** | Distributed to participants through reward layers — keeping some NUT transferable |
| **Basket Member** | Reserved and rebalanced at a defined weight inside the pNUT index |
| **Price** | Exposed to exchange — markets keep some NUT liquid for trading and price discovery |

A conserved supply can perform all four jobs; what it cannot do is satisfy all four without competing demands on its allocation. Because root quantity cannot expand, competing uses resolve through **reallocation rather than issuance**.

Fungibility does not imply functional equivalence of placement: 0.01 NUT is always 1% of root supply wherever it resides, but 0.01 NUT in an AMM, a collateral reserve, an index basket, or an inactive wallet occupies a different economic state. **Prices are commensurable; functions are heterogeneous.**

## The Liquidity Machine

NUT does not move through a passive market. It moves through a machine it rewrites by moving:

> **object → position → graph → field → motion → backreaction → dynamics**

- **Object** — one conserved quantity, Q_NUT
- **Position** — a distributed allocation over economic compartments, ∑xᵢ = 1
- **Graph** — markets define the permitted paths through which allocation can change
- **Field** — prices, fees, reserves, liquidity generate a directed opportunity field over those paths
- **Motion** — agents exploit the directed opportunity field; those actions are transactions
- **Backreaction** — transactions change reserves and liquidity, changing the field that caused them
- **Dynamics** — the repeated loop generates endogenous market behavior

A road stays put when a car crosses it. A liquidity network does not: a swap is not just passing through a pipe — it is reshaping the pipe. Using the graph changes the state of the graph (reserves, prices, ticks, edge weights); only adding or removing pools changes its topology.

> state → incentive → transaction → new state → new incentive

## One Conserved Root. Many Local Price Surfaces.

The same fungible NUT trades on Uniswap V2, V3, Aerodrome, and Balancer — none speaks the other's language, yet fractions of the one unit live inside all of them. Each venue produces an executable exchange rate from its own reserves, liquidity, fees, and curve.

**There is no canonical on-chain price of NUT** — only local executable prices, coupled by arbitrage, which exists precisely because those prices are commensurable. The spread is not a flaw; it is the honest observable of one root living in many jobs.

> Price is not stored in NUT. Price is produced by the state of the market observing NUT.

## Arbitrage, in Plain Words

The same NUT trades in many markets at once — Uniswap V2, V3, Aerodrome, Balancer, bonding curves. Every market has its own price, so sometimes the same NUT is cheaper in one place and pricier in another.

**Arbitrage is buying it where it is cheap and instantly selling it where it is dear**, pocketing the difference. That gap-closing is not cheating or a bug — it is the ecosystem keeping itself honest. Bots race to find these gaps, which pulls every venue's price back into line. Multi-venue fragmentation creates the possibility of discrepancies; arbitrage economically couples those venues back into line. Because NUT is one conserved unit spread across many venues, its price surfaces are coupled by a shared root.

## The Reflexivity Loop

> scarce root → multiple venues → child minting → index wrapping → price gaps → arbitrage → root reprices → repeat

The system is **reflexive** — child assets derive value from NUT, and their activity feeds back to NUT's price. Contracts execute deterministically and agents choose actions under those rules — the graph does not vote. NUT itself just shows up.

## The Full State

The allocation vector x_t is fundamental, but it is not the whole ecosystem. The full state is a tuple of observables:

| Component | Meaning |
|---|---|
| x_t — NUT allocation | The conserved simplex share of NUT itself |
| R_t — reserves | Counter-asset and collateral reserves per venue |
| L_t — liquidity | Liquidity positions, range, and depth |
| Q_t — derived states | Child-token and index states built on NUT |
| Θ_t — parameters | Fees, curve parameters, weights, mechanism settings |
| M_t — memory | History-dependent observables such as TWAP |
| E_t — external environment | wETH, cbBTC, AERO, gas, block conditions, broader liquidity |

Valid actions are **lawful state transformations**: swaps, curve mints, redemptions, joins, exits, and liquidity moves are different transition operators. Every valid transition changes state while preserving the conservation identity ∑x(t+1) = ∑x(t) = 1.

A pNUT claim is not NUT counted twice; child-token supply is not additional NUT. Derived claims live in the broader state vector, not the conserved sum. **One conserved root — everything interesting happens around that equality.**

### State versus History

Two histories can land on the same NUT allocation while leaving different TWAP observations, LP configurations, or agent positions behind. That is why the allocation map is fundamental but insufficient — and what gives "TWAP is memory" a real function: the machine can carry history beyond the current allocation vector.

## Macro Observables — Proposed Metrics, Not Doctrine

NUT is observable at several scales: assignments and ticks (micro); pools, bonding curves, index balances (meso); effective float, concentration, price dispersion (macro).

| Observable | What it measures |
|---|---|
| HHI | Concentration of allocation |
| Entropy | Dispersion of allocation |
| Effective float | Accessible NUT, F ≤ 1 |
| Price dispersion | Spread across venues |
| Arbitrage half-life | How fast gaps close |
| Collateral-lock ratio | NUT committed as collateral |
| Routing centrality | How much flow passes each venue |
| NUT velocity | How often the same NUT moves |

Δ S_NUT = 0 does not imply Δ economic complexity = 0. A monetary system does not need an expanding base asset to support an expanding economy — **economic expansion can occur through increasingly sophisticated structures built around that base**.

**The experiment:** can more markets, routes, claims, liquidity configurations, derived assets, and economic relationships expand economic state and functionality while S_NUT = 1 remains invariant?

## Open Questions — Research Lenses, Not Claims

> Doctrine is the conservation law; research is the test. These frameworks exist to test, not decorate. Each must earn its place by explaining, predicting, compressing, or falsifying something observable. **Conservation is doctrine. Dynamics are measurable. Mathematics enters only where the machine gives it something real to explain.**

| Lens | Research question |
|---|---|
| Spectral modes & eigenmodes | Are there persistent modes of system-wide NUT redistribution, or is movement idiosyncratic? |
| Koopman operator analysis | Can observables (reserve ratios, price dispersion, spreads) reveal coherent modes of nonlinear NUT dynamics? |
| Stability theory | After a disturbance, does the ecosystem return toward a bounded region, remain displaced, or transition regimes? |
| Fixed points & no-arbitrage regions | Does the system repeatedly return to a measurable no-arbitrage region, and how wide is it? |
| Limit cycles | Do repeated NUT flows emerge from internal feedback alone, or from external shocks? |
| Bifurcations & regime transitions | Are there parameter values at which the machine changes regime? |
| Renormalization & multiscale dynamics | Which variables remain informative when microscopic detail is coarse-grained away? |
| Hypergraph theory | Does a liquidity hypergraph capture systemic dependencies pairwise routing graphs miss? |
| Recursive structural analysis | Which deployed cycles, if any, repeatedly map reserve → claim → market → reserve in a structurally equivalent way? |
| Prime-factor state encoding | Can canonical arithmetic encoding simplify proofs about restricted classes of NUT state transitions? |
| FRACTRAN state machines | Can restricted NUT transition systems be represented as arithmetic programs while preserving conservation? |
| Compositional algebra | Which classes of NUT transformations commute, which are path-dependent, and which algebraic structures describe them? |
| State estimation | What is the smallest sufficient set of on-chain observables needed to reconstruct the economically relevant state? |
| On-chain economic genealogy | Can the ancestry of derived claims be formally tracked through collateral, reserve, index, and liquidity relationships? |
| Propagation & memory | How do shocks propagate across venues, and what are the delays in their transmission? |

## Doctrine Close

> One root. Many markets. Many states. One conserved whole.
>
> The doctrine is conservation. The machine is liquidity. The frontier is dynamics.

> ⚠️ **Experimental Memefi.** NUT is an experimental cryptoeconomic liquidity topology — an unregulated experimental asset and a documented Network Utility Token within the BASED NUT ecosystem. Not investment advice; no guarantee of profit or value retention. Use at your own risk.
