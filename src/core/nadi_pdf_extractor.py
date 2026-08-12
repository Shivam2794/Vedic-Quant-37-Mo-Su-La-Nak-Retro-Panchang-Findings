import os
import sys
import fitz
import base64
import requests

API_KEY = "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"

def is_valid_astrology_chart(base64_image):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "bytedance-seed/seed-1.6-flash",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Is this image an astrological chart, table, or technical diagram? Reply ONLY with YES or NO."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.0
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        ans = result["choices"][0]["message"]["content"].strip().upper()
        return "YES" in ans
    except Exception as e:
        print(f"Error checking image validity: {e}")
        # Default to True on failure so we don't miss anything important
        return True

def get_image_description(base64_image):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen3.6-35b-a3b",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is an image from a Vedic/Jaimini Astrology book. Please describe the image in detail. If it's a chart, list the planets and their positions. If it's a figure or text, transcribe and explain it."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error getting image description: {e}")
        return "[Image description extraction failed]"

def extract_pdf(pdf_path, output_path):
    print(f"Extracting {pdf_path}...")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# SOURCE BOOK: {os.path.basename(pdf_path)}\n\n")
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            f.write(f"\n\n--- PAGE {page_num + 1} ---\n\n")
            f.write(text)
            
            # Extract images
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    base64_img = base64.b64encode(image_bytes).decode('utf-8')
                    print(f"  Page {page_num + 1}: Found image {img_index + 1}. Checking validity with Seed 1.6 Flash...")
                    is_valid = is_valid_astrology_chart(base64_img)
                    if is_valid:
                        print(f"  Page {page_num + 1}: Image {img_index + 1} is valid. Requesting description from Qwen 3.6 35B...")
                        description = get_image_description(base64_img)
                        f.write(f"\n\n[IMAGE {img_index + 1} DESCRIPTION]\n{description}\n[/IMAGE {img_index + 1} DESCRIPTION]\n")
                    else:
                        print(f"  Page {page_num + 1}: Image {img_index + 1} rejected (not a chart/diagram). Skipping.")
                except Exception as e:
                    print(f"  Page {page_num + 1}: Failed to extract image {img_index + 1}: {e}")
                    
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <pdf1> <pdf2> ...")
        sys.exit(1)
        
    for pdf in sys.argv[1:]:
        out_name = os.path.basename(pdf).replace(".pdf", "_extracted.txt")
        out_path = os.path.join(r"C:\Users\Shivam Patel\.gemini\antigravity\scratch", out_name)
        extract_pdf(pdf, out_path)
