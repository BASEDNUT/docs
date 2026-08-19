# BASED NUT — Docs

Draft repo for the next-generation BASED NUT documentation.

## Status

- **v1 baseline imported 2026-08-19** — all 19 pages mirrored from live docs.basednut.com (GitBook) with original GitBook-style markup preserved (tabs, figures, tables).
- This repo is the drafting ground. Live docs remain untouched at docs.basednut.com until a decision is made.
- Platform + hosting decision pending. Vercel deployment (same account as ecosystem sites) is the working assumption; nothing deployed yet.

## Layout

```
based-nut/                      # v1 mirror, structure = live site tree
  based-nut.md                  # Main overview
  the-orchard.md                # MetaDEX framework
  the-orchard/                  # Tokens, nested tokens, Nut Army
llms.txt                        # Machine-readable index (live fetch)
```

## Rules

- No secrets, no internal state, no unverified claims.
- v1 content is the canonical base — rewrites extend, not discard.
- Every address/claim must trace to on-chain or verified evidence.
