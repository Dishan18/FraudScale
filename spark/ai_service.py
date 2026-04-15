import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from sentence_transformers import SentenceTransformer
import pandas as pd
from typing import Iterator
import numpy as np
import faiss

DIM = 384
MAX_INDEX_SIZE = 20000
INDEX_PATH = "output/faiss.index"

faiss.omp_set_num_threads(1)

index = None
next_id = 0
_model = None

def init_index():
    global index, next_id

    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        next_id = index.ntotal
    else:
        base_index = faiss.IndexFlatIP(DIM)
        index = faiss.IndexIDMap(base_index)


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def generate_embeddings(batch_iter: Iterator[pd.DataFrame]) -> Iterator[pd.DataFrame]:
    global index, next_id
    model = get_model()
    if index is None:
        init_index()
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
            D_hist, _ = index.search(embeddings, k=5)
            similarity_scores = D_hist.mean(axis=1)
        else:
            similarity_scores = np.zeros(len(embeddings), dtype=float)

        if len(embeddings) > 1:
            sim_matrix = np.dot(embeddings, embeddings.T)
            np.fill_diagonal(sim_matrix, 0)
            batch_max = sim_matrix.max(axis=1)
            similarity_scores = np.maximum(similarity_scores, batch_max)

        ids = np.arange(next_id, next_id + len(embeddings)).astype("int64")
        index.add_with_ids(embeddings, ids)
        next_id += len(embeddings)

        if index.ntotal > MAX_INDEX_SIZE:
            current_ids = faiss.vector_to_array(index.id_map)
            remove_ids = current_ids[:1000].astype("int64")
            index.remove_ids(remove_ids)

        pdf["embedding"] = embeddings.tolist()
        pdf["similarity_score"] = similarity_scores.tolist()

        yield pdf