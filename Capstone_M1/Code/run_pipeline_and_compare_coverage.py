from pathlib import Path
import subprocess
import sys
import pandas as pd




BASE_DIR = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")
SRC_DIR = BASE_DIR / "src"
CLEAN_DIR = BASE_DIR / "data" / "clean"
FINAL_DIR = BASE_DIR / "data" / "final"



scripts = [
    SRC_DIR / "01_clean_dpe_ban_version.py",
    SRC_DIR / "02_clean_filosofi_200m.py",
    SRC_DIR / "03_merge_commune_first.py",
    SRC_DIR / "03b_merge_200_from_ban_coords.py",
]

for script in scripts:
    print(f"\nRunning: {script.name}")
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"Script failed: {script.name}")


print("\n--- Coverage comparison ---")

dpe = pd.read_parquet(CLEAN_DIR / "dpe_clean_latest_building.parquet")
analysis_commune = pd.read_parquet(FINAL_DIR / "analysis_commune.parquet")
analysis_200m = pd.read_parquet(FINAL_DIR / "analysis_200m.parquet")
analysis_200m_non_imputed = pd.read_parquet(FINAL_DIR / "analysis_200m_non_imputed.parquet")

print(f"Full cleaned DPE rows: {len(dpe):,}")
print(f"Communes with at least one DPE observation: {analysis_commune['n_dpe_obs'].notna().sum():,}")
print(f"200m cells with at least one DPE observation: {analysis_200m['n_dpe_obs'].notna().sum():,}")
print(f"Non-imputed 200m cells with at least one DPE observation: {analysis_200m_non_imputed['n_dpe_obs'].notna().sum():,}")

print(f"Commune-level match share: {analysis_commune['n_dpe_obs'].notna().mean():.3f}")
print(f"200m-level match share: {analysis_200m['n_dpe_obs'].notna().mean():.6f}")
print(f"Non-imputed 200m-level match share: {analysis_200m_non_imputed['n_dpe_obs'].notna().mean():.6f}")