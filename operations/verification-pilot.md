# Candidate project: reproducible verification for AI-assisted mathematics

**Discussion draft, 19 October 2026.** A six-month option for founder and maintainer review, not an
adopted research agenda, a grant application, a discovery claim or a promise by any named person.
Compare it against other founders' priorities before selecting a first project.

## Problem and public benefit

AI-assisted mathematics can produce candidate results faster than people can examine them. A useful
public contribution would be a small, reusable pipeline that records the exact claim, source commit,
assumptions, checker and outcome, so another researcher can reproduce both accepted and rejected
claims. This follows the charter's “propose freely, verify strictly” principle and the existing
repository's distinction between claimed and verified results.

Foundation0 already has [a gated mathematical race feed](../README.md#the-integer-multiplication-race-tracker)
and links to [member research](../docs/research/index.html). These are starting examples, not evidence
that a generalized pipeline is already built or that every listed result is independently verified.

## Proposed scope and outputs

- Select **two willing mathematics project maintainers** and agree on ten representative public
  claims/artifacts, including failures or uncertain cases. Participation and redistribution permission
  must be confirmed; no project or maintainer is committed by this proposal.
- Publish a minimal claim manifest: source/commit, claim and hypotheses, dependencies/environment,
  data/license provenance, checker version and execution recipe, expected output, reviewer role,
  strongest evidence status and known limitations.
- Build reproducible runners for two artifact types, with documented resource limits and archived
  logs. Never automatically execute untrusted research code with credentials or privileged access.
  Use isolation and a named human review step for unexpected access or dependencies.
- Add must-fail controls and distinguish numerical replay, independent checking and formal proof.
  A successful numerical checker must not be promoted to a mathematical proof automatically.
- Publish documentation, machine-readable results, a worked tutorial, negative findings, and a
  maintenance/hand-off plan. Honor each upstream license and credit both human and AI work.

Out of scope: certifying all mathematics, proving the superiority of a model, claiming new records,
rebuilding third-party proof assistants, transferring upstream ownership, or funding unrelated
commercial products. A short existing-tool/prior-art review should determine what to reuse before
building another framework.

## Milestones and acceptance evidence

| Target | Deliverable | Acceptance evidence |
|---|---|---|
| Month 1 | Baseline and rights review; maintainers/lead confirmed; ten cases selected. | Public scope and prior-art note, license inventory, dated baseline runs and failure categories. |
| Months 2–3 | Manifest and two prototype runners. | Pinned examples, readable logs, documented environments/resource caps, all selected cases classified without evidence inflation. |
| Month 4 | Adversarial controls and independent reproduction. | Altered artifacts/hypotheses and corrupted outputs are rejected; a non-author reproduces a documented subset and reports discrepancies. |
| Months 5–6 | Release, tutorial, evaluation and maintenance decision. | Grant-compliant open code/data release; comparison with baseline on reviewer effort, reproducibility and error detection; public limitations and continuation/stop recommendation. |

Proposed evaluation measures: setup and reviewer time, repeat-run agreement, success on a second
environment, failure explanations, and detection of intentionally corrupted artifacts. Pre-register
the cases and scoring before comparing results. Report the sample size and negative outcomes; do not
set a funding narrative that depends on discovering a new theorem. Exact numerical targets should be
chosen after the baseline, then fixed before the final evaluation.

Resolve any incompatible data or code rights before including them in a proposal. For AI for Math,
all funded code must be open source and all funded datasets openly shared with documentation; an
upstream restriction is a reason to change the proposed scope, not an exception to the grant terms.

## Illustrative budget: US$90,000 total

This is an arithmetic example for scope discussion, not vendor quotes, agreed compensation or an
approved spending plan. Replace every rate with justified costs, availability and applicable tax/
employment treatment before submission.

| Cost | Assumption | US$ |
|---|---|---:|
| Research/software implementation | 800 hours × $60 | 48,000 |
| Independent mathematical review and evaluation | 200 hours × $90 | 18,000 |
| Compute | 6 months × $1,500 capped allowance | 9,000 |
| Documentation and reproducibility work | 120 hours × $50 | 6,000 |
| Indirect administration | 10% of total award | 9,000 |
| **Total** | **Direct $81,000 + indirect $9,000** | **90,000** |

The 10% line uses the AI for Math seed RFP's **total-award** basis, not 10% of direct costs. It does not
establish that any sponsor will work at this fee. A sponsor charging 15% of incoming cash would require
US$13,500 at this award size; resolve the US$4,500 difference before claiming this budget is feasible.
See [the funding note](funding.md#fiscal-sponsorship-is-administration-not-funding). Personnel rates
must include or separately account for benefits, payroll/contractor charges and taxes where applicable;
if total cost is higher, reduce scope or revise the request rather than hiding costs.

Keep a separate core-operations forecast for formation advice, accounting, insurance, website/domain
costs and maintenance after month six. These are not automatically allowable direct costs of this
project. An award restricted to this pilot is not unrestricted funding for the whole organization.

## Risks and stop/change decisions

- **Existing tools already solve it:** reuse or improve them; publish the gap analysis instead of
  creating unnecessary infrastructure.
- **No maintainer demand or redistribution rights:** narrow the pilot to consenting projects and
  publish only permitted artifacts; stop if there is no real reusable problem.
- **Review bottleneck or resource overrun:** cap the case set and compute; do not loosen verification
  requirements merely to reach a favorable result.
- **No reproducibility improvement:** publish that finding and the causes. Negative evidence is a
  legitimate outcome; do not imply success based solely on a release.
- **Sponsor/grant incompatibility:** obtain an approved admin/budget arrangement before submission;
  do not sign or incur expenses while the plan is unresolved.

## Required human decisions

Choose this or another project; name a lead and consenting maintainers; approve reviewers, metrics,
scope and rates; verify IP/public-benefit arrangements; select the applicant/admin route; approve the
current funder terms and final submission. All are pending. See [F4–F7](README.md#decisions-needed-from-named-people).
