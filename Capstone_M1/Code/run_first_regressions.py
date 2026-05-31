from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf

project = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")

final_dir = project / "data" / "final"
tables_dir = project / "outputs" / "tables"
tables_dir.mkdir(parents=True, exist_ok=True)

# Use non-imputed 200m cells as the main clean spatial sample
path_200m = final_dir / "analysis_200m_non_imputed_fixed.parquet"
df = pd.read_parquet(path_200m)

print("Raw 200m non-imputed shape:", df.shape)

# Keep cells with at least one DPE observation
df = df[df["n_dpe_obs"] > 0].copy()

print("200m cells with DPE observations:", df.shape)

# Main variables
vars_needed = [
    "share_low_efficiency_fg",
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

df_model = df.dropna(subset=vars_needed).copy()

print("Regression sample shape:", df_model.shape)

# Model 1: poverty only
m1 = smf.wls(
    "share_low_efficiency_fg ~ poor_household_share",
    data=df_model,
    weights=df_model["n_dpe_obs"],
).fit(cov_type="HC1")

# Model 2: more extended model 
m2 = smf.wls(
    """
    share_low_efficiency_fg
    ~ poor_household_share
    + social_housing_share
    + old_housing_share_pre1945
    + owner_household_share
    """,
    data=df_model,
    weights=df_model["n_dpe_obs"],
).fit(cov_type="HC1")

# Model 3: housing stock controls
m3 = smf.wls(
    """
    share_low_efficiency_fg
    ~ poor_household_share
    + social_housing_share
    + old_housing_share_pre1945
    + owner_household_share
    + house_share
    + collective_housing_share
    + avg_dwelling_surface
    + log_avg_winsorized_living_standard
    """,
    data=df_model,
    weights=df_model["n_dpe_obs"],
).fit(cov_type="HC1")

print("\nMODEL 1")
print(m1.summary())

print("\nMODEL 2")
print(m2.summary())

print("\nMODEL 3")
print(m3.summary())

# Save readable text output
out_txt = tables_dir / "first_200m_regressions.txt"

with open(out_txt, "w", encoding="utf-8") as f:
    f.write("MODEL 1: Poverty only\n")
    f.write(str(m1.summary()))
    f.write("\n\nMODEL 2: Professor baseline\n")
    f.write(str(m2.summary()))
    f.write("\n\nMODEL 3: Fuller controls\n")
    f.write(str(m3.summary()))

print("\nSaved regression output to:")
print(out_txt)

# It is the regression of the 3 ideas. In this i code, I selected the required variables to do the regressions and analysis without any missing values according to three consecutive models. 1: relationship between poverty and low performance. 2: more extended model including social housing and housing characterstics. 3: additional controls like housing type and dwelling size. 