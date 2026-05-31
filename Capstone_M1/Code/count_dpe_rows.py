from pathlib import Path
import time

dpe_path = Path(r"C:\Users\CompuCenter\Downloads\capstone_m1")

start = time.time()

row_count = 0

with open(dpe_path, "r", encoding="utf-8", errors="ignore") as f:
    for row_count, line in enumerate(f, start=0):
        pass

# subtract 1 for the header row
data_rows = row_count

print("Total lines including header:", row_count + 1)
print("Data rows without header:", data_rows)

elapsed = time.time() - start
print(f"Time taken: {elapsed:.1f} seconds")

# what i did in this code is that I imported the needed libraries, define the path for python to follow, count the rows from the DPE file (excluding the header)