import os
import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings


_model = None


def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.RAG_EMB_MODEL)
        return _model




def embed_texts(texts):
        model = get_embedder()
        vecs = model.encode(texts, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
        return np.asarray(vecs, dtype="float32")