# Save this as sorter.py (Same as before, just run it)
import time
from collections import defaultdict

def create_inverted_index():
    print("--- CREATING INVERTED INDEX ---")
    start_time = time.time()
    inverted_index = defaultdict(list)

    try:
        with open("forward_index.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) < 2: continue
                doc_id = parts[0]
                word_ids = parts[1].split()
                for w_id in word_ids:
                    inverted_index[w_id].append(doc_id)
    except FileNotFoundError: return

    print("Saving Inverted Index...")
    with open("inverted_index.txt", "w", encoding="utf-8") as f_out:
        sorted_keys = sorted(inverted_index.keys(), key=lambda x: int(x))
        for w_id in sorted_keys:
            f_out.write(f"{w_id}:{','.join(inverted_index[w_id])}\n")

    print(f"--- SUCCESS --- Time: {round(time.time() - start_time, 2)}s")

create_inverted_index()