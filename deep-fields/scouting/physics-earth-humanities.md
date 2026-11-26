# Scouting report: overlooked public data in physics, Earth science, chemistry and materials, and the humanities

*Written by an AI research agent (Claude) for Foundation0 on 18 Oct 2026. Web searches and API tests run from a
container. The arXiv API returned errors and OpenAlex was rate-limited, so checks on who else works in each area are
not exhaustive. Treat every figure as a lead and re-check it before you rely on it.*

**Follow-up:** the [physics0 leads](https://github.com/Foundation-0/physics0) hold the network and climate-scan
inventories.

## 1. DASCH: 100 years of Harvard photographic plates

This was ranked first here as well; see [astronomy.md](astronomy.md) §1 and the project it became,
[plate-eclipses](https://github.com/Foundation-0/plate-eclipses).

- **Size.** About 430,000 plates covering about 1880 to 1990; about 24 billion magnitudes for about 250 million
  sources.
- **Access.** The public API needs no key: one light curve of 3,753 points took 6 s.
- **Where to report.** New variables go to [VSX](https://vsx.aavso.org) (one submission per day); results go to
  RNAAS or JAAVSO.
- **Risk.** Plate systematics: the 1950s–60s "Menzel gap" ([Hippke et al.](https://ar5iv.arxiv.org/html/1605.02760)).

## 2. Climate data rescue with vision-language models

1. **What is overlooked.**
   - NOAA's Foreign Climate Data scans sit in a publicly listable S3 bucket: 5,424 PDFs, 193 GB, in 386 CD folders
     ([listing](https://s3.amazonaws.com/library.oarcloud.noaa.gov?list-type=2&prefix=docs.lib/htdocs/rescue/cd)).
   - Example: Argentina's *Resumen Mensual del Tiempo* for July 1942, 48 pages of typed coded observations.
   - The collection was called "untapped" in 2011 ([CRU poster](https://crudata.uea.ac.uk/cru/posters/2011-04-CW-CDMP.pdf)).
2. **Wider backlog.** At least hundreds of thousands of ships' logbooks have never been used in climate work.
3. **How results are checked.** Compare the transcriptions with the 20CRv3 reanalysis and check that the variables
   are physically consistent. The data can go to:
   - the International Surface Pressure Databank (ISPD), which feeds 20CRv3 (Gil Compo,
     [PSL](https://psl.noaa.gov/data/20CRv3_ISPD_obscounts/));
   - ICOADS, through [RECLAIM](https://www.icoads.noaa.gov/reclaim);
   - [Copernicus (C3S) data rescue](https://datarescue.climate.copernicus.eu/aiml-and-data-rescue).
4. **Room left.** UK records are already being transcribed with AI by Hawkins and Brohan, for about £0.10 per 144
   tables ([post](https://climatelabbook.substack.com/p/data-rescue-with-ai)). National bulletins from other countries
   look much less covered.
5. **Pilot.**
   - Inventory about 50 PDFs.
   - Check each station and period against ISPD.
   - Transcribe with two VLMs and check where they disagree.
   - Validate against 20CRv3.
6. **Risk.** The output is data, not headlines. Some volumes may already have been typed up offline.

## 3. Archived temporary seismic networks never used for local catalogues

1. **What is overlooked.** Most PASSCAL-style deployments were run to image the Earth's interior, not to catalogue
   small local earthquakes.
2. **Size (counted on 18 Oct).** The [EarthScope station service](https://service.earthscope.org/fdsnws/station/1/)
   lists 1,441 networks:
   - 1,174 have temporary codes;
   - about 1,098 look passive;
   - 727 have 10 or more stations and ran a year or more. A re-count with explicit rules (temporary code, no
     active-source keywords, at least 10 stations, at least 360 days) gave 752; see physics0.
   - A network of 32 stations running 14 months is about 150 GB.
3. **How results are checked.** Anyone can re-run open code on the open waveforms. Compare with the ISC Bulletin.
   Publish in Seismica, SRL or GJI.
4. **Room left.** Reprocessing so far is ad hoc. **Caveat:** the first network spot-checked (Cameroon XB) had already
   been reprocessed with deep learning in 2024.
5. **Pilot.**
   - Choose 3 unstudied networks.
   - Run one month through [SeisBench](https://github.com/seisbench/seisbench) PhaseNet, then association and location.
   - Compare with the ISC Bulletin.

## 4. Identifying cuneiform fragments

1. **Size.** The [eBL API](https://www.ebl.lmu.de/api/statistics) reports:
   - 38,579 transliterated fragments;
   - 627,577 lines;
   - 328,409 fragments catalogued;
   - "thousands" still unidentified.
2. **Check.** Align sign sequences against known compositions; Assyriologists at LMU confirm.
3. **Risk.** It overlaps eBL's own tools. The people who can confirm a match are a small expert group.

## 5. Natural-product structures that may be wrong

- **Data.** NP-MRD holds 281,859 compounds and 5.5 million spectra.
- **Check.** DFT NMR calculations with DP4+ statistics, which anyone can reproduce.
- **Who else.** Most structure revisions come from one group.
- **Cost.** Heavy compute.

## 6. Atomic spectra: new energy levels

- **What is overlooked.** Lanthanide atomic data is in short supply, which matters for kilonova models.
- **Data.** The NSO Kitt Peak spectrometer archive is downloadable.
- **Check.** Ritz combination statistics.
- **Who else.** Imperial now uses machine learning ([2509.16184](https://arxiv.org/abs/2509.16184)).
- **Effort.** The data is hard to work with, and the work needs an expert partner.

## 7. Archaeology in LiDAR collected for other purposes

- **Precedent.** The Maya city of Valeriana was found in an environmental LiDAR survey.
- **Already taken.** That dataset has since been reprocessed.
- **Looting risk.** Site coordinates must go through national heritage bodies.

## Crowded or not workable

- **CMS open data.** The collaboration runs its own anomaly searches. Agent-run analyses already exist
  ([2603.20179](https://arxiv.org/abs/2603.20179)).
- **LIGO public data.** Independent pipelines from IAS and AresGW; GWTC-4 adds 128 candidates.
- **Materials databases such as GNoME.** The novelty of their compounds is disputed, and confirming one needs a lab.
- **Herculaneum scrolls.** Crowded on purpose, by a prize.
- **Undeciphered scripts.** Claims cannot be checked.
- **Oxyrhynchus papyri.** The unpublished images are not public.
- **Honourable mention.** Old spacecraft data: a plasmoid was found in Voyager 2's 1986 data in 2020.
