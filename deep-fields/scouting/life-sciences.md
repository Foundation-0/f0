# Scouting report: overlooked corners of public life-science data

*Written by an AI research agent (Claude) for Foundation0 on 18 Oct 2026. Treat every figure as a lead and re-check
it before you rely on it.*

**Access checks the agent ran from a Linux container** (all anonymous HTTPS or S3):

- **Logan** (`s3://logan-pub`): lists fine.
  - Downloaded HeLa RNA-seq unitigs (57 MB) in about a second.
  - A 31-mer scanner found a strong HPV18 signal in HeLa: 1,086 unitigs containing HPV18, covering 55% of HPV18's
    31-mers.
  - It found **no** HPV18 or HPV16 in MCF-7 runs, the correct negative control.
  - The scan took 12–34 s per run on 4 cores. The scripts are in [`logan-qc/`](logan-qc/).
- **Tools:** MMseqs2, Foldseek, DIAMOND 2.1.10 and pyhmmer all install and run (15 GB RAM, 4 cores).
- **Verified live:**
  - PMC Open Access on S3 (`pmc-oa-opendata`, about 8 million article versions);
  - ClinicalTrials.gov API v2 (607,349 studies; 80,551 with posted results);
  - GBIF API (3.98 billion occurrences; 287.6 million preserved specimens; 78.5 million with images);
  - the SRA open-data bucket on S3 and the SRA taxonomy table on BigQuery;
  - the NCBI Datasets API (74,180 eukaryote assemblies, 12,342 annotated by NCBI).

## Headline

The famous targets in Logan and the SRA are now **crowded** and should not count as overlooked: new RNA viruses,
obelisks, antimicrobial peptides and PET-degrading enzymes (evidence below). The real openings are of two kinds:

- **metascience and quality control of public data,** at a scale nobody has reached;
- **a few biological niches** the big teams have skipped.

Each area is ranked by three things multiplied together: the chance of a checkable result within days to weeks, its
significance, and how overlooked it is.

## 1. Literature integrity: automated reagent and statistics checks across PubMed Central

1. **What is overlooked.** Error-detection tools are a decade old, and the bottleneck is checking each hit by hand,
   not access to data. Seek & Blastn checks whether a paper's primer or siRNA sequence matches its stated target. It
   has been applied to only about 11,700 papers, because every hit was checked by hand. statcheck and GRIM have the
   same limit. An AI agent removes exactly that bottleneck.
