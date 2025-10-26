import json, os, re

BASE = "lkk_knowledge_base"

def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def find_relevant_knowledge(query: str):
    """
    Keyword-based lightweight RAG (no vector DB needed yet).
    """
    results = []

    # Search in rule texts
    for fname in os.listdir(os.path.join(BASE, "rules")):
        text = _read(os.path.join(BASE, "rules", fname))
        if any(k in text for k in query.split()):
            results.append(("rule", fname, text))

    # Search in pattern JSON
    for fname in os.listdir(os.path.join(BASE, "patterns")):
        data = json.load(open(os.path.join(BASE, "patterns", fname), "r"))
        if any(k in json.dumps(data) for k in query.split()):
            results.append(("pattern", fname, data))

    return results[:5]   # Return top 5 matches
