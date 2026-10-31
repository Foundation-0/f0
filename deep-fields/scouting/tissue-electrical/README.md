# Tissue dielectric models pilot: do the tables everyone simulates with agree with each other and with physics?

Scripts from the tissue-electrical-properties scouting of 31 Oct 2026 ([../tissue-electrical.md](../tissue-electrical.md)).

Nearly every simulation of fields in the body (MRI heating, phone and 5G exposure, brain stimulation, EEG source
localisation, hyperthermia) takes tissue conductivity and permittivity from one of a few parameter tables. This pilot
cross-checks the three that are public:

- **IT'IS Tissue Properties Database V5.0** (21 Aug 2025, [DOI 10.13099/VIP21000-05-0](https://itis.swiss/virtual-population/tissue-properties/downloads/database-v5-0)).
  Its main dielectric entries are the four-term Cole-Cole fits of Gabriel, Lau and Gabriel (1996), with surrogate
  tissues where no fit exists. It also holds a literature compilation of low-frequency conductivity (1 Hz to 1 MHz) and,
  since V4.2, an "alternative" set taken from Sasaki, Wake and Watanabe (2014).
- **Sasaki, Wake and Watanabe (2014)**, [Radio Science 49:459](https://doi.org/10.1002/2013RS005345): least-squares
  refits, 1 MHz to 20 GHz, of Gabriel's own 1996 measurements. Table 2 is transcribed in `sasaki2014_table2.tsv`.
- **NICT Database of Tissue Dielectric Properties** ([site](https://www2.nict.go.jp/cgi-bin/202303080003/public_html/index.py), launched 30 Mar 2023):
  fits to NICT's own measurements, 1 MHz to 100 GHz, of mostly animal tissue at 30–37 °C.

| File | What |
|---|---|
| `fetch.sh` | Downloads IT'IS V5.0 (two ASCII tables and the SQLite material database) and the NICT parametric-model CSV into `data/` (not committed; neither source's terms allow redistribution). |
| `models.py` | The Cole-Cole forms of the three sources, and two references for pure water. |
| `data_sources.py` | Readers for the IT'IS ASCII exports (one is UTF-16), the NICT CSV and the Sasaki table. |
| `audit.py` | Five checks; writes `results/*.tsv` and `results/summary.txt`. |

```
./fetch.sh && python3 audit.py      # Python 3 with numpy and pandas; about 2 s
```

The files fetched on 31 Oct 2026 had these SHA-256 sums: `itis-v5.0.zip` `531adcee…a063c0`, `nict-model.csv`
`940b98a6…d219f3` (full sums are printed by `fetch.sh`).

## What the checks found

All numbers come from `results/summary.txt`. Each is a lead to check, not an established error, until the database
maintainers or the original authors confirm it.

**B. One row is transcribed wrongly (checkable now).** 94 of the 95 entries in the IT'IS V5.0 "alternative" dielectric
set reproduce the row of Sasaki (2014) Table 2 that their declared source names. The exception is **Urinary Bladder
Wall**. It declares itself as bladder, but its parameters are row 1, Aorta (εs,1 2.27, σ 0.292 S/m, Δ1 28.2 at
15.2 GHz, Δ2 1360 at 22.5 kHz). Row 2, Bladder, is used by no entry. At 128 MHz the wrong row gives εr 61.5 and
σ 0.45 S/m, where Sasaki's bladder row gives 19.2 and 0.27 S/m. The SQLite material database in the same download
(the file Sim4Life imports) has the same row in its "4.2-sasaki" and "5.0-sasaki" versions. So the error dates from
the V4.2 release (June 2024), and a pelvic simulation run with the alternative set gets these values.

**C, D. Gabriel's bladder is itself an outlier.** Both fits of Gabriel's 1996 bladder measurements (Gabriel's own and
Sasaki's) give εr ≈ 19–22 at 128 MHz. NICT's 2023 bladder fit gives 73.7, and its conductivity is 2.8 times
higher. Across the other 29 tissues with their own fit in all three sources, NICT's conductivity at 128 MHz is a
median 0.87 times Gabriel's (interquartile range 0.76 to 0.98), so the bladder runs the opposite way to the usual
offset. Against water content, Gabriel's bladder is also the largest outlier among 40 tissues: εr 18.9 at
900 MHz, where the trend for 70% water predicts 46.6 (residual −3.4 times the rms scatter). One plausible cause is
that a thin bladder wall measured with an open-ended coaxial probe also samples what lies behind it. That is a
hypothesis; it has not been checked against Gabriel's sample notes.

**E. The IT'IS "Water" entry mixes two temperatures.** It is the same in every database version from 4.0 to 5.0.
Its parameters sum to a static permittivity of 84.6, the value
for pure water at 7.9 °C (Malmberg and Maryott 1956). Its relaxation time, 8.38 ps, is that of water at 24.4 °C
(Liebe, Hufford and Manabe 1991). A two-term Debye fit at about 25 °C has a static permittivity near 78.3. The sum
would match if 78.32 were the static permittivity entered as Δ1, rather than the step of the first relaxation.

**A. Gabriel's model is not meant for low frequencies, and the size of the gap is now explicit.** At 100 Hz the
model's conductivity is more than 3 times below the mean of the IT'IS compilation for 11 of 22 tissues that have
their own fit and at least 5 compiled values. Examples: nerve ×12, brain white matter ×6, grey matter ×4.7, liver
×4.9. For 15 of the 22 the model falls outside the compiled minimum–maximum range. Gabriel et al. (1996) and the IT'IS
documentation both warn that the model is uncertain below 1 MHz. The point is for low-frequency studies that still
evaluate it at 50 Hz or 1 kHz.

**E. Fits used outside the band they were fitted to.** Sasaki's Table 1 says the measured data for cerebrospinal fluid,
dura and vitreous humour start at 130 MHz. IT'IS documents the alternative set as valid above 1 MHz. Extrapolated to
1 MHz, the CSF fit gives εr 9,111 (73 at 130 MHz).

**Softer flags.**
- Fluids with no cells should not be more polarisable than pure water (74.15 at 37 °C). Several fits are, between
  10 and 300 MHz: Gabriel's CSF (up to 108.6), Gabriel's bile, and NICT's vitreous, aqueous humour and bile.
  Electrode polarisation or fitting artefacts are likely for CSF. For bile and vitreous, which contain
  macromolecules, a real dispersion can't be ruled out.
- NICT's fat and breast-fat values differ from Gabriel's by factors of 0.5 to 4.4. Animal fat differs from human
  fat, so these pairs are not like-for-like.
- In the IT'IS alternative set, "Fat (Average Infiltrated)" takes Sasaki's single "Fat" fit, which halves fat
  permittivity compared with the main set (εr 5.7 vs 12.4 at 128 MHz). This is a mapping choice, not a
  transcription error, but users switching sets should know.

## Next

This pilot continues as its own project, Foundation-0/tissue-dielectrics (private for now), which also compares the
models with the measured spectra. See section 4 of [../tissue-electrical.md](../tissue-electrical.md). The list below
was the plan on the day of the pilot.

- Ask the IT'IS Foundation about the bladder row and the water entry (a person sends this, not an agent).
- NICT also publishes its **measured** spectra, behind a terms-of-use page. A person who accepts those terms can
  compare every fit above with the raw data, tissue by tissue. Gabriel's 1996 measured data are published as graphs in
  the [IFAC mirror of the 1996 report](https://niremf.ifac.cnr.it/docs/DIELECTRIC/home.html).
- Repeat check B for other tools that ship these tables (for example the IFAC calculator, SimNIBS, Sim4Life's
  material database), and check A against each tool's low-frequency defaults.
