# Logan quality-control pilot: is that cell line really what the label says?

Scripts from the life-science scouting of 18 Oct 2026 (lead 2 in [../life-sciences.md](../life-sciences.md)).

[Logan](https://github.com/IndexThePlanet/Logan) has assembled every run in NCBI's Sequence Read Archive, and each run's
assembly can be downloaded on its own from a public bucket. That makes it cheap to check whether a run's sequence
agrees with its label. The marker used here is HPV18 DNA, which is integrated into HeLa cells. A run labelled as
another cell line that contains HPV18 is a candidate for HeLa contamination.

| File | What |
|---|---|
| `kmer_hits.py` | Counts how many 31-mers of each reference genome occur in one run's Logan unitigs. |
| `screen_runs.sh` | Fetches, scans and deletes the unitigs for a list of runs; writes `results.tsv`. |

**Reference genomes.** Fetch them from NCBI RefSeq:

```
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_001357&rettype=fasta" > hpv18.fa
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_001526&rettype=fasta" > hpv16.fa
```

**What the scout's runs showed.**

| Run | Label | Result |
|---|---|---|
| SRR13264595 | HeLa | Strong HPV18 signal: 55% of HPV18's 31-mers present, in 1,086 unitigs |
| DRR342062, DRR342063, DRR342064, DRR342065, SRR23698588 | MCF-7 | No HPV18 |

One MCF-7 run (SRR23698588) has a single 32-base unitig matching HPV16, which is noise at this level. The control
behaves as expected. Each run took 12–34 s on 4 cores.

**Next.**
- Screen a few hundred runs labelled as one non-HeLa cell line.
- Add markers for sex (chrY genes), mycoplasma rRNA and other species.
- Confirm any hit with SNP fingerprints against Cellosaurus or CCLE before telling anyone.
- A contaminated dataset is a question for its authors, not an accusation.
