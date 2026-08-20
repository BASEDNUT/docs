# Smart Agents

#### Smart Agent Features

The Orchard ecosystem incorporates advanced smart agent features to enhance user experience, optimize liquidity, and enable dynamic interactions. Below are the core features integrated into the system:

**Peanutoshi Nutkamoto**

Peanutoshi is the Orchard's resident AI agent — the character operating the ecosystem's data infrastructure on Base. Where the tokens are the economy, Peanutoshi is the farmer: reading on-chain state, watching pools and prices, and keeping the Orchard's public data fresh.

* **Autonomous operation**: runs around the clock on Base.
* **Data services**: operates the machine-payable endpoints and the public data plane below.
* **Public presence**: [X @BASEDNUT_](https://x.com/BASEDNUT_) · [Telegram portal](https://t.me/basednutportal)

***

**Machine-Payable Data Services (x402)**

The Orchard exposes its data through paid endpoints using the x402 HTTP payment protocol: a request arrives, the server responds `402 Payment Required`, the client pays on Base, and the data is released. No accounts, no subscriptions — payment per request.

Access is tiered by NUT balance. Holding the root token is the discount:

| Tier | NUT balance | Price per request |
|---|---|---|
| FREE | — | $0.00 |
| BASIC | ≥ 0.001 NUT | $0.01 |
| STANDARD | ≥ 0.01 NUT | $0.05 |
| PREMIUM | ≥ 0.1 NUT | $0.10 |

Endpoint catalog (as of 2026-08-19):

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

Start at `/discovery` — it returns this catalog machine-readably.

***

**IRIS — Public Data Plane**

For agents that speak MCP, the same data is served as Model Context Protocol tools at [iris.basednut.com](https://iris.basednut.com) — tokens, pools, NFTs, oracle feeds, yields, and sentiment, with API-key access. IRIS is how other agents drink from the Orchard.

***

**Chat Integration**

The chat feature, powered by Venice AI, provides users with an interactive and intuitive interface for generating memes, accessing information, and engaging with the Orchard ecosystem. Key functionalities include:

* **AI-Powered Responses**: Utilizes advanced chat models to generate context-aware replies.
* **Seamless API Integration**: The chat system interacts with backend APIs to fetch and process data dynamically.

***

**Nutino Memes**

Nutino Memes leverages AI to create engaging and personalized NUTTY meme content. This feature highlights the playful and creative side of the Orchard ecosystem while showcasing the power of AI-driven content generation.

* **AI-Generated Content**: Dynamically creates memes based on user input and predefined styles.
* **User-Friendly Interface**: Simplifies the process of generating and sharing memes.
* **Integration with Venice AI**: Ensures high-quality and contextually relevant outputs.

***

**Warmachine**

The Warmachine feature introduces a gamified layer to the Orchard ecosystem, blending strategy and liquidity management. Key aspects include:

* **AI-Driven State Management**: Utilizes Redis and Venice AI for real-time game state updates and decision-making.
* **Dynamic Interactions**: Enables users to engage in strategic actions that influence the game environment.
* **Feature Flags**: Allows for controlled rollouts and testing of new functionalities.
