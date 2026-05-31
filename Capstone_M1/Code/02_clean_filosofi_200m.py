from pathlib import Path
import pandas as pd
import numpy as np


# First I imported the needed libraries for the following code
# I Used the path to call for the files 

BASE_DIR = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")
CLEAN_DIR = BASE_DIR / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

FILOSOFI_FILES = [
    BASE_DIR / "data" / "raw" / "carreaux_200m_met.csv",
    BASE_DIR / "data" / "raw" / "carreaux_200m_mart.csv",
    BASE_DIR / "data" / "raw" / "carreaux_200m_reun.csv",
]


# I tried to make the manipulate the data set by helping making it in simialr form and not doing the same work over and over again 
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[ /\\\-]+", "_", regex=True)
        .str.replace(r"[()]", "", regex=True)
        .str.replace(r"__+", "_", regex=True)
    )
    return df


def convert_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# FIrst i want to load then merge the data sets together 

frames = []

for file_path in FILOSOFI_FILES:
    temp = pd.read_csv(file_path, sep=",", low_memory=False)
    temp = standardize_columns(temp)
    temp["source_file"] = file_path.name
    frames.append(temp)

filo = pd.concat(frames, ignore_index=True)

print("Combined FiLoSoFi shape:", filo.shape)
print("Columns:")
print(filo.columns.tolist())


# it is a way to only select the needed columns related to the needed variables and remove the unecessary variables 
needed_cols = [
    "idcar_200m",
    "idcar_1km",
    "id_car_nat",
    "i_est_200",
    "i_est_1km",
    "lcog_geo",
    "ind",
    "men",
    "men_pauv",
    "men_1ind",
    "men_5ind",
    "men_prop",
    "men_fmp",
    "ind_snv",
    "men_surf",
    "men_coll",
    "men_mais",
    "log_av45",
    "log_45_70",
    "log_70_90",
    "log_ap90",
    "log_inc",
    "log_soc",
    "ind_0_3",
    "ind_4_5",
    "ind_6_10",
    "ind_11_17",
    "ind_18_24",
    "ind_25_39",
    "ind_40_54",
    "ind_55_64",
    "ind_65_79",
    "ind_80p",
    "ind_inc",
    "source_file",
]

filo = filo[[c for c in needed_cols if c in filo.columns]].copy()

print("\nSelected FiLoSoFi columns:")
print(filo.columns.tolist())


# this is a classic work in python, since some of the variables are in frensh and long to be written each time, everytime we try to rename the variables for clarity and simplicity 
rename_map = {
    "idcar_200m": "grid_id_200m",
    "idcar_1km": "grid_id_1km",
    "id_car_nat": "grid_id_natural",
    "i_est_200": "is_imputed_200m",
    "i_est_1km": "is_imputed_1km",
    "lcog_geo": "commune_insee",
    "ind": "n_individuals",
    "men": "n_households",
    "men_pauv": "n_poor_households",
    "men_1ind": "n_single_person_households",
    "men_5ind": "n_large_households_5plus",
    "men_prop": "n_owner_households",
    "men_fmp": "n_single_parent_households",
    "ind_snv": "sum_winsorized_living_standard",
    "men_surf": "sum_dwelling_surface",
    "men_coll": "n_households_collective_housing",
    "men_mais": "n_households_house",
    "log_av45": "n_dwellings_pre1945",
    "log_45_70": "n_dwellings_1945_1969",
    "log_70_90": "n_dwellings_1970_1989",
    "log_ap90": "n_dwellings_post1990",
    "log_inc": "n_dwellings_unknown_year",
    "log_soc": "n_social_housing",
    "ind_0_3": "n_age_0_3",
    "ind_4_5": "n_age_4_5",
    "ind_6_10": "n_age_6_10",
    "ind_11_17": "n_age_11_17",
    "ind_18_24": "n_age_18_24",
    "ind_25_39": "n_age_25_39",
    "ind_40_54": "n_age_40_54",
    "ind_55_64": "n_age_55_64",
    "ind_65_79": "n_age_65_79",
    "ind_80p": "n_age_80_plus",
    "ind_inc": "n_age_unknown",
}

filo = filo.rename(columns=rename_map)


# the aim here is to convert numeric variables dor the analysis 
numeric_cols = [c for c in filo.columns if c not in ["grid_id_200m", "grid_id_1km", "grid_id_natural", "commune_insee", "source_file"]]
filo = convert_numeric(filo, numeric_cols)



