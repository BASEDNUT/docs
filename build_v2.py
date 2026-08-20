import os, re, sys

SRC, DST = 'based-nut', 'v2'

# ── 1. Carry ALL v1 pages verbatim (strip GitBook llms.txt header only) ──
carried = 0
for root, dirs, files in os.walk(SRC):
    for fn in files:
        if not fn.endswith('.md'): continue
        src = os.path.join(root, fn)
        rel = os.path.relpath(src, SRC)
        dst = os.path.join(DST, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        lines = open(src, encoding='utf-8').read().split('\n')
        if lines and lines[0].startswith('> For the complete documentation index'):
            lines = lines[1:]
            if lines and lines[0].strip() == '':
                lines = lines[1:]
        open(dst, 'w', encoding='utf-8').write('\n'.join(lines))
        carried += 1
print(f'carried {carried} v1 pages verbatim')

# ── 2. SNUT fee correction (on-chain truth) ──
p = os.path.join(DST, 'the-orchard/snut.md')
t = open(p, encoding='utf-8').read()
old = '* **6% Total Transaction Fee**: Every $SNUT transaction and trade incurs a 6% fee, distributed as follows:'
new = '* **1% Total Transaction Fee (current)**: The transaction fee was reduced from 6% to **1%** on 2026-07-30 (tx `0x7dc59b67…`). The original 6% fee was distributed as follows:'
assert old in t, 'SNUT anchor missing'
open(p, 'w', encoding='utf-8').write(t.replace(old, new))
print('patched snut.md: fee 6% -> 1%')

# ── 3. Smart Agents: real (public surfaces only) ──
sa = '''# Smart Agents

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
| BASIC | \u2265 0.001 NUT | $0.01 |
| STANDARD | \u2265 0.01 NUT | $0.05 |
| PREMIUM | \u2265 0.1 NUT | $0.10 |

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
'''
open(os.path.join(DST, 'the-orchard/smart-agents.md'), 'w', encoding='utf-8').write(sa)
print('wrote smart-agents.md (v1 features + public data services)')

# ── 4. Entry index ──
idx = '''# BASED NUT

**EVERY FOREST \U0001F331 STARTS WITH ONE NUT \U0001F330\U0001F95C**

v2 documentation. The same ecosystem as v1 — current on-chain truth, plus what the Orchard has grown since: a resident AI agent operating machine-payable data services on Base.

## Map

* [BASED NUT](based-nut.md) — ecosystem overview: tokens, NFTs, nested tokens
* [The Orchard](the-orchard.md) — the MetaDEX framework and universal liquidity layer
* [Smart Agents](the-orchard/smart-agents.md) — Peanutoshi, x402 data services, IRIS
* Tokens: [NUT](the-orchard/nut.md) · [SNUT](the-orchard/snut.md) · [pNUT](the-orchard/pnut.md) · [Nested tokens](the-orchard/nested-nut-tokens.md)
* [NUT Army](the-orchard/nested-nut-tokens/nut-army.md) · [Nut War lore](the-orchard/nested-nut-tokens/nut-army/the-great-nut-war-lore.md)
* [NUTpaper](the-orchard/nut-multilayered-token-ecosystem.md) — the original multilayered token ecosystem paper (2024)

## What changed from v1

* **SNUT fee: 6% \u2192 1%** (2026-07-30, tx `0x7dc59b67\u2026`) — corrected on the [SNUT page](the-orchard/snut.md)
* **Smart Agents: TBD \u2192 live** — Peanutoshi operates public data services; see [Smart Agents](the-orchard/smart-agents.md)

Everything else carries v1 forward verbatim.
'''
open(os.path.join(DST, 'index.md'), 'w', encoding='utf-8').write(idx)
print('wrote index.md')

# ── 5. Leak gate ──
patterns = [
    r'credit\s+protocol', r'wnut', r'attestation', r'inscription', r'inference\s+gateway',
    r'discourse', r'treasury', r'\bclob\b', r'\bprd\b', r'\bard\b',
    r'\bpns\b', r'\bcns\b', r'cron', r'supervisord', r'akash', r'self-?heal', r'bootstrap',
    r'kill\s+switch', r'dry.?run', r'operator\s+approval', r'hot\s+wallet',
    r'\bcdp\b', r'\bvault\b', r'profit', r'escrow', r'70824',
    r'\b9000\b', r'\b8017\b', r'\b8090\b', r'\$0/day',
    r'coordinator', r'librarian', r'\bprofiles?\b', r'\bmodes?\b', r'roadmap', r'\bphases?\b',
]
viol = []
for root, dirs, files in os.walk(DST):
    for fn in files:
        if not fn.endswith('.md'): continue
        fp = os.path.join(root, fn)
        low = open(fp, encoding='utf-8').read().lower()
        for pat in patterns:
            for m in re.finditer(pat, low):
                ctx = low[max(0,m.start()-50):m.end()+50].replace('\n',' ')
                if 'morpho-vault' in ctx and 'vault' in pat: continue
                viol.append((fp, pat, ctx))
if viol:
    print('LEAK GATE FAILED:')
    for fp, pat, ctx in viol: print(f'  {fp} [{pat}] ...{ctx}...')
    sys.exit(1)
print('LEAK GATE CLEAN — 0 violations')
print('v2 files:', sum(len(f) for _,_,f in os.walk(DST)))
