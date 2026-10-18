# Deep fields: where Foundation0 should look next

In December 1995 the Hubble Space Telescope spent ten days on a patch of sky that looked empty, and found about
3,000 galaxies. This folder applies the same idea to science: look for the corners of public data and open problems
that nobody is looking at, where a few people working with AI agents could find something checkable.

On 18 October 2026, four research agents scouted four areas:

- mathematics and computing;
- astronomy archives;
- life-science data;
- physics, Earth science and the humanities.

The most promising lead was then tested in one pilot: [the DASCH pilot](dasch-pilot/). It found two previously
unreported eclipses of the 12-year binary ASASSN-21co, in 1902 and 1985, and measured its period over 120 years.

**Status of this page.** The counts and claims below were checked by the agents on 18 Oct 2026; each links its source.
They are a starting map, not a survey of record. Check a number before you build on it.

## What "overlooked" means now

1. **Famous long tails are no longer empty.** Between July and October 2026, people working with AI swept the
   well-known record tables, often within weeks:
   - [Friedman's Packing Center](https://erich-friedman.github.io/packing/);
   - the [degree–diameter table](https://web.mat.upc.edu/francesc.comellas/delta-d/table_degree_diameter.html), with
     about 15 new contributors in three months;
   - [Brouwer's constant-weight codes](https://www.win.tue.nl/~aeb/codes/Andw.html);
   - Kéri's covering codes ([83 improvements](https://arxiv.org/abs/2608.19872), the first since 2011);
   - [sorting networks](https://bertdobbelaere.github.io/sorting_networks_extended.html);
   - classical Ramsey numbers ([AlphaEvolve](https://arxiv.org/abs/2603.09172),
     [integer programming](https://arxiv.org/abs/2608.18769)).

   A public table with gaps no longer means nobody is working on it.
2. **What stays empty** is work with one of four properties:
   - **Data released as a project ends,** with nobody funded to mine it. DASCH's final data release came in
     December 2024; the recent arXiv papers that mention it each study a single known star.
   - **Joins between archives that no one team owns.** Century-old plates and modern surveys; TESS light curves and
     Gaia DR4.
   - **Results that need a specialised checker before anyone can trust them.** For example, the minimum distance of a
     code over GF(q), or a transfer-matrix proof of a recurrence.
   - **Value that lies in the aggregate rather than a headline.** Thousands of small records, or station-years of
     rescued weather data.
3. **Three questions tell you whether a field is crowded:**
   - Who has published on it in the last 12 months?
   - Is the maintainer still taking submissions, and from how many people?
   - How many entries or objects changed in 2025–26?

## Shortlist

Ranked by the chance of a checkable result within days to weeks, times its significance, times how overlooked the
field is.

| # | Area | Why it is overlooked | How a result is checked | Where to start |
|---|---|---|---|---|
| 1 | **DASCH × modern surveys** (astronomy) | 430,000 Harvard plates scanned, about 252 million sources from 1880 to 1990 ([DR7](https://dasch.cfa.harvard.edu/dr7/)). The project has ended, and nobody is systematically pairing the plates with modern surveys. | Retrodicted and predicted eclipse times; plate images; [VSX](https://www.aavso.org/vsx/), RNAAS | **Pilot done**: [dasch-pilot/](dasch-pilot/). Next: every long-period eclipsing binary or dipper brighter than B ≈ 13.5 with an uncertain period |
| 2 | **Gaia DR4 on day one, checked against TESS** (astronomy) | Out 2 Dec 2026, about 400 TB, including 1,007 planetary-transit candidates and 2.39 million eclipsing binaries ([DR4](https://www.cosmos.esa.int/web/gaia/dr4)). Foundation0 already holds TESS light curves for 4 million stars ([eumemic/exoplanets](https://github.com/eumemic/exoplanets)). | The same-epoch TESS light curve confirms or refutes each Gaia signal | **Time-critical.** The archive closes on 25 Nov ([release](https://www.cosmos.esa.int/web/gaia/release)). Build the TIC-to-Gaia mapping and the folding checker before then |
| 3 | **Linear codes over GF(3)–GF(9)** (mathematics) | About 79,000 open entries in [codetables.de](https://www.codetables.de/BKLC/index.html) outside the binary table. In a random sample, 77% were last changed in 2001–2009. AI work so far targets binary codes. | A generator matrix, whose minimum distance anyone can recompute; sent to the maintainer, Markus Grassl | Build an open minimum-distance checker over GF(q) first. Many gaps reflect weak upper bounds, and Grassl runs his own quasi-cyclic sweep |
| 4 | **Literature integrity at full PubMed Central scale** (metascience) | The largest screen of wrong nucleotide reagents covered about 11,700 papers ([Park et al. 2022](https://www.life-science-alliance.org/content/5/4/e202101203)), limited by checking each hit by hand. About 8 million article versions sit in [an open S3 bucket](https://registry.opendata.aws/ncbi-pmc). | Anyone can re-run BLAST or redo the arithmetic | Frame every hit as a question for the authors (PubPeer), not an accusation. Requires a person's judgement before anything is posted |
| 5 | **Quality control of public sequence data with Logan** (biology) | [Logan](https://github.com/IndexThePlanet/Logan) assembled all 38 million runs in NCBI's sequence archive. Audits of cell-line contamination and mislabelled samples predate it. | Marker k-mers, such as HPV18 for HeLa cells, that anyone can re-check from the public run. The scout found HPV18 in a HeLa run and none in runs labelled MCF-7. | Screen a few hundred runs labelled with one cell line |
| 6 | **OEIS "empirical" recurrences** (mathematics) | About 16,180 entries by R. H. Hardin give recurrences found by computer but never proved ([search](https://oeis.org/search?q=Empirical+author%3AHardin)). | Transfer-matrix proofs a small program can check | OEIS [requires permission](https://oeis.org/wiki/Use_of_AI_for_OEIS_Submissions) for bulk AI submissions. Publish the proofs on Zenodo first, then ask the editors |
| 7 | **Circulant weighing matrices and design existence** (mathematics) | 2,773 open cases in [Gordon's table](https://dmgordon.org/circulant-weighing-matrices/); Handbook design types the [CPro1](https://github.com/Constructive-Codes/CPro1) tool never tried. | The first row of the matrix, checked instantly | Exclude the cases recently proved impossible ([2608.18468](https://arxiv.org/abs/2608.18468)) |
| 8 | **Climate data rescue** (Earth science) | 5,424 scanned foreign weather bulletins, 193 GB, in a public NOAA bucket. AI transcription so far has focused mainly on UK records. | Agreement between two AI models; comparison with the 20CRv3 reanalysis | Transcribe station-years missing from ISPD and offer them to its curators. Little headline value, but a high chance of useful output |
| 9 | **Archived temporary seismic networks** (Earth science) | About 727 passive networks of 10 or more stations, each running a year or more, built to image the Earth's interior and rarely used to catalogue local earthquakes ([EarthScope](https://service.earthscope.org/fdsnws/station/1/)). | Anyone can re-run open code on the open waveforms; compare with the ISC Bulletin | Check prior work for each network: the first one spot-checked had already been reprocessed |
| 10 | **Alternative genetic codes in metagenome-assembled genomes (MAGs)** (biology) | Codon-reassignment screens covered isolate genomes; the 1.16 million MAGs in [SPIRE](https://spire.embl.de) are largely unscreened. A new reassignment turned up in 2025. | Three independent signals: codon usage, loss of the matching release factor, and a tRNA with the right anticodon | Run [Codetta](https://github.com/kshulgina/codetta) on one biome |

**Also worth a look:**
- unpublished results posted to ClinicalTrials.gov (80,551 trials have posted results);
- structured-RNA candidates waiting to enter Rfam;
- matching cuneiform fragments in the [eBL](https://www.ebl.lmu.de/) corpus;
- searching TESS for long-period planets that show only two transits years apart (a direct extension of eumemic's search);
- asteroids in public JWST images.

## Crowded: not deep fields any more

- **Mathematics:** the record tables listed above, plus cages and kissing numbers. Erdős problems:
  [DeepMind's proof agent](https://arxiv.org/abs/2605.22763) and
  [formal-conjectures](https://github.com/google-deepmind/formal-conjectures) are there. Busy Beaver BB(6) has an
  active community.
- **Astronomy:**
  - Fermi's unassociated gamma-ray sources (already classified with machine learning);
  - Kepler and K2 leftovers;
  - Gaia DR3 orbits;
  - NEOWISE brown dwarfs (Backyard Worlds);
  - VASCO's vanishing stars;
  - archival asteroids in survey catalogues.
- **Biology:** finding new RNA viruses, obelisks, antimicrobial peptides and plastic-degrading enzymes in the
  sequence archive; reclassifying ClinVar variants of uncertain significance.
- **Physics and humanities:** CMS open data (now including agent-run analyses), LIGO public data, materials
  databases such as GNoME, the Herculaneum scrolls, and undeciphered scripts. Claims about undeciphered scripts cannot
  be checked.

## Recommendation

1. **Scale the DASCH pilot.** It already produced a checkable result.
   - Write up ASASSN-21co after a person has checked it, as a short RNAAS note with the ASAS-SN authors.
   - Then run the targeted test on every bright, long-period eclipsing binary that has one or two modern eclipses.
2. **Prepare for Gaia DR4 with eumemic before 25 November.** No one else holds full-frame TESS light curves for
   4 million stars ready for a same-day check.
3. **Start one mathematics thread with a checker first:** non-binary codes or the OEIS recurrences. Contact the
   maintainer before submitting in bulk.
4. **Life sciences:** choose between the literature screen and Logan quality control. Both need a person's judgement
   on how findings are reported.

## Files

- [`dasch-pilot/`](dasch-pilot/): code, results and write-up of the first pilot.
