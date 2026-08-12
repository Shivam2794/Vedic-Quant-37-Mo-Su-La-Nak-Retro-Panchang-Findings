import pyarrow as pa
import pyarrow.compute as pc

table = pa.Table.from_arrays([pa.array([2440587.5, 2440588.5])], names=['jd'])
diff = pc.subtract(table.column('jd'), 2440587.5)
sec = pc.multiply(diff, 86400.0)
ns = pc.multiply(sec, 1e9)
ns_int = pc.cast(ns, pa.int64())
print(ns_int)
