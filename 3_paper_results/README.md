# 3. Paper Results

This directory contains the scripts used to generate the figures and summary statistics reported in the paper.

## Structure

* `scripts/` – Python scripts used to generate tables and figures from the final analysis dataset.
* `figures/` – Output directory containing the generated figures.

## Inputs

The scripts read data from the completed worksheets in:

```
2_manual_analysis/analysis_files/
```

Most analyses use `final_no_evidence.csv`, which contains the final manually assigned labels without supporting evidence columns.

## Reproducing the figures

Run the desired script from the `scripts/` directory, for example:

```bash
python3 sq2-thread-model.py
```

Generated figures are written to the `figures/` directory.
