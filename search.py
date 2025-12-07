import time
import sys
import os
import json

# CONFIGURATION
BARREL_SIZE = 10000
BARRELS_DIR = "barrels"
METADATA_FILE = "document_metadata.json"

def load_lexicon():
    print("Loading Lexicon...", end=" ")
    lexicon = {}
    if os.path.exists("lexicon.txt"):
        with open("lexicon.txt", "r", encoding="utf-8") as f:
            for line in f:
                try:
                    parts = line.strip().split('\t')
                    lexicon[parts[0]] = int(parts[1])
                except: pass
        print(f"Done ({len(lexicon)} words).")
        return lexicon
    else:
        print("\nERROR: lexicon.txt missing.")
        sys.exit()

def get_docs_from_barrel(word_id):
    barrel_id = word_id // BARREL_SIZE
    barrel_path = os.path.join(BARRELS_DIR, f"barrel_{barrel_id}.txt")
    
    if not os.path.exists(barrel_path):
        return set()

    target_key = str(word_id) + ":"
    try:
        with open(barrel_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(target_key):
                    parts = line.split(':')
                    return set(parts[1].strip().split(','))
    except: return set()
    return set()

def get_metadata(doc_id):
    target_id = int(doc_id)
    if not os.path.exists(METADATA_FILE):
        return "Error", "Metadata missing", ""

    # Scanning JSON lines sequentially
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if data['id'] == target_id:
                    return data['title'], data['authors'], data['abstract']
                # Optimization: Since IDs are sorted, stop if we pass the target
                if data['id'] > target_id: 
                    break
            except: continue
    return "Unknown Document", "Unknown Author", ""

# --- MAIN EXECUTION ---
print("--- NEXA SEARCH ENGINE (BARRELS ACTIVE) ---")
lexicon = load_lexicon()

if not os.path.exists(BARRELS_DIR):
    print(f"WARNING: '{BARRELS_DIR}' directory not found. Search will fail.")

while True:
    query = input("\nSearch (type 'exit' to quit): ").lower().strip()
    if query == 'exit': break
    
    words = query.split()
    if not words: continue
    
    start_time = time.time()
    
    # 1. Validate First Word
    if words[0] not in lexicon:
        print(f"Word '{words[0]}' not found.")
        continue
    
    # 2. Retrieve Initial Results from Barrel
    first_id = lexicon[words[0]]
    result_docs = get_docs_from_barrel(first_id)
    
    # 3. Intersect with remaining words
    for word in words[1:]:
        if word in lexicon:
            next_id = lexicon[word]
            next_docs = get_docs_from_barrel(next_id)
            result_docs = result_docs.intersection(next_docs)
        else:
            print(f"Word '{word}' not found.")
            result_docs = set()
            break
            
    # 4. Display Results
    results = sorted(list(result_docs), key=lambda x: int(x))
    search_time = round(time.time() - start_time, 3)
    
    print(f"Found {len(results)} results in {search_time} seconds.")
    
    # Show Top 3 Results
    for i, doc_id in enumerate(results[:3]):
        title, author, abstract = get_metadata(doc_id)
        print(f"\n[{i+1}] {title}")
        print(f"    Author: {author[:50]}...")
        print(f"    Abstract: {abstract[:100]}...")