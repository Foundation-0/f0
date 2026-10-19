# Scouting report: overlooked corners of public astronomy archives

*Written by an AI research agent (Claude) for Foundation0 on 18 Oct 2026.*

**Checked against the source:** where the agent could, it checked access from a Linux container: DASCH API, Gaia
TAP, MAST TAP and the arXiv API.

**Not checked:** who else works in each area comes from web and arXiv searches, not a full ADS literature search.

Treat every figure as a lead and re-check it before you rely on it. Follow-up: the astronomy hub [astr0](https://github.com/Foundation-0/astr0) and the project this report led
to, [plate-eclipses](https://github.com/Foundation-0/plate-eclipses).

Each area is ranked by three things multiplied together: the chance of a checkable find within days to weeks, its
significance, and how overlooked it is.

## 1. DASCH: century-long light curves from the Harvard plates (highest score)

1. **What is overlooked.** DASCH DR7 is the final data release (29 Dec 2024). It covers the whole sky from about
   1880 to 1990, but almost nobody searches it systematically.
   - arXiv has only 30 abstracts that mention DASCH. Every recent one studies a single known star: V854 Cen
     ([2603.14085](https://arxiv.org/abs/2603.14085)), an R CrB star ([2608.21923](https://arxiv.org/abs/2608.21923))
     and CZ Tuc ([2610.00471](https://arxiv.org/abs/2610.00471)).
   - The project's [publications page](https://dasch.cfa.harvard.edu/publications/) says its lists have not been
     maintained "since around 2013".
   - No all-sky DR7 variability search turned up. Caveat: the search covered arXiv abstracts only, not ADS full text.
2. **Size.**
   - 252,458,490 sources and 23,574,404,199 measurements, from 429,274 plates ([DR7](https://dasch.cfa.harvard.edu/dr7)).
   - Most stars brighter than B ≈ 15 have hundreds to thousands of detections ([2501.12977](https://arxiv.org/abs/2501.12977)).
   - Access: a public JSON API (`api.starglass.cfa.harvard.edu/public/dasch/dr7/{querycat,lightcurve,cutout}`).
     Measured at about 0.55 s per light curve (about 3,200 rows each), with no API key. A FITS plate cutout also
     worked without logging in.
   - Bulk data is about 7.2 TiB of APASS-calibrated photometry. It is not on S3; you request it on the DASCH email
     list, which asks you to request a higher API rate limit first
     ([bulk formats](https://dasch.cfa.harvard.edu/dr7/bulk-formats/)).
3. **How a find is verified.**
   - **Retrodiction and prediction.** Eclipses or dimmings found on the plates imply a period. That period predicts
     events that can be checked straight away against modern surveys (ASAS-SN, ZTF, ATLAS, Gaia epoch photometry), and
     it predicts future events.
   - **Independent plates.** APPLAUSE DR4 has about 70,000 direct plates from other observatories, Gaia-calibrated and
     licensed CC0 ([2404.17355](https://arxiv.org/abs/2404.17355)).
   - **Visual check.** Plate cutouts from the API let anyone look at the plates themselves.
   - **Where to report.** New variables go to [AAVSO VSX](https://www.aavso.org/vsx/); results go to RNAAS or arXiv.
4. **Existing efforts.** The method is proven, but only one star at a time.
   - ASASSN-24fw (a 4.1 mag, 8-month dimming) was traced back to earlier events in 1937 and 1981 using DASCH
     ([2507.03080](https://arxiv.org/abs/2507.03080), [2507.05367](https://arxiv.org/abs/2507.05367)).
   - Modern searches for long eclipses and dimmings use only about a decade of data: the ASAS-SN Big Dippers search
     found 13 single-eclipse long-period binary candidates ([2507.19594](https://arxiv.org/abs/2507.19594)); ZTF
     searched for occultations by circumbinary disks ([2601.16828](https://arxiv.org/abs/2601.16828)).
5. **Pilot proposed.**
   - Fetch DASCH light curves for the 31 Big Dippers objects and look for historical eclipses.
   - Then scan one 10° × 10° field blind.
   - A simple rule (at least 3 consecutive non-detections on deep plates, spanning at least 2 plate series) blindly
     recovered ASASSN-24fw's 1937 and 1981 events.
   - **The catch.** The same rule flagged 21 of 80 stars in that field. The top "event" was a blend with a neighbour
     25″ away. So the pipeline must check comparison stars and the plate images.
6. **Risk.**
   - Artefacts dominate; see DASCH's [known issues](https://dasch.cfa.harvard.edu/dr7/ki/).
   - Only events deeper than about 0.3–0.5 mag are reachable.
   - The payoff is real, citable results that are modest per object.
   - **Outcome:** run on 18 Oct 2026, now [plate-eclipses](https://github.com/Foundation-0/plate-eclipses). It found
     eclipses of ASASSN-21co in 1902 and 1985.

## 2. TESS: long-period transits on stars seen only in full-frame images (extends eumemic/exoplanets)

1. **What is overlooked.** eumemic's search fits periods of 0.5–30 d. Periods of 20–100 d were searched only for
   3,661 K/M dwarfs and 3,271 TOI hosts ([README](https://github.com/eumemic/exoplanets)). Signals with only one or
   two transits on the 4 million full-frame-image stars are untouched. 82% of eumemic's candidates sit on stars outside
   NASA's multi-sector search.
2. **Size.** The 4,039,203 stars and TESS sectors 1–104 the pipeline already holds. Full-frame images are taken every
   30 min in sectors 1–27, every 10 min in 28–55, and every 200 s from sector 56.
3. **How a find is verified.**
   - For each pair of transits, list the possible periods and rule out those contradicted by sectors without a
     transit. The survivors predict transit windows in sectors TESS has not yet observed.
   - Then the existing checks: centroids, Gaia RUWE and TRICERATOPS.
   - Submit as community TOIs on [ExoFOP](https://exofop.ipac.caltech.edu/tess/view_ctoi.php).
4. **Existing efforts.**
   - Hawthorn et al.: 85 candidates with two transits, southern hemisphere, years 1 and 3 only
     ([2310.17268](https://arxiv.org/abs/2310.17268)).
   - Planet Hunters TESS.
   - A TESS single-transit working group.
   - COUNTESS in the northern continuous viewing zone ([2606.13789](https://arxiv.org/abs/2606.13789)).
   - No northern or all-years catalogue of two-transit candidates turned up.
5. **Pilot.**
   - Day 1: a matched filter for single transits (durations 1–24 h) on each sector.
   - Day 2: pair events more than a year apart; list the possible periods; vet.
   - Day 3: cross-match with TOIs.
6. **Risk.** Moderately crowded. Confirmation needs follow-up by other telescopes. Single events are prone to
   systematics.

## 3. Gaia DR4 on day one, checked against TESS (time-critical)

1. **Dates and size.**
   - Release 2 Dec 2026; the archive closes 25 Nov 12:00 CET ([release](https://www.cosmos.esa.int/web/gaia/release)).
   - Epoch photometry: 121,845,163,512 rows (7.2 TB). Epoch astrometry: 62 TB. RVS epoch spectra: 49 TB. About 400 TB
     in total.
   - 1,007 planetary-transit candidates and 2,392,500 eclipsing binaries ([DR4](https://www.cosmos.esa.int/web/gaia/dr4)).
2. **The niche.** Checking Gaia's transit candidates and eclipsing binaries against same-epoch TESS light curves at
   full scale. eumemic's pipeline already holds those light curves.
3. **Competition.**
   - A Flatiron DR4 sprint on 2–4 Dec, and the "Gaia Relay".
   - The Gaia processing consortium itself.
4. **Pilot before 25 Nov.**
   - A fetcher for epoch data through DataLink, tested on DR3.
   - A mapping from TIC to Gaia source IDs.
   - A checker that folds TESS light curves at Gaia's periods.
   - On release day: a public confirm/refute table within 48 h.

## 4. Moving objects in public JWST and recent HST images

1. **What is overlooked.** No search covers the whole archive.
   - One TRAPPIST-1 programme yielded 138 new decametre-size asteroids ([2502.01744](https://arxiv.org/abs/2502.01744)).
   - Hubble Asteroid Hunter covered HST only up to March 2021 ([2202.00246](https://arxiv.org/abs/2202.00246)).
2. **Size (MAST TAP counts).**
   - Public JWST imaging within 10° of the ecliptic: 4,779 observations, about 3,531 h.
   - HST ACS/WFC and WFC3 since March 2021: 26,801 products, about 6,934 h.
3. **Verification.** Recover known asteroids via SkyBoT as a control; submit astrometry to the MPC.
4. **Competition and risk.**
   - Emerging field: Burdanov and de Wit's group; Girmenia & Metchev ([2609.27140](https://arxiv.org/abs/2609.27140)).
   - Heavy compute.
   - Tracklets from a single visit rarely earn designations.

## 5. eROSITA DR1 X-ray sources × TESS/ZTF periodicity: new compact binaries

- **Size.** 930,203 sources ([2401.17274](https://arxiv.org/abs/2401.17274)).
- **Verification.** Public spectra from DESI, LAMOST and SDSS.
- **Competition.** Moderately crowded: counterparts for 656,614 sources ([2509.02842](https://arxiv.org/abs/2509.02842)),
  and 1,000 cataclysmic variables found from DESI spectra ([2607.22836](https://arxiv.org/abs/2607.22836)).
- **Significance.** Modest.

## 6. White dwarfs in TESS 200-second full-frame images

- **Size.** About 359,000 high-confidence white-dwarf candidates ([2106.07669](https://arxiv.org/abs/2106.07669)).
- **Earlier work.** A 2021 search found no planets. WD 1856+534 b, a planet transiting a white dwarf, was rejected by
  an automated classifier and found by eye ([2009.07282](https://arxiv.org/abs/2009.07282)).
- **Risk.** Low chance of a find, very high significance if there is one. TESS pixels (about 20″) dilute the signal.

## Considered and ranked lower (crowded or hard to verify)

- **Fermi 4FGL-DR4.** More than 2,200 unassociated sources, already classified by machine learning
  ([2510.08654](https://arxiv.org/abs/2510.08654)).
- **NEOWISE and unWISE.** Backyard Worlds is still scanning them.
- **Eclipse timing and circumbinary planets.** TESS Ten Thousand ([2506.05631](https://arxiv.org/abs/2506.05631)),
  27 candidates from apsidal precession ([2512.07934](https://arxiv.org/abs/2512.07934)), and others.
- **ZTF and ASAS-SN.** The survey teams mine their own data.
- **VLASS radio transients** ([2506.04522](https://arxiv.org/abs/2506.04522)).
- **Archival asteroids.** The Asteroid Institute mined the NOIRLab Source Catalog DR2. 3I/ATLAS precoveries came
  within weeks.
- **Gaia DR3 orbits.** Heavily mined.
- **Kepler and K2.** Even Campaign 19 has been searched ([2305.18516](https://arxiv.org/abs/2305.18516)).
- **VASCO.** Contested ([2507.15896](https://arxiv.org/abs/2507.15896)).
- **SPHEREx Quick Release.** Watch list: open on AWS, but too new to judge.
