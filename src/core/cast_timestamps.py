import os
import glob
import pyarrow as pa
import pyarrow.parquet as pq

TARGET_DIR = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\features_partitioned"
RETURNS_FILE = r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet"

def cast_file(f):
    try:
        table = pq.read_table(f)
        schema = table.schema
        idx = schema.get_field_index('date')
        if idx == -1: return
        
        field = schema.field(idx)
        if isinstance(field.type, pa.TimestampType) and field.type.unit == 'ns':
            import pyarrow.compute as pc
            col = table.column(idx)
            
            # Cast unit to 'us' first, keeping original timezone
            col = col.cast(pa.timestamp('us', tz=field.type.tz))
            
            # Enforce UTC timezone without dropping/shifting hours
            if field.type.tz is None:
                col = pc.assume_timezone(col, 'UTC')
            elif field.type.tz != 'UTC':
                col = col.cast(pa.timestamp('us', tz='UTC'))
                
            new_type = pa.timestamp('us', tz='UTC')
            new_field = field.with_type(new_type)
            new_schema = schema.set(idx, new_field)
            
            # Replace column
            new_table = table.set_column(idx, new_field, col)
            
            # Overwrite
            pq.write_table(new_table, f)
            print(f"Fixed {f}")
    except Exception as e:
        print(f"Error on {f}: {e}")

if __name__ == "__main__":
    print("Fixing feature matrices...")
    for f in glob.glob(os.path.join(TARGET_DIR, "**", "*.parquet"), recursive=True):
        cast_file(f)
    print("Fixing stock_returns...")
    cast_file(RETURNS_FILE)
    print("Done!")
