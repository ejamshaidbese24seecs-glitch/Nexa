import os
import shutil

BARREL_SIZE = 10000 
INPUT_FILE = "inverted_index.txt"
OUTPUT_DIR = "barrels"

def create_barrels():
    print(f"--- STARTING BARREL CREATION ---")
    
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    print(f"Reading {INPUT_FILE}...")
    
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            count = 0
            
            current_barrel_id = -1
            current_file = None
            
            for line in f:
                parts = line.split(':', 1)
                if len(parts) < 2: continue
                
                word_id = int(parts[0])
                
                barrel_id = word_id // BARREL_SIZE
                
                if barrel_id != current_barrel_id:
                    if current_file:
                        current_file.close()
                    
                    filename = os.path.join(OUTPUT_DIR, f"barrel_{barrel_id}.txt")
                    current_file = open(filename, "a", encoding="utf-8")
                    current_barrel_id = barrel_id
                    print(f"Writing Barrel {barrel_id}...")

                current_file.write(line)
                count += 1

            if current_file:
                current_file.close()
                
    except FileNotFoundError:
        print("Error: inverted_index.txt not found. Run sorter.py first.")
        return

    print(f"\n--- SUCCESS ---")
    print(f"Processed {count} lines.")
    print(f"Barrels created in '{OUTPUT_DIR}/'")

create_barrels()