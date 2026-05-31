from pathlib import Path
import pandas as pd
import numpy as np

# import the needed libraries, choose the path and create another for the clean data 

BASE_DIR = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")
DPE_PATH = BASE_DIR / "data" / "raw" / "dpe03existant.csv"
CLEAN_DIR = BASE_DIR / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

OUT_PATH = CLEAN_DIR / "dpe_clean.parquet"

print("Project folder:", BASE_DIR)
print("DPE path:", DPE_PATH)
print("DPE file exists:", DPE_PATH.exists())

if not DPE_PATH.exists():
    raise FileNotFoundError(f"DPE file not found: {DPE_PATH}")

# I selected only some relevant variables to keep and renamed them with easier english to make the analysis easier 
KEEP_COLS = [
    "numero_dpe",
    "date_etablissement_dpe",
    "etiquette_dpe",
    "etiquette_ges",
    "surface_habitable_logement",
    "annee_construction",
    "periode_construction",
    "type_batiment",
    "type_energie_principale_chauffage",
    "id_rnb",
    "adresse_ban",
    "nom_commune_ban",
    "code_postal_ban",
    "code_insee_ban",
    "identifiant_ban",
    "coordonnee_cartographique_x_ban",
    "coordonnee_cartographique_y_ban",
]

RENAME = {
    "numero_dpe": "dpe_id",
    "date_etablissement_dpe": "dpe_date",
    "etiquette_dpe": "dpe_label",
    "etiquette_ges": "ges_label",
    "surface_habitable_logement": "dwelling_surface",
    "annee_construction": "construction_year",
    "periode_construction": "construction_period",
    "type_batiment": "building_type",
    "type_energie_principale_chauffage": "main_heating_energy",
    "adresse_ban": "address_ban",
    "nom_commune_ban": "commune_name_ban",
    "code_postal_ban": "postal_code_ban",
    "code_insee_ban": "commune_insee",
    "identifiant_ban": "ban_id",
    "coordonnee_cartographique_x_ban": "x_ban",
    "coordonnee_cartographique_y_ban": "y_ban",
}

# Because the dataset is very large, this code is to read and clean the dtaa in chunks
chunks = []
raw_rows = 0

print("\nReading DPE file in chunks...")

for i, chunk in enumerate(
    pd.read_csv(
        DPE_PATH,
        sep=",",
        usecols=lambda c: c in KEEP_COLS,
        chunksize=200_000,
        low_memory=False,
    ),
    start=1,
):
    raw_rows += len(chunk)

    chunk = chunk.rename(columns=RENAME)

    # Labels
    chunk["dpe_label"] = chunk["dpe_label"].astype(str).str.strip().str.upper()
    chunk["ges_label"] = chunk["ges_label"].astype(str).str.strip().str.upper()

    # Numeric variables
    chunk["dwelling_surface"] = pd.to_numeric(chunk["dwelling_surface"], errors="coerce")
    chunk["construction_year"] = pd.to_numeric(chunk["construction_year"], errors="coerce")
    chunk["x_ban"] = pd.to_numeric(chunk["x_ban"], errors="coerce")
    chunk["y_ban"] = pd.to_numeric(chunk["y_ban"], errors="coerce")

    # Commune code
    chunk["commune_insee"] = (
        chunk["commune_insee"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
        .str.zfill(5)
    )

    chunk.loc[
        chunk["commune_insee"].isin(["00nan", "0None", "00000", ""]),
        "commune_insee"
    ] = np.nan

    # Low-efficiency indicators
    chunk["is_low_efficiency_fg"] = chunk["dpe_label"].isin(["F", "G"]).astype(int)
    chunk["is_low_efficiency_efg"] = chunk["dpe_label"].isin(["E", "F", "G"]).astype(int)

    # DPE score: higher = worse
    score_map = {
        "A": 1,
        "B": 2,
        "C": 3,
        "D": 4,
        "E": 5,
        "F": 6,
        "G": 7,
    }
    chunk["dpe_score"] = chunk["dpe_label"].map(score_map)

    # Old dwelling indicator
    chunk["is_old_pre1945"] = np.where(
        chunk["construction_year"].notna(),
        (chunk["construction_year"] < 1945).astype(int),
        np.nan,
    )

    # DPE year
    chunk["dpe_year"] = pd.to_datetime(chunk["dpe_date"], errors="coerce").dt.year

    chunks.append(chunk)

    print(f"Finished chunk {i}: total raw rows so far = {raw_rows}")


print("\nCombining chunks...")
dpe_clean = pd.concat(chunks, ignore_index=True)

print("\nRaw DPE shape:", (raw_rows, "selected columns only"))
print("Cleaned DPE shape before duplicate check:", dpe_clean.shape)


before = len(dpe_clean)

if "dpe_id" in dpe_clean.columns:
    dpe_clean = dpe_clean.drop_duplicates(subset=["dpe_id"], keep="first")

after = len(dpe_clean)

print("Rows before dpe_id duplicate removal:", before)
print("Rows after dpe_id duplicate removal:", after)
print("Rows removed as duplicate dpe_id:", before - after)


print("\nFinal cleaned DPE shape:", dpe_clean.shape)

print("\nMissingness check:")
for col in [
    "dpe_label",
    "ges_label",
    "dwelling_surface",
    "construction_year",
    "construction_period",
    "building_type",
    "main_heating_energy",
    "commune_insee",
    "x_ban",
    "y_ban",
]:
    if col in dpe_clean.columns:
        missing_share = dpe_clean[col].isna().mean()
        print(f"{col}: {missing_share:.3%} missing")

print("\nDPE label distribution:")
print(dpe_clean["dpe_label"].value_counts(dropna=False).sort_index())

# here save the file and the results at the end 
dpe_clean.to_parquet(OUT_PATH, index=False)

print("\nSaved cleaned DPE to:")
print(OUT_PATH)

# A small summary for the last parts, within each chuck, categorecal variables are standardized, numerical var are converted to numeric formats. Then i create analytical var including low performance classes, year of the assesment, ranging A to G as numbers. Then combine everything together 