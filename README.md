# pumpdata skills

pump.fun's whole on-chain history for coding agents and the command line: every pump.fun trade, ever, from [pumpdata.fun](https://pumpdata.fun).

Ask your agent "check this coin", "who are these buyers", "which wallets are worth copying" or "how often do coins at $20K reach 2x", and it answers from the chain's record instead of guessing:

- **the pre-buy check:** the deployer's record, the bundle in the first 10 seconds, whether the curve was bought whole at launch, the insiders' share, how launches like it went, and which skip rules fire
- **wallet classes:** winner, net loser, bot, supply seller or new, for up to 50 wallets at once, each with the reason
- **the wallet leaderboard:** wallets that win over their whole record and still trade, filtered to the ones a copier can keep up with
- **deployer records** and **base rates** for any market-cap band

Facts, not advice. Free with no key and no signup (30 calls every five minutes, 300 a day per IP); a free key from [pumpdata.fun/keys](https://pumpdata.fun/keys?utm_source=skills) gives 2,000 calls a day.

## Install

**Claude Code**, as a plugin (the skill), plus the MCP server:

```sh
/plugin marketplace add pumpdatafun/pumpdata-skills
/plugin install pumpdata@pumpdata
claude mcp add --transport http pumpdata https://pumpdata.fun/mcp
```

Or by hand: `git clone https://github.com/pumpdatafun/pumpdata-skills && cp -r pumpdata-skills/skills/pumpdata ~/.claude/skills/`.

**Cursor**, in `~/.cursor/mcp.json`:

```json
{ "mcpServers": { "pumpdata": { "url": "https://pumpdata.fun/mcp" } } }
```

**OpenClaw:** copy `skills/pumpdata` into `~/.openclaw/skills/`.

**Hermes:** `hermes skills install well-known:https://pumpdata.fun/.well-known/skills/pumpdata`

**OpenBB:** `pip install openbb-pumpdata`, then `obb.pumpdata.check(mint=...)`, `obb.pumpdata.deployer(address=...)` and seven more ([openbb-pumpdata](https://github.com/pumpdatafun/openbb-pumpdata)).

**Vibe-Trading** (HKUDS), in `~/.vibe-trading/agent.json`, read-only tools only:

```json
{ "mcpServers": { "pumpdata": {
    "type": "streamableHttp",
    "url": "https://pumpdata.fun/mcp",
    "enabledTools": ["check_coin", "launch_record", "similar_launches", "deployer_record", "wallet_records", "top_wallets", "base_rate", "find_coin", "stats"]
} } }
```

Add `"headers": { "x-api-key": "pdk_..." }` with a free key from [pumpdata.fun/keys](https://pumpdata.fun/keys?utm_source=skills) for 2,000 calls a day. The paid `replay` tool is left out of that list on purpose.

**TradingAgents:** five pump.fun tools for its analysts, point-in-time like its own: [examples/tradingagents](examples/tradingagents).

**Any other agent:** point it at [pumpdata.fun/skill.md](https://pumpdata.fun/skill.md), [pumpdata.fun/llms.txt](https://pumpdata.fun/llms.txt) or the [OpenAPI spec](https://pumpdata.fun/openapi.json).

## The CLI

No install, no dependencies, Node 18 or newer:

```sh
npx github:pumpdatafun/pumpdata-skills check <mint>
```

```
pumpdata check <mint>                   the pre-buy check: findings, flags, rules_say
pumpdata launch <mint>                  a launch's record (deployer, bundle, insiders, look-alikes)
pumpdata deployer <address>             a deployer's launches and how they went
pumpdata wallets <address> [...]        each wallet's class, why, PnL and pace (up to 50)
pumpdata top [--followable] [--limit N] the wallet leaderboard
pumpdata similar <mint>                 the launches most like this one, and what each did next
pumpdata baserate <band> [days]         how often coins in a band reached 2x/5x/10x/20x (e.g. 15k-28k 7)
pumpdata stats [YYYY-MM-DD]             a day on pump.fun (yesterday by default)
pumpdata status                         how fresh each layer of the data is right now
```

Add `--json` to any command for the raw answer, which is what an agent should read. Set `PUMPDATA_KEY` to use a key.

```
$ pumpdata check 9cRCn9rGT8V2imeM2BaKs13yhMEais3ruM3rPvTGpump
...
Flags: bundled (2 wallets bought 79.3% of the supply in the first 10 seconds); insiders (the deployer and its first buyers hold 79.3% of the supply)
Rules say: skip. Page: https://pumpdata.fun/check/9cRCn9rGT8V2imeM2BaKs13yhMEais3ruM3rPvTGpump

$ pumpdata top --followable --limit 3
333 wallets a copier can follow; the first 3:
#9     DfMxre4cKmvogbLrPigxmibVTTQDuzjdXojWzjCXXhzj    24,481.3 SOL  29202 coins, 13.8 trades/day, holds 247 s
...
```

## How the numbers are made

[pumpdata.fun/methodology](https://pumpdata.fun/methodology) says how each field is built (every record about a launch counts only what happened before it, so a backtest on them has no lookahead), and [pumpdata.fun/status](https://pumpdata.fun/status) shows how fresh each layer is right now.

MIT licensed. Questions: support@pumpdata.fun.
