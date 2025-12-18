class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self): self.root = TrieNode()
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children: node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children: return []
            node = node.children[char]
        return self._dfs(node, [])

    def _dfs(self, node, results):
        if len(results) >= 5: return
        if node.is_end_of_word: results.append(node.word)
        for char in node.children: self._dfs(node.children[char], results)
