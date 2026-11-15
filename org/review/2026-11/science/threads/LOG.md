# Log of the threads pass

15 November 2026. This is the working record of how the threads were pulled, in the order things happened, with the dead ends and the corrections. The results are in the notes. This file is here so that the route is not lost.

Marks: **[F]** fact, **[I]** inference.

## 1. Starting point

- [F] The science pass (draft PRs 51 to 57) ended with `new-ground.md`, a list of eleven threads.
- [F] A reviewer requested changes on all seven drafts. The fixes were made first and pushed as one new commit per branch. Two review points were not applied, with the evidence given in the PR bodies.
- [F] From that review on, no seat, model or tool name appears in any text or commit message.

## 2. How the threads were run

Each thread was given to a separate worker with a narrow brief: the question, what was already known, where the files were, what would count as done, and one shared set of rules.

The rules that mattered:

1. Mark every statement as a fact or an inference.
2. "Independent" means separate code that does not import or copy the code it checks. A re-run of the repository's own verifier is a reproduction.
3. A count is proved only if both halves are proved: each solution exists and is alone in its box, and there are no others.
4. Floating point finds candidates. Proof steps use exact rationals or rigorous ball arithmetic.
5. Corrupt an input and confirm the checker rejects it, also under `python3 -O`.
6. A negative result, stated exactly, is a result.

Every result that came back was then re-run by the reviewer. For the results marked VERIFIED, a further program was written apart from the one that found the result.

## 3. Order of events

| Step | What happened |
|---|---|
| 1 | Review fixes prepared, checked and pushed. |
| 2 | Nine threads started together: point charges, complex count, 11-vertex push, code tables, recurrences, lattice referee, acceleration scale, central configurations, review fixes. |
| 3 | Gravity tested by the reviewer directly against SPARC and a giant-spiral sample, then handed to a tenth worker for four more tests. |
| 4 | Complex count back: 880 and 2,288 by three implementations. |
| 5 | Code tables back: all 1,519 certificates then passed the reviewer's own checker, and nine live lookups matched. |
| 6 | Lattice referee back: theorem holds to dimension 9, one wording error. |
| 7 | An eleventh thread started: the rigid-graph engine on the open Maxwell cases. |
| 8 | Point charges back: separate proof of the five counts, plus exact 49 and 64. |
| 9 | Gravity tests and the acceleration fit back. |
| 10 | Recurrences back: 211 proved. The reviewer re-proved 46 with a separate machine. |
| 11 | 11-vertex push back: 2,288 of 2,288. The reviewer's exact checker confirmed it. The same worker was sent on to 12 vertices. |
| 12 | Maxwell push back: nothing above the bound. The reviewer certified its second four-charge family. |
| 13 | Central configurations back: 20, 42 and 67 classes. |
| 14 | Notes written, draft PR 58 opened, findings posted to the matching issues. |
| 15 | Second round: full reports captured, a durable archive made, and four statistical studies started (see `convergences.md`). |

## 4. Dead ends and corrections

These are kept because each one changed what was done next.

- **A false signal in the first gravity test.** [F] Sorted by speed, the eight fastest SPARC spirals sit 0.10 dex above the standard relation, which is what the model predicts. [F] Sorted by baryonic mass the excess is gone. Sorting by speed selects galaxies that are fast for their mass, and the statistic contains the speed. [I] Every later test states which variable it sorts on and which way that biases the answer.
- **A slope that looked like confirmation.** [F] In the giant-spiral sample the offset rises with speed at 0.553 ± 0.063 per dex, close to what the fitted model predicts. [I] In a sample chosen in a narrow range of mass, any scatter in speed gives a slope near 1. The slope is not evidence.
- **A brief that named the wrong repository.** The lattice brief quoted two rod thresholds. Those belong to another repository. The worker reported that the files did not exist at the pinned head, and nothing was built on the error.
- **Data that could not be fetched.** The first SPARC mirror did not answer and a second address did. The per-galaxy data of the 79-galaxy sample named in the acceleration folder timed out on two servers and was never retrieved. The 100-galaxy table used in its place is an image in the paper and was typed in by hand, then checked by a second reading.
- **A reported result that needed care.** The code-table scan reported over two thousand improved entries, far more than expected. It was not accepted until every certificate had passed a checker written earlier for a different purpose and table values had been looked up live a second time.
- **A census that missed a class.** For 10 equal masses, about 1.1 million random starts never found the regular decagon. A search started near the regular polygon found it. A census that has stopped finding new classes is evidence, not proof.
- **A search that cannot be replayed.** One solver setting was changed during the 11-vertex push. The certificate stands alone, but the path to it cannot be rerun step for step.
- **Workers could not write report files.** Their reports came back as messages. They are kept in full under `reports/`.

## 5. What was not done

- The reviews of work package F5 and the 48 verdict rows not yet judged in the science pass.
- A third proof of the central-configuration lists.
- A literature search for earlier proofs of the recurrences.
- An injected-signal test of the acceleration fit.
- Any message to anyone outside the organisation.

## 6. Where everything is

- The notes, programs, certificates and saved outputs: this folder.
- The full reports of each thread: `reports/`.
- Outside sources, with checksums of the copies used: `SOURCES.md`.
- A checksum of every file here: `MANIFEST.sha256`.
- The whole working folder, including cached sources and search states too large for the repository, is archived outside the repository by the owner.
