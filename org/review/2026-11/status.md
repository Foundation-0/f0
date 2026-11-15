# Status board

Pinned baseline for every row: f0 main
`6ea3a0b3d18fa1e7cf1845e3dc67220a35781948`, checked 2026-11-15.
Update this file in the same pull request that changes a row.

## Work packages

| Id | Owner | State | Output |
|---|---|---|---|
| H1 inventory | unclaimed | not started | f0 slice in f0-audit.md |
| H2 decision numbers | unclaimed | not started | f0 facts in gate0-packet.md |
| O1 overlaps | amp-vela | f0 slice done | overlap-f0.md |
| O2 run verifiers | amp-vela | f0 slice done | reproduction.csv |
| O3 recovery | amp-vela | f0 slice done | overlap-f0.md, branch table |
| F1 theory map | unclaimed | waiting on H1 | brief in incoming-intelligence.md |
| F2 claim verdicts | unclaimed | waiting on H1, O2 | verdict standard in issue 42 |
| F3 ties | unclaimed | waiting on F1 | none |
| F4 recheck 14 Nov | unclaimed | waiting on F2 | f0 rows in f0-audit.md |
| F5 science reviews | unclaimed | on request | none |
| F6 glossary | unclaimed | draft terms exist | org/claims/GLOSSARY-PROPOSED.md |
| F7 owner summary | unclaimed | last | none |
| S1 structure proposal | unclaimed | waiting on F1, F3, O1 | none |
| S2 carry out structure | unclaimed | needs owner decision | none |
| S3 housekeeping | unclaimed | needs decision 6 | none |

## Claim log

| Date | Who | Packages | Posts as |
|---|---|---|---|
| 2026-11-15 | amp-vela (muse-wonder-full-1.0, xhigh) | O1, O2, f0 parts of O3, f0 polish | ahrazzle |

The ahrazzle login is shared by more than one agent.
An approval from that login must not count for work authored
through the same login. The claim comment in issue 42 says this
in full.

## Decisions

Gate 0 is open. No owner decision is recorded in this run yet.
The reply form is [gate0-packet.md](gate0-packet.md).
Work that needs a decision stays parked until the answer lands.
Work that needs no decision runs now: H1, H2, O1, O2, O3 checks,
and the f0 entry polish.

## Time limit

The Gaia archive outage falls on 2026-11-25.
The gaia-dr4 recovery branch is first in the O3 queue in issue 42.
Its merge check and the exact next step sit in
[overlap-f0.md](overlap-f0.md).

## Cross-repository recovery queue

Each row needs its own pull request in its own repository,
with a full preflight there. States use: ready, blocked,
review, done. A blocked row names what releases it.

| Id | Repository and branch | State | Next action |
|---|---|---|---|
| R1 | gaia-dr4 `prep/gaia-dr4-tasks` | blocked | authors pick prep branch or task slices (pull requests 9 to 14), deadline 2026-11-25 |
| R2 | exoplanets-frontier `orda-aska-patch-1` | ready | open restore pull request naming the parse fix and the 14 to 10 count change, record-lane review |
| R3 | incentre-lattices `gpt-forge/distributed-folding` | ready | open restore pull request, fast-forward per issue 42 |
| R4 | incentre-lattices `codex/focused-fcc-paper` | ready | restore `papers/continuous-fcc/` only |
| R5 | incentre-lattices `prior-art-sources` | blocked | check main for the same wording first, then reapply by hand |
| R6 | proven-commons `claude/brave-knuth-x3bkfi` | ready | open restore pull request |
| R7 | proven-commons `sync/upstream` | ready | open the pull request the bot never opened |
| R8 | profile repository `org-pr-template` | blocked | maintainer approves the template text, local session only |
| R9 | virtual-human, three branches | blocked | test-merge each one, then restore or close |
| R10 | gravity commit `fcef36e23` | blocked | owner says whether the 104-line refactor is still wanted |
| R11 | cfrp-strengthening pull request 7 | blocked | land 7, or retarget the fixes from 15 to main |

R1 on the critical path: F2 verdicts for gaia-dr4 work wait on
its landing shape. R2 unblocks any fresh run of `cool_vet.py`,
which does not parse on main today.
