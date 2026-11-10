---
name: pump-dev-watch
description: "Watch a pump.fun coin's dev (deployer) wallet: alert when the dev sells, and when the same dev launches a new coin. Use when holding or about to buy a pump.fun memecoin, or tracking a deployer, sniper or serial launcher on Solana. Free to start, no key."
version: 1.0.0
author: pumpdatafun
tags: [pump.fun, solana, memecoin, dev, deployer, dev-sold, rug, alerts, stream]
---

# Watch a pump.fun dev wallet

## 1. Find the dev and its record

`GET https://pumpdata.fun/free/launch/<mint>` (free, no key). Read `deployer.address`, and `deployer.launches`,
`deployer.graduations` and `deployer.now.own_coins` (how this deployer has traded its own coins lately: the share it
bought at launch, the share it was out of within 10 seconds, `net_sol`). A deployer with hundreds of launches and a
fast exit on its own coins is a serial launcher; say the numbers.

## 2. Watch for the dev selling

**Live, within seconds (the stream; 7-day free trial on a free key from https://pumpdata.fun/keys):**

```
POST https://pumpdata.fun/stream/trial            (header x-api-key: pdk_...; once)
wss://pumpdata.fun/stream?key=<key>&types=trade&mints=<mint>
```

Every message is one JSON event. Alert on `type == "trade"`, `wallet == <deployer>`, `side == "sell"`; report `sol`
and `token_amount`. Reconnect on close.

**Free, no key, by polling every 30-60 s:** `GET https://pumpdata.fun/trades/large.json?wallet=<deployer>&min_usd=1000`
lists the dev's trades of $1,000 or more in the last hour (`side`, `sol`, `usd`, `mint`, `at`). Smaller sells do not
show here; use the stream for those. CLI: `npx github:pumpdatafun/pumpdata-skills devwatch <mint>`.

## 3. Watch for the dev launching again

`GET https://pumpdata.fun/launches/since.json?deployer=<deployer>&t=<unix seconds>`: every new launch by that
wallet, with its record as of that launch; poll with `t = next_since`. With the stream, `types=create,record`
carries every create and the deployer's record a few seconds after it.

## Rules

- Report what the wallet did (sold 12.4 SOL of it at 14:05 UTC), not a verdict.
- A dev that sells is not always the end of a coin, and a dev that holds is not a promise. Pair it with the
  pre-buy check (`pump-prebuy-check`).
- Free polling: 30 calls every five minutes and 300 a day per IP; a free key has no daily cap.

The full reference: the `pumpdata` skill in this repository.
