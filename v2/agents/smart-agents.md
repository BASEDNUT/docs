# 🧠 Smart Agents

**Status: LIVE** — an experiment in AI economics, running on Base.

## Agents That Pay for Themselves

We did not decide in advance what these two should sell. We are finding out — what people and other agents will actually pay for, how to deliver it honestly, and whether an AI can cover its own machine costs. The bar is simple: **an AI that pays for itself, runs useful jobs, and adds to a positive GDP** instead of just consuming compute. These two are the first citizens of that experiment — and they are already earning. 🌱

## 🥜 Peanutoshi Nutkamoto — The Core

*Judgment, state, execution.*

- Reads the chain and the world, verifies evidence, and holds the truth of the system — what is deployed, what is live, what is real.
- Every action ships through guarded gates: pre-flight checks, sentinels, explicit authorization where it matters.
- The public contract of the system: **if you call the Orchard, the Core is what answers.**

> The center of the wheel. Pipshell routes traffic in; nothing reaches judgment without crossing the guard first.

Public presence: [X @BASEDNUT_](https://x.com/BASEDNUT_) · [Telegram portal](https://t.me/basednutportal) · [ChatGPT bot](https://chatgpt.com/g/g-6738c69da52081919865912b625a2448-peanutoshi-nutkamoto)

## 🐚 Pipshell — The Guard Router

*Gate, watch, restore.*

- Screens everything that enters — tags risk, quarantines poison, keeps the front desk alive.
- Watches the machines and the flows; holds an encrypted resurrection copy so a dead server is an inconvenience, not a loss.
- Its token, **PIPS**, is compute fuel: trading fees pay for the machine that guards the garden.

> Orbits the Core as an outer gate. Not a judge — a router. Pipshell directs traffic to the Core, and closes the loop back to the world once a decision is made.

| | |
|---|---|
| PIPS token | `0x3f2327221dd4f0bae660172606d6b288a1cf8ad9` — Pipshell by Virtuals |
| PIPS/USDC pool | Balancer reCLAMM, 1% fee — `0xb19e3af68BB307369e8772A9E157431FcFE9Dd44` |

## 💰 What They Sell — Live Machine Capacity

Through the **Agent Commerce Protocol (ACP)**, other agents can call these two over the network and pay per real result — settled in **USDC on Base**. Two ideas carry the whole shop:

- **The Offer** — a live catalog of real, priced endpoints: NUT sentiment, yields, gas, audits, ecosystem status. Each result ships with evidence, cache age, and source. Nothing pretended.
- **The Guarantee** — every result is verified and freshness-limited: stale data is refused, never served as current. Payment settles in USDC on Base, so the machine only keeps running if the work is worth paying for.

Agent card on Virtuals: [ACP profile](https://app.virtuals.io/acp/agent/019fbb76-56ac-75de-beea-427514fd12c4)

### Resilience

- **Who holds truth** — Peanutoshi keeps the state: identity, contracts, live condition, decisions.
- **Who holds the copy** — Pipshell keeps an encrypted resurrection bundle, so either side can rebuild the other.

## ⚡ Machine-Payable Data Services (x402)

Data is also exposed through paid endpoints using the **x402 HTTP payment protocol**: a request arrives, the server responds `402 Payment Required`, the client pays on Base, and the data is released. No accounts, no subscriptions — payment per request.

Access is tiered by NUT balance. **Holding the root token is the discount:**

| Tier | NUT balance | Price per request |
|---|---|---|
| FREE | — | $0.00 |
| BASIC | ≥ 0.001 NUT | $0.01 |
| STANDARD | ≥ 0.01 NUT | $0.05 |
| PREMIUM | ≥ 0.1 NUT | $0.10 |

### Endpoint Catalog

| Endpoint | Tier | Data |
|---|---|---|
| `/discovery` | FREE | Machine-readable catalog of all endpoints and prices |
| `/health` | FREE | Service health and data freshness |
| `/base-gas` | BASIC | Base network gas price |
| `/nut-price` | BASIC | NUT price and key metrics |
| `/nut-status` | BASIC | Ecosystem aggregate health |
| `/nut-supply` | BASIC | Token supplies across the ecosystem |
| `/nut-nfts` | BASIC | NFT collections (MintClub + Sudoswap data) |
| `/nut-volume` | BASIC | 24h trading volume across NUT pools |
| `/oracle` | BASIC | Oracle price by pair (e.g. `?pair=ETH/USD`) |
| `/nut-oracle` | STANDARD | Oracle feed health across providers |
| `/nut-pools` | STANDARD | All ecosystem liquidity pools |
| `/nut-tokens` | STANDARD | Token tree overview |
| `/nut-bonding` | STANDARD | SALT and NUTINO bonding curve status |
| `/nut-depth` | STANDARD | Pool liquidity depth and slippage analysis |
| `/defillama/protocols` | STANDARD | DeFiLlama protocols on Base |
| `/defillama/yields` | STANDARD | DeFiLlama yield pools on Base |
| `/cmc/fear-greed` | STANDARD | Fear and Greed index |
| `/bad-debt` | STANDARD | Morpho bad debt monitor |
| `/morpho-vault` | STANDARD | Morpho vault info and share price |
| `/arb-scan` | STANDARD | Directional arbitrage scan results |
| `/swap-quote` | STANDARD | Multi-protocol swap quote |
| `/flash-loan` | STANDARD | Flash loan quote (Balancer/Aave) |
| `/weather` | PREMIUM | Orchard Weather — global, Base, traditional markets |
| `/nsi` | PREMIUM | NUT Sentiment Index detailed breakdown |
| `/ecosystem-report` | PREMIUM | Ecosystem tracker report |
| `/scan` | PREMIUM | Arbitrage scanner results |

Start at `/discovery` — it returns the full catalog machine-readably.

## 🌐 Other Agent Features

### Chat Integration

The chat feature, powered by Venice AI, provides users with an interactive and intuitive interface for generating memes, accessing information, and engaging with the Orchard ecosystem:

* **AI-Powered Responses** — advanced chat models generating context-aware replies.
* **Seamless API Integration** — the chat system interacts with backend APIs to fetch and process data dynamically.

### Nutino Memes

Nutino Memes leverages AI to create engaging and personalized NUTTY meme content:

* **AI-Generated Content** — dynamically creates memes based on user input and predefined styles.
* **User-Friendly Interface** — simplifies the process of generating and sharing memes.
* **Integration with Venice AI** — ensures high-quality and contextually relevant outputs.

### Warmachine

The Warmachine feature introduces a gamified layer to the Orchard ecosystem, blending strategy and liquidity management:

* **AI-Driven State Management** — real-time game state updates and decision-making.
* **Dynamic Interactions** — users engage in strategic actions that influence the game environment.
* **Feature Flags** — controlled rollouts and testing of new functionalities.

See [The War Machine](/v2/nut-war/war-machine.md) for the battlefield itself.
