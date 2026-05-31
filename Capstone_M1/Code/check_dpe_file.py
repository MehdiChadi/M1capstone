from pathlib import Path
import os
import csv

dpe_path = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")

print("File exists:", dpe_path.exists())

size_gb = dpe_path.stat().st_size / (1024 ** 3)
print(f"File size: {size_gb:.2f} GB")

# Read only the header, not the full file
with open(dpe_path, "r", encoding="utf-8", errors="ignore", newline="") as f:
    first_line = f.readline()

print("\nFirst line / header preview:")
print(first_line[:1000])

# Detect separator
sample = first_line
if ";" in sample:
    sep = ";"
elif "," in sample:
    sep = ","
else:
    sep = None

print("\nDetected separator:", sep)