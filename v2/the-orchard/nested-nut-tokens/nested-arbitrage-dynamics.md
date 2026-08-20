# Nested Arbitrage Dynamics

## SALT as an Example of Arbitrage Dynamics

SALT is a synthetic derivative of NUT, created through the MintClub bonding system. Its issuance is **pegged to NUT**:

$$
\text{Effective SALT Price} = \frac{\text{Locked NUT}}{\text{SALT Minted}}
$$

***

### Arbitrage Coupling

Arbitrage involves three instruments:

* **SALT** (synthetic derivative)
* **NUT** (root asset)
* **USDC** (stable reference)

When SALT’s AMM price diverges from its mint cost (NUT peg), arbitrage opportunities exist.

***

### Market Dynamics

1. **Mint Side**
   * SALT can be minted at a flat bonding curve rate using NUT.
2. **AMM Side**
   * SALT trades against USDC in AMMs like Aerodrome.
   * Price follows the **x·y = k** invariant.

### NUT Locking for SALT

* **Float reduction:** Minting SALT reduces the circulating float of NUT.
* **Feedback:** Less circulating NUT can influence NUT’s own market price.
* **Peg effect:** Because SALT’s peg references NUT, shifts in NUT’s market dynamics flow through to SALT’s implied cost.

***

**Example Spread**

* In this example, SALT is **cheaper on MintClub** than on Aerodrome.
* Arbitrage: mint SALT by locking NUT → sell SALT for USDC.
* This process pushes the AMM price down toward the peg and simultaneously locks NUT in the bonding curve.

### Convergence

Arbitrage ends once the AMM price ≈ peg price. At that point, the arbitrage window becomes narrower.

***

###

SALT shows how synthetic token systems create cross-asset arbitrage. Arbitrage exist only while AMM price diverges from the peg. Arbitrage itself enforces alignment towards a balance.
