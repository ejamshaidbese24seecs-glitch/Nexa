import json
import re
import time

# CONFIGURATION
dataset_path = r"C:\Users\Ehsan Ullah\Downloads\archive (4)\arxiv-metadata-oai-snapshot.json"
limit = 2000000 

# STOP WORDS
STOP_WORDS = {
    "the", "and", "for", "that", "this", "with", "from", "which", "are", "was", "were", 
    "have", "has", "had", "can", "could", "should", "would", "will", "not", "but", 
    "into", "about", "than", "then", "they", "their", "them", "these", "those", "such",
    "some", "only", "also", "very", "more", "most", "been", "being", "its", "it's",
    "between", "through", "over", "under", "above", "below", "during", "while",
    "before", "after", "where", "when", "why", "how", "what", "who", "whom", "whose",
    "because", "until", "unless", "since", "upon", "within", "without", "there"
}

def clean_text(text):
    # STRICT REGEX: [a-z]+ 
    # This matches ONLY letters. It rejects numbers (0-9) and underscores (_).
    words = re.findall(r'[a-z]+', text.lower())
    
    filtered_words = []
    for w in words:
        # FILTER:
        # 1. Must be longer than 2 letters (removes 'is', 'to', 'at', 'my')
        # 2. Must not be a stop word
        if len(w) > 2 and w not in STOP_WORDS:
            filtered_words.append(w)
            
    return filtered_words

def build_indices():
    print(f"--- STARTING STRICT INDEXING FOR {limit} DOCUMENTS ---")
    start_time = time.time()

    lexicon = {}
    word_id_counter = 0

    with open("forward_index.txt", "w", encoding="utf-8") as f_out, \
         open(dataset_path, 'r', encoding='utf-8') as f_in:
        
        doc_id = 1
        
        for line in f_in:
            if doc_id > limit:
                break
            
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                title = data.get('title', '').strip()
                abstract = data.get('abstract', '').strip()
                full_text = f"{title} {abstract}"

                words = clean_text(full_text)
                
                if not words:
                    continue

                doc_word_ids = []

                for word in words:
                    if word not in lexicon:
                        lexicon[word] = word_id_counter
                        word_id_counter += 1
                    
                    doc_word_ids.append(str(lexicon[word]))

                f_out.write(f"{doc_id}\t{' '.join(doc_word_ids)}\n")

                if doc_id % 50000 == 0:
                    print(f"Indexed {doc_id} documents...")
                
                doc_id += 1

            except Exception:
                pass

    print("Saving Lexicon...")
    with open("lexicon.txt", "w", encoding="utf-8") as f_lex:
        for word, w_id in lexicon.items():
            f_lex.write(f"{word}\t{w_id}\n")

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Total Unique Words: {len(lexicon)}")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

build_indices()