import time
from collections import defaultdict

def create_inverted_index():
    print("--- CREATING INVERTED INDEX ---")
    start_time = time.time()

    # Using defaultdict to automatically create lists for new words
    inverted_index = defaultdict(list)

    try:
        print("Reading Forward Index (this may take time)...")
        with open("forward_index.txt", "r", encoding="utf-8") as f:
            count = 0
            for line in f:
                parts = line.strip().split('\t')
                
                # Skip empty or malformed lines
                if len(parts) < 2:
                    continue
                
                doc_id = parts[0]
                # Split the string of IDs into a list
                word_ids = parts[1].split()
                
                # The Core Logic: Map WordID -> DocID
                for w_id in word_ids:
                    inverted_index[w_id].append(doc_id)
                
                count += 1
                if count % 100000 == 0:
                    print(f"Processed {count} documents...")

    except FileNotFoundError:
        print("Error: forward_index.txt not found. Run indexer.py first.")
        return

    print(f"Sorting and Saving Inverted Index for {len(inverted_index)} unique words...")
    
    with open("inverted_index.txt", "w", encoding="utf-8") as f_out:
        # Sort by WordID (numerically) so the file is organized
        # We convert keys to int for sorting, then back to string for writing
        sorted_keys = sorted(inverted_index.keys(), key=lambda x: int(x))
        
        for w_id in sorted_keys:
            doc_list = inverted_index[w_id]
            # Format: WordID: DocID, DocID, DocID...
            f_out.write(f"{w_id}: {','.join(doc_list)}\n")

    end_time = time.time()
    print(f"\n--- SUCCESS ---")
    print(f"Time Taken: {round(end_time - start_time, 2)} seconds")
    print("File created: 'inverted_index.txt'")

# Run the function
create_inverted_index()