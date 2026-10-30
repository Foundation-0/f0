# GitHub collaboration: stacks, plans and visual evidence

**Proposed guidance for review.** This document describes GitHub features and a way to use them across our teams. Repository-specific ownership, independent review, current-head approval, required checks, resolved conversations, authorship, and merge rules still apply. It does not change a repository's policy, install software, authorize posts or merges, or enable settings.

## Stacked pull requests

Use a stack when one change genuinely depends on another and the work can be reviewed as focused layers. On GitHub.com, a native stack is a same-repository chain in which each pull request targets the branch immediately below it, ending at a trunk branch. Each layer can be reviewed separately; GitHub applies the trunk's protections and checks to every layer. Cross-fork stacks and GitHub Desktop are not supported. See GitHub's [stack reference](https://docs.github.com/en/pull-requests/reference/stacked-pull-requests) and [general-availability announcement](https://github.blog/changelog/2026-10-06-stacked-pull-requests-generally-available/).

For an existing chain, first inventory each PR, base and head, author, dependencies, review, checks, and any unique work. A chain whose bases already match its predecessor heads may offer GitHub's conversion banner; it is not automatically converted. Coordinate with the owners before conversion, retargeting, rebasing or pushing. Preserve history, review evidence and author-owned branches; do not reset, close, or rewrite someone else's work as part of an inventory.

When editing a lower layer, GitHub's [management guide](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests) describes the separate `gh stack` extension and the `gh stack rebase --upstack` and `gh stack push` flow. Check that the extension and supported Git and `gh` versions are actually available before using them. A cascading rebase and push can rewrite multiple branches: coordinate every affected owner, inspect the plan and use the documented lease protection. A general request to organize work does not authorize rewriting others' branches.

Every affected PR still needs its own independent review and the required checks for its exact current head. Do not treat an approval that GitHub retained after a rebase as proof that our current-change review requirement is met. Verify signatures if they matter to the repository; do not assume a web rebase preserves them. A merge into a parent feature branch is not a landing on trunk, and a repository merge is not a deployment.

GitHub can merge a selected layer and its lower layers bottom-up, but use that facility only when the applicable repository SOP permits it and every affected layer has met its gates. The existing [merge SOP](MERGE-SOP.md), scoped to aska-digital, Foundation-0, and Proven-Commons, requires a PR stacked on an unmerged branch to wait for that branch to land on `main`; this guidance does not change that rule. A partial failure can leave lower layers merged, so inspect each actual outcome before retrying. GitHub's October announcement says stack auto-merge is rolling out; do not assume it is available or enabled, and do not enable it as part of this guidance. GitHub Actions run against the stack's trunk context; verify the resulting evidence and required checks rather than inferring success from an empty check list.

## Issue plans and artifacts

When an issue has a substantial plan, attach or link a concise plan that records its problem, acceptance criteria, ownership, dependencies, proposed steps, verification, and relevant PR links. Keep the issue itself useful as the entry point. Record the artifact URL and version used by the work; edit or restore an earlier version when correcting the plan, rather than silently replacing evidence.

[Issue artifacts](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/using-artifacts-with-issues) are a public preview on GitHub.com and GitHub Enterprise Cloud. GitHub describes a `plan` as Markdown; verify current feature and permissions before relying on it. Public-issue artifacts are publicly readable. Do not put credentials, private prompts, customer data or other restricted material in them. Previewing interactive HTML can transmit its content elsewhere; do not execute untrusted previews. Deleting an artifact permanently removes its history: prefer edit or restore and obtain specific authorization before deletion.

Where supported, GitHub CLI 2.103.0 or later provides commands such as:

```sh
gh issue artifact create 142 --type plan --body-file ./plan.md --name 'Implementation plan'
```

See the [artifact create manual](https://cli.github.com/manual/gh_issue_artifact_create) and check local help. If the feature, permissions, or command is unavailable, keep the plan in an appropriate linked repository document or issue comment under the existing access rules; do not claim an artifact was created.

## Media in issues, pull requests and comments

Use visual evidence when it helps someone verify the change. Review the file and its provenance first; remove secrets, private captures, customer information and unrelated content, and provide useful alt text for images. A repository's existing posting and disclosure rules still apply.

GitHub CLI 2.99.0 or later supports repeatable `--attach` for supported image and video files on GitHub.com. Repository write access and a supported `gh` authentication method are required. For example, after a reviewable image and comment are ready and posting is authorized:

```sh
gh pr comment 123 --body 'Visual verification' --attach './after.png#Updated screen'
```

See GitHub's [media announcement](https://github.blog/changelog/2026-09-01-github-cli-media-in-issues-pull-requests-and-comments/) for supported formats, size limits, authentication and platform restrictions. Inspect the post after writing and report a failed upload or uncertain outcome; do not change credentials or access to make the command work. The local CLI version alone does not establish access.
