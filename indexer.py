import json
import re
import time

dataset_path = r"C:\Users\Ehsan Ullah\Downloads\archive (4)\arxiv-metadata-oai-snapshot.json"
limit = 1000000

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "of", "at", "by", "for", "with", 
    "about", "against", "between", "into", "through", "during", "before", "after", 
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", 
    "under", "again", "further", "then", "once", "here", "there", "when", "where", 
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", 
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", 
    "very", "can", "will", "just", "don", "should", "now", "are", "is", "was", "were"
}

def clean_text(text):
    words = re.findall(r'\w+', text.lower())
    filtered_words = [
        w for w in words 
        if w not in STOP_WORDS and len(w) > 1 and not w.isdigit()
    ]
    return filtered_words

def build_indices():
    print(f"--- STARTING INDEXING FOR {limit} DOCUMENTS ---")
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

                if doc_id % 10000 == 0:
                    print(f"Indexed {doc_id} documents...")
                
                doc_id += 1

            except Exception:
                pass

    with open("lexicon.txt", "w", encoding="utf-8") as f_lex:
        for word, w_id in lexicon.items():
            f_lex.write(f"{word}\t{w_id}\n")

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Total Unique Words: {len(lexicon)}")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

build_indices()