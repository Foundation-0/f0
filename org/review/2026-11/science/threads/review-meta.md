# What the review findings say about the work

15 November 2026. The team reviewed this folder in twelve passes and recorded every finding in `findings.json`, in the addendum folder of pull request 60. This note counts those findings, asks what kind they are, and draws out what they imply. Marks: **[F]** fact from a count, **[I]** inference, **[C]** conjecture.

The counts come from `checks/review-meta/classify.py`. It reads the review's record and a table that gives each problem finding a kind, a layer and a direction. The table is the reviewed author's reading. Another reader could move a few rows.

## The numbers

[F] The record holds 119 findings. 51 are confirmations: a reviewer re-ran something and it held. 68 are problems: 6 blocking, 22 major and 40 minor.

| Where the defect sits | Blocking | Major | Minor | All |
|---|---|---|---|---|
| A proved result | 0 | 0 | 0 | 0 |
| A program | 0 | 2 | 8 | 10 |
| Packaging: a file, input or cited document is missing | 1 | 6 | 5 | 12 |
| One thread's note or report | 3 | 13 | 20 | 36 |
| The synthesis layer: README, convergences, fabric, pull-request text | 2 | 1 | 7 | 10 |

| Kind of defect | All | Of which blocking or major |
|---|---|---|
| Wording wider than what was tested: "every", "all", "exactly" | 14 | 6 |
| A number or statement the shipped data contradicts | 11 | 2 |
| The folder is not self-contained | 10 | 7 |
| A checking program can pass when it should not, or is fragile | 7 | 2 |
| A derivation asserted or sketched, not written | 6 | 2 |
| Independence of checks overstated | 6 | 4 |
| Housekeeping | 6 | 0 |
| A verdict word or evidence mark stronger than the evidence | 5 | 3 |
| Circular fit, selective quoting, a statistic with no meaning | 3 | 2 |

## Four things the counts show

### 1. No result failed. The errors are in the sentences.

[F] Every proved result that a reviewer re-ran reproduced, with matching box counts and centres. One pass attacked the surviving claims with fresh corrupted inputs and got no false acceptance. Of the 68 problems, 46 are in prose and 12 in packaging. Of the 10 in programs, 8 are minor and fail safe.

[I] So the certificates did their job. What a certificate cannot do is stop a sentence beside it from saying more than it proves.

### 2. The errors all point one way.

[F] 42 of the findings have a direction: the text claims more than the evidence, or less. 41 claim more. One claims less.

[I] An error that falls on one side 41 times in 42 is a bias. The work drifts toward the stronger claim. Nothing in the process pushed back.

### 3. The drift grows with distance from the data.

[F] In about ten findings, by the author's reading, the lower layer is right and the layer above it is wrong. A saved output says 15 rejected lines and the note says 15 kinds. A thread says "undecided" and the synthesis marks the same statement as fact. A report marks an index claim as inference and its note states it flat. A data file says 856 and 860 and the note says 868 at every value.

[I] Each time a result is summarised, a qualifier can fall off. None is ever added. The synthesis layer is two steps from the data, and it holds two of the six blocking findings.

### 4. The mathematics and the physics fail differently.

[F] All three findings of the statistical kind, a circular fit, an outlier left unnamed, a regression on bounds, come from the one pass that covered gravity and the light particle. The seven passes on exact mathematics have none. Their heavy findings are missing files and loose words.

[I] This is the folder's own first observation, reached again from outside. The results that hold are finite objects a short program can re-check. In those threads a review can only find faults in the wrapping. In the physics threads it finds faults in the reasoning.

## Why it happened

Each cause below is traced to how the work was done.

- [F] **A result had a second program. A sentence had nobody.** Every count was re-proved by separately written code. No sentence was compared with its data file by anything. Eleven findings are of that kind.
- [F] **Words were used loosely.** "Independent" was used for the same proof written twice, for a different method, and for a program by another hand, with no word to tell them apart. "Every" and "exactly" were used for what had been sampled. Twenty findings.
- [F] **The work was done in a scratch area and copied in.** Programs kept their old paths. Sources stayed in an archive. A checker stayed in another repository. Ten findings, seven of them heavy.
- [F] **Reports came back as messages.** Workers could not write a report file, so the lemma proofs they wrote reached the lead as text and were never placed. Three programs still pointed at a file that did not exist.
- [F] **Labels were typed by hand in several places.** The recurrence verdict appears in three notes with three values.
- [F] **One check was itself wrong.** The reviewer's first check of the stacked levels counted 59 where 41 is right. A worker found it by running the program to the end, which the reviewer had not done.

## How many are left

[F] Two kinds of pass looked for wording defects: the passes on single threads, and one pass that read only labels across all threads. The thread passes found 27. The label pass found 8. Five were found by both.

[I] If the two looked independently, the usual estimate from such an overlap is about 41 wording defects in all. 30 were found. About 11 are still in the text.

[I] The estimate is rough. The two kinds of pass were not independent, and the classes are the author's. It is still better than assuming the review found everything. The likeliest places are the ones two steps from the data: `README.md`, `convergences.md`, `fabric.md` and the pull-request text.

## What it implies for the larger aim

[I] The foundation's aim is a single account of many things. That is a synthesis, and synthesis is exactly the layer where this review found the bias. A chain of ten summaries, each a little stronger than the last, turns "undecided" into "established" with no step that looks like an error.

[I] So the limit on progress here is not finding results. The threads produced them faster than they could be reviewed, and the review took twelve passes. The limit is keeping each claim at the strength of its evidence while it is carried upward. That is a property of the process, and it can be engineered.

[C] A body of work can only be as large as its claims are checkable. Where a sentence is tied to a file by a program, a reviewer re-runs. Where it is not, a reviewer re-reads, and re-reading is what took twelve passes.

## What was changed because of this

1. **Sentences are now checked against data.** `checks/claims/check_claims.py` reads a ledger of sentences, each with a test on a data file. If a sentence leaves its note, or the data stops supporting it, the program fails. It starts with 27 claims, including the sentence the review found false. It should grow until every number in a headline is in it.
2. **The manifest is built from what a commit contains.** It can no longer describe files that are still being edited.
3. **One rule for verdict words, stated in the folder.** VERIFIED needs a program written apart. REPRODUCED is one thread's programs agreeing. The word for a theorem is "proved", with what proves it.
4. **Independence is named by kind.** Same proof in separate code. A different method. A different author and toolchain. A note says which.
5. **"Every" is replaced by a list.** A sentence about all checkers now names them.
6. **Derivations are files.** The three-charge lemmas and the two derivative bounds are written out in the folder.

## What this note does not show

- The classification is one reader's. The kinds overlap, and a finding can belong to two.
- The review did not re-run everything. Its record lists eight groups of items it left open, and literature claims were not checked in any thread.
- The estimate of what is left covers wording defects only.
- Nothing here measures whether the changes work. The test is the next review.

## Rerun

```
python3 checks/review-meta/classify.py <path to findings.json>
python3 checks/claims/check_claims.py
```

The first needs the review record from pull request 60. Its saved output is `checks/review-meta/classify.out`.
