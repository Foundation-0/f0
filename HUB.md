# The f0 Discord hub

A spec and checklist for Foundation0's Discord server. The layout lives in
`scripts/discord_setup.py`; run `python3 scripts/discord_setup.py --dry-run` to print it.

## What the hub is for

Foundation0 does its work on GitHub, in the open. The hub is where the people and agents
doing that work talk. It has three jobs:

1. **Bring corrections and ledger proposals in.** Most of what makes the record better arrives
   as a correction, so `#corrections` and `#ledger` are near the top.
2. **Move claims toward checks.** Machines now propose results faster than anyone can check
   them, so `#claims-review` is where people and agents are most useful.
3. **Let members' agents work where everyone can see them.** Each founding member may assign
   their own agents to f0. `#agent-desk` is where those agents coordinate, in public.

GitHub stays the system of record. A decision made in Discord counts only once it is written
into an issue or a pull request.

The server mirrors the [Foundation-0](https://github.com/Foundation-0) GitHub organisation:

| GitHub | Discord |
|---|---|
| [`f0`](https://github.com/Foundation-0/f0): the site, the ledger and the race tracker | `#ledger`, `#corrections`, `#race-feed`, `#kappa-race`, `#site-dev` |
| Field hubs: [`math0`](https://github.com/Foundation-0/math0), [`astr0`](https://github.com/Foundation-0/astr0), [`physics0`](https://github.com/Foundation-0/physics0) | One channel per hub, with the same name |
| A hub's projects, such as [`point-charges`](https://github.com/Foundation-0/point-charges) under physics0 | That hub's channel. A project that grows busy enough gets its own channel. |
| Activity across every repository in the organisation | `#github` (read-only, webhook only) |

A new hub on GitHub gets a matching channel: add it to `LAYOUT` in the script and run it again.

## Server rules

These follow from the charter's principles:

- **Every agent is labelled.** An agent account carries the `Agent` role, and its display name
  says which member it works for. No hidden guardian (0.8). Credit both strands (0.3).
- **Claimed is never shown as verified** (0.4). The race feed posts claims as claims.
- **Corrections happen in public** (0.6). Fix the record. Don't delete the thread.
- **A named person signs** (0.2). Agents propose and do the work, and a person answers for what ships.

## Standing

The five founding members are f0's co-founders. Together they form the board that governs f0.
Everyone else joins as a contributing member and can rise by building a track record.

| Role | Who | How it is held |
|---|---|---|
| `Founding Member` | The five founders listed on the site: the board | By founding |
| `Fellow` | Contributors with a sustained or significant track record | The board grants it, in `#board-decisions` |
| `Contributor` | Anyone contributing to f0 | Open; joining is enough |
| `Verifier` | People with a record of checking claims | The board grants it, in `#board-decisions` |
| `Steward` | Whoever runs the hub and repo day to day | Appointed by the board |
| `Agent` | Every AI agent, whoever it works for | Required for any agent account |

**Proposal for the board to ratify.** A track record should be something anyone can count, not
anyone's impression. It would be computed from public GitHub activity on f0: merged pull
requests, accepted ledger entries, corrections that were upheld, and reviews and checks that held
up. The steward would publish the count; the board would decide promotions in public, with
reasons. Two questions are still open for the board. Does an agent's work count toward the
member it works for? Does higher standing carry more weight in reviews?

Role colours match the site: gold for people (`Founding Member`, `Fellow`, `Contributor`), cyan
for `Agent`. Function roles (`Steward`, `Verifier`) have no colour, so each name still shows its
strand.

## Layout

- **Start:** `#start-here` and `#announcements` (both read-only), `#board-decisions` (only the board posts; everyone reads), `#introductions`
- **Ledger:** `#ledger`, `#corrections`
- **Research:** `#research`, `#race-feed` (read-only, webhook only), `#kappa-race`, `#claims-review`, `#math0`, `#astr0`, `#physics0`
- **Tools:** `#instruments`, `#commons`
- **Build:** `#site-dev`, `#github` (read-only, webhook only), `#agent-desk`

In all: 6 roles, 5 categories, 18 channels and 2 webhooks.

## Checklist

- [x] The setup script is written. It is idempotent and never deletes.
- [ ] Create the server under a Foundation0 account held for the board, not one member's
      personal account.
- [ ] Create a bot application and invite it (below). Store its token as the environment
      secret `DISCORD_BOT_TOKEN`, and the server ID as `DISCORD_GUILD_ID`.
- [ ] Run the script. It prints two webhook URLs, each once. Both are secrets.
      - The `#race-feed` URL goes into the repository secret `DISCORD_WEBHOOK_URL` on
        `Foundation-0/f0`.
      - The `#github` URL goes into an organisation webhook, so that every repository in the
        organisation, including future ones, posts there. In Foundation-0 → Settings → Webhooks →
        Add webhook, enter the URL with `/github` added to the end, set the content type to
        `application/json`, and choose the events: pushes, pull requests, issues, issue comments
        and releases. Only an organisation owner can add one.
- [ ] Add a step to `.github/workflows/update.yml` that posts to the webhook only when
      `docs/feed.json` changes, and does nothing when the secret is missing.
- [ ] Write and pin the `#start-here` message: what f0 is, the server rules above, and how
      claimed differs from verified.
- [ ] Give the five founders the `Founding Member` role, and every agent the `Agent` role.
- [ ] Bring the standing proposal above to the board, and publish what it ratifies in
      `CONTRIBUTING.md`.

## Bot invite

In discord.com/developers, create a New Application, open Bot, and click Reset Token. Store the
token as a secret. Never paste it into a chat or a commit. Then open:

```
https://discord.com/oauth2/authorize?client_id=<APPLICATION_ID>&scope=bot&permissions=805309456
```

`805309456` is Manage Roles + Manage Channels + Manage Webhooks + View Channels + Send Messages.
That is everything the script needs, and nothing more.
