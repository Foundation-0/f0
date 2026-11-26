"""Count how many 31-mers of each reference FASTA occur in a Logan unitigs .fa.zst file.
Usage: python3 -I kmer_hits.py UNITIGS.fa.zst REF1.fa [REF2.fa ...]
"""
import sys, io, zstandard

K = 31
COMP = str.maketrans("ACGT", "TGCA")


def canon(s):
    r = s.translate(COMP)[::-1]
    return s if s < r else r


def read_fasta_seq(path):
    seq = []
    with open(path) as f:
        for line in f:
            if not line.startswith(">"):
                seq.append(line.strip().upper())
    return "".join(seq)


refs = {}
for p in sys.argv[2:]:
    s = read_fasta_seq(p)
    s2 = s + s[: K - 1]  # circular genome
    refs[p] = {canon(s2[i:i + K]) for i in range(len(s)) if "N" not in s2[i:i + K]}

allk = {}
for p, ks in refs.items():
    for k in ks:
        allk.setdefault(k, set()).add(p)

found = set()
n_unitigs = 0
dctx = zstandard.ZstdDecompressor()
with open(sys.argv[1], "rb") as fh:
    text = io.TextIOWrapper(dctx.stream_reader(fh), encoding="ascii")
    for line in text:
        if line.startswith(">"):
            n_unitigs += 1
            continue
        s = line.strip().upper()
        for i in range(len(s) - K + 1):
            c = canon(s[i:i + K])
            if c in allk:
                found.add(c)

print("unitigs", n_unitigs)
for p, ks in refs.items():
    hit = len(ks & found)
    print(f"{p}\t{hit}/{len(ks)}\t{hit/len(ks):.3f}")