for col in ["grid_id_200m", "grid_id_1km", "grid_id_natural", "commune_insee"]:
    if col in filo.columns:
        filo[col] = filo[col].astype(str).str.strip()
        filo.loc[filo[col].isin(["nan", "None", ""]), col] = np.nan

if "is_imputed_200m" in filo.columns:
    filo["is_imputed_200m"] = filo["is_imputed_200m"].fillna(0).astype("Int64")
if "is_imputed_1km" in filo.columns:
    filo["is_imputed_1km"] = filo["is_imputed_1km"].fillna(0).astype("Int64")


# here is the most important code in this page because i created some analytical variables including poor houshold share, add different periods of time together, remove or drop dupplications 

filo["n_dwellings_total_known_period"] = (
    filo["n_dwellings_pre1945"].fillna(0)
    + filo["n_dwellings_1945_1969"].fillna(0)
    + filo["n_dwellings_1970_1989"].fillna(0)
    + filo["n_dwellings_post1990"].fillna(0)
)

filo["n_dwellings_total"] = filo["n_dwellings_total_known_period"] + filo["n_dwellings_unknown_year"].fillna(0)

filo["poor_household_share"] = np.where(
    filo["n_households"] > 0,
    filo["n_poor_households"] / filo["n_households"],
    np.nan
)

filo["owner_household_share"] = np.where(
    filo["n_households"] > 0,
    filo["n_owner_households"] / filo["n_households"],
    np.nan
)

filo["single_parent_share"] = np.where(
    filo["n_households"] > 0,
    filo["n_single_parent_households"] / filo["n_households"],
    np.nan
)

filo["house_share"] = np.where(
    filo["n_households"] > 0,
    filo["n_households_house"] / filo["n_households"],
    np.nan
)

filo["collective_housing_share"] = np.where(
    filo["n_households"] > 0,
    filo["n_households_collective_housing"] / filo["n_households"],
    np.nan
)

filo["old_housing_share_pre1945"] = np.where(
    filo["n_dwellings_total_known_period"] > 0,
    filo["n_dwellings_pre1945"] / filo["n_dwellings_total_known_period"],
    np.nan
)

filo["social_housing_share"] = np.where(
    filo["n_dwellings_total"] > 0,
    filo["n_social_housing"] / filo["n_dwellings_total"],
    np.nan
)

filo["avg_dwelling_surface"] = np.where(
    filo["n_households"] > 0,
    filo["sum_dwelling_surface"] / filo["n_households"],
    np.nan
)

filo["avg_winsorized_living_standard"] = np.where(
    filo["n_individuals"] > 0,
    filo["sum_winsorized_living_standard"] / filo["n_individuals"],
    np.nan
)

filo["log_avg_winsorized_living_standard"] = np.log(
    filo["avg_winsorized_living_standard"].where(filo["avg_winsorized_living_standard"] > 0)
)

filo["share_age_18_39"] = np.where(
    filo["n_individuals"] > 0,
    (filo["n_age_18_24"].fillna(0) + filo["n_age_25_39"].fillna(0)) / filo["n_individuals"],
    np.nan
)

filo["share_age_65_plus"] = np.where(
    filo["n_individuals"] > 0,
    (filo["n_age_65_79"].fillna(0) + filo["n_age_80_plus"].fillna(0)) / filo["n_individuals"],
    np.nan
)


# remove duplication based on 200 grid 

before = len(filo)
filo = filo.drop_duplicates(subset=["grid_id_200m"], keep="first")
after = len(filo)

print(f"\nDuplicate 200m rows removed: {before - after}")


# calculate the missing values 
missing_summary = (
    filo.isna().mean()
    .sort_values(ascending=False)
    .rename("share_missing")
    .reset_index()
    .rename(columns={"index": "variable"})
)

print("\nMissingness summary:")
print(missing_summary.head(20))

print("\nImputation counts:")
print(filo["is_imputed_200m"].value_counts(dropna=False))


# finally save the file for the other part of the regression 

filo.to_parquet(CLEAN_DIR / "filosofi_200m_clean.parquet", index=False)
missing_summary.to_csv(CLEAN_DIR / "filosofi_200m_missingness_summary.csv", index=False)

print("\nSaved:")
print(CLEAN_DIR / "filosofi_200m_clean.parquet")
print(CLEAN_DIR / "filosofi_200m_missingness_summary.csv")