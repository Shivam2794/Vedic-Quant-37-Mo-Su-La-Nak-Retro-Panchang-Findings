
from astro_vargas import get_varga_sign, get_all_vargas
import time

print("Testing Numba compilation...")
t0 = time.time()
res = get_varga_sign(134.5678, 9) # Compile step
t1 = time.time()
print(f"Compilation time: {t1-t0:.4f}s")

t0 = time.time()
for _ in range(100000):
    get_varga_sign(134.5678, 9)
t1 = time.time()
print(f"Execution time for 100,000 calls: {t1-t0:.4f}s")

vargas = get_all_vargas(134.5678)
print("All Vargas:", vargas)

