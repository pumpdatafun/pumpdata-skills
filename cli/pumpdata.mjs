#!/usr/bin/env node
// pumpdata: pump.fun's whole on-chain history from the command line, for people and for coding agents.
// Free with no key (30 calls every five minutes, 300 a day per IP); set PUMPDATA_KEY to a free key from
// https://pumpdata.fun/keys for 2,000 calls and 2,000 wallet lookups a day. No dependencies; Node 18 or newer.
//
//   pumpdata check <mint>                  the pre-buy check: findings, flags, rules_say
//   pumpdata launch <mint>                 a launch's record (deployer, bundle, insiders, look-alikes)
//   pumpdata deployer <address>            a deployer's launches and how they went
//   pumpdata wallets <address> [...]       each wallet's class, why, PnL and pace (up to 50)
//   pumpdata top [--followable] [--limit N] the wallet leaderboard: whole-record winners that still trade
//   pumpdata similar <mint>                the launches most like this one, and what each did next
//   pumpdata baserate <band> [days]        how often coins in a market-cap band reached 2x/5x/10x/20x (e.g. 15k-28k 7)
//   pumpdata stats [YYYY-MM-DD]            a day on pump.fun (yesterday by default)
//   pumpdata status                        how fresh each layer of the data is right now
//
// Add --json to any command for the raw answer. Every answer is a count or a rule over the chain's record, not advice.

import { readFileSync } from "node:fs";

const SITE = process.env.PUMPDATA_URL || "https://pumpdata.fun";
const KEY = process.env.PUMPDATA_KEY || "";
const args = process.argv.slice(2);
const flag = (name) => args.includes(name);
const opt = (name, dflt) => { const i = args.indexOf(name); return i >= 0 && args[i + 1] ? args[i + 1] : dflt; };
const pos = args.filter((a, i) => !a.startsWith("--") && args[i - 1] !== "--limit");
const [cmd, ...rest] = pos;
const asJson = flag("--json");
const MINT = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;
// answered free for everyone, key or not; the rest go to /free/<path> without a key and to <path> with one
const OPEN = ["/check/", "/wallets/top", "/stats", "/status"];

function usage(code = 0) {
  const lines = readFileSync(new URL(import.meta.url), "utf8").split("\n").filter((l) => l.startsWith("//   pumpdata")).map((l) => l.slice(5));
  console.log("pumpdata: pump.fun's whole on-chain history from the command line\n\n" + lines.join("\n") + "\n\nPUMPDATA_KEY: a free key from https://pumpdata.fun/keys (optional). Add --json for raw answers.");
  process.exit(code);
}

async function call(path, init = {}) {
  const open = OPEN.some((p) => path.startsWith(p));
  const keyed = !!KEY && !open;
  const url = SITE + (open || keyed ? path : "/free" + path);
  const headers = { accept: "application/json", "user-agent": "pdcli/1.0 (+https://github.com/pumpdatafun/pumpdata-skills)", ...(init.body ? { "content-type": "application/json" } : {}), ...(keyed ? { "x-api-key": KEY } : {}) };
  const res = await fetch(url, { ...init, headers });
  const text = await res.text();
  let body;
  try { body = JSON.parse(text); } catch { body = { raw: text.slice(0, 500) }; }
  if (!res.ok) {
    const why = body.why || body.error || `HTTP ${res.status}`;
    const reset = res.headers.get("retry-after");
    console.error(`pumpdata: ${res.status}: ${typeof why === "string" ? why : JSON.stringify(why)}${reset ? ` (retry in ${reset} s)` : ""}`);
    if (res.status === 402 || res.status === 429) console.error(KEY ? "More: https://pumpdata.fun/keys" : "A free key has its own allowance: https://pumpdata.fun/keys (then PUMPDATA_KEY=...)");
    process.exit(1);
  }
  return body;
}

const out = (o) => console.log(JSON.stringify(o, null, 2));
const pct = (x, d = 1) => (typeof x === "number" ? `${(x * 100).toFixed(d)}%` : "n/a");
const sol = (x) => (typeof x === "number" ? `${x.toLocaleString("en-US", { maximumFractionDigits: 1 })} SOL` : "n/a");

