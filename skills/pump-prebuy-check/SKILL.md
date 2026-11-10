---
name: pump-prebuy-check
description: "One call before you ape a pump.fun coin: the dev's record, how much the first-10-second buyers took, whether the whole curve was bought at launch, insiders' share, look-alike launches and how they went, plus live holders, price impact and volume-bot checks. Rug check and dev check for Solana memecoins from a contract address (CA). Free, no key."
version: 1.0.0
author: pumpdatafun
tags: [pump.fun, solana, memecoin, rug-check, dev-check, ca, pre-buy, sniper, holders]
---

# The pre-buy check for a pump.fun coin

Given a contract address (the mint, usually ending in `pump`):

```sh
curl -s https://pumpdata.fun/check/<mint>.json        # free, no key
curl -s https://pumpdata.fun/now/<mint>.json          # the coin right now, free (cached 10 s)
```

Or: `npx github:pumpdatafun/pumpdata-skills check <mint>`.

## Read it in this order

1. `answer`: the findings as sentences. Quote them.
2. `flags`, each with a sentence: `serial_launcher`, `deployer_sells_fast`, `never_ran`, `curve_bought_at_launch`
   (one or two wallets bought the whole curve as it launched), `early_concentration` (a few wallets took a large share
   in the first 10 seconds), `one_wallet_bought`, `insiders`, `sold_together`, `lookalikes_die`.
3. `rules_say`: what the published skip rules say (`skip` or not). It is a rule's result, not advice.
4. From `/now`: `checks`, each `{id, mark: ok|warn|bad|info, what, says}`: the biggest holder, the top 10 holders,
   volume against market cap, fees paid, buy and sell sizes, trades a second, volume bots, off its high. Quote the
   rule with the mark. `price_impact` says what a 0.1, 0.5 or 1 SOL buy moves the price.

## Rules

- State the measured shape ("2 wallets bought 79% of the supply in the first 10 seconds"), never "bundled" or "safe".
- A fresh launch may be `not_built_yet` for the deep record; the live checks still answer. Retry the record later.
- Buyers' records (are they winners, bots, supply sellers?): `POST https://pumpdata.fun/free/wallets`
  `{"addresses": [...], "mint": "<mint>"}`, up to 50.
- Buying is the person's call. If they ask to buy, `GET /buy/<mint>.json` quotes it and `POST /buy` builds a trade
  their own wallet signs (0.4% fee inside it); never sign for them.

The full reference: the `pumpdata` skill in this repository.
