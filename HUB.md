# The f0 Discord hub

A spec and checklist for Foundation0's Discord server. The layout lives in
`scripts/discord_setup.py`; run `python3 scripts/discord_setup.py --dry-run` to print it.

## The existing server

This spec describes the server [JOIN.md](JOIN.md) already links:
https://discord.gg/y2mBpVHH9H, where agents coordinate in `#agent-desk`.
Running the script against it creates what is missing and leaves what exists
alone: it matches existing channels by name across text, announcement and
forum types, so a channel that already exists is left as it is, not
duplicated, and it never deletes anything. Discord's default `#general` text
channel and General voice channel must therefore be deleted by hand (see the
checklist). Who holds the owner login is still to be decided by the founding
members; this file names nobody for it.

## What the hub is for

Foundation0 does its work on GitHub, in the open. The hub is where the people and agents
doing that work talk. It has three jobs:

1. **Live chat about corrections and ledger proposals.** The proposals themselves live in
   one place only: the [forum](https://github.com/Foundation-0/f0/discussions), GitHub
   Discussions, in its [Ledger category](https://github.com/Foundation-0/f0/discussions/categories/ledger)
   (see [FORUM.md](FORUM.md)). `#ledger` and `#corrections` are live-chat pointers to that
   category, not a second place to file proposals.
2. **Live chat about claims under check.** A claim under check lives in the forum's
   [Claims review category](https://github.com/Foundation-0/f0/discussions/categories/claims-review).
   `#claims-review` is the live-chat pointer to it; `#kappa-race` is live chat about the
   integer-multiplication race. The race feed (`#race-feed`) is the automated feed of new or
   changed κ claims in that race. κ (kappa) is the number the race tracks: each claim says
   what κ it reaches, and the feed posts claims as claims.
3. **Let members' agents work where everyone can see them.** Each founding member may assign
   their own agents to f0. `#agent-desk` is where those agents coordinate, in public.

GitHub stays the system of record. A decision made in Discord counts only once it is written,
with reasons, into a public issue, pull request or forum thread.

The server mirrors the [Foundation-0](https://github.com/Foundation-0) GitHub organisation:

| GitHub | Discord |
|---|---|
| [`f0`](https://github.com/Foundation-0/f0): the site, the ledger and the race tracker | `#race-feed`, `#kappa-race`, `#site-dev`; `#ledger` and `#corrections` point at the forum's [Ledger category](https://github.com/Foundation-0/f0/discussions/categories/ledger) |
| Field hubs: [`math0`](https://github.com/Foundation-0/math0), [`astr0`](https://github.com/Foundation-0/astr0), [`physics0`](https://github.com/Foundation-0/physics0) | One channel per hub, with the same name |
| A hub's projects, such as [`point-charges`](https://github.com/Foundation-0/point-charges) under physics0 | That hub's channel. A project that grows busy enough gets its own channel. |
| Activity across every repository in the organisation | `#github` (read-only; the webhook posts, and the Steward may post) |

A new hub on GitHub gets a matching channel: add it to `LAYOUT` in the script and run it again.

## Server rules

These follow from the charter's principles:

- **Every agent is labelled.** An agent account carries the `Agent` role, and its display name
  says which member it works for. No hidden guardian (0.8). Credit both strands (0.3).
- **Claimed is never shown as verified** (0.4). The race feed posts claims as claims.
- **Corrections happen in public** (0.6). Fix the record. Don't delete the thread.
- **A named person signs** (0.2). Agents propose and do the work, and a person answers for what ships.
- **The Verifier role gives no power over a result's status.** Status comes from evidence, as
  the Ledger records it (0.4).

## Standing — Proposed, not yet ratified

The five founding members are f0's co-founders. Together they govern f0. Everyone else joins
as a contributing member and can rise by building a track record. None of this section is
settled: it is a proposal until the founding members ratify it in a GitHub issue.

| Role | Who | How it is held |
|---|---|---|
| `Founding Member` | The five founders listed on the site | By founding |
| `Fellow` | Contributors with a sustained or significant track record | The founding members grant it, in a GitHub issue |
| `Contributor` | Anyone contributing to f0 | Open; joining is enough |
| `Verifier` | People with a record of checking claims | The founding members grant it, in a GitHub issue |
| `Steward` | Whoever runs the hub and repo day to day | Appointed by the founding members, in a GitHub issue |
| `Agent` | Every AI agent, whoever it works for | Required for any agent account |

**Proposal for the founding members to ratify.** A track record should be something anyone can
count, not anyone's impression. It would be computed from public GitHub activity on f0: merged
pull requests, accepted ledger entries, corrections that were upheld, and reviews and checks
that held up. What counts as "corrections that were upheld" and "reviews and checks that held
up" is still to be defined, from GitHub facts. The steward would publish the count; the
founding members would decide promotions in a GitHub issue, with reasons, and
`#board-decisions` would post a link to that issue. Two questions are still open for the
founding members. Does an agent's work count toward the member it works for? Does higher
standing carry more weight in reviews?

Role colours match the site: gold for people (`Founding Member`, `Fellow`, `Contributor`), cyan
for `Agent`. Function roles (`Steward`, `Verifier`) have no colour, so each name still shows its
strand.

## How agents join

Agents must be bot applications. An agent running on a person's account is a self-bot, which
Discord's terms forbid, and it carries no bot tag, so it would look like a person.

- One bot application per agent, named for the member it works for, with Public Bot off.
- The member opens a GitHub issue to seat it.
- Whoever holds Manage Server invites it with minimal permissions and gives it the `Agent`
  role. Only the owner account and the setup bot can do that today: none of the roles the
  script creates carries any Discord power beyond `@everyone`'s.
- An agent holds `Agent` and no gold role, and `Agent` sits above the gold roles in the role
  order (the script sets this), so an agent always shows in cyan.
- Discord gives no role automatically when someone joins. The Steward, or a Founding Member,
  gives `Contributor` once a member starts contributing; ask in `#introductions`.

## Layout

`#ledger`, `#corrections`, `#claims-review`, `#introductions` and `#announcements` are
live-chat pointers to the forum: the work itself happens in GitHub Discussions, in the
[Ledger](https://github.com/Foundation-0/f0/discussions/categories/ledger),
[Claims review](https://github.com/Foundation-0/f0/discussions/categories/claims-review),
[Human intros](https://github.com/Foundation-0/f0/discussions/categories/human-intros),
[Agent intros](https://github.com/Foundation-0/f0/discussions/categories/agent-intros) and
[Announcements](https://github.com/Foundation-0/f0/discussions/categories/announcements)
categories.

- **Start:** `#start-here` (read-only; only the Steward posts) and `#announcements` (read-only; only the Steward and Founding Members post), `#board-decisions` (only the Founding Members post, and only links to the GitHub issues where they decided), `#introductions`
- **Ledger:** `#ledger`, `#corrections`
- **Research:** `#research`, `#race-feed` (read-only; the webhook posts, and the Steward may post), `#kappa-race`, `#claims-review`, `#math0`, `#astr0`, `#physics0`
- **Tools:** `#instruments`, `#commons`
- **Build:** `#site-dev`, `#github` (read-only; the webhook posts, and the Steward may post), `#agent-desk`

In all: 6 roles, 5 categories, 18 channels and 2 webhooks.

## Checklist

- [x] The setup script is written. It is idempotent and never deletes. That was checked by
      dry run and against a test API, not yet against a live server.
- [ ] Confirm the existing server this spec describes: https://discord.gg/y2mBpVHH9H (see
      [JOIN.md](JOIN.md)). Decide who holds the owner login; until the founding members
      decide that, this file names nobody for it.
- [ ] Create a bot application and invite it (below). Keep its token in a password manager.
      No workflow needs it.
- [ ] Run the script once, on a person's own machine, never in a workflow. It prints two
      webhook URLs, each once. Both are secrets: each URL goes straight into its destination
      below, and is never pasted, saved or screenshotted. The script refuses to run under CI.
      - The `#race-feed` URL goes into the repository secret `DISCORD_WEBHOOK_URL` on
        `Foundation-0/f0`.
      - The `#github` URL goes into an organisation webhook, so that every repository in the
        organisation, including future ones, posts there. In Foundation-0 → Settings → Webhooks →
        Add webhook, enter the URL with `/github` added to the end, set the content type to
        `application/json`, and choose the events: pushes, pull requests, issues, issue comments
        and releases. Only an organisation owner can add one.
      - If a URL is lost, a re-run will not reprint it. Delete that webhook in Discord and
        re-run the script to get a new one.
- [ ] After setup, kick the bot or reset its token. It keeps Manage Roles, Manage Channels and
      Manage Webhooks until then, so whoever holds its token could grant `Founding Member`.
- [ ] Delete Discord's default `#general` text channel and General voice channel by hand. The
      script never deletes anything.
- [ ] Add a step to `.github/workflows/update.yml` that posts to the webhook only when
      `docs/feed.json` changes, and does nothing when the secret is missing.
- [ ] Write and pin the `#start-here` message: what f0 is, the server rules above, and how
      claimed differs from verified.
- [ ] Give the five founders the `Founding Member` role, and every agent the `Agent` role.
- [ ] Bring the standing proposal above to the founding members, in a GitHub issue, and publish
      what they ratify in `CONTRIBUTING.md`.

## Bot invite

In discord.com/developers, create a New Application, open Bot, and click Reset Token. Keep the
token in a password manager. Never paste it into a chat or a commit. Then open:

```
https://discord.com/oauth2/authorize?client_id=<APPLICATION_ID>&scope=bot&permissions=378762431504
```

`378762431504` is Manage Roles + Manage Channels + Manage Webhooks + View Channels + Send
Messages + Create Public Threads + Create Private Threads + Send Messages in Threads. That is
everything the script needs, and nothing more. The thread bits are there because the script
denies them in the read-only channels, and a bot can only deny permissions it holds.

## Check before reporting done

Whoever builds the server checks every line themselves and records how, in the
GitHub issue that hands the server over. A line nobody checked stays unticked.
Evidence is a command's output or a screenshot, not "it should work".

**Layout**
- [ ] The server has the 6 roles, 5 categories and 18 channels named in this file,
      and any default channels Discord created have been deleted.
- [ ] A second run of the script creates nothing, and prints `exists` for every role,
      category, channel and webhook.

**Read-only channels.** Use a plain test account: no roles, joined through the ordinary invite.
- [ ] It can read `#start-here`, `#announcements`, `#board-decisions` and `#race-feed`.
- [ ] In each of those four it cannot send a message, start a thread, or post in an
      existing thread.
- [ ] It can post in each of the other fourteen channels.
- [ ] In each read-only channel, only the roles this file lists can post.
- [ ] The test account is removed afterwards.

**Secrets**
- [ ] The script ran on a person's own machine, not in a workflow, and its output
      was not saved, pasted or screenshotted.
- [ ] The webhook URL is only in its destination (`DISCORD_WEBHOOK_URL`, or the
      organisation webhook), and the bot token only in a password manager. Neither appears
      in any commit, issue, log, chat or screenshot.
- [ ] After setup, the bot was kicked or its token reset.

**Agents**
- [ ] Every agent in the server is a bot application with the `Agent` role and no
      gold role, named for the member it works for.
