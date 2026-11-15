# Organisation claims registry (design stub)

Status: empty by design. Rows arrive with work package H1
(the inventory) and verdicts with F2. No claim id is invented
here. Ids copy word for word from each repository and its
claims file.

## Files

- `GLOSSARY-PROPOSED.md`: the draft words for decision 4.
- `registry.csv`: one row per claim across the organisation.

## Columns in registry.csv

| Column | Rule |
|---|---|
| claim_id | as written in the source repository |
| repo | repository name under Foundation-0 |
| file | path in that repository |
| line | line of the claim statement |
| label_current | the label the claim carries today |
| verdict | empty until F2 rules, then a glossary word |
| evidence_link | run, proof or quote behind the verdict |
| plain_summary | two plain sentences for a general reader |
| checked_at_commit | commit the verdict was made against |
| checker | model or person who made the verdict |

## Rules

- One row per claim. A claim restated in a second repository
  gets a second row, linked by the same claim_id where the
  sources share one.
- The registry records. It never promotes a claim by itself.
  The claim label changes only in its home repository, by
  pull request, after the owners settle decision 4.
- A row with no verdict means unchecked, never false.
