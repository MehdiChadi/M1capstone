#rerunning the commune merge with the correct DPE file: 
from pathlib import Path
import pandas as pd

project = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")

dpe_path = project / "data" / "clean" / "dpe_clean.parquet"
filo_path = project / "data" / "clean" / "filosofi_200m_clean.parquet"

final_dir = project / "data" / "final"
final_dir.mkdir(parents=True, exist_ok=True)

out_path = final_dir / "analysis_commune_fixed.parquet"

dpe = pd.read_parquet(dpe_path)
filo = pd.read_parquet(filo_path)

print("DPE shape:", dpe.shape)
print("FiLoSoFi shape:", filo.shape)


dpe = dpe.dropna(subset=["commune_insee"]).copy()
filo = filo.dropna(subset=["commune_insee"]).copy()

print("DPE rows with commune code:", len(dpe))
print("FiLoSoFi rows with commune code:", len(filo))

# DPE commune aggregation
dpe_commune = (
    dpe.groupby("commune_insee")
    .agg(
        n_dpe_obs=("dpe_id", "count"),
        share_low_efficiency_fg=("is_low_efficiency_fg", "mean"),
        share_low_efficiency_efg=("is_low_efficiency_efg", "mean"),
        avg_dpe_score=("dpe_score", "mean"),
        avg_dpe_surface_m2=("dwelling_surface", "mean"),
        share_pre1945_dpe=("is_old_pre1945", "mean"),
        avg_construction_year=("construction_year", "mean"),
    )
    .reset_index()
)

# FiLoSoFi commune aggregation
# Weighted by households where possible
def weighted_avg(group, value_col, weight_col="n_households"):
    x = group[value_col]
    w = group[weight_col]
    valid = x.notna() & w.notna() & (w > 0)
    if valid.sum() == 0:
        return pd.NA
    return (x[valid] * w[valid]).sum() / w[valid].sum()

rows = []

for commune, g in filo.groupby("commune_insee"):
    row = {
        "commune_insee": commune,
        "n_200m_cells": len(g),
        "n_individuals": g["n_individuals"].sum(skipna=True),
        "n_households": g["n_households"].sum(skipna=True),
        "n_poor_households": g["n_poor_households"].sum(skipna=True),
        "poor_household_share": (
            g["n_poor_households"].sum(skipna=True) / g["n_households"].sum(skipna=True)
            if g["n_households"].sum(skipna=True) > 0 else pd.NA
        ),
        "owner_household_share": weighted_avg(g, "owner_household_share"),
        "single_parent_share": weighted_avg(g, "single_parent_share"),
        "house_share": weighted_avg(g, "house_share"),
        "collective_housing_share": weighted_avg(g, "collective_housing_share"),
        "old_housing_share_pre1945": weighted_avg(g, "old_housing_share_pre1945"),
        "social_housing_share": weighted_avg(g, "social_housing_share"),
        "avg_dwelling_surface": weighted_avg(g, "avg_dwelling_surface"),
        "avg_winsorized_living_standard": weighted_avg(g, "avg_winsorized_living_standard"),
        "log_avg_winsorized_living_standard": weighted_avg(g, "log_avg_winsorized_living_standard"),
        "share_age_18_39": weighted_avg(g, "share_age_18_39"),
        "share_age_65_plus": weighted_avg(g, "share_age_65_plus"),
        "share_imputed_200m": g["is_imputed_200m"].mean(),
    }
    rows.append(row)

filo_commune = pd.DataFrame(rows)

analysis_commune = filo_commune.merge(
    dpe_commune,
    on="commune_insee",
    how="left",
)

analysis_commune["n_dpe_obs"] = analysis_commune["n_dpe_obs"].fillna(0)

print("Commune-level DPE shape:", dpe_commune.shape)
print("Commune-level FiLoSoFi shape:", filo_commune.shape)
print("Final commune-level analysis shape:", analysis_commune.shape)
print(
    "Share of communes matched to at least one DPE observation:",
    round((analysis_commune["n_dpe_obs"] > 0).mean(), 4)
)

analysis_commune.to_parquet(out_path, index=False)

csv_path = project / "outputs" / "csv_exports" / "analysis_commune_fixed.csv"
csv_path.parent.mkdir(parents=True, exist_ok=True)
analysis_commune.to_csv(csv_path, index=False, encoding="utf-8-sig")

print("\nSaved:")
print(out_path)
print(csv_path)

# this code is created using the corrected cleaned dataset. DPE data are aggregated by commune, and the socioeconomic data are aggregated using number of households. The commune level socioeconomic indicators are combined and merged with the aggregated DPE indicators. 