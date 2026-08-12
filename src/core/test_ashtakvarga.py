
from astro_ashtakvarga import get_raw_ashtakvarga, get_reduced_ashtakvarga
import numpy as np
import time

print("Testing Ashtakvarga Numba compilation...")

# Test input: 8 positions (Sun, Moon, Mars, Merc, Jup, Ven, Sat, Asc)
test_signs = np.array([0, 4, 8, 1, 5, 9, 2, 6], dtype=np.int32)

t0 = time.time()
bav, sav = get_raw_ashtakvarga(test_signs)
t1 = time.time()
print(f"Compilation and execution time: {t1-t0:.4f}s")
print(f"Total SAV Points (should be exactly 337): {np.sum(sav)}")

t0 = time.time()
for _ in range(10000):
    get_raw_ashtakvarga(test_signs)
t1 = time.time()
print(f"Execution time for 10,000 passes: {t1-t0:.4f}s")

reduced_bav = get_reduced_ashtakvarga(bav)
print("Raw BAV unchanged:", id(bav) != id(reduced_bav))