async function main() {
  if (!cmd || flag("--help") || cmd === "help") usage(0);
  switch (cmd) {
    case "check": {
      const [m] = rest; if (!MINT.test(m || "")) usage(2);
      const j = await call(`/check/${m}.json`);
      if (asJson) return out(j);
      console.log(j.answer.join("\n\n"));
      console.log(`\nFlags: ${j.flags.length ? j.flags.map((f) => `${f.flag} (${f.says})`).join("; ") : "none"}`);
      console.log(`Rules say: ${j.rules_say}. Page: ${j.page}`);
      return;
    }
    case "launch": case "similar": {
      const [m] = rest; if (!MINT.test(m || "")) usage(2);
      return out(await call(`/${cmd}/${m}`));
    }
    case "deployer": {
      const [a] = rest; if (!MINT.test(a || "")) usage(2);
      return out(await call(`/deployer/${a}`));
    }
    case "wallets": {
      const addrs = rest.filter((a) => MINT.test(a)).slice(0, 50); if (!addrs.length) usage(2);
      const j = await call("/wallets", { method: "POST", body: JSON.stringify({ addresses: addrs }) });
      if (asJson) return out(j);
      for (const [a, w] of Object.entries(j)) {
        if (!w || typeof w !== "object" || !("class" in w)) continue;
        const r = w.recent || {};
        console.log(`${a}  ${String(w.class).padEnd(13)} ${sol(w.pnl_sol).padStart(14)}  ${w.coins} coins${r.median_hold_s != null ? `, holds ${Math.round(r.median_hold_s)} s, ${r.trades_per_day} trades/day` : ""}\n    ${w.why || ""}`);
      }
      return;
    }
    case "top": {
      const qs = new URLSearchParams({ limit: opt("--limit", "25") });
      if (flag("--followable")) qs.set("followable", "1");
      const j = await call(`/wallets/top?${qs}`);
      if (asJson) return out(j);
      console.log(`${j.total} wallets${j.followable_only ? " a copier can follow" : ""}; the first ${j.wallets.length}:`);
      for (const w of j.wallets) console.log(`#${String(w.rank).padEnd(5)} ${w.address}  ${sol(w.pnl_sol).padStart(14)}  ${w.coins} coins, ${w.recent?.trades_per_day ?? "?"} trades/day, holds ${w.recent?.median_hold_s ?? "?"} s`);
      return;
    }
    case "baserate": {
      const [band = "15k-28k", days = "1"] = rest;
      const to = new Date(); to.setUTCHours(0, 0, 0, 0);
      const from = new Date(to.getTime() - Number(days) * 86400_000);
      const j = await call(`/baserate?band=${encodeURIComponent(band)}&from=${from.toISOString().slice(0, 19)}Z&to=${to.toISOString().slice(0, 19)}Z&venue=any`);
      if (asJson) return out(j);
      const r = j.reached || {};
      console.log(`${j.crossed} coins crossed ${band} in the window; reached within 3 h: 2x ${pct(r["2x"])}, 5x ${pct(r["5x"])}, 10x ${pct(r["10x"])}, 20x ${pct(r["20x"])}; median peak ${j.median_peak}x`);
      return;
    }
    case "stats": {
      const [day] = rest;
      const j = await call(day ? `/stats/${day}.json` : "/stats.json");
      if (asJson) return out(j);
      console.log(j.summary || JSON.stringify(j.totals));
      return;
    }
    case "status": {
      const j = await call("/status.json");
      if (asJson) return out(j);
      console.log(`Overall: ${j.overall}`);
      for (const c of j.components) console.log(`  ${c.level.padEnd(5)} ${c.name}: ${c.as_of ?? "unknown"}`);
      return;
    }
    default:
      usage(2);
  }
}

main().catch((e) => { console.error(`pumpdata: ${e.message || e}`); process.exit(1); });
