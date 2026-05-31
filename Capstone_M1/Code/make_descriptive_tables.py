from pathlib import Path
import pandas as pd

project = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")

final_dir = project / "data" / "final"
tables_dir = project / "outputs" / "tables"
tables_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(final_dir / "analysis_200m_non_imputed_fixed.parquet")

# Keep cells with at least one DPE observation
df_dpe = df[df["n_dpe_obs"] > 0].copy()

vars_main = [
    "share_low_efficiency_fg",
    "share_low_efficiency_efg",
    "avg_dpe_score",
    "poor_household_share",
    "social_housing_share",
    "old_housing_share_pre1945",
    "owner_household_share",
    "house_share",
    "collective_housing_share",
    "avg_dwelling_surface",
    "log_avg_winsorized_living_standard",
    "n_dpe_obs",
]

desc = df_dpe[vars_main].describe().T

out_csv = tables_dir / "descriptive_statistics_200m_non_imputed.csv"
out_xlsx = tables_dir / "descriptive_statistics_200m_non_imputed.xlsx"

desc.to_csv(out_csv, encoding="utf-8-sig")
desc.to_excel(out_xlsx)

print("200m non-imputed cells with DPE observations:", df_dpe.shape)
print("\nDescriptive statistics:")
print(desc)

print("\nSaved:")
print(out_csv)
print(out_xlsx)

#In order to reach the descriptive statistics, I first loaded the cleaned dataset ( making sure that I am analyzing data with DPE label). The code describe is a function which calculates descriptive statistics such as mean, standard deviation, min, max...