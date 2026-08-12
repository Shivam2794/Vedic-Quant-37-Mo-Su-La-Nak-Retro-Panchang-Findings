import fitz
import sys

pdf_path = r"C:\Users\Shivam Patel\Downloads\VedicReport6-13-20262-40-48AM.pdf"

try:
    doc = fitz.open(pdf_path)
    print(f"Total pages: {len(doc)}")
    
    pages_to_check = [1, 15] # 0-indexed for page 2 and page 16
    for idx in pages_to_check:
        if idx < len(doc):
            print(f"\n--- PAGE {idx+1} TEXT ---")
            page = doc[idx]
            text = page.get_text()
            print(text)
            
            print(f"--- PAGE {idx+1} TABLES ---")
            try:
                tables = page.find_tables()
                if tables:
                    for i, table in enumerate(tables):
                        print(f"Table {i}:")
                        for row in table.extract():
                            print(row)
            except Exception as e:
                print(f"Failed to extract tables from page {idx+1}: {e}")
        else:
            print(f"Page {idx+1} does not exist.")
            
except Exception as e:
    print("Error:", e)
