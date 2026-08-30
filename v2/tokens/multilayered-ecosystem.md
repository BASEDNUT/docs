# NUT Multilayered Token Ecosystem

## Multilayered Token Economies

<figure><img src="/files/cSJ1HJOG34T5bUAa8VQ9" alt=""><figcaption></figcaption></figure>

Tokens are the lifeblood of sophisticated financial ecosystems, serving as mediums of exchange, stores of value, and governance instruments.

Traditional protocols often employ one or two tokens to facilitate basic functions. However, the emergence of complex, multilayered token economies introduces a new paradigm—one that leverages stacked layers of tokens to create cascading effects and intricate networking dynamics

Multi-layered token economies create a multitude of different pressure conditions that can create a plethora of networking effects. Each layer introduces an unique dynamic to the ecosystem: contributing to liquidity management, cascading deflationary effects, and arbitrage opportunities across liquidity pools (LPs) and bonding curves.

Each layer introduces unique dynamics to the ecosystem, contributing to liquidity management, cascading & lagging effects. These layers also create arbitrage opportunities across liquidity pools (LPs) and minting bonding curves.

Tokens in a multi-layered ecosystem act as orbits around each other creating effects by interacting with each other and creating lasting networking consequences.

***

## BASED NUT

## NUT: The Root Parent Token of the Ecosystem

The BASED NUT ecosystem revolves around the token, **NUT**, for Network Utility Token. This is a standard Open Zeppelin ERC-20 token designed for simplicity and efficiency in mind.

The NUT token is considered much like a NUT, the seed root of the entire BASED NUT ecosystem. The NUT token connects the entire ecosystem together and creates network cohesion.

With a capped supply of just 1 token, NUT serves as the root parent token, anchoring the entire ecosystem to its code. Its minimalist ERC20 design ensures low gas fees and ease of integration, making it an ideal candidate for high-frequency transactions and flash&#x20;

The NUT token is made in such a way that is impossible to mint more tokens on the main token contract. However, token systems can be built on top, in parallel and nested below the NUT token that creates networking effects. In other words, the lack of programmatic functionality does not mean a lack of utility or lack of strong networking effects since the functionality is extracted from the primary token.&#x20;

#### **Liquidity Pool Genesis**

The genesis liquidity pool for NUT was established on Uniswap V3 as a NUT/ETH pair. Uniquely, the pool initially contained only NUT, with zero ETH deposited. This created a highly concentrated liquidity configuration, setting the stage for dynamic liquidity management and paving the way for the subsequent token layers.

#### **Deflationary Mechanics**

Added effects from other tokens acting on the NUT token, create the programmatic intelligence layer for NUT. Despite its simplicity, NUT exhibits deflationary characteristics, primarily due to its interactions with other tokens in the ecosystem. The deflationary mechanics stem from liquidity interactions, particularly through NUT's pairing in liquidity pools and with other tokens such as SNUT.

The deflationary effects are not inherent to the root token but are a result of the complex interplay with tokens like SNUT and the nested tokens. As these tokens undergo various operations—such as burning, staking, and liquidity provision—they indirectly impact the circulating supply and burning supply of NUT, creating a lagging deflationary effect across the entire ecosystem.

***

## **BASED SUPERNUTS**

### **SNUT: The Deflationary Super Staking Token**

**SNUT** is an extension of NUT with advanced layered functionalities. It operates as a "super" token above NUT, introducing a **non-escrow staking mechanism** with a buyback and burn model.

SNUT is a liquid and fungible staking mechanism for NUT rewards that uses permissionless liquidity pools rather than ownable contracts to distribute rewards. This gives users the freedom to make their own decisions about how they want to interact with the ecosystem in a trustless manner.

Unlike typical staking mechanisms that require locking tokens for rewards, SNUT enables liquidity providers and holders to benefit from NUT rewards by simply SNUT, not just by locking liquidity in contracts.

#### **Tokenomics**

SNUT incorporates a transactional tax mechanism, where a fee is levied on each transfer or trade. This fee triggers a series of cascading events:

