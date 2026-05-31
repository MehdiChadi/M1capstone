from pathlib import Path
import pandas as pd

project = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")

final_dir = project / "data" / "final"
csv_dir = project / "outputs" / "csv_exports"
csv_dir.mkdir(parents=True, exist_ok=True)

files_to_export = {
    "analysis_200m_fixed.parquet": "analysis_200m_fixed.csv",
    "analysis_200m_non_imputed_fixed.parquet": "analysis_200m_non_imputed_fixed.csv",
    "dpe_filosofi_micro_merged_fixed.parquet": "dpe_filosofi_micro_merged_fixed.csv",
}

for parquet_name, csv_name in files_to_export.items():
    parquet_path = final_dir / parquet_name
    csv_path = csv_dir / csv_name

    print("\nReading:", parquet_path)
    df = pd.read_parquet(parquet_path)

    print("Shape:", df.shape)
    print("Saving CSV:", csv_path)

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print("Saved:", csv_path)


# import libraries, define create and export files from parquet to csv or excel, save the final outputs 

print("\nAll CSV exports saved in:")
print(csv_dir)