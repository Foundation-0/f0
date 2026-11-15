# Draft OEIS comments (NOT sent, nothing submitted)

These are drafts for a human to review. Each needs a public link to the certificate before anyone posts it. The link is left as a placeholder.

## Template

The recurrence given above is proved, not only empirical, for all n >= START.

Rows are added one at a time. A state is the last row plus the number of counted pairs so far (0 or 1). This gives D states. Let M be the D X D transition matrix and v the vector of one-row states. Let p be the characteristic polynomial of the recurrence. Then p(M)v is either zero after m more multiplications by M, or its residuals vanish for D consecutive indices. The recurrence fails at n = START-1.

Certificate and checker: [LINK].

## A268882 (n X 4, exactly one pair, horizontal or antidiagonal, both cells 1)

The recurrence a(n) = 16*a(n-1) - 88*a(n-2) + 200*a(n-3) - 208*a(n-4) + 96*a(n-5) - 16*a(n-6) holds for all n >= 8 This is proved with an exact integer transfer matrix with 21 states. The residual at n = 7 is 4, so the recurrence needs the stated range. Certificate and checker: [LINK].

## A268898 (n X 2, 0..2 arrays, exactly one pair with sum 2, horizontal or antidiagonal)

The recurrence a(n) = 8*a(n-1) - 16*a(n-2) holds for all n >= 3. Proved with an exact integer transfer matrix with 15 states: the vector p(M)v is zero, so the recurrence follows from the first terms. Certificate and checker: [LINK].

## A268909 (6 X n, 0..2 arrays, exactly one pair with sum 2, horizontal or antidiagonal)

The recurrence of order 18 holds for all n >= 27. The transfer matrix has 1458 states. The residuals are nonzero for n = 19..26 and zero for the next 1458 consecutive indices, which by the Cayley-Hamilton theorem forces them to be zero for all later n. Certificate and checker: [LINK].

## Notes for the person posting

- The OEIS editors may want the proof written out, not only linked. The method is in `recurrences.md` in this folder's parent.
- Do not post until the certificate repository is public and a human has read the proof.
- None of this was sent to the OEIS.
