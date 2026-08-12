import sys
sys.path.append(r"C:\Users\patel\Desktop\Python\Learn\umbrella")
from mcp_god_system import query_god_system, _read_primer

print("Testing _read_primer...")
primer = _read_primer()
print(f"Primer length: {len(primer)}")

print("Testing query_god_system...")
res = query_god_system("fleet scheduler")
print(f"Result length: {len(res)}")
print(res[:500])
