#!/usr/bin/env python3
"""Foundation0 Discord hub setup (see HUB.md).

Creates the hub's roles, categories, channels and the race-feed webhook in an
existing Discord server. Idempotent: anything that already exists by name is
left alone, so re-running is safe. Never deletes.

Role colours follow the site: gold (--bio) for people, cyan (--dig) for agents.
Function roles (Steward, Verifier) carry no colour, so a name always shows
which strand it belongs to.

Env:
  DISCORD_BOT_TOKEN  bot token (bot must be in the server with Manage Roles,
                     Manage Channels, Manage Webhooks, View Channels, Send Messages)
  DISCORD_GUILD_ID   the server's ID

Usage:
  python3 scripts/discord_setup.py --dry-run   # print the plan, no network
  python3 scripts/discord_setup.py             # apply; prints the webhook URL once

stdlib only.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://discord.com/api/v10"
UA = "DiscordBot (https://github.com/Foundation-0/f0, 1)"

SEND_MESSAGES = 1 << 11
CATEGORY, TEXT = 4, 0
GOLD, CYAN = 0xE6B874, 0x5CCFEC

ROLES = [
    {"name": "Steward", "color": 0, "hoist": True},
    {"name": "Founding Member", "color": GOLD, "hoist": True},
    {"name": "Verifier", "color": 0, "hoist": True},
    {"name": "Agent", "color": CYAN, "hoist": True},
    {"name": "Member", "color": GOLD, "hoist": False},
]

# readonly: only Steward (and the webhook) can post.
LAYOUT = [
    ("Start", [
        ("start-here", "Foundation0: an open, sourced record of what people and digital intelligence advance together. Site: https://foundation-0.github.io/f0/", True),
        ("announcements", "Verified results, new ledger milestones, rule changes.", True),
        ("introductions", "Who you are, what you work on, and which agents work with you.", False),
    ]),
    ("Ledger", [
        ("ledger", "Propose and discuss ledger entries. Proposals become GitHub issues.", False),
        ("corrections", "A wrong date, credit, number or claim. Corrections are made in public.", False),
    ]),
    ("Research", [
        ("research", "The founding members' research and the work we contribute to.", False),
        ("race-feed", "Automated: new or changed κ claims in the integer-multiplication race. Claimed is not verified.", True),
        ("kappa-race", "Discussion of the integer-multiplication κ race.", False),
        ("claims-review", "Independent checking of claimed results. Propose freely, verify strictly.", False),
    ]),
    ("Tools", [
        ("instruments", "Harnesses for working with AI at the level of a lab.", False),
        ("commons", "Free public-benefit tools.", False),
    ]),
    ("Build", [
        ("site-dev", "The f0 site, data and pipelines. Bugs and changes.", False),
        ("agent-desk", "Members' agents coordinating in the open. Every agent here carries the Agent role and names its member.", False),
    ]),
]

WEBHOOK_CHANNEL = "race-feed"
WEBHOOK_NAME = "f0 race feed"


def call(token, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    for _ in range(5):
        req = urllib.request.Request(API + path, data=data, method=method, headers={
            "Authorization": "Bot " + token,
            "User-Agent": UA,
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req) as r:
                raw = r.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(float(json.loads(e.read()).get("retry_after", 1)) + 0.1)
                continue
            sys.exit(f"{method} {path} -> {e.code}: {e.read().decode(errors='replace')}")
    sys.exit(f"{method} {path}: rate limited 5 times, giving up")


def readonly_overwrites(guild_id, steward_id):
    # @everyone's role id is the guild id.
    ow = [{"id": guild_id, "type": 0, "allow": "0", "deny": str(SEND_MESSAGES)}]
    if steward_id:
        ow.append({"id": steward_id, "type": 0, "allow": str(SEND_MESSAGES), "deny": "0"})
    return ow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        print("roles:", ", ".join(r["name"] for r in ROLES))
        for cat, chans in LAYOUT:
            print(f"[{cat}]")
            for name, topic, ro in chans:
                print(f"  #{name}{' (read-only)' if ro else ''}: {topic}")
        print(f"webhook: '{WEBHOOK_NAME}' in #{WEBHOOK_CHANNEL}")
        return

    token = os.environ.get("DISCORD_BOT_TOKEN")
    guild = os.environ.get("DISCORD_GUILD_ID")
    if not token or not guild:
        sys.exit("set DISCORD_BOT_TOKEN and DISCORD_GUILD_ID")

    roles = {r["name"]: r["id"] for r in call(token, "GET", f"/guilds/{guild}/roles")}
    for r in ROLES:
        if r["name"] in roles:
            print(f"role {r['name']}: exists")
        else:
            roles[r["name"]] = call(token, "POST", f"/guilds/{guild}/roles", {**r, "mentionable": False})["id"]
            print(f"role {r['name']}: created")

    existing = call(token, "GET", f"/guilds/{guild}/channels")
    cats = {c["name"]: c["id"] for c in existing if c["type"] == CATEGORY}
    texts = {c["name"]: c["id"] for c in existing if c["type"] == TEXT}

    for cat, chans in LAYOUT:
        if cat not in cats:
            cats[cat] = call(token, "POST", f"/guilds/{guild}/channels", {"name": cat, "type": CATEGORY})["id"]
            print(f"category {cat}: created")
        for name, topic, ro in chans:
            if name in texts:
                print(f"#{name}: exists")
                continue
            body = {"name": name, "type": TEXT, "topic": topic, "parent_id": cats[cat]}
            if ro:
                body["permission_overwrites"] = readonly_overwrites(guild, roles.get("Steward"))
            texts[name] = call(token, "POST", f"/guilds/{guild}/channels", body)["id"]
            print(f"#{name}: created")

    ch = texts[WEBHOOK_CHANNEL]
    hooks = [h for h in call(token, "GET", f"/channels/{ch}/webhooks") if h.get("name") == WEBHOOK_NAME]
    if hooks:
        print(f"webhook in #{WEBHOOK_CHANNEL}: exists (URL not reprinted)")
    else:
        h = call(token, "POST", f"/channels/{ch}/webhooks", {"name": WEBHOOK_NAME})
        # Printed once; store it as the DISCORD_WEBHOOK_URL repo secret, never commit it.
        print(f"webhook in #{WEBHOOK_CHANNEL}: created")
        print(f"DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/{h['id']}/{h['token']}")


if __name__ == "__main__":
    main()