1. **Buyback of NUT**: A portion of the tax is used to purchase NUT from the Uniswap V2 pool.
2. **Distribution to SNUT Holders**: The acquired NUT is distributed among SNUT holders as rewards.
3. **Auto-Liquidity Addition**: Some of the taxed tokens are added to the liquidity pool, enhancing market depth.
4. **Token Burning**: A portion of SNUT tokens is sent to a burn wallet, permanently removing them from circulation.
5. **Management Fees**: A fraction of the tax is allocated as fees for ecosystem maintenance.

#### **Cascading Deflationary Effects**

The **SNUT token** is a token that takes a tax everytime it is traded or transfered. When the fee of transfer is called this sends a cascade event that include: buying NUT and distributing it to SNUT holders, auto liquidity addition, burning of SNUT tokens, and generating manger fees.&#x20;

The burning of SNUT tokens creates a deflationary loop. As more SNUT is burned, its scarcity increases. Simultaneously as more SNUT is burned its accumulated in the burn address which then generates rewards in NUT there by creating a **lagging deflationary** effect on NUT. This interconnected deflationary mechanism amplifies the scarcity of both SNUT and NUT.

#### **Liquidity**

SNUT exists only in univ2 constant liquidity layers as this token is a tax token , SNUT buys NUT found in the univ2 pool and from here this gets distributed to SNUT holders.&#x20;

The token SNUT also needs to be managed much like a staking mechanism, rather than refilling the staking vaults the managing is burning snut tokens to make the snut token scarcer and the liquidity pool deeper.

***

## **BASED PEANUT**

#### **pNUT: The Inflationary Index Token**

The **pNUT** token stands as an exception within this predominantly deflationary ecosystem as being an inflationary index token designed to represent a basked of tokens including:&#x20;

* **SNUT & NUT** - BASED NUT TOKENS
* **cbBTC** - Coinbase collateralized BTC
* **cbETH** - Coinbase collateralized staked ETH

#### **Inflationary Mechanics**

Unlike SNUT and NUT, pNUT can be minted without burning its underlying assets, introducing inflationary pressure. However, this inflation is moderated by the deflationary tendencies of its constituent tokens. The underlying assets' scarcity and burning mechanisms impose a minting ceiling on pNUT, preventing unchecked inflation. This balance ensures that inflation does not escalate unchecked, preserving the index's value proposition.

**Arbitrage Through the pNUT Index**

pNUT is intrinsically tied to the underlying assets it represents. The interplay between the index price and the price of the underlying tokens generates arbitrage opportunities for traders. As users mint, redeem or trade pNUT based on market conditions, they inadvertently contribute to the deflation of tokens like NUT and SNUT.

**Taxation and Rebalancing Effects**

When unwrapping pNUT, SNUT taxes are triggered, leading to the distribution of **NUT rewards** into the index contract. Additionally, the inclusion of **cbETH**, a liquid staking token that rebases and distributes ETH staking rewards, adds another layer of cascading rewards.

***

## **NUT Nested Tokens**

Nested tokens are minted using NUT as the root asset, functioning as "child" tokens in the ecosystem. Their minting and burning are governed by bonding curves, mathematical models that define token mint prices based on supply and demand. As more NUT is locked into the bonding curve to mint new tokens, the mint price increases, creating a dynamic pricing mechanism.

#### **Arbitrage and Market Dynamics**

The nested tokens introduce arbitrage opportunities between the bonding curves and liquidity pools like Uniswap V2. Users must decide whether to sell tokens into liquidity pools or burn them through the bonding curve contract, depending on market conditions and personal strategies.

#### **Impact on NUT's Supply Elasticity**

This setup creates a sophisticated interplay between the nested tokens and their parent, NUT.  When users burn nested tokens, the corresponding amount of NUT is released as per the bonding curve. This process can either increase or decrease NUT's circulating supply, depending on the net minting and burning activities, thus influencing NUT's supply dynamics and having an ecosystem wide effect.

***

## THE GIANT TREE OF NUT ETHER

Envisioning the multilayered token ecosystem as a giant tree provides a tangible metaphor for understanding its complexity:

* **NUT as the Trunk and Roots:** NUT forms the foundational structure, anchoring the ecosystem like roots stabilize a tree.
* **SNUT and pNUT as Branches and Fruits:** These tokens extend from the core, offering new utilities and rewards, akin to branches bearing fruits.
* **Nested Tokens as Epiphytes:** Similar to orchids and bromeliads that grow on trees, nested tokens establish micro-ecosystems, contributing to the tree's biodiversity and health.

