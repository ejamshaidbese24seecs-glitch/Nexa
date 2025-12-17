from flask import Flask, render_template, request, jsonify
import time
import os
from collections import Counter
import json
import difflib  # <--- NEW: For "Did you mean?" AI correction

app = Flask(__name__)

# --- CONFIGURATION ---
BARREL_SIZE = 10000
BARRELS_DIR = "barrels"
LEXICON_FILE = "lexicon.txt"
METADATA_FILE = "document_metadata.json"
METADATA_INDEX_FILE = "metadata_index.json"

# --- TRIE DATA STRUCTURE ---
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.word = None

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.word = word

    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        results = []
        self._dfs(node, results)
        return results[:5]

    def _dfs(self, node, results):
        if len(results) >= 5: return
        if node.is_end_of_word:
            results.append(node.word)
        for char in sorted(node.children.keys()):
            self._dfs(node.children[char], results)

# --- GLOBAL VARIABLES ---
lexicon = {}
trie = Trie()
meta_index = {}

def load_data():
    global lexicon, meta_index, trie
    print("Loading Lexicon & Building Trie...", end=" ")
    if os.path.exists(LEXICON_FILE):
        with open(LEXICON_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    parts = line.strip().split('\t')
                    word = parts[0]
                    lexicon[word] = int(parts[1])
                    trie.insert(word)
                except: pass
    print(f"Done ({len(lexicon)} words).")

    print("Loading Metadata Index...", end=" ")
    if os.path.exists(METADATA_INDEX_FILE):
        try:
            with open(METADATA_INDEX_FILE, "r", encoding="utf-8") as f:
                raw_map = json.load(f)
                meta_index = {int(k): v for k, v in raw_map.items()}
        except: pass
    print(f"Done ({len(meta_index)} locations).")

def get_word_scores(word_id):
    barrel_id = word_id // BARREL_SIZE
    barrel_path = os.path.join(BARRELS_DIR, f"barrel_{barrel_id}.txt")
    scores = {}
    if not os.path.exists(barrel_path): return scores
    target_key = str(word_id) + ":"
    try:
        with open(barrel_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(target_key):
                    parts = line.split(':')
                    doc_ids = parts[1].strip().split(',')
                    scores = dict(Counter(doc_ids))
                    return scores
    except: pass
    return scores

def get_metadata(doc_id):
    target_id = int(doc_id)
    if target_id in meta_index:
        offset = meta_index[target_id]
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                f.seek(offset)
                line = f.readline()
                return json.loads(line)
        except: return {'title': 'Error', 'authors': 'Unknown', 'abstract': ''}
    return {'title': 'Unknown', 'authors': 'Unknown', 'abstract': ''}

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_query = request.form.get('search_query', '').lower().strip()
        if not original_query: return render_template('index.html')

        start_time = time.time()
        words = original_query.split()
        
        # --- "AI" SPELLING CORRECTION LOGIC ---
        corrected_words = []
        was_corrected = False
        
        for word in words:
            if word in lexicon:
                corrected_words.append(word)
            else:
                # Find closest match using Levenshtein Distance
                # n=1 means find top 1 match, cutoff=0.6 means must be 60% similar
                matches = difflib.get_close_matches(word, lexicon.keys(), n=1, cutoff=0.6)
                if matches:
                    corrected_words.append(matches[0])
                    was_corrected = True
                else:
                    # If no close match, keep original (it will fail search, but user sees it)
                    corrected_words.append(word)
        
        # Use the corrected list for the actual search
        final_query_list = corrected_words
        
        # 1. Search Logic
        if final_query_list[0] not in lexicon:
            return render_template('index.html', error=f"No results found for '{original_query}'.", query=original_query)
        
        first_id = lexicon[final_query_list[0]]
        final_scores = get_word_scores(first_id)
        
        for word in final_query_list[1:]:
            if word in lexicon:
                next_scores = get_word_scores(lexicon[word])
                intersected = {}
                for doc_id in final_scores:
                    if doc_id in next_scores:
                        intersected[doc_id] = final_scores[doc_id] + next_scores[doc_id]
                final_scores = intersected
            else:
                 return render_template('index.html', error=f"No results for '{word}'", query=original_query)

        ranked_docs = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        results = []
        for doc_id, score in ranked_docs:
            meta = get_metadata(doc_id)
            if meta:
                meta['score'] = score
                results.append(meta)

        duration = round(time.time() - start_time, 4)
        
        # Pass both original and corrected query to HTML
        corrected_string = " ".join(corrected_words)
        return render_template('index.html', 
                               results=results, 
                               query=original_query, 
                               time=duration,
                               corrected_query=corrected_string if was_corrected else None)

    return render_template('index.html')

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '').lower()
    if not query: return jsonify([])
    suggestions = trie.search_prefix(query)
    return jsonify(suggestions)

if __name__ == '__main__':
    load_data()
    app.run(debug=True)