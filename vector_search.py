import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss

VAULT_DIR = Path("lynker_master_vault")
VSTORE_DIR = VAULT_DIR / "vector_store"
INDEX_FILE = VSTORE_DIR / "faiss.index"
META_FILE  = VSTORE_DIR / "meta.json"

_model = None
_index = None
_meta  = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("shibing624/text2vec-base-chinese")
    return _model

def load_store():
    global _index, _meta
    if _index is None:
        if not INDEX_FILE.exists():
            raise FileNotFoundError(f"索引文件不存在: {INDEX_FILE}")
        _index = faiss.read_index(str(INDEX_FILE))
    if _meta is None:
        if not META_FILE.exists():
            raise FileNotFoundError(f"元数据文件不存在: {META_FILE}")
        _meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    return _index, _meta

def search(query: str, topk=5):
    model = get_model()
    index, meta = load_store()
    q = model.encode([query], normalize_embeddings=True).astype("float32")
    D, I = index.search(q, topk)
    hits = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(meta["items"]):
            continue
        item = meta["items"][idx]
        hits.append({
            "score": float(score),
            **item
        })
    return hits

if __name__ == "__main__":
    from pprint import pprint
    if not INDEX_FILE.exists():
        print("⚠️ 索引不存在，请先运行：python vector_indexer.py --rebuild")
    else:
        pprint(search("同命匹配 与 八字 验证"))
