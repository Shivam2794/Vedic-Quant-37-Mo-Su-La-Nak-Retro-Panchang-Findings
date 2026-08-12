import numpy as np

a = np.array(['feat_1', 'feat_2'], dtype=object)
b = np.array(['feat_1', 'feat_2'], dtype=object)

print("a.tobytes() == b.tobytes():", a.tobytes() == b.tobytes())

a2 = np.array(['feat_1', 'feat_2'])
b2 = np.array(['feat_1', 'feat_2'])

print("a2.tobytes() == b2.tobytes():", a2.tobytes() == b2.tobytes())
