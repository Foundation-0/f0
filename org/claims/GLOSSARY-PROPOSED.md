# Claim words: proposed shared glossary

Status: proposed. This file is the draft for decision 4 in
[issue 42](https://github.com/Foundation-0/f0/issues/42).
It binds nobody until the owners adopt it. Work package F6
owns the final wording. Until then, no merged claim changes
its label because of this page.

## Why one set of words

Today the same word means different strengths in different
repositories. A reader cannot tell what PROVEN promises.
One shared set, defined by the evidence each word needs,
fixes that without judging any single claim here.

## The nine verdict words

The execution plan in issue 42 defines eight words. This proposal
adds a ninth, CLAIMED, for a claim stated but not yet checked here.
Decision 4 names four of them as the public claim labels:
CLAIMED, REPRODUCED, VERIFIED, PROVEN. The other five
(KNOWN, OPEN, OVERSTATED, CONTRADICTED, NOT CHECKABLE)
belong to review records. [I] The split between
public label and review verdict is part of the proposal.

| Word | Meaning | Evidence the word needs |
|---|---|---|
| CLAIMED | stated, not yet checked here | the statement and its source |
| REPRODUCED | repo code gives the stated numbers | fresh-clone run, command, output hash |
| VERIFIED | rigorous computation settles it | exact or interval method, fresh rerun, fails closed under `-O` and on bad input |
| PROVEN | a complete proof checks | Lean on standard axioms only, statement matches the claim, or a written proof checked line by line |
| KNOWN | true and already published | the citation, quoted word for word |
| OPEN | plausible, evidence does not settle it | the reason it stays open |
| OVERSTATED | label claims more than evidence shows | what the evidence does show |
| CONTRADICTED | wrong | a counterexample, a failing fresh run, or an exact quote that conflicts |
| NOT CHECKABLE | data or code missing | what is missing and where it should sit |

Three judgments stay separate for every claim: the
statement, the evidence offered, and the label it carries.
OPEN is the default and carries no blame.

## Mapping from the Ledger words

The Ledger in this repository grades how far a result has
been checked, with six words in
[CONTRIBUTING.md](../../CONTRIBUTING.md). The two sets grade
related ground from different sides. This mapping is a
proposal for F6, not a rename. [I]

| Ledger word | Closest shared word | Gap to mind |
|---|---|---|
| claimed | CLAIMED | same sense |
| preprint | CLAIMED | preprint also says where it appeared |
| independently-replicated | REPRODUCED | shared word needs the fresh-clone record |
| formally-verified | PROVEN | shared word also needs statement match and axiom limits |
| peer-reviewed | none | peer review is a publication fact, not a truth grade |
| deployed | none | deployment is a use fact, kept beside the verdict |

The kappa feed in this repository already keeps two tiers
apart by construction: claimed rows never enter the verified
chart, and `scripts/gate.py` blocks any file that mixes them.
That split shows the CLAIMED side of the mapping at work.
It is an illustration of the words, not a verdict on content.

## Rules for using the words

- A label rises only on evidence recorded beside the claim.
- Who produced the work never changes the standard.
- A downgrade keeps its history in the open (charter 0.6).
- Each verdict in a review ends in plain sentences:
  what the claim says, the verdict, and why.
