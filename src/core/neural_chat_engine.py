import os
import json
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Initializing Neural Semantic Transcriber...")

output_file = r'C:\Users\Shivam Patel\.gemini\antigravity\brain\ac09686f-b2e2-4349-aa40-8ff7fa4bba80\usa_vedic_master_transcript.md'

search_dirs = [
    r'C:\Users\Shivam Patel\.gemini',
    r'C:\Users\Shivam Patel\Downloads',
    r'C:\Users\patel\Desktop\Python\Learn'
]

valid_chats = []
for d in search_dirs:
    if not os.path.exists(d): continue
    for root, dirs, files in os.walk(d):
        # Exclude known heavy non-text folders or India-specific folders from reading
        if 'india' in root.lower() or 'nifty' in root.lower() or 'node_modules' in root.lower():
            dirs[:] = []
            continue
        
        for f in files:
            path = os.path.join(root, f)
            if f.endswith('.jsonl') or f.endswith('.md') or f.endswith('.txt'):
                valid_chats.append(path)

print(f"Found {len(valid_chats)} potential text files to parse. Loading contents into memory...")

documents = []
doc_paths = []
doc_contents = []

for path in valid_chats:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            if not content.strip(): continue
            
            parsed_text = []
            if path.endswith('.jsonl'):
                lines = content.strip().split('\n')
                for line in lines:
                    try:
                        obj = json.loads(line)
                        if obj.get('source') in ['USER_EXPLICIT', 'MODEL'] and obj.get('content'):
                            parsed_text.append(obj.get('content'))
                    except: pass
                full_text = " ".join(parsed_text)
            else:
                full_text = content
                
            documents.append(full_text)
            doc_paths.append(path)
            doc_contents.append(content)
    except: pass

print(f"Successfully loaded {len(documents)} valid documents. Vectorizing...")

# Anchor paragraph describing the EXACT conceptual architecture of the USA Vedic Quant project
anchor_text = """
We are building a massive algorithmic trading quantitative architecture for the USA market, specifically SPY and QQQ options.
This involves extracting astrological features, utilizing the 740+ baseline rules provided previously.
We are combining this with rule extraction and parsing from classical astrology books like Bhrigu Nandi Nadi and Jamini sutras.
The goal is to feed these parsed Nadi rules and planetary features into a multiphase machine learning architecture, involving deep learning or a multi-agent council.
This project explicitly targets USA options and does not involve the Indian stock market, Nifty, NSE, or Zerodha.
"""

# Add anchor to the documents for vectorization
corpus = [anchor_text] + documents

# Vectorize using TF-IDF (removing english stop words)
vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
tfidf_matrix = vectorizer.fit_transform(corpus)

# Calculate cosine similarity between the anchor (index 0) and all documents
anchor_vector = tfidf_matrix[0:1]
similarities = cosine_similarity(anchor_vector, tfidf_matrix[1:]).flatten()

# We want files with a similarity threshold > 0.05 (adjusting for strictness)
# However, to be safe and catch implicit conversations, we will rank them and pick the highly related ones.
# Also strongly penalize if the document heavily mentions 'india' or 'nifty'
threshold = 0.04
matched_indices = []

for i, score in enumerate(similarities):
    doc_lower = documents[i].lower()
    india_score = doc_lower.count('india') + doc_lower.count('nifty') + doc_lower.count('nse')
    usa_score = doc_lower.count('usa') + doc_lower.count('qqq') + doc_lower.count('spy')
    
    # Penalize the score heavily if it's clearly an India project file
    adjusted_score = score
    if india_score > 5 and usa_score == 0:
        adjusted_score -= 0.1
        
    if adjusted_score >= threshold:
        matched_indices.append((i, adjusted_score))

# Sort by similarity
matched_indices.sort(key=lambda x: x[1], reverse=True)

print(f"Neural Vectorizer isolated {len(matched_indices)} highly relevant transcripts/files.")

master_text = ["# USA Vedic Quant Project - Monolithic Transcripts\n\n"]
master_text.append(f"Generated via TF-IDF Neural Semantic Extraction. Processed {len(documents)} total files.\n")
master_text.append(f"Identified {len(matched_indices)} conceptually clustered files.\n\n")

for idx, score in matched_indices:
    path = doc_paths[idx]
    master_text.append(f"\n\n{'='*80}\n")
    master_text.append(f"FILE/CHAT SOURCE: {path}\n")
    master_text.append(f"SEMANTIC RELEVANCE SCORE: {score:.4f}\n")
    master_text.append(f"{'='*80}\n\n")
    
    # Parse appropriately for the monolithic file
    if path.endswith('.jsonl'):
        lines = doc_contents[idx].strip().split('\n')
        for line in lines:
            try:
                obj = json.loads(line)
                if obj.get('source') in ['USER_EXPLICIT', 'MODEL'] and obj.get('content'):
                    role = 'USER' if obj.get('source') == 'USER_EXPLICIT' else 'AI'
                    master_text.append(f"[{role}]:\n{obj.get('content')}\n\n")
            except: pass
    else:
        master_text.append(doc_contents[idx])

with open(output_file, 'w', encoding='utf-8') as file:
    file.write("".join(master_text))

print(f"Done! Monolithic transcript saved to {output_file}")