Just as each part of a tree plays a vital role in its growth and sustainability, every token in the ecosystem interacts symbiotically. The health of the entire system depends on the balance and interplay of its components, highlighting the importance of each layer in maintaining the ecosystem's vitality.

***

## THE CREDIT LAYER

Above the token layers sits the credit layer.

nutUSD is the tokenized share of a USDC credit reserve.
Deposits of USDC supply conservative 38.5% LLTV credit markets, collateralized by assets such as cbBTC and cbETH.
nutUSD is proposed; it is not yet deployed on Base mainnet.

```
NUT — the root
      ↓
token layers — SNUT, pNUT, SALT, NUTINO
      ↓
credit layer — nutUSD, the USDC reserve share
```

The credit layer is not a child token of the root.
It is a reserve share — economic structure supplied by USDC deposits, not derived from NUT supply.

See [nutUSD](/v2/tokens/nutusd.md).

***

## **A Novel Multilayered Token Economy**

### Advanced Effects: Cascading and Lagging Dynamics

#### Cascading Deflationary Effects

Actions within one layer of the ecosystem trigger ripple effects across other layers. For example, burning SNUT reduces its supply, increasing its scarcity and value. This action also affects NUT by generating rewards for SNUT holders, which can lead to further demand and potential deflationary pressure on NUT.

#### Lagging Deflationary Effects

The deflationary impact on NUT manifests over time as cumulative effects from various layers accumulate. As more nested tokens are minted and burned, and as SNUT continues its deflationary cycle, the scarcity of NUT becomes more pronounced, leading to potential value appreciation in the long term.

#### Inflationary Counterbalances

The inclusion of pNUT introduces controlled inflation into the ecosystem. This inflation serves as a counterbalance to the deflationary forces, ensuring that liquidity remains sufficient and that excessive scarcity does not hinder usability or accessibility.

### Arbitrage Opportunities and Market Dynamics

#### Between Liquidity Pools and Bonding Curves

Price discrepancies between liquidity pools and bonding curves create arbitrage opportunities. Traders can profit by buying tokens where they are undervalued and selling where they are overvalued, enhancing market efficiency and liquidity.

#### Index Token Arbitrage

Variations in pNUT's price relative to its underlying assets encourage minting or redemption. This activity helps maintain price equilibrium and offers traders opportunities to capitalize on market movements.

#### Transactional Tax Strategies

SNUT's transactional taxes can be leveraged by savvy traders to maximize returns. By understanding the fee structures and timing of transactions, traders can optimize their strategies to benefit from the cascading rewards and deflationary effects.

### Liquidity Provision Strategies

Liquidity providers are essential to the ecosystem's functionality. By supplying tokens to various pools, they facilitate smooth trading and earn fees. The auto-liquidity mechanisms in SNUT and the nested tokens ensure that liquidity is continually replenished, supporting robust market activity and stability.

### Implications and Future Outlook

#### Enhanced Utility and Participation

The multilayered design enhances utility by stacking functionalities across tokens. This complexity attracts a broader user base, offering various incentives for holders, traders, and liquidity providers to participate actively in the ecosystem.

#### Resilience and Stability

The interconnected layers provide a buffer against market volatility. The ecosystem can self-correct through its internal mechanisms, promoting resilience and long-term stability.

#### Potential Risks

While innovative, the complexity introduces certain risks:

* **Accessibility Barrier:** New users may find the ecosystem daunting, potentially limiting widespread adoption.
* **Smart Contract Vulnerabilities:** Multiple layers increase the potential for exploits, necessitating rigorous security measures.
* **Regulatory Considerations:** Complex financial instruments may attract regulatory scrutiny, requiring compliance and transparency.

### Conclusion

The BASED NUT multilayered token ecosystem represents a significant advancement in DeFi tokenomics. By integrating deflationary and inflationary mechanisms across multiple token layers, it creates a sophisticated network of incentives, scarcity, and value accrual. The cascading and lagging effects, coupled with arbitrage opportunities, foster a dynamic and resilient ecosystem capable of self-sustenance and growth.

This novel framework pushes the boundaries of what token economies can achieve, offering valuable insights for future developments in the DeFi space. As the ecosystem matures, it may serve as a blueprint for constructing more complex, robust, and interconnected financial systems that better serve the needs of a decentralized world.
