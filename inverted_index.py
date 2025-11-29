import time
from collections import defaultdict

def create_inverted_index():
    print("--- CREATING INVERTED INDEX ---")
    start_time = time.time()

    inverted_index = defaultdict(list)

    try:
        with open("forward_index.txt", "r", encoding="utf-8") as f:
            count = 0
            for line in f:
                parts = line.strip().split('\t')
                
                if len(parts) < 2:
                    continue
                
                doc_id = parts[0]
                word_ids = parts[1].split()
                
                for w_id in word_ids:
                    inverted_index[w_id].append(doc_id)
                
                count += 1
                if count % 50000 == 0:
                    print(f"Processed {count} documents...")

    except FileNotFoundError:
        print("Error: forward_index.txt not found.")
        return

    print(f"Saving Inverted Index for {len(inverted_index)} words...")
    
    with open("inverted_index.txt", "w", encoding="utf-8") as f_out:
        sorted_keys = sorted(inverted_index.keys(), key=lambda x: int(x))
        
        for w_id in sorted_keys:
            doc_list = inverted_index[w_id]
            f_out.write(f"{w_id}:{','.join(doc_list)}\n")

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")

create_inverted_index()