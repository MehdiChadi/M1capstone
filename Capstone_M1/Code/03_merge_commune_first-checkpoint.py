from pathlib import Path
import pandas as pd
import numpy as np


# In this file, I am trying to merge the cleaned file of DPE with the file related to poverty, then use the file with the commune level in order to create the final file that will be used later in the regression 

BASE_DIR = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")
CLEAN_DIR = BASE_DIR / "data" / "clean"
FINAL_DIR = BASE_DIR / "data" / "final"

FINAL_DIR.mkdir(parents=True, exist_ok=True)


# Ask python to load the files 

dpe = pd.read_parquet(CLEAN_DIR / "dpe_clean_latest_building.parquet")
filo = pd.read_parquet(CLEAN_DIR / "filosofi_200m_clean.parquet")

print("DPE shape:", dpe.shape)
print("FiLoSoFi shape:", filo.shape)




if "commune_insee" not in dpe.columns:
    raise ValueError("The cleaned DPE file does not contain 'commune_insee'.")

if "commune_insee" not in filo.columns:
    raise ValueError("The cleaned FiLoSoFi file does not contain 'commune_insee'.")

# if the raw has no commune code then drop it from analysis


for df in [dpe, filo]:
    df["commune_insee"] = df["commune_insee"].astype(str).str.strip()
    df.loc[df["commune_insee"].isin(["nan", "None", ""]), "commune_insee"] = np.nan

dpe = dpe.dropna(subset=["commune_insee"]).copy()
filo = filo.dropna(subset=["commune_insee"]).copy()

print("DPE rows with commune code:", dpe.shape[0])
print("FiLoSoFi rows with commune code:", filo.shape[0])


# in this code i am trying to aggregate the DPE file into the commune file
# looking at different variables like the size of the dwelling, dwellings with low energy efficiency, and the old buildings

dpe_agg = {
    "dpe_id": "count",
    "is_low_efficiency_fg": "mean",
    "is_low_efficiency_efg": "mean",
    "dpe_score": "mean",
    "surface_m2": "mean",
}

if "is_old_pre1945" in dpe.columns:
    dpe_agg["is_old_pre1945"] = "mean"

if "construction_year" in dpe.columns:
    dpe_agg["construction_year"] = "mean"

dpe_commune = (
    dpe.groupby("commune_insee", as_index=False)
    .agg(dpe_agg)
    .rename(columns={
        "dpe_id": "n_dpe_obs",
        "is_low_efficiency_fg": "share_low_efficiency_fg",
        "is_low_efficiency_efg": "share_low_efficiency_efg",
        "dpe_score": "avg_dpe_score",
        "surface_m2": "avg_dpe_surface_m2",
        "is_old_pre1945": "share_pre1945_dpe",
        "construction_year": "avg_construction_year",
    })
)

print("Commune-level DPE shape:", dpe_commune.shape)


# here i am trying to aggregate the povery to commune file, mainly by usig the share of poor households and different control variables related to the owner of the house and put the income into log 

sum_vars = [
    "n_individuals",
    "n_households",
    "n_poor_households",
    "n_single_person_households",
    "n_large_households_5plus",
    "n_owner_households",
    "n_single_parent_households",
    "sum_winsorized_living_standard",
    "sum_dwelling_surface",
    "n_households_collective_housing",
    "n_households_house",
    "n_dwellings_pre1945",
    "n_dwellings_1945_1969",
    "n_dwellings_1970_1989",
    "n_dwellings_post1990",
    "n_dwellings_unknown_year",
    "n_social_housing",
    "n_dwellings_total_known_period",
    "n_dwellings_total",
]

sum_vars = [c for c in sum_vars if c in filo.columns]

filo_commune = filo.groupby("commune_insee", as_index=False)[sum_vars].sum()

filo_commune["poor_household_share"] = np.where(
    filo_commune["n_households"] > 0,
    filo_commune["n_poor_households"] / filo_commune["n_households"],
    np.nan
)

filo_commune["owner_household_share"] = np.where(
    filo_commune["n_households"] > 0,
    filo_commune["n_owner_households"] / filo_commune["n_households"],
    np.nan
)

filo_commune["single_parent_share"] = np.where(
    filo_commune["n_households"] > 0,
    filo_commune["n_single_parent_households"] / filo_commune["n_households"],
    np.nan
)

filo_commune["house_share"] = np.where(
    filo_commune["n_households"] > 0,
    filo_commune["n_households_house"] / filo_commune["n_households"],
    np.nan
)

filo_commune["collective_housing_share"] = np.where(
    filo_commune["n_households"] > 0,
    filo_commune["n_households_collective_housing"] / filo_commune["n_households"],
    np.nan
)

filo_commune["social_housing_share"] = np.where(
    filo_commune["n_dwellings_total"] > 0,
    filo_commune["n_social_housing"] / filo_commune["n_dwellings_total"],
    np.nan
)

filo_commune["old_housing_share_pre1945"] = np.where(
    filo_commune["n_dwellings_total_known_period"] > 0,
    filo_commune["n_dwellings_pre1945"] / filo_commune["n_dwellings_total_known_period"],
    np.nan
)

filo_commune["avg_dwelling_surface"] = np.where(
    filo_commune["n_households"] > 0,
    filo_commune["sum_dwelling_surface"] / filo_commune["n_households"],
    np.nan
)

filo_commune["avg_winsorized_living_standard"] = np.where(
    filo_commune["n_individuals"] > 0,
    filo_commune["sum_winsorized_living_standard"] / filo_commune["n_individuals"],
    np.nan
)

filo_commune["log_avg_winsorized_living_standard"] = np.log(
    filo_commune["avg_winsorized_living_standard"].where(filo_commune["avg_winsorized_living_standard"] > 0)
)

print("Commune-level FiLoSoFi shape:", filo_commune.shape)


# here as before i am merging the data together 

analysis_commune = filo_commune.merge(
    dpe_commune,
    on="commune_insee",
    how="left",
    validate="one_to_one"
)

print("Final commune-level analysis shape:", analysis_commune.shape)
print(f"Share of communes matched to at least one DPE observation: {analysis_commune['n_dpe_obs'].notna().mean():.3f}")


# and finally i am saving the result for the actual work 

analysis_commune.to_parquet(FINAL_DIR / "analysis_commune.parquet", index=False)

print("\nSaved:")
print(FINAL_DIR / "analysis_commune.parquet")