import PyPDF2
import fitz  # PyMuPDF
import sys
import traceback

pdf_path = r"C:\Users\Shivam Patel\Downloads\VedicReport6-13-20262-40-48AM.pdf"

try:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    
    with open("parsed_pdf.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Extracted successfully using fitz.")
except Exception as e:
    print("fitz failed:", e)
    traceback.print_exc()
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        with open("parsed_pdf.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Extracted successfully using PyPDF2.")
    except Exception as e2:
        print("PyPDF2 failed:", e2)
        traceback.print_exc()
