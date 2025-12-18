from flask import Flask, render_template, request, jsonify
import time
import os
from collections import Counter
import json

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
            if char not in node.children: return []
            node = node.children[char]
        results = []
        self._dfs(node, results)
        return results[:5]

    def _dfs(self, node, results):
        if len(results) >= 5: return
        if node.is_end_of_word: results.append(node.word)
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('search_query', '').lower().strip()
        if not query: return render_template('index.html')

        start_time = time.time()
        words = query.split()
        
        # Simple Search (No Spell Check)
        if words[0] not in lexicon:
            return render_template('index.html', error=f"Word '{words[0]}' not found.", query=query)
        
        first_id = lexicon[words[0]]
        final_scores = get_word_scores(first_id)
        
        for word in words[1:]:
            if word in lexicon:
                next_scores = get_word_scores(lexicon[word])
                intersected = {}
                for doc_id in final_scores:
                    if doc_id in next_scores:
                        intersected[doc_id] = final_scores[doc_id] + next_scores[doc_id]
                final_scores = intersected
            else:
                 return render_template('index.html', error=f"Word '{word}' not found.", query=query)

        ranked_docs = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        results = []
        for doc_id, score in ranked_docs:
            meta = get_metadata(doc_id)
            if meta:
                meta['score'] = score
                meta['id'] = doc_id  # <--- WE SAVE ID HERE TO USE IN LINK
                results.append(meta)

        duration = round(time.time() - start_time, 4)
        return render_template('index.html', results=results, query=query, time=duration)

    return render_template('index.html')

# --- THIS IS THE NEW PAGE FOR VIEWING A DOCUMENT ---
@app.route('/view/<int:doc_id>')
def view_document(doc_id):
    meta = get_metadata(doc_id)
    # This generates a simple, clean page for just that one document
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{meta['title']}</title>
        <style>
            body {{
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                color: #f8fafc;
                margin: 0;
                padding: 40px;
                min-height: 100vh;
                display: flex;
                justify-content: center;
            }}
            .container {{
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 40px;
                max-width: 800px;
                width: 100%;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            }}
            .btn {{
                display: inline-block;
                margin-bottom: 20px;
                color: #818cf8;
                text-decoration: none;
                font-weight: 600;
                font-size: 0.9rem;
            }}
            .btn:hover {{ color: white; text-decoration: underline; }}
            h1 {{
                font-size: 2rem;
                margin-bottom: 10px;
                line-height: 1.2;
                color: #e2e8f0;
            }}
            .meta-info {{
                color: #94a3b8;
                font-size: 1rem;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                font-style: italic;
            }}
            .content {{
                line-height: 1.8;
                font-size: 1.1rem;
                color: #cbd5e1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="btn">← Back to Search Results</a>
            <h1>{meta['title']}</h1>
            <div class="meta-info">Authors: {meta['authors']}</div>
            
            <div class="content">
                <strong>Abstract:</strong><br><br>
                {meta['abstract']}
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '').lower()
    if not query: return jsonify([])
    suggestions = trie.search_prefix(query)
    return jsonify(suggestions)

if __name__ == '__main__':
    load_data()
    app.run(debug=True)