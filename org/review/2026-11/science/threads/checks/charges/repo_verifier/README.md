# The point-charges repository's verifier, corrected form

`verify_arb.py` here is a copy from the Foundation-0 point-charges repository, branch `symbiosis/2026-11-review` at commit 4305645 (pull request 22 of that repository). It differs from the version at the pinned head a2fd159 in one way: each proof step raises an error where the old version used `assert`, so it also rejects a bad certificate under `python3 -O`.

It is copied here so that this folder holds both exact programs for the four-charge result. It is under that repository's licence, Apache 2.0.

Run it from `checks/charges/`:

```
python3 -O repo_verifier/verify_arb.py ../four/verify/n4_eleven_short.repo.json
```

Saved output for the three four-charge certificates: `../out/repo_verifier_fixed_under_O_on_four.txt`.
