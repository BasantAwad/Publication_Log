import os
from pathlib import Path
from typing import List, Dict

import faiss
import pandas as pd
import numpy as np
from django.conf import settings
from .embedding import embed_texts

class Retriever:
    def __init__(self):
        self.index_dir = Path(settings.RAG_INDEX_DIR)
        self.index = faiss.read_index(str(self.index_dir / 'faiss.index'))
        self.store = pd.read_parquet(self.index_dir / 'store.parquet')
        assert len(self.store) == self.index.ntotal, "Index and store size mismatch"

    def search(self, query: str, k: int = 8, scope: str = None) -> List[Dict]:
        scope = scope or settings.RAG_SCOPE
        scope_mask = self.store['scope'] == scope
        meta = self.store[scope_mask].reset_index(drop=True)
        qvec = embed_texts([query])
        D, I = self.index.search(qvec, min(k * 4, self.index.ntotal))
        hits = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            row = self.store.iloc[idx].to_dict()
            if row.get('scope') != scope:
                continue
            row['score'] = float(score)
            hits.append(row)

        # إزالة التكرارات وأخذ الأفضل
        unique = {}
        for h in hits:
            if h['id'] not in unique or h['score'] > unique[h['id']]['score']:
                unique[h['id']] = h
        hits = list(unique.values())
        hits.sort(key=lambda x: x['score'], reverse=True)
        return hits[:k]

    def build_context(self, hits: List[Dict]) -> str:
        ctx_lines = []
        for h in hits:
            cite = f"[{h['title']} — chunk {h['chunk_index']}]"
            snippet = h['text']
            ctx_lines.append(f"{cite}:\n{snippet}\n")
        return "\n".join(ctx_lines)
