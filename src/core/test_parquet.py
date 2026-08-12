import pyarrow.parquet as pq

def inspect():
    table = pq.read_table(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch\stock_returns.parquet")
    schema = table.schema
    idx = schema.get_field_index('date')
    if idx == -1:
        print("No date column")
        return
    field = schema.field(idx)
    print("Field type:", field.type)
    print("Sample data:")
    print(table.column(idx).take([0, 1, 2]))

if __name__ == "__main__":
    inspect()
