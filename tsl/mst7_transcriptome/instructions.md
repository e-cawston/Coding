
---

# instructions.md

## Overview

This repository contains the analysis workflow for two RNA‑seq experiments investigating gene regulation during appressorium development in *Magnaporthe oryzae*. All analyses are performed in WSL using VS Code and GitHub Copilot.

The workflow includes:

- Kallisto quantification  
- Sleuth differential expression  
- Rank products analysis  
- DEG visualisation  
- Upset plots  
- Correlation matrices  
- Cross‑experiment comparisons  

All modular analysis scripts are generated using GitHub Copilot.

---

## Directory structure

```
instructions.md

analysis/
  DGE_sleuth_V3.Rmd
  rank_products_analysis.Rmd
  scripts/
    dge_functions.R
    upset_functions.R
    correlation_functions.R
    rank_products_functions.R

raw/
  run_metadata.txt
  kallisto_abundances/
  all_samples_tpm_matrix.txt

results/
  dge/
  rank_products/
  figures/
  tables/
```

---

## Comparison table (single source of truth)

All differential expression comparisons must be defined in a single tibble:

```r
library(tibble)

comparisons <- tribble(
  ~label,               ~experiment, ~control,  ~test,

  # Exp1 core comparisons
  "Guy11_vs_mst7",      "Exp1",      "Guy11",   "mst7",
  "Guy11_vs_MST7WT",    "Exp1",      "Guy11",   "MST7WT",
  "MST7WT_vs_mst7",     "Exp1",      "MST7WT",  "mst7",
  "MST7WT_vs_PM",       "Exp1",      "MST7WT",  "MST7PM",
  "MST7WT_vs_PD",       "Exp1",      "MST7WT",  "MST7PD",

  # Exp2 core comparison
  "Guy11M_vs_pmk1",     "Exp2",      "Guy11M",  "pmk1",

  # Cross‑experiment comparisons
  "mst7_vs_pmk1",       "Cross",     "mst7",    "pmk1",
  "Guy11_vs_Guy11M",    "Cross",     "Guy11",   "Guy11M"
)
```

This table drives:

- Sleuth DGE  
- DEG visualisation  
- Upset plots  
- Rank products  
- Correlation matrices  
- Cross‑experiment biology  

---

## Workflow

### 1. Sleuth differential expression

Use `analysis/scripts/dge_functions.R` to:

- Run sleuth models  
- Extract DEGs  
- Save tables  
- Generate comparison‑specific plots  

### 2. Upset plots

Use `analysis/scripts/upset_functions.R` to:

- Load DEG tables  
- Generate overlap plots for each comparison group  
- Generate cross‑experiment overlap plots (pmk1 vs mst7)  

### 3. Correlation matrices

Use `analysis/scripts/correlation_functions.R` to:

- Compute sample‑wise correlations  
- Generate matrices for:
  - All samples  
  - Experiment 1 only  
  - Experiment 2 only  
  - Key strains (Guy11, mst7, Guy11M, pmk1)  

### 4. Rank products analysis

Use `analysis/scripts/rank_products_functions.R` to:

- Compute rank products for each comparison  
- Preserve signed fold‑change  
- Generate correct inverse plots for A_vs_B and B_vs_A  

---

## Copilot usage

Use the following prompt in the **Copilot Chat sidebar** in VS Code:

```
You are assisting with a fungal RNA-seq analysis pipeline using kallisto and sleuth.
I will provide a tibble of comparisons and a directory structure.

Your task is to generate modular, parameterised R functions that:

1. Run sleuth differential expression for any pair of conditions.
2. Save DGE tables in a standardised format.
3. Generate ggplot2 visualisations for each comparison.
4. Generate upset plots for DEG overlaps.
5. Generate correlation matrices for selected subsets of samples.
6. Fix rank-products visualisation so that A_vs_B and B_vs_A are inverses.

All code must:
- Use tidyverse style
- Accept parameters rather than hard-coded values
- Write outputs to paths I specify
- Use consistent naming conventions
- Avoid duplicated logic


Wait for me to provide the comparison tibble and directory paths
The comparison tibble and directory paths are in instructions.md which I want you to use for context. 
```

Paste this prompt into Copilot Chat **after opening the file you want Copilot to rewrite** (e.g., `dge_functions.R`). Copilot will rewrite the entire file for you.

---

## Git workflow

Create a new branch for modularisation:

```bash
git checkout -b modular_pipeline
```

Then:

- Add `instructions.md`  
- Add `comparison_table.R`  
- Add empty script files in `analysis/scripts/`  
- Use Copilot Chat to generate modular functions  
- Commit frequently  
- Merge when stable  

---

## Notes

- All scripts should be modular and parameterised.  
- No hard‑coded paths or condition names.  
- All outputs must be written to `results/figures` and `results/tables`.  
- All comparisons must be defined in the comparison tibble.  

---
