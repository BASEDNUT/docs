# 🌱 Agricultural Credit — RWA

**Status: PROPOSED** — design-stage credit architecture; no agricultural credit contracts are deployed on Base mainnet. The capital layer is described in [nutUSD](/v2/tokens/nutusd.md); the emissions ledger it responds to is the [Environmental Balance Sheet](/v2/rwa/carbon-debt.md).

> **Nutkamoto:** data onchain is a photograph. A claim onchain is a deed. The Orchard finances deeds, not photographs. 🥜

## What This Is

Agricultural credit is the first designed application of the nutUSD credit system: financing real farms against future, attestable, monetizable real-world value.

The distinction that governs everything on this page:

> **Data becoming onchain is not itself an RWA. A legally or economically enforceable claim on land, production, inventory, receivables, carbon, or cash flow is the RWA.**

A soil reading in a database is data.
A token representing the right to repayment from a harvest is an asset.
The Orchard builds the second kind.

## The Physical Chain

Carbon credits are not invented — they are grown and proven. Every credible agricultural carbon program runs the same physical chain:

```
regenerative practice change
        ↓
MRV — measure, report, verify
        ↓
CO₂e delta vs emissions baseline
        ↓
independent verifier + registry methodology
        ↓
issued credit — 1 credit = 1 tonne CO₂e
        ↓
corporate buyer
        ↓
farmer revenue
```

A credit exists because a verified delta exists between a baseline and an attested practice outcome.
Sinking carbon through changed farm practice is what creates the asset.

Companies already buy these outcomes at scale off-chain. Farmers need capital years before the credits mature. Agricultural credit bridges that gap.

## NUTS ≠ Carbon Credits

A nut farm produces several economic outputs from one productive system:

```
            ORCHARD
               │
        ┌──────┼──────┐
        ↓      ↓      ↓
      NUTS  CARBON   LAND
        ↓      ↓      ↓
    harvest  credits  value
    inventory offtake  collateral
    receivables revenue
```

NUTS are not carbon credits and never become carbon credits.
NUTS are a product of work done on land — attributable farm output, harvest revenue, stored inventory, tradeable receivables, committed offtake.

That is exactly what makes them useful to a credit system: NUTS provide evidence of productive activity, secondary repayment capacity, and empirical operating history.

Attestations do not create the carbon credit either. An attestation establishes attributable evidence about a project — these trees were planted, this acreage is under management, this soil sample was collected, this quantity was harvested. The carbon methodology and the independent verifier determine what those observations mean in CO₂e terms. The registry ultimately issues the credit.

```
Orchard attestation  →  what happened
Carbon methodology   →  what it means in CO₂e
Registry             →  what becomes a credit
```

## The Credit Loop

```
Carbon Debt
     ↓
nutUSD Credit
     ↓
Orchard — land, trees, practice, harvest
     ↓
Attestation — attributable evidence onchain
     ↓
Carbon Credit — registry-issued, independently verified
     ↓
Corporate Capital — buyers of verified outcomes
     ↓
Orchard — repayment, expansion, next cycle
```

The loop closes through repayment, not through belief.

## The Onchain Stack

Each physical reality maps to one onchain representation:

| Physical world | Onchain representation |
|---|---|
| Land / lease | Orchard asset ID + lien claim |
| Trees / acreage / practices | Attestations |
| Harvest | Batch / inventory assets |
| Warehouse inventory | Warehouse receipts |
| Carbon outcome | MRV attestations |
| Carbon credit | Registry-linked claim |
| Buyer commitment | Offtake receivable |
| Farmer debt | Credit claim |

nutUSD is the capital layer that finances these claims. Anyone can supply liquidity to the vault; the credit system and its claims are what the vault funds.

## Core Constructs

The architecture is a set of composable claims, not one product:

