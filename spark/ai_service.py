import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from sentence_transformers import SentenceTransformer
import pandas as pd
from typing import Iterator
import numpy as np
import faiss

DIM = 384
THRESHOLD = 0.60
MAX_INDEX_SIZE = 50000
INDEX_PATH = "output/faiss.index"
faiss.omp_set_num_threads(1)
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = faiss.IndexFlatIP(DIM)

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def generate_embeddings(batch_iter: Iterator[pd.DataFrame]) -> Iterator[pd.DataFrame]:
    model = get_model()
    global index
    for pdf in batch_iter:
        if pdf.empty:
            yield pdf
            continue

        texts = pdf["sample_text"].tolist()
        embeddings = model.encode(
            texts,
            batch_size=128,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        if index.ntotal > 0:
            D, I = index.search(embeddings, k=1)
            is_similar = (D.flatten() > THRESHOLD).astype(int)
        else:
            is_similar = np.zeros(len(embeddings), dtype=int)
        if index.ntotal > MAX_INDEX_SIZE:
            index = faiss.IndexFlatIP(DIM)     
        index.add(embeddings)
        #faiss.write_index(index, INDEX_PATH)
        pdf["embedding"] = embeddings.tolist()
        pdf["is_similar"] = is_similar.tolist()
        yield pdf