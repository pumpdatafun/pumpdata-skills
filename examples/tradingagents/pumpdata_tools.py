"""pump.fun tools for TradingAgents (https://github.com/TauricResearch/TradingAgents), from pumpdata.fun.

Drop this file next to your graph and add the tools to an analyst's tool list (see README.md here). Each tool follows
TradingAgents' rule for dated tools: it takes the run's `trade_date` from graph state and never answers with data from
after it.

- `get_pump_base_rate` and `get_pump_day_stats` honour any trade_date: a base rate is read over a window that ends
  before it, and the day's stats are the day before it.
- `get_pump_coin_check`, `get_pump_deployer` and `get_pump_wallets` describe the chain as it is now (a deployer's
  record counts every launch to date). They answer only when trade_date is today; on a past trade_date they say so
  instead of leaking the future into a backtest.

No key is needed (pumpdata.fun's free tier: 300 lookups a day per IP). Set PUMPDATA_KEY to a free key from
https://pumpdata.fun/keys?utm_source=skills for 2,000 a day. Standard library HTTP only.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

BASE = os.environ.get("PUMPDATA_URL", "https://pumpdata.fun")
KEY = os.environ.get("PUMPDATA_KEY", "")
UA = "tradingagents-pumpdata/0.1 (+https://github.com/pumpdatafun/pumpdata-skills)"
OPEN = ("/check/", "/wallets/top", "/stats")  # free for everyone, key or not


def _call(path: str, body: dict | None = None) -> dict:
    """GET (or POST with a JSON body) a pumpdata.fun path: /free/<path> without a key, <path> with one."""
    keyed = bool(KEY) and not path.startswith(OPEN)
    url = BASE + (path if path.startswith(OPEN) or keyed else "/free" + path)
    headers = {"accept": "application/json", "user-agent": UA}
    if keyed:
        headers["x-api-key"] = KEY
    data = None
    if body is not None:
        headers["content-type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            why = json.loads(e.read()).get("error")
        except Exception:  # noqa: BLE001
            why = None
        raise RuntimeError(f"pumpdata.fun {e.code}: {why or e.reason}") from None


def _day(trade_date: str) -> date:
    return datetime.strptime(trade_date[:10], "%Y-%m-%d").date() if trade_date else datetime.now(timezone.utc).date()


def _now_only(trade_date: str) -> str | None:
    """None when trade_date is today (UTC); otherwise the reason a 'now' tool will not answer."""
    if _day(trade_date) >= datetime.now(timezone.utc).date():
        return None
    return (
        f"Not available for trade_date {trade_date}: this tool describes the chain as it is now, so answering for a "
        "past date would use information from after it. Use get_pump_base_rate or get_pump_day_stats, which honour "
        "any trade_date."
    )


def _pct(x) -> str:
    return f"{x * 100:.1f}%" if isinstance(x, (int, float)) else "n/a"


@tool
def get_pump_base_rate(
    band: Annotated[str, "Market-cap band in USD, e.g. '15k-28k', '28k-40k', '40k-60k', '60k-100k', '100k-250k'"] = "15k-28k",
    look_back_days: Annotated[int, "How many days before the trade date to count"] = 4,
    trade_date: Annotated[str, InjectedState("trade_date")] = "",
) -> str:
    """Of the pump.fun coins that crossed a market-cap band, the share that went on to 2x, 5x, 10x and 20x within three
    hours: the base rate to weigh any single pump.fun call against. Counts only crossings before the trade date."""
    end = min(
        datetime.combine(_day(trade_date), datetime.min.time(), tzinfo=timezone.utc),
        datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=3),
    )
    start = end - timedelta(days=max(1, min(int(look_back_days), 30)))
    f = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: E731
    try:
        j = _call(f"/baserate?band={band}&from={f(start)}&to={f(end)}&venue=any")
    except RuntimeError as e:
        return str(e)
    r = j.get("reached") or {}
    return (
        f"pump.fun base rate, band ${band}, {f(start)} to {f(end)}: {j.get('crossed')} coins crossed it; "
        f"within 3 h {_pct(r.get('2x'))} reached 2x, {_pct(r.get('5x'))} 5x, {_pct(r.get('10x'))} 10x, "
        f"{_pct(r.get('20x'))} 20x; median peak {j.get('median_peak')}x. Every coin counted, dead ones included."
    )


@tool
def get_pump_day_stats(trade_date: Annotated[str, InjectedState("trade_date")] = "") -> str:
    """The pump.fun market on the UTC day before the trade date: coins launched and graduated, SOL traded, and how
    many traders ended up or down."""
    day = _day(trade_date) - timedelta(days=1)
    try:
        j = _call(f"/stats/{day.isoformat()}.json")
    except RuntimeError as e:
        return str(e)
    return j.get("summary") or j.get("headline") or json.dumps(j.get("totals"))


@tool
def get_pump_coin_check(
    mint: Annotated[str, "The pump.fun coin's mint address"],
    trade_date: Annotated[str, InjectedState("trade_date")] = "",
) -> str:
    """The pre-buy check for a pump.fun coin: who launched it and their record, whether the first buyers took the
    whole curve, the insiders' share, how launches like it went, and the flags. As of now: today's trade date only."""
    if why := _now_only(trade_date):
        return why
    try:
        j = _call(f"/check/{mint}.json")
    except RuntimeError as e:
        return str(e)
    flags = ", ".join(f.get("flag", "") for f in j.get("flags") or []) or "none"
    answer = " ".join(j.get("answer") or [])
    return f"{answer}\nFlags: {flags}. The check's rules say: {j.get('rules_say')} (a rule over the record, not advice)."


@tool
def get_pump_deployer(
    address: Annotated[str, "The deployer's wallet address"],
    trade_date: Annotated[str, InjectedState("trade_date")] = "",
) -> str:
    """A pump.fun deployer's whole record: launches, graduations, how its last 90 days of launches did, and the base
    rate for its next launch. As of now: today's trade date only."""
    if why := _now_only(trade_date):
        return why
    try:
        j = _call(f"/deployer/{address}")
    except RuntimeError as e:
        return str(e)
    r, w = j.get("record") or {}, j.get("last_90_days") or {}
    return (
        f"Deployer {address}: {r.get('launches')} launches, {r.get('graduations')} graduated "
        f"({_pct(r.get('graduation_rate'))}); best first-day peak ${r.get('best_peak_usd')}. Last 90 days: "
        f"{w.get('launches_measured')} measured, {_pct(w.get('doubled_share'))} doubled, {_pct(w.get('ten_x_share'))} "
        f"did 10x, {_pct(w.get('dead_share'))} dead the next day."
    )


@tool
def get_pump_wallets(
    addresses: Annotated[str, "Up to 50 wallet addresses, comma-separated"],
    trade_date: Annotated[str, InjectedState("trade_date")] = "",
) -> str:
    """What wallets did on pump.fun over their whole record: winner, net loser, bot, supply seller, new or none, with
    the reason and PnL in SOL. As of now: today's trade date only."""
    if why := _now_only(trade_date):
        return why
    addrs = [a.strip() for a in addresses.split(",") if a.strip()][:50]
    try:
        j = _call("/wallets", {"addresses": addrs})
    except RuntimeError as e:
        return str(e)
    lines = []
    for a in addrs:
        w = j.get(a) or {}
        lines.append(f"{a}: {w.get('class')} ({w.get('why')}); PnL {w.get('pnl_sol')} SOL over {w.get('coins')} coins")
    return "\n".join(lines)


PUMPDATA_TOOLS = [get_pump_base_rate, get_pump_day_stats, get_pump_coin_check, get_pump_deployer, get_pump_wallets]
