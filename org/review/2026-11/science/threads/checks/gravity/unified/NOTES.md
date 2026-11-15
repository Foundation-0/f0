# gravity2/unified notes (working notes; the report is in the hand-back message)

- Erratum found while building the table: ../t3_atlas3d.py v1 read distance from the wrong column (M_K instead of D) of
  ATLAS3D paper I Table 3. Fixed (t1[g][6]); old output kept as ../t3_atlas3d.out.v1_Dbug. T3 conclusions unchanged:
  step test A -0.351 +/- 0.039 (9.1 sigma), B -0.104 +/- 0.030 (3.4 sigma).
- RC41 (Genzel 2020) is not a separate class: at least 31 of its 41 galaxies are in RC100 (refit). RC100 used.
- Assumed errors: SPARC M_b 0.1 dex x stellar share; DT 0.2 dex; ATLAS3D M_tot 0.05, M_b 0.10 dex; cluster stars 30%.
- DT radii are not tabulated: r = 3 R_d with R_d = j*/(2 V_flat); M_b(<r) = 0.8 M_b. Flagged in the sel column.
- Fit score: class-balanced mean square of log10(M_tot obs / M_tot pred); each local class has equal weight.
- Threshold sharpness bounded to s in (0.5, 6); free fits sit at s = 0.5 (soft onset), so "threshold" location depends on s.
- Multiprocessing on macOS re-imports part2b.py in workers, so part2b.log repeats section (1); part2b.out is clean.
- Repository scripts copied unmodified into repo_copy/ (gravity@8f96c4b) to recompute collapse and cooling scales.
- KATRIN bound quoted from memory (not re-fetched): m_nu < 0.45 eV (90% CL), arXiv:2406.13516.
