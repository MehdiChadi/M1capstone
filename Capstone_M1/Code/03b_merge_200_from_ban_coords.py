from pathlib import Path
import pandas as pd
import numpy as np


# import the needed libraries, choose the path for python to follow, and create a path for the final file 

BASE_DIR = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")
CLEAN_DIR = BASE_DIR / "data" / "clean"
FINAL_DIR = BASE_DIR / "data" / "final"

FINAL_DIR.mkdir(parents=True, exist_ok=True)


# load and verify the file related to DPE and poverty from parquet files 
dpe = pd.read_parquet(CLEAN_DIR / "dpe_clean_latest_building.parquet")
filo = pd.read_parquet(CLEAN_DIR / "filosofi_200m_clean.parquet")

print("DPE shape:", dpe.shape)
print("FiLoSoFi shape:", filo.shape)


# I needed to verify that the DPE dataset contains the needed geographic information, any row that does not contin the geographic location will be removed as it will be considered as a missing value 
required_cols = ["x_ban", "y_ban"]
missing_required = [c for c in required_cols if c not in dpe.columns]

if missing_required:
    raise ValueError(f"Missing BAN coordinate columns in cleaned DPE file: {missing_required}")

dpe_geo = dpe.dropna(subset=["x_ban", "y_ban"]).copy()

print("DPE rows with BAN coordinates:", dpe_geo.shape[0])



dpe_geo["grid_east_200m"] = (np.floor(dpe_geo["x_ban"] / 200) * 200).astype(int)
dpe_geo["grid_north_200m"] = (np.floor(dpe_geo["y_ban"] / 200) * 200).astype(int)

dpe_geo["grid_id_200m"] = (
    "CRS3035RES200mN"
    + dpe_geo["grid_north_200m"].astype(str)
    + "E"
    + dpe_geo["grid_east_200m"].astype(str)
)

print("\nSample reconstructed grid IDs:")
print(dpe_geo["grid_id_200m"].head())

# in the following code, the aim is to merge the DPE file with the poverty related file at 200 m level 
merged_micro = dpe_geo.merge(
    filo,
    on="grid_id_200m",
    how="left",
    validate="many_to_one"
)

match_rate = merged_micro["poor_household_share"].notna().mean()
print(f"Share of DPE rows matched to a 200m social cell: {match_rate:.3f}")

# In this code i wanted to calculte the merge between energy perfoemance and housing charactristics at 200 m level 
# then renome the variables for clarity and simplicity 


dpe_area = (
    merged_micro.groupby("grid_id_200m", as_index=False)
    .agg({
        "dpe_id": "count",
        "is_low_efficiency_fg": "mean",
        "is_low_efficiency_efg": "mean",
        "dpe_score": "mean",
        "surface_m2": "mean",
        "is_old_pre1945": "mean"
    })
    .rename(columns={
        "dpe_id": "n_dpe_obs",
        "is_low_efficiency_fg": "share_low_efficiency_fg",
        "is_low_efficiency_efg": "share_low_efficiency_efg",
        "dpe_score": "avg_dpe_score",
        "surface_m2": "avg_dpe_surface_m2",
        "is_old_pre1945": "share_pre1945_dpe"
    })
)

analysis_200m = filo.merge(
    dpe_area,
    on="grid_id_200m",
    how="left",
    validate="one_to_one"
)

analysis_200m_non_imputed = analysis_200m.loc[
    analysis_200m["is_imputed_200m"] == 0
].copy()

print("Final 200m analysis shape:", analysis_200m.shape)
print("Non-imputed 200m analysis shape:", analysis_200m_non_imputed.shape)
print(f"200m cells with at least one DPE observation: {analysis_200m['n_dpe_obs'].notna().sum()}")


# saved the merged file 
merged_micro.to_parquet(FINAL_DIR / "dpe_filosofi_micro_merged.parquet", index=False)
analysis_200m.to_parquet(FINAL_DIR / "analysis_200m.parquet", index=False)
analysis_200m_non_imputed.to_parquet(FINAL_DIR / "analysis_200m_non_imputed.parquet", index=False)

print("\nSaved:")
print(FINAL_DIR / "dpe_filosofi_micro_merged.parquet")
print(FINAL_DIR / "analysis_200m.parquet")
print(FINAL_DIR / "analysis_200m_non_imputed.parquet")