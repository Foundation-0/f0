#!/usr/bin/env bash
# Download the two public tissue databases this pilot reads into ./data (not committed).
# Their terms do not allow redistribution, so each user fetches them from the source.
#   IT'IS Tissue Properties Database V5.0 (21 Aug 2025), DOI 10.13099/VIP21000-05-0
#   NICT Database of Tissue Dielectric Properties, parametric-model CSV (launched 30 Mar 2023)
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data
curl -fsSL https://itis.swiss/assets/Downloads/TissueDb/Database-V5-0.zip -o data/itis-v5.0.zip
(cd data && unzip -oq itis-v5.0.zip \
  "Thermal_dielectric_acoustic_MR properties_database_V5.0(ASCII).txt" \
  "Alternative_dielectric_properties_database_V5.0(ASCII).txt" \
  "IT'IS_Material_database_V5.0.db")
curl -fsSL "https://www2.nict.go.jp/cgi-bin/202303080003/public_html/index.py/model/csv" -o data/nict-model.csv
sha256sum data/itis-v5.0.zip data/nict-model.csv
