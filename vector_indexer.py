import os, json, re, time, argparse
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

try:
    from pdfminer.high_level import extract_text as pdf_extract
except ImportError:
    pdf_extract = None

try:
    from docx import Document
except ImportError:
    Document = None

VAULT_DIR = Path("lynker_master_vault")
VSTORE_DIR = VAULT_DIR / "vector_store"
VSTORE_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = VSTORE_DIR / "faiss.index"
META_FILE  = VSTORE_DIR / "meta.json"

_model = None

def get_model():
    global _model
    if _model is None:
        print("🧠 Loading embedding model (shibing624/text2vec-base-chinese)...")
        _model = SentenceTransformer("shibing624/text2vec-base-chinese")
    return _model

def read_text(path: Path) -> str:
    p = str(path).lower()
    try:
        if p.endswith(".md") or p.endswith(".txt"):
            return path.read_text(encoding="utf-8", errors="ignore")
        if p.endswith(".pdf") and pdf_extract:
            return pdf_extract(str(path))
        if p.endswith(".docx") and Document:
            doc = Document(str(path))
            return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"⚠️ 读取失败 {path.name}: {e}")
    return ""

def split_chunks(text, chunk_size=600, overlap=120):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
        if end == len(text):
            break
    return chunks

def scan_docs():
    exts = (".md", ".txt", ".pdf", ".docx")
    for cat in ["project_docs", "dev_brainstorm", "api_docs", "memory"]:
        folder = VAULT_DIR / cat
        if not folder.exists():
            continue
        for f in folder.glob("*"):
            if f.is_file() and f.suffix.lower() in exts:
                yield cat, f

def build_or_update(rebuild=False):
    meta = {"items": []}
    xb = None
    index = None

    if INDEX_FILE.exists() and META_FILE.exists() and not rebuild:
        print("🔁 Loading existing index for incremental update...")
        index = faiss.read_index(str(INDEX_FILE))
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))

    model = get_model()
    added = 0
    for cat, f in scan_docs():
        file_id = f"{cat}/{f.name}"
        if not rebuild and any(it["file_id"] == file_id for it in meta["items"]):
            continue

        txt = read_text(f)
        chunks = split_chunks(txt)
        if not chunks:
            continue
        
        embs = model.encode(chunks, normalize_embeddings=True)
        embs = np.array(embs, dtype="float32")

        if index is None:
            index = faiss.IndexFlatIP(embs.shape[1])
        index.add(embs)

        for i, c in enumerate(chunks):
            meta["items"].append({
                "file_id": file_id,
                "category": cat,
                "chunk_id": i,
                "text": c
            })
        added += len(chunks)
        print(f"📚 Indexed: {file_id} ({len(chunks)} chunks)")

    if index is None:
        print("⚠️ 没有文档可索引。")
        return

    faiss.write_index(index, str(INDEX_FILE))
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 索引完成：{len(meta['items'])} chunks | 新增 {added} chunks")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true", help="重建索引（忽略历史）")
    args = ap.parse_args()
    t0 = time.time()
    build_or_update(rebuild=args.rebuild)
    print(f"⏱️ 用时：{time.time()-t0:.2f}s")
