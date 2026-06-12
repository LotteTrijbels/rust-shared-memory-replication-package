# Replication Package

This repository contains the data, scripts, and intermediate steps required to reproduce the analyses presented in the paper.

## Repository structure

* `1_data_selection/` – Repository selection pipeline, intermediate outputs, and scripts used to construct the analysed dataset.
* `2_manual_analysis/` – Completed qualitative analysis worksheets, label definitions, and scripts used to assist file selection.
* `3_paper_results/` – Scripts used to generate the figures and summary statistics reported in the paper.

## Requirements

The replication package was developed and tested on Ubuntu Linux with Python 3.10+.

The Python scripts require common scientific packages, including:

* `pandas`
* `matplotlib`
* `seaborn`

These can be installed with:

```bash
pip install pandas matplotlib seaborn
```

Some scripts also rely on standard command-line utilities such as `jq`, `curl`, and `bash`.

## LLM-assisted repository selection

The repository classification stage used OpenAI Codex with the GPT-5.5 model. Reproducing this step requires access to Codex and appropriate authentication. Installation and setup instructions are available from the official documentation. Because LLM outputs may vary across model versions and over time, rerunning this stage may not produce identical results. For this reason, the intermediate steps and final outputs used in the study are included in this replication package and should be used for exact replication.

## Reproducing the study

1. Follow the instructions in `1_data_selection/README.md` to reproduce the repository selection pipeline.
2. Inspect the completed worksheets and documentation in `2_manual_analysis/`.
3. Run the scripts in `3_paper_results/scripts/` to regenerate the figures and summary statistics from the included analysis data.

## Notes

The local clones of analysed GitHub repositories are **not** included in this replication package. Scripts that operate on source code assume that these repositories have been cloned separately into the expected directory structure.
