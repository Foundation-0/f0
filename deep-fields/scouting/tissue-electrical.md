# Scouting report: electrical properties of human tissue

*Written by an AI research agent (Claude) for Foundation0 on 31 Oct 2026, at a person's request. Treat
every figure as a lead and re-check it before you rely on it. Nothing here has been sent to anyone yet.*

**What "electrical properties" means here.** These are conductivity σ (S/m) and relative permittivity εr, from DC to
about 100 GHz. They set how fields and currents spread through the body. Every simulation of MRI heating, phone and 5G
exposure, transcranial and deep-brain stimulation, EEG and MEG source localisation, electrical impedance tomography,
tumour-treating fields or hyperthermia needs a value for each tissue.

**Access checks the agent ran from a Linux container** (all anonymous HTTPS):

- **IT'IS Tissue Properties Database V5.0** (21 Aug 2025, [DOI 10.13099/VIP21000-05-0](https://itis.swiss/virtual-population/tissue-properties/downloads/database-v5-0)):
  a direct 5.7 MB zip, with no registration. It includes ASCII and Excel tables and the SQLite material database that
  Sim4Life imports. The documentation PDF has no text layer, so the agent read it from page images.
- **NICT Database of Tissue Dielectric Properties** ([site](https://www2.nict.go.jp/cgi-bin/202303080003/public_html/index.py),
  launched 30 Mar 2023): the parametric-model CSV for 57 tissues downloads directly. NICT's measured spectra
  (58 tissues, 1 MHz to 100 GHz) sit behind a terms-of-use page. The agent did not accept the terms for anyone, so
  those spectra were not used.
- **IFAC-CNR** ([tissprop](https://niremf.ifac.cnr.it/tissprop/)): the standard calculator for the Gabriel model, and
  an authorised mirror of the 1996 Gabriel report. Its parameter and data tabs load by script, so the agent did not
  scrape them.
- **Sasaki, Wake and Watanabe (2014)**, [Radio Science 49:459](https://doi.org/10.1002/2013RS005345), is paywalled;
  the person who asked for this report supplied a copy. Table 2 is transcribed in the pilot.
- **NHANES 1999–2004 bioimpedance** (`BIX` files) downloads directly from CDC (4.9 MB for 1999–2000).

## Headline

1. **The field runs on one 30-year-old parametric model.** The four-term Cole-Cole fits of
   [Gabriel, Lau and Gabriel (1996)](https://doi.org/10.1088/0031-9155/41/11/003) to 1990s measurements, mostly of
   animal tissue, are the default in IT'IS, Sim4Life, the IFAC calculator and most dosimetry. Two newer public sets
   exist: Sasaki's 2014 refits of Gabriel's own data (1 MHz–20 GHz), and NICT's 2023 fits to new measurements
   (1 MHz–100 GHz). The agent found no published tissue-by-tissue cross-check of the three public tables. That is the opening.
2. **A pilot found one transcription error and one outlier tissue.** The pilot cross-checked the three tables tissue
   by tissue ([`tissue-electrical/`](tissue-electrical/)):
   - The IT'IS "alternative" (Sasaki) dataset gives the **urinary bladder wall the aorta's parameters**, in both the
     ASCII table and the SQLite database Sim4Life imports, since V4.2 (June 2024).
   - **Gabriel's bladder permittivity is 30–40%** of what NICT measured (128 MHz) and of what its water content
     predicts (900 MHz).
   - The IT'IS **"Water"** entry mixes 8 °C and 24 °C parameters.

   All three can be checked from public files in seconds.
3. **Low-frequency conductivity is the weakest number in the field, and the most consequential.** At 100 Hz the
   Gabriel model is 4–12 times below the measured literature for brain, nerve, liver, heart and cartilage. Gabriel and
   IT'IS both say so, but low-frequency work still evaluates it there. Skull conductivity in the IT'IS compilation
   ranges from 0.0032 to 0.114 S/m across studies. Together with head segmentation
   ([Puonti et al. 2020](https://doi.org/10.1016/j.neuroimage.2019.116431)), that spread is a leading source of error
   in EEG source localisation and brain-stimulation dosimetry.

## 1. The pilot: three tables, checked against each other and against physics

Full results, method and caveats: [`tissue-electrical/README.md`](tissue-electrical/README.md). It runs in about
2 s with `./fetch.sh && python3 audit.py`.

| # | Check | Result | How anyone re-checks it |
|---|---|---|---|
| B | Each IT'IS V5.0 "alternative" entry against the row of Sasaki (2014) Table 2 its declared source names | 94 of 95 match. **Urinary Bladder Wall carries row 1 (Aorta)** instead of row 2 (Bladder), which no entry uses. The same is true in the SQLite database's "4.2-sasaki" and "5.0-sasaki" versions. At 128 MHz this gives εr 61.5 / σ 0.45 S/m instead of 19.2 / 0.27. | Compare `Alternative_dielectric_properties_database_V5.0(ASCII).txt` with Table 2 of the paper |
| C | Gabriel vs Sasaki vs NICT at 64 MHz–2.45 GHz, 45 tissue pairs | 19 of 45 pairs agree within 25% at 128 MHz. NICT's conductivity is typically a little lower (median 0.87× Gabriel, IQR 0.76–0.98), which is consistent with measurements at 30–37 °C. **Bladder runs the other way:** εr 73.7 vs 21.9, σ 2.8× higher. Surrogate assignments in IT'IS (thyroid for pancreas, mammary gland, pituitary and pineal; muscle for diaphragm) differ from NICT's direct measurements by up to 2.2× in σ (diaphragm). | Evaluate the three published parameter sets |
| D | Gabriel εr at 900 MHz against IT'IS water content, 40 tissues | εr ≈ 0.80 × water% − 9.5, rms scatter 8.0. **Bladder is the largest outlier**: 18.9 where 46.6 is expected (−3.4 rms). Nerve is next (−2.5 rms). NICT's bladder (59.7) lies above the trend. | Same |
| E | Physical bounds | The IT'IS **Water** entry's static permittivity is 84.6 (pure water at 7.9 °C) but its relaxation time is that of water at 24.4 °C; unchanged since V4.0. The Sasaki CSF fit, whose data start at 130 MHz, gives εr 9,111 at 1 MHz, while IT'IS documents the set as valid above 1 MHz. Several fluid fits exceed pure water's permittivity between 10 and 300 MHz. | Malmberg & Maryott (1956); Liebe et al. (1991) |
| A | Gabriel σ at 100 Hz against the IT'IS low-frequency compilation | More than 3× below for 11 of 22 tissues with their own fit (nerve ×12, white matter ×6, liver ×4.9, grey matter ×4.7). Outside the compiled min–max range for 15. This is a documented limitation, now with numbers per tissue. | Same |

**Why bladder matters.** The bladder wall sits next to the uterus, prostate and rectum. Its properties enter
specific-absorption-rate (SAR) estimates for pelvic MRI, for pregnant-patient and fetal exposure models, and for
hyperthermia and electroporation planning. The transcription error can be confirmed today. Gabriel's bladder
*measurements*, not only his fit, appear to be low: Sasaki's least-squares fit to the same data gives εr 19.2 at
128 MHz. Why is open. One possibility is that a thin wall measured with a probe also senses the backing. Gabriel's
1996 measured spectra are now downloadable for 41 tissues from the [IFAC/webnir mirror](https://webnir.eu/04-Dosimetry/04-Gabriel.php?lang=gb),
so the next step is to compare those spectra with NICT's.

**What the pilot does not show.** Simulations using these tables are not wrong in general. Sasaki (2014) found
whole-body average SAR changed by less than 5% between its fits and Gabriel's. Local quantities (peak SAR in an organ,
the field in the bladder or prostate) are what a wrong row moves.

## 2. Leads

Ranked by the chance of a checkable result within days to weeks, times its significance, times how overlooked it is.
Numbers marked *(survey)* come from a second agent's literature survey of 31 Oct 2026. It opened each source, but
those numbers were not re-checked for this report.

| # | Lead | Why it is overlooked | How a result is checked | Start |
|---|---|---|---|---|
| 1 | **Finish the cross-check of the public tissue tables** | Everyone uses the tables; nobody audits them against each other. The pilot found a transcription error in a release used by a commercial simulator. | Deterministic: anyone re-runs `audit.py` | Report the bladder row and the water entry to IT'IS (a person sends it). Add Gabriel's 1996 measured spectra (webnir CSV) and NICT's measured spectra (after a person accepts NICT's terms), then compute residuals per tissue and band. |
| 2 | **NHANES 1999–2004 raw bioimpedance spectra** | About 13,300 people aged 8–49 (4,269 in 1999–2000; 2001–04 counts from the survey) measured at 50 frequencies (5 kHz–1 MHz) on a Xitron Hydra 4200, with the raw resistance and reactance at every frequency, and linked to mortality. In 1999–2000 alone, 133 spectra "could not be fit" and 1,042 have no data. The survey found 6 papers using these files, all with 50 kHz values or CDC's own Cole outputs; none refit the raw spectra *(survey; PubMed keyword search, may be incomplete)*. | Refit the Cole model and reproduce CDC's Re, Ri and fc. Then test whether full-spectrum features predict mortality better than 50 kHz phase angle, holding out one survey cycle. Public data, open code. | [BIX.htm](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/1999/DataFiles/BIX.htm), `BIX_B`, `BIX_C`; no application needed |
| 3 | **Score head-model conductivity defaults against in vivo intracranial voltages** | Tools disagree on the skull-to-brain conductivity ratio: about 1:27 in SimNIBS and ROAST, 1:80 in FieldTrip and Brainstorm, and 1:50 in the McCann meta-analysis *(survey)*. The [CRCNS tes-1](https://crcns.org/data-sets/methods/tes-1/about-tes-1) data (14 patients, 1,846 intracranial electrodes, MRI and segmentations; free account) allow scoring. | Error against measured voltages per subject; anyone can re-run | Partly done: [Huang et al. 2017](https://doi.org/10.7554/eLife.18834) calibrated on it, and [Puonti et al. 2020](https://doi.org/10.1016/j.neuroimage.2019.116431) compared four pipelines and showed segmentation differences matter. What is open is a conductivity-only scoreboard with segmentation held fixed. |
| 4 | **The skin values behind the 6–300 GHz limits** | ICNIRP 2020 Table 10 takes dermis values from Sasaki's porcine in vitro measurements *(survey)*. NICT now publishes the dermis and epidermis data; in vivo human skin at 15–110 GHz depends strongly on stratum corneum thickness *(survey; [Christ et al. 2025](https://doi.org/10.1002/bem.70025))*. | Recompute penetration depths from NICT's data to two significant figures and compare with the in vivo skin models | NICT dermis/epidermis CSVs (terms page); ICNIRP 2020 Table 10 |
| 5 | **In vivo vs ex vivo correction table** | Gabriel's human samples were autopsy tissue taken 24–48 h after death (IFAC mirror). Grey-matter conductivity falls about 11–15% within an hour of death in pigs, and 7 T MR-EPT reads higher than ex vivo tables *(survey)*. No per-tissue table of in vivo/ex vivo ratios exists. | Each ratio traces to a paired measurement; a reviewer can recompute it | PubMed. The IT'IS documentation says its low-frequency compilation mixes direct-current, EIT, MREIT and DTI-derived values, so start from its reference list |
| 6 | **Is tumour "contrast" just water?** | Breast cancer differs from fibroglandular tissue by about 10% at most (Lazebnik 2007); lung tumour matches dense fibrosis (Farina 2023) *(survey)*. Raw spectra are not public. | Pool the published Cole-Cole tables with water content; reproducible from published numbers alone | [Lazebnik 2007](https://doi.org/10.1088/0031-9155/52/20/002), [Farina 2023](https://doi.org/10.3390/cancers15143738) |

**Also worth a look:**

- Test-retest repeatability of open MR-EPT methods on the public UNSW in vivo brain scans: 5 subjects, GPL licence,
  [doi:10.26190/M3F9-1N36](https://doi.org/10.26190/M3F9-1N36). The survey could not open the page.
- Muscle anisotropy in vivo: 0.13 vs 0.56 S/m across vs along fibres below 10 kHz, with a supplementary table *(survey;
  [doi:10.1002/bem.22541](https://doi.org/10.1002/bem.22541))*. Compare with the IT'IS anisotropic entries, whose
  maximum along-fibre muscle value is 5.37 S/m, an outlier worth tracing to its source.
- Diffusion-to-conductivity models (NODDI, SANDI and SMT) give substantially different conductivity tensors from the
  same scans, and none has been checked against direct in vivo measurement *(survey;
  [Hakhu et al. 2025](https://doi.org/10.3389/fradi.2025.1492479))*.

**Who could pick this up.** Lead 1 is a checker in the Foundation0 pattern: exact recomputation, then a message to a
maintainer. Lead 2 is a data-analysis project with a clean holdout. Leads 3 and 4 need someone who knows the
stimulation or RF-safety community. Every lead involves telling a database maintainer or an author that a number
looks wrong, so each needs a person's judgement before anything is sent.

## 3. Crowded

- **Deep-learning MR-EPT.** It is a small, busy community: about 18 PubMed hits from May 2025 to Oct 2026, an ISMRM
  reconstruction challenge (39 submissions, "large variability" on measured data), and new acquisition and
  standardisation guidelines in JMRI 2026 *(survey)*. AI's role there is as an instrument. With no in vivo ground
  truth, "validation" means agreement with ex vivo tables, which is the problem lead 5 addresses.
- **Electric-field modelling for tES, TMS and temporal interference.** Many groups, open pipelines (SimNIBS, ROAST)
  and public head-model collections. What is new there is uncertainty in conductivity, not more solvers.
- **Microwave breast imaging and EIT lung monitoring.** These are established, with commercial systems.
- **The ADEPT simulated EPT database** is less open than its description: most of its files sit behind an access
  request *(survey; [doi:10.34894/V0HBJ8](https://doi.org/10.34894/V0HBJ8))*.

## 4. Follow-up, 31 October 2026

Later the same day, with Ahraz Arifuddin's go-ahead, the leads became work. Each result below is **claimed**: not
reviewed by a person yet, and nothing has been sent to any maintainer.

- **The tissue tables became a project** (Foundation-0/tissue-dielectrics, private for now). Ahraz accepted NICT's
  terms of use for Foundation0, so the project now also compares every model with the measured spectra behind it:
  NICT's (58 tissues) and Gabriel's 1996 data from IFAC's mirror (41 tissues).
  - The IFAC copy of Gabriel's data reproduces Sasaki's Table 3 for 37 of 40 tissues, so it is the data Sasaki
    fitted.
  - **Bladder:** the gap is in the measured data. Gabriel's single human bladder sample reads εr 19.5 at 128 MHz,
    NICT's bladder 70.7. Gabriel's other human autopsy samples are not systematically off (NICT/Gabriel median 0.89,
    against 0.93 for his animal samples). The bladder is a one-sample anomaly.
  - **Fluids:** the excess permittivity of vitreous, aqueous humour and bile near 10 MHz is in NICT's measured
    spectra, likely electrode polarisation. Gabriel's CSF data start at 130 MHz, so his CSF model below that is
    extrapolation.
  - **Skin above 6 GHz:** ICNIRP 2020 Table 10 is internally consistent. NICT's published dermis spectra give 25–27%
    lower conductivity at 60–100 GHz, and a 0.44 mm instead of 0.35 mm penetration depth at 100 GHz.
  - A draft report to IT'IS (the bladder row and the water entry) waits in Ahraz's mailbox; draft questions for NICT
    are in the project.
  - The literature leads (in vivo vs ex vivo, tumour contrast vs water, tool defaults, the 5.37 S/m muscle value)
    are issues there.
  - The intracranial-recordings scoreboard is planned, but needs a CRCNS account in a person's name.
- **NHANES became a project** ([Foundation-0/nhanes-bioimpedance](https://github.com/Foundation-0/nhanes-bioimpedance)).
  - All 13,276 spectra were refitted, reproducing CDC's Cole parameters (median difference 0.2% for Re, 2.3% for Ri).
  - On a held-out survey cycle, the full spectrum adds almost nothing to a 50 kHz equation for DXA lean mass
    (R² gain 0.000–0.002).
  - For mortality, in adults 20–49 (286 deaths to 2019), it adds no consistent discrimination over 50 kHz phase
    angle (C-index changes +0.016, +0.001, −0.008).
  - The answer to lead 2 is "little, for these outcomes"; membrane-sensitive outcomes are next.
- **A life-sciences hub,** Foundation-0/bi0 (private for now), now holds the life-science leads from all three
  scouting passes.

The pilot below stays here unchanged, so this report remains reproducible on its own.

## Sources

Primary sources the pilot reads or checks against:

- Gabriel S, Lau RW, Gabriel C (1996). The dielectric properties of biological tissues II and III. *Phys Med Biol* 41:2251 and 2271.
  [doi:10.1088/0031-9155/41/11/002](https://doi.org/10.1088/0031-9155/41/11/002),
  [doi:10.1088/0031-9155/41/11/003](https://doi.org/10.1088/0031-9155/41/11/003). The 1996 report and its measured
  data are mirrored at [IFAC/webnir](https://webnir.eu/04-Dosimetry/04-Gabriel.php?lang=gb).
- IT'IS Foundation (2025). Tissue Properties Database V5.0. [doi:10.13099/VIP21000-05-0](https://itis.swiss/virtual-population/tissue-properties/downloads/database-v5-0).
  The documentation and the change log are in the download.
- Sasaki K, Wake K, Watanabe S (2014). Development of best fit Cole-Cole parameters for measurement data from biological
  tissues and organs between 1 MHz and 20 GHz. *Radio Science* 49:459–472. [doi:10.1002/2013RS005345](https://doi.org/10.1002/2013RS005345).
  Corrected 1 May 2015 (equations 1 and 2 only; Table 2 unchanged).
- NICT. Database of Tissue Dielectric Properties for Electromagnetic Modeling of Human Body (2023).
  [Site](https://www2.nict.go.jp/cgi-bin/202303080003/public_html/index.py).
- Malmberg CG, Maryott AA (1956). Dielectric constant of water from 0 to 100 °C. *J Res NBS* 56:1.
  [doi:10.6028/jres.056.001](https://doi.org/10.6028/jres.056.001).
- Liebe HJ, Hufford GA, Manabe T (1991). A model for the complex permittivity of water at frequencies below 1 THz.
  *Int J Infrared Millimeter Waves* 12:659. [NTIA copy](https://its.ntia.gov/publications/download/LiebeHuffordManabe1991.pdf).
- McCann H, Pisano G, Beltrachini L (2019). Variation in reported human head tissue electrical conductivity values.
  *Brain Topography* 32:825. [doi:10.1007/s10548-019-00710-2](https://doi.org/10.1007/s10548-019-00710-2).
- CDC NHANES 1999–2000 Bioelectrical Impedance Analysis (BIX). [Documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/1999/DataFiles/BIX.htm).
- Huang Y et al. (2017). *eLife* 6:e18834, [doi:10.7554/eLife.18834](https://doi.org/10.7554/eLife.18834); data at
  [CRCNS tes-1](https://doi.org/10.6080/K0XW4GQ1).
- Puonti O, Saturnino GB, Madsen KH, Thielscher A (2020). *NeuroImage* 208:116431.
  [doi:10.1016/j.neuroimage.2019.116431](https://doi.org/10.1016/j.neuroimage.2019.116431).
