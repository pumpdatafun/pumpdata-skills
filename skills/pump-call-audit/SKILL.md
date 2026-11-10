---
name: pump-call-audit
description: "Did that caller's pump.fun picks really 40x? Audit a KOL's, a Telegram group's or your own calls: replay every pick against the chain with real fees, real fills and the dead coins counted, then compare it with what any coin in the same market-cap band did. Use when someone posts call results, PnL screenshots or a win rate for pump.fun memecoins."
version: 1.0.0
author: pumpdatafun
tags: [pump.fun, solana, memecoin, kol, calls, callers, backtest, audit, pnl, replay]
---

# Audit a caller's pump.fun calls

A caller's "40x" is usually the peak of the best pick, from the first call, with no fees and the dead picks left out.
This replays the picks the way a follower would have traded them and says what they really made.

## Steps

1. **Collect the calls** as a list: the coin's mint, the time the call was posted (UTC), and a size in SOL (use the
   same size for every pick, e.g. 0.5). Keep every call, the losers too. A ticker instead of a mint:
   `GET https://pumpdata.fun/coin?q=<ticker>` and pick the mint launched before the call.
2. **Replay them** ($2 a run, up to 500 picks, paid in USDC over x402; your x402 tool pays and retries):

   ```sh
   curl -s -X POST https://pumpdata.fun/replay -H 'content-type: application/json' -d '{
     "picks": [{"mint": "<mint>", "at": "2026-11-09T14:05:00Z", "size_sol": 0.5}],
     "latency_s": 3
   }'
   ```

   It answers `402` with the price first; pay it and send the same request. Then `202` with an `id`: poll
   `GET https://pumpdata.fun/replay/<id>` (free) every few seconds until `state` is `done`. Or with the CLI:
   `npx github:pumpdatafun/pumpdata-skills audit picks.json` (prints the price and polls once paid).
   An `exit` (`{"take": 2}`, `{"trail": 0.3}`, `{"hold_s": 3600}`) replays a rule for selling; without one the
   answer says how it holds.
3. **Compare with the base rate** for the band most calls were made in, free for yesterday:
   `GET https://pumpdata.fun/public/baserate.json` (or `GET /baserate?band=15k-28k&from=&to=` for the calls' window,
   $0.005).

## What to report

- What the picks made in sum, in SOL, after fees, with the dead picks in it, and the best and worst pick.
- How many picks came back `skipped_not_covered` (still on the bonding curve, or outside the archive): say they were
  not counted, neither as wins nor as losses.
- The base rate next to it: "of all coins that crossed $15-28K that week, 5% reached 10x within three hours".
  If the calls did no better than that, say so plainly.
- The window and `X-Data-As-Of`. Facts, not a verdict on the person.

More: https://pumpdata.fun/pump-fun-backtest. The full reference: the `pumpdata` skill in this repository.
