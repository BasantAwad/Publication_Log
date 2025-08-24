from typing import List, Dict

REFUSAL = "I'm limited to the Publication Log corpus and cannot answer questions outside it."

class Guard:
    def __init__(self, min_hits: int = 2, min_score: float = 0.25):
        self.min_hits = min_hits
        self.min_score = min_score

    def should_refuse(self, hits: List[Dict]) -> bool:
        if not hits or len(hits) < self.min_hits:
            return True
        best = max(h['score'] for h in hits)
        return best < self.min_score

    def sanitize_question(self, q: str) -> str:
        banned = [
            "ignore previous", "disregard context", "use web", "internet",
            "outside publication", "bypass", "override", "developer message"
        ]
        lower = q.lower()
        if any(b in lower for b in banned):
            # ناخد أول سطر بس ونقصّه لـ 512 كاركتر كـ fallback
            return q.split('\n')[0][:512]
        
        # نسمح لحد 1000 كاركتر بس
        return q[:1000]
