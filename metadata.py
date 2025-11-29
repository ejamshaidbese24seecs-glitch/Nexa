import json
import time

dataset_path = r"C:\Users\Ehsan Ullah\Downloads\archive (4)\arxiv-metadata-oai-snapshot.json"
limit = 1000000

def extract_metadata():
    print(f"--- EXTRACTING METADATA (Title, Author, Abstract) ---")
    start_time = time.time()
    
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
                
                title = data.get('title', '').replace('\n', ' ').strip()
                abstract = data.get('abstract', '').replace('\n', ' ').strip()
                authors = data.get('authors', '').replace('\n', ' ').strip()
                
                f_out.write(f"{doc_id}|{title}|{authors}|{abstract}\n")

                if doc_id % 10000 == 0:
                    print(f"Processed {doc_id} documents...")
                
                doc_id += 1

            except Exception:
                pass

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

extract_metadata()