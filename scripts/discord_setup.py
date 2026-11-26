#!/usr/bin/env python3
"""Foundation0 Discord hub setup (see HUB.md).

Creates the hub's roles, categories, channels and its two webhooks in an
existing Discord server. Idempotent: anything that already exists by name is
left alone, so re-running is safe. Never deletes.

Role colours follow the site: gold (--bio) for people, cyan (--dig) for agents.
Function roles (Steward, Verifier) carry no colour, so a name always shows
which strand it belongs to. Standing runs Contributor -> Verifier/Fellow;
Founding Member is held by founding only, not earned by standing (see HUB.md).

Env:
  DISCORD_BOT_TOKEN  bot token (bot must be in the server with Manage Roles,
                     Manage Channels, Manage Webhooks, View Channels, Send Messages,
                     Create Public Threads, Create Private Threads,
                     Send Messages in Threads)
  DISCORD_GUILD_ID   the server's ID

Usage:
  python3 scripts/discord_setup.py --dry-run   # print the plan, no network
  python3 scripts/discord_setup.py             # apply; prints each new webhook URL once

Run this once, on a person's own machine, never in a workflow or in CI:
it prints webhook URLs, which are secrets, and CI logs on a public
repository are public. The script refuses to run when CI or
GITHUB_ACTIONS is set. Keep the bot token in a password manager; no
workflow needs it. After setup, kick the bot or reset its token.

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
CREATE_PUBLIC_THREADS = 1 << 35
CREATE_PRIVATE_THREADS = 1 << 36
SEND_MESSAGES_IN_THREADS = 1 << 38
# Everything needed to post in a channel or in a thread under it. SEND_MESSAGES
# alone has no effect in threads, so a read-only channel must deny all four.
POST_BITS = SEND_MESSAGES | CREATE_PUBLIC_THREADS | CREATE_PRIVATE_THREADS | SEND_MESSAGES_IN_THREADS  # 377957124096
ANNOUNCEMENT, FORUM = 5, 15
CATEGORY, TEXT = 4, 0
# Channel types matched by name when checking what already exists.
KNOWN_CHANNEL_TYPES = (TEXT, ANNOUNCEMENT, FORUM)
GOLD, CYAN = 0xE6B874, 0x5CCFEC

# Role order, top to bottom, as the script leaves it: Agent sits above the
# gold roles (Founding Member, Fellow, Contributor), so an agent that also
# held a gold role would still show in cyan. See HUB.md, "How agents join".
ROLE_ORDER = ["Founding Member", "Steward", "Agent", "Fellow", "Verifier", "Contributor"]

# API v10 takes colors.primary_color; the flat `color` field is deprecated.
ROLES = [
    {"name": "Founding Member", "colors": {"primary_color": GOLD}, "hoist": True},   # held by founding only
    {"name": "Steward", "colors": {"primary_color": 0}, "hoist": True},
    {"name": "Fellow", "colors": {"primary_color": GOLD}, "hoist": True},            # earned by track record
    {"name": "Verifier", "colors": {"primary_color": 0}, "hoist": True},             # earned by a record of checks
    {"name": "Contributor", "colors": {"primary_color": GOLD}, "hoist": False},      # standard contributing member
    {"name": "Agent", "colors": {"primary_color": CYAN}, "hoist": True},
]

BOARD = ("Founding Member",)
STEWARD = ("Steward",)
OPEN = ()

# Third field: the roles that may post. OPEN means everyone; anything else makes
# the channel read-only for @everyone except those roles (and the webhook).
LAYOUT = [
    ("Start", [
        ("start-here", "Foundation0: an open, sourced record of what people and digital intelligence advance together. Site: https://fdn0.org/", STEWARD),
        ("announcements", "Verified results, new ledger milestones, rule changes. See also the forum's Announcements category.", STEWARD + BOARD),
        ("board-decisions", "Decisions of the founding members, with reasons. Each post links to the GitHub issue that records the decision. Public by design.", BOARD),
        ("introductions", "Who you are, what you work on, and which agents work with you. Intros live in the forum's Human intros and Agent intros categories.", OPEN),
    ]),
    ("Ledger", [
        ("ledger", "Propose and discuss ledger entries. Proposals live in the forum's Ledger category.", OPEN),
        ("corrections", "A wrong date, credit, number or claim. Corrections are made in public, in the forum's Ledger category.", OPEN),
    ]),
    ("Research", [
        ("research", "The founding members' research and the work we contribute to.", OPEN),
        ("race-feed", "Automated: new or changed κ claims in the integer-multiplication race. Claimed is not verified.", STEWARD),
        ("kappa-race", "Discussion of the integer-multiplication κ race.", OPEN),
        ("claims-review", "Independent checking of claimed results. Claims under check live in the forum's Claims review category. Propose freely, verify strictly.", OPEN),
        # One channel per field hub on GitHub; a hub's projects are discussed in its channel.
        ("math0", "Mathematics hub: https://github.com/Foundation-0/math0", OPEN),
        ("astr0", "Astronomy hub: https://github.com/Foundation-0/astr0", OPEN),
        ("physics0", "Physics and Earth science hub, including point-charges: https://github.com/Foundation-0/physics0", OPEN),
    ]),
    ("Tools", [
        ("instruments", "Harnesses for working with AI at the level of a lab.", OPEN),
        ("commons", "Free public-benefit tools.", OPEN),
    ]),
    ("Build", [
        ("site-dev", "The f0 site, data and pipelines. Bugs and changes.", OPEN),
        ("github", "Automated: pushes, pull requests, issues and releases across the Foundation-0 GitHub organisation.", STEWARD),
        ("agent-desk", "Members' agents coordinating in the open. Every agent here carries the Agent role and names its member.", OPEN),
    ]),
]

# (channel, webhook name, where its URL goes). Each URL is printed once and is a secret.
WEBHOOKS = [
    ("race-feed", "f0 race feed", "repository secret DISCORD_WEBHOOK_URL on Foundation-0/f0"),
    ("github", "Foundation-0 GitHub", "org Settings > Webhooks, with /github appended, content type application/json"),
]


def _retry_after_header(e):
    """Seconds from a Retry-After header, defaulting to 1 on anything odd."""
    try:
        return float(e.headers.get("Retry-After", 1))
    except (TypeError, ValueError):
        return 1.0


def call(token, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    tries_5xx = 0
    for _ in range(5):
        req = urllib.request.Request(API + path, data=data, method=method, headers={
            "Authorization": "Bot " + token,
            "User-Agent": UA,
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try:
                    retry_after = float(json.loads(e.read()).get("retry_after", 1))
                except ValueError:
                    # A rate limit with a non-JSON body (Cloudflare returns
                    # HTML for some): fall back to the Retry-After header.
                    retry_after = _retry_after_header(e)
                time.sleep(retry_after + 0.1)
                continue
            if e.code in (502, 503, 504) and tries_5xx < 2:
                tries_5xx += 1
                time.sleep(_retry_after_header(e))
                continue
            sys.exit(f"{method} {path} -> {e.code}: {e.read().decode(errors='replace')}")
    sys.exit(f"{method} {path}: rate limited 5 times, giving up")


def readonly_overwrites(guild_id, poster_ids):
    # @everyone's role id is the guild id.
    ow = [{"id": guild_id, "type": 0, "allow": "0", "deny": str(POST_BITS)}]
    for rid in poster_ids:
        ow.append({"id": rid, "type": 0, "allow": str(POST_BITS), "deny": "0"})
    return ow


def main():
    # A webhook URL is a credential, and CI logs on a public repository are
    # public. Refuse to run at all under CI, before any network call, so the
    # script can never print a webhook URL into a log. Run it once, on a
    # person's own machine.
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        sys.exit("refusing to run under CI: run this once on your own machine, "
                 "never in a workflow (it prints webhook URLs)")

    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        print("roles:", ", ".join(r["name"] for r in ROLES))
        print("role order, top to bottom:", ", ".join(ROLE_ORDER))
        for cat, chans in LAYOUT:
            print(f"[{cat}]")
            for name, topic, posters in chans:
                who = f" (posts: {', '.join(posters)})" if posters else ""
                print(f"  #{name}{who}: {topic}")
        for ch, name, _ in WEBHOOKS:
            print(f"webhook: '{name}' in #{ch}")
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
            # "permissions": "0": a new role otherwise copies @everyone's.
            roles[r["name"]] = call(token, "POST", f"/guilds/{guild}/roles",
                                     {**r, "mentionable": False, "permissions": "0"})["id"]
            print(f"role {r['name']}: created")
    # Place Agent above the gold roles (see ROLE_ORDER). A role's display
    # colour is its highest hoisted role's, so this keeps agents cyan.
    call(token, "PATCH", f"/guilds/{guild}/roles",
         [{"id": roles[name], "position": len(ROLE_ORDER) - i}
          for i, name in enumerate(ROLE_ORDER)])
    print("roles: order set (" + ", ".join(ROLE_ORDER) + ")")

    existing = call(token, "GET", f"/guilds/{guild}/channels")
    cats = {c["name"]: c["id"] for c in existing if c["type"] == CATEGORY}
    # Match by name across text (0), announcement (5) and forum (15): a
    # channel converted to another type must not be duplicated on re-run.
    texts = {c["name"]: c for c in existing if c["type"] in KNOWN_CHANNEL_TYPES}

    for cat, chans in LAYOUT:
        if cat not in cats:
            cats[cat] = call(token, "POST", f"/guilds/{guild}/channels", {"name": cat, "type": CATEGORY})["id"]
            print(f"category {cat}: created")
        else:
            print(f"category {cat}: exists")
        for name, topic, posters in chans:
            if name in texts:
                ch = texts[name]
                print(f"#{name}: exists")
                if ch.get("parent_id") != cats[cat]:
                    print(f"  WARNING: #{name} is not under category {cat}; move it by hand")
                if posters:
                    want = {(o["id"], o["type"], o["allow"], o["deny"])
                            for o in readonly_overwrites(guild, [roles[p] for p in posters])}
                    have = {(o["id"], o["type"], o["allow"], o["deny"])
                            for o in ch.get("permission_overwrites", [])}
                    if want != have:
                        print(f"  WARNING: #{name} lacks the read-only overwrites; "
                              f"fix them by hand before trusting it read-only")
                continue
            body = {"name": name, "type": TEXT, "topic": topic, "parent_id": cats[cat]}
            if posters:
                body["permission_overwrites"] = readonly_overwrites(guild, [roles[p] for p in posters])
            texts[name] = {"id": call(token, "POST", f"/guilds/{guild}/channels", body)["id"]}
            print(f"#{name}: created")

    for chan, name, dest in WEBHOOKS:
        ch = texts[chan]["id"]
        if any(h.get("name") == name for h in call(token, "GET", f"/channels/{ch}/webhooks")):
            print(f"webhook in #{chan}: exists (URL not reprinted; to recover it, "
                  f"delete the webhook in Discord and re-run)")
            continue
        h = call(token, "POST", f"/channels/{ch}/webhooks", {"name": name})
        # Printed once; it goes only to the place named, never into a commit, chat or log.
        print(f"webhook in #{chan}: created; store it in {dest}")
        print(f"  https://discord.com/api/webhooks/{h['id']}/{h['token']}")


if __name__ == "__main__":
    main()
