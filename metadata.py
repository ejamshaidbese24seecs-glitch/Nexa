import json
import time

# UPDATE THIS PATH
dataset_path = r"C:\Users\Ehsan Ullah\Downloads\archive (4)\arxiv-metadata-oai-snapshot.json"
limit = 2000000  # Must match your indexer limit

def extract_metadata():
    print(f"--- EXTRACTING METADATA (Title, Author, Abstract) ---")
    start_time = time.time()
    
    # We use '|' as a separator because titles rarely contain this symbol
    with open("document_metadata.txt", "w", encoding="utf-8") as f_out, \
         open(dataset_path, 'r', encoding='utf-8') as f_in:
        
        doc_id = 1
        
        for line in f_in:
            if doc_id > limit:
                break
            
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                
                # Clean newlines so the file stays 1 line per document
                title = data.get('title', '').replace('\n', ' ').replace('|', '').strip()
                abstract = data.get('abstract', '').replace('\n', ' ').replace('|', '').strip()
                authors = data.get('authors', '').replace('\n', ' ').replace('|', '').strip()
                
                # Format: DocID | Title | Authors | Abstract
                f_out.write(f"{doc_id}|{title}|{authors}|{abstract}\n")

                if doc_id % 50000 == 0:
                    print(f"Processed {doc_id} documents...")
                
                doc_id += 1

            except Exception:
                pass

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")
    print("File created: 'document_metadata.txt'")

extract_metadata()