2. **Untouched data.**
   - PMC Open Access on AWS: `s3://pmc-oa-opendata`, about 8 million article versions, readable by anyone
     ([README](https://pmc-oa-opendata.s3.amazonaws.com/README.txt)).
   - Largest prior screen: 712 problematic papers among about 11,700; 1,535 wrong sequences; cited 17,183 times
     ([Park, Byrne, Labbé 2022](https://www.life-science-alliance.org/content/5/4/e202101203)).
3. **How a find is checked.** Anyone can reproduce a wrong-reagent hit by re-running BLAST, and a GRIM failure is
   arithmetic. Post findings as PubPeer comments that give the exact sequence and BLAST output, and cross-check against
   the [ICLAC register](https://iclac.org/databases/cross-contaminations/) of misidentified cell lines.
4. **Room left.** Byrne, Labbé, Bik and the Problematic Paper Screener are limited by capacity. Publishers screen only
   new submissions.
5. **Pilot.**
   - Pull the text of 5,000 open-access oncology papers.
   - Extract nucleotide sequences and their "targets"/"non-targeting" claims; BLAST them; flag mismatches.
   - Recompute the reported p-values from the stated test statistics.
6. **Risk.** Reputational care: present each finding as "needs an author response", not as fraud. Filter out
   legitimate non-targeting controls.

## 2. Quality control of public sequence data with Logan (cell-line, contaminant and species mislabels)

1. **What is overlooked.** The last systematic audits predate Logan:
   - sex-label mismatches in about 46% of transcriptomic datasets
     ([Toker 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5034794/));
   - mycoplasma in about 11% of SRA series ([2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4357728));
   - about 33,000 papers using misidentified cell lines
     ([Horbach & Halffman 2017](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0171435)).
2. **Untouched data.** Logan v1.2 covers 38.1 million SRA runs with each run's assembly downloadable on its own
   ([Logan](https://github.com/IndexThePlanet/Logan)). The SRA holds about 2.5 million human RNA-seq experiments.
3. **How a find is checked.**
   - Marker k-mers: HPV18 integration for HeLa.
   - SNP fingerprints against Cellosaurus and CCLE.
   - Expression of sex-chromosome markers.
   - The STAT taxonomy table.
   - Mycoplasma rRNA k-mers.
4. **Pilot (validated here).** `zstd -dc run.unitigs.fa.zst | grep -F -f marker_kmers`. Screen a few hundred runs
   labelled as one cell line.
5. **Risk.** Minimal biosafety risk. The output cleans the inputs to thousands of downstream analyses.

## 3. Alternative genetic codes across metagenome-assembled and eukaryotic genomes

1. **What is overlooked.**
   - Screens so far covered about 250,000 isolate genomes of bacteria and archaea
     ([Codetta](https://elifesciences.org/articles/71402)).
   - A fourth phylum with UGA read as tryptophan turned up in 34 gut metagenome-assembled genomes (MAGs) only in
     Dec 2025 ([bioRxiv](https://www.biorxiv.org/content/10.64898/2025.12.01.691617v1)).
   - The large MAG catalogues and most eukaryotic nuclear genomes have never been screened.
2. **Data.** [SPIRE](https://spire.embl.de): 1.16 million MAGs, including 78,804 species clusters that cannot be
   classified. GTDB. About 62,000 eukaryote assemblies with no annotation.
3. **How a find is checked.** Three independent signals:
   - the codon is used in frame where homologous genes have a specific amino acid;
   - the matching release factor is lost;
   - a tRNA with the matching anticodon exists.
4. **Pilot.** Run Codetta on a few thousand SPIRE MAGs from one biome, then confirm with release factors and tRNA
   anticodons.
5. **Risk.** None for biosafety. A new genetic code is a textbook-level finding.

## 4. Unpublished clinical-trial results: bringing the file drawer into evidence reviews

1. **What is overlooked.**
   - About half of the trials with results posted on ClinicalTrials.gov were never published in a journal.
   - Few systematic reviews search the registry: 11.3–11.8% in two specialties
     ([PubMed](https://pubmed.ncbi.nlm.nih.gov/40542645/)).
2. **Data.** ClinicalTrials.gov API v2: 80,551 studies with posted results ([API](https://clinicaltrials.gov/data-api/api)).
3. **How a find is checked.** The sponsor-posted tables speak for themselves. Show whether adding them changes a
   published meta-analysis.
4. **Pilot.** Pick one drug class, pull every registry result, find the published meta-analyses, and pool them again.

## 5. Structured RNAs from metagenomes, to fill the Rfam gap

- **What is overlooked.** Rfam 15 added only about 16 new non-miRNA families and cannot take in many published
  candidates ([Rfam 15](https://pmc.ncbi.nlm.nih.gov/articles/PMC11701678/)). Thousands of candidates sit unused in
  papers ([Fremin & Bhatt](https://pmc.ncbi.nlm.nih.gov/articles/PMC8040213/)).
- **How a find is checked.** Statistically significant covariation of paired bases (R-scape), the gold standard.
- **Effort.** Slower than the other leads.

## 6. Dark protein families, assigned a function from genomic context

- **What is overlooked.** Clustering protein structures is crowded: Foldseek clusters of the AlphaFold Database,
  AFESM, and an ESM atlas of 1.1 billion structures. Assigning functions from operon context and co-occurrence is
  much less done.
- **Data.** Logan's protein clusters (`s3://logan-pub/p/`).
- **Phenotype evidence.** The [LBNL Fitness Browser](https://fit.genomics.lbl.gov) has phenotypes for 11,779 genes
  of unknown function.
- **Competition.** DOE's BERIL project is starting on this.
- **Red line.** Avoid toxin and virulence families.

## 7. Undescribed species in museum and GBIF records (honourable mention)

- **What is overlooked.** More than half of undescribed flowering plants may already sit in herbaria
  ([Bebber 2010](https://www.pnas.org/doi/10.1073/pnas.1011841108)).
- **Data.** GBIF has 78.5 million specimen records with images.
- **Limit.** Describing a new species needs a taxonomist. Agents can only flag candidates.

## Avoid (crowded)

- **New RNA viruses, obelisks, antimicrobial peptides and PET enzymes from Logan or the SRA:**
  - LucaProt found 161,979 RNA-virus species ([PubMed](https://pubmed.ncbi.nlm.nih.gov/39389057/));
  - obelisks number 29,959;
  - AMPSphere holds 863,498 antimicrobial peptides;
  - the Logan paper itself mined most of these.
- **Biosafety red line:** cataloguing divergent viruses from public assemblies is acceptable. Anything approaching
  reconstructing a pathogen, expanding its host range or enhancing it is out.
- **ClinVar variants of uncertain significance and FAERS signals:** crowded, and causality is weak. Avoid
  controlled-access patient data entirely.
