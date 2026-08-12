import pyarrow.parquet as pq
import json

try:
    table = pq.read_table(r'C:\Users\Shivam Patel\.gemini\antigravity\scratch\orion_pipeline\smart_ml\output\orion_alpha_registry.parquet')
    
    unique_rows = set()
    features_col = table.column('features').to_pylist()
    anchors_col = table.column('anchors').to_pylist()
    
    unique_features = set()
    unique_anchors = set()
    
    for f in features_col:
        unique_features.add(str(f))
        
    for a in anchors_col:
        unique_anchors.add(str(a))
        
    for i in range(table.num_rows):
        row = []
        for col_name in table.column_names:
            val = table.column(col_name)[i].as_py()
            row.append(str(val))
        unique_rows.add(tuple(row))
        
    out = {
        "total_rows": table.num_rows,
        "unique_rows": len(unique_rows),
        "unique_features": len(unique_features),
        "unique_anchors": len(unique_anchors)
    }
    
    with open('output_pyarrow.json', 'w') as f:
        json.dump(out, f, indent=2)
except Exception as e:
    with open('output_pyarrow.json', 'w') as f:
        json.dump({"error": str(e)}, f)
