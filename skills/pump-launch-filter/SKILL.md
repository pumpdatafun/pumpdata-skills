---
name: pump-launch-filter
description: "Watch every new pump.fun launch and keep only the ones that pass your rules: skip serial launchers, devs who sell fast, launches where a few wallets took most of the supply in the first 10 seconds. Filters thousands of Solana memecoin launches a day down to a short list for a sniper bot, alert channel or trading agent. Free, no key."
version: 1.0.0
author: pumpdatafun
tags: [pump.fun, solana, memecoin, new-launches, sniper, filter, screener, alerts, bot]
---

# Filter pump.fun launches as they happen

## The loop

1. Poll `GET https://pumpdata.fun/launches/since.json?t=<unix seconds>` every 20-60 s (no `t`: the last ten
   minutes), then again with `t = next_since`. Each row (`columns` names them) is one launch: `mint`, `created`,
   `creator`, `deployer_launches_before`, `deployer_graduations_before`, `deployer_gap_s`,
   `deployer_launches_last_day`, `buyers_first_10s`, `bundle_supply_share`, `source`. Keep each mint once.
2. Drop the launches your rules reject, from the row alone (no extra call). A starting rule set, to tune:
   - `deployer_launches_last_day` above 10, or `deployer_launches_before` above 50 with
     `deployer_graduations_before` 0: a serial launcher;
   - `bundle_supply_share` above 0.3: a few wallets took most of the supply in the first 10 seconds
     (`null` while `source` is `live`: decide again after the hourly fill, or call the check);
3. For the few left, call the pre-buy check: `GET https://pumpdata.fun/check/<mint>.json` (free), and keep the ones
   whose `rules_say` is not `skip`.
4. Hand the short list on (an alert, a channel, a human). With `min_launches=20` the feed returns only serial
   deployers' launches; with `deployer=<wallet>` one deployer's.

For seconds instead of a minute: the stream, `wss://pumpdata.fun/stream?key=<key>&types=create,record` (7-day free
trial on a free key); `record` is each new coin's deployer record a few seconds after its create.

## Check the rules before trusting them

How often coins like the ones you keep have paid: `GET https://pumpdata.fun/public/baserate.json` (free, yesterday,
by market-cap band). To test a rule on the past, collect what it would have picked with the time it decided and
replay them with `pump-call-audit` ($2 a run): fees, fills and the dead coins counted. Most launches die; a filter
that does not beat the base rate is not an edge.

## Rules

- Free: 30 calls every five minutes and 300 a day per IP; a free key (https://pumpdata.fun/keys) has no daily cap.
- Report the rule that kept or dropped a coin, with its numbers. Not advice.

The full reference: the `pumpdata` skill in this repository.
