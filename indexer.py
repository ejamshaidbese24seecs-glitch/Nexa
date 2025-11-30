import json
import re
import time

# CONFIGURATION
dataset_path = r"C:\Users\Ehsan Ullah\Downloads\archive (4)\arxiv-metadata-oai-snapshot.json"
limit = 2000000 

# 1. LANGUAGE MARKERS
# If we see these, it's definitely English
ENGLISH_STOP = {"the", "and", "is", "of", "in", "to", "with", "that", "for", "are", "this"}
# If we see these, it's definitely German
GERMAN_STOP = {"der", "die", "und", "ist", "den", "von", "zu", "das", "sich", "des", "eine", "mit"}
# If we see these, it's definitely French
FRENCH_STOP = {"le", "la", "et", "des", "en", "un", "une", "que", "dans", "pour", "sur", "qui"}

# 2. FILTER WORDS TO IGNORE IN INDEX
STOP_WORDS_FILTER = {
    "a", "an", "the", "and", "or", "but", "if", "of", "at", "by", "for", "with", 
    "about", "against", "between", "into", "through", "during", "before", "after", 
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", 
    "under", "again", "further", "then", "once", "here", "there", "when", "where", 
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", 
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", 
    "very", "can", "will", "just", "don", "should", "now", "are", "is", "was", "were",
    "this", "that", "these", "those", "have", "has", "had", "which"
}

def is_strictly_english(text):
    """
    Scores the document.
    It passes ONLY if it has significantly more English words than German/French.
    """
    # Check first 500 words to be fast
    words = text.lower().split()[:500]
    
    eng_score = 0
    foreign_score = 0
    
    for w in words:
        if w in ENGLISH_STOP:
            eng_score += 1
        elif w in GERMAN_STOP or w in FRENCH_STOP:
            foreign_score += 1

    # RULE 1: Must have at least some English markers
    if eng_score < 3:
        return False
        
    # RULE 2: Foreign words must be very rare (less than 10% of English markers)
    # This kills German papers that just happen to use "in" or "pro"
    if foreign_score > (eng_score * 0.1):
        return False
        
    return True

def clean_text(text):
    # Strict regex: Only letters a-z. 
    words = re.findall(r'[a-z]+', text.lower())
    
    filtered_words = []
    for w in words:
        # Keep word if > 2 chars and not in the stop list
        if len(w) > 2 and w not in STOP_WORDS_FILTER:
            filtered_words.append(w)
            
    return filtered_words

def build_indices():
    print(f"--- STARTING STRICT ENGLISH INDEXING ---")
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

                # 1. STRICT LANGUAGE CHECK
                if not is_strictly_english(full_text):
                    continue # Skip German/French docs

                # 2. CLEAN TEXT
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