| Construct | What it is |
|---|---|
| Orchard Credit Claim | Tokenized loan claim recording principal, interest, maturity, borrower, collateral package, and repayment history. The fundamental primitive |
| Attestation-Drawn Facility | Credit capacity that unlocks as real-world milestones are attested — land secured, planting complete, survival threshold, practices adopted, first harvest |
| Land Lien Claim | A token representing a legal lien or lease over productive land — the deed, not the farm |
| NUTS Warehouse Receipt | A claim against a custodied, inspected inventory lot — grade, moisture, origin, custodian recorded onchain |
| Future Harvest Claim | A finite claim on a specific harvest's proceeds — bounded, unlike perpetual crop-share |
| NUTS Offtake | A committed buyer contract converted into a financeable receivable |
| Carbon Forward | A claim on the contractual right to future credit proceeds — the contract, not a nonexistent credit |
| Quality-Linked Offtake | Buyer funds locked in a contract that release automatically when a verified batch meets specification — quality becomes an explicit price component |
| Dual-Output Credit | One facility supported by both harvest value and carbon value — the signature construct |
| Repayment Waterfall | Proceeds from nut sales, carbon sales, and insurance flow into one contract that pays expenses, interest, principal, reserves, then farmer equity — in order, by code |
| Provenance Graph | The accumulating record of every attestation, inspection, shipment, and payment — an operating history that improves future underwriting |

## Coverage

A single-output lender asks: can the crop repay?
The Orchard asks: what fraction of many outputs covers the debt?

```
Orchard Coverage Ratio
=
  risk-adjusted NUTS value
+ risk-adjusted carbon value
+ risk-adjusted receivables
+ recoverable collateral
────────────────────────
    outstanding debt
```

One productive system, several independent repayment channels — harvest cash, carbon revenue, committed buyers, recoverable land value.
Diversification of repayment is the collateral.

## Quality Becomes Underwriting

The distinctive move: verified food quality stops being an externality and becomes a priced input.

```
better farming
     ↓
verified batch meets specification
     ↓
quality + regenerative + carbon premiums in the contract price
     ↓
higher expected receivable
     ↓
stronger debt coverage
     ↓
greater or cheaper credit
```

The system does not ask corporations to value quality altruistically.
It builds contracts where verified quality carries explicit economic value — and that value flows directly into how credit is priced.

The same logic inverts onto the borrower: a facility can price down against verified practice adoption, achieved quality targets, signed premium offtake, and completed harvest history. The metric moves the loan, not a scorecard next to it.

## Evidence Infrastructure

Structured attestations already run natively on Base. Schemas, attestations, and resolver-style contracts — the machinery for milestone-gated credit — are an existing Base capability, not a foreign import. The Orchard's attestation layer is designed to sit on this native foundation: the credit facility reads attestations; the attestation infrastructure records them.

> **Nutkamoto:** the evidence layer is a public utility of the chain. The Orchard's edge is not owning the notary — it is being the first farm ledger that reads the notary fluently. 🌰

## Scope

Carbon-credit-backed agricultural finance is the first application, not the boundary.

The same credit system can finance land acquisition and improvement, irrigation, equipment, processing and storage infrastructure, nurseries and genetics, working capital, and season-to-season production — each drawing against the claims, inventory, and receivables the farm generates.

nutUSD is not a carbon instrument.
nutUSD is the credit-capital system; carbon is merely the cleanest first thing it can underwrite.

## Where to Read Next

| If you want… | Read |
|---|---|
| The capital layer itself — vault, shares, markets, risk | [nutUSD](/v2/tokens/nutusd.md) |
| The emissions side of the ledger | [Environmental Balance Sheet](/v2/rwa/carbon-debt.md) |
| The physical nut economy — crops, prices, trade flows | [US Nut Economy](/v2/rwa/nuts-production.md) |
| Every asset in the ecosystem | [Token Catalog](/v2/tokens/catalog.md) |


> ⚠️ **Experimental Memefi.** No intrinsic value, no expectation of financial gain. Entertainment only — nut responsibly. 🌰
