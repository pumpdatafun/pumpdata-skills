# TradingAgents on pump.fun

[TradingAgents](https://github.com/TauricResearch/TradingAgents) has analysts, researchers, a trader and a risk team
argue before every trade. It reads stock and crypto exchange data. `pumpdata_tools.py` gives its analysts pump.fun's
on-chain record instead: who launched a coin, whether its first buyers took the whole curve, how launches like it went,
what the buyers have done before, and the base rate for a coin at its market cap.

## The tools

| Tool | Answers | Past trade dates |
|---|---|---|
| `get_pump_base_rate(band, look_back_days)` | Of the coins that crossed a market-cap band, the share that reached 2x, 5x, 10x, 20x within three hours | Yes: counts only crossings before the trade date |
| `get_pump_day_stats()` | The pump.fun market on the day before the trade date | Yes |
| `get_pump_coin_check(mint)` | The pre-buy check: deployer, bundle, insiders, look-alikes, flags | Today only |
| `get_pump_deployer(address)` | A deployer's whole record and how its last 90 days went | Today only |
| `get_pump_wallets(addresses)` | Each wallet's class (winner, net loser, bot, supply seller, new), its reason and PnL | Today only |

The last three describe the chain as it is now, so on a past `trade_date` they decline rather than leak the future into
a backtest, the same rule TradingAgents' own dated tools follow.

## Use

```bash
pip install langchain-core langgraph   # TradingAgents already has both
cp pumpdata_tools.py <your TradingAgents checkout>/
```

Add the tools to an analyst's tool list where your graph builds it, for example beside the market analyst's:

```python
from pumpdata_tools import PUMPDATA_TOOLS

market_tools = [get_stock_data, get_indicators, *PUMPDATA_TOOLS]
```

and tell that analyst in its prompt when to reach for them: "For a pump.fun coin, call get_pump_coin_check with its
mint, get_pump_deployer with its deployer, and get_pump_base_rate for its market-cap band before forming a view."

No key is needed (300 lookups a day per IP). `PUMPDATA_KEY` with a free key from
[pumpdata.fun/keys](https://pumpdata.fun/keys?utm_source=skills) gives 2,000 a day.

These are counts over the chain's record, not predictions or advice. How every field is made:
[pumpdata.fun/methodology](https://pumpdata.fun/methodology).
