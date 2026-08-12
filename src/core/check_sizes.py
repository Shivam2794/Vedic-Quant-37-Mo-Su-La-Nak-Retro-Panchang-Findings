import os
mds = ['history.md', 'failures_and_fixes.md', 'backtests.md']
for md in mds:
    p = f"F:\\Fleet_Master_Archive\\Bot_1_Hybrid_8_Sleeve\\{md}"
    if os.path.exists(p):
        print(f"{md}: {os.path.getsize(p)}")
    else:
        print(f"{md}: not found")
