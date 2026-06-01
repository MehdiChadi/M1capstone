# M1capstone

## Research question

Are energy inefficient dwellings concentrated in poorer neighbourhods?

Deeper version:
Can housing stocks and characteristics shape the distribution of low energy performance dwellings in France?

## Current data decision

The full ADEME DPE database could not be downloaded locally. The project therefore uses a large ADEME DPE extract:

- File: dpe03existant.csv
- Approximate size: 2.14 GB, it is a part of complete national DPE population. 

## Correct DPE file

 I used:

data/clean/dpe_clean.parquet


## Correct FiLoSoFi file

Used:

data/clean/filosofi_200m_clean.parquet


## Correct final files

Used these:

data/final/dpe_filosofi_micro_merged_fixed.parquet
data/final/analysis_200m_fixed.parquet
data/final/analysis_200m_non_imputed_fixed.parquet
data/final/analysis_commune_fixed.parquet



## Recommended empirical order

1. Descriptive statistics on DPE labels.
2. Descriptive statistics on 200m cells.
3. Main analysis using non-imputed 200m cells with at least one DPE observation.
4. Weighted OLS regressions, weighting by n_dpe_obs.
5. Commune-level robustness analysis.


# Model
the final model is : share low efficiency as the dependent variable, in the other part of the equation i have the intercept, error terms, and explanatory variables including poor household share, old housing, social housing, and the owner of the house 


The analysis uses a large extract of ADEME’s DPE database for existing dwellings ( also suggested by open data university), containing approximately 1.36 million observations. The results should therefore be interpreted as based on the available extract rather than the full national DPE population.

# libraries required during coding 
-pandas
-numpy
-pyarrow
-openpyxl
-matplotlib
-jupyter
-statsmodels
