---
name: pump-follow-wallets
description: "Which pump.fun wallets are worth watching or copy-trading: wallets that win over their whole record (not one lucky week) and still trade, filtered to the ones a copier can keep up with. Also: is this wallet a winner, a bot, a sniper or a supply seller? Smart money and whale wallets on Solana memecoins. Free, no key."
version: 1.0.0
author: pumpdatafun
tags: [pump.fun, solana, memecoin, smart-money, copy-trading, wallets, whales, leaderboard, kol]
---

# Wallets worth following on pump.fun

## The leaderboard

`GET https://pumpdata.fun/wallets/top?followable=1&limit=25` (free). Each wallet is a whole-record winner (took out
10+ SOL and 1% more than it put in, over 20+ coin-weeks) that traded recently, with `why`, `pnl_sol`, `coins` and
`recent` (trades a day, median hold). `followable=1` keeps the ones a copier can keep up with: under 20 trades a day,
a median hold of 2 minutes or more. CLI: `npx github:pumpdatafun/pumpdata-skills top --followable`.

Not pump.fun's own leaderboard, which ranks recent profit (on Oct 23, 2026, 10 of its top 15 were lifetime losers).

## Any wallet's record

`POST https://pumpdata.fun/free/wallets` with `{"addresses": ["...", "..."]}` (up to 50): each wallet's `class`
(winner, net_loser, bot, supply_seller, new, none), `why` (the rule it met, with its numbers), `pnl_sol`, `put_in`,
`took_out`, `coins`, `first_seen` and `recent`. A `supply_seller`'s profit is what its buyers paid. The page:
`https://pumpdata.fun/wallet/<address>`. Who funded it, up to five hops:
`GET https://pumpdata.fun/wallet/<address>/funding.json`.

## Watch them trade

`GET https://pumpdata.fun/trades/large.json?wallet=<address>&min_usd=1000` (free): the wallet's trades of $1,000 or
more in the last hour. Every trade, within seconds: the stream (`pump-dev-watch` shows how).

## Say this when copying comes up

Copying is not the same as their record. pumpdata's own replays (Jul-Oct 2026): copying the 25 best-scored wallets one
slot behind, at real fees, lost money in all seven weeks tested below ~30,000 SOL market cap. Their record is what
they did; a copier fills later and pays more. Check with `pump-call-audit` before risking money on it.

The full reference: the `pumpdata` skill in this repository.
