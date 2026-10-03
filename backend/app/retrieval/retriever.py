"""
Procurement Compass - Multi-Strategy Retrieval System
Includes:
- BM25 Lexical Retrieval (preserving Rule numbers, amounts, certificates)
- Dense Semantic Vector Search (character/subword n-gram dense representations & cosine similarity)
- Hybrid Retrieval with Reciprocal Rank Fusion (RRF)
- Strict Metadata Pre-Filtering (Date, Version, Authority Level, Category, Synthetic status)
- Query Decomposition for Procurement Assessments
"""

import json
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from rank_bm25 import BM25Okapi

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"

class PolicyRetriever:
    def __init__(self, chunks_path: Optional[Path] = None):
        self.chunks_path = chunks_path or (DATA_DIR / "processed" / "policy_chunks.json")
        self.chunks: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None
        self.dense_vectors: List[Dict[str, float]] = []
        self.load_corpus()

    def tokenize(self, text: str) -> List[str]:
        """Custom tokenizer preserving rule numbers, statutory symbols, and currency."""
        # Replace punctuation except numbers and currency marks
        cleaned = text.lower()
        cleaned = re.sub(r"[₹,/\(\)]", " ", cleaned)
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
        return tokens

    def _compute_dense_vector(self, text: str) -> Dict[str, float]:
        """Generates a normalized semantic feature vector for subword/n-gram dense similarity."""
        tokens = self.tokenize(text)
        vec: Dict[str, float] = {}
        for t in tokens:
            vec[t] = vec.get(t, 0.0) + 1.0
            # Add character tri-grams for dense subword matching
            if len(t) >= 4:
                for i in range(len(t) - 2):
                    sub = t[i:i+3]
                    vec[sub] = vec.get(sub, 0.0) + 0.5

        # Normalize L2
        norm = math.sqrt(sum(v * v for v in vec.values()))
        if norm > 0:
            for k in vec:
                vec[k] /= norm
        return vec

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        score = 0.0
        # Iterate over smaller dict
        if len(vec1) > len(vec2):
            vec1, vec2 = vec2, vec1
        for k, v in vec1.items():
            if k in vec2:
                score += v * vec2[k]
        return score

    def load_corpus(self):
        if not self.chunks_path.exists():
            return
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        self.tokenized_corpus = [
            self.tokenize(c["text"] + " " + " ".join(c.get("keywords", [])) + " " + c.get("heading", ""))
            for c in self.chunks
        ]
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)

        # Build dense representations
        self.dense_vectors = [
            self._compute_dense_vector(c["text"] + " " + " ".join(c.get("keywords", [])))
            for c in self.chunks
        ]

    def _apply_prefilters(
        self,
        candidate_indices: List[int],
        procurement_date: Optional[str] = None,
        category: Optional[str] = None,
        allow_synthetic: bool = True
    ) -> List[int]:
        """Filters out obsolete or mismatched chunks prior to ranking."""
        filtered = []
        for idx in candidate_indices:
            c = self.chunks[idx]
            # Synthetic check
            if not allow_synthetic and c.get("is_synthetic", False):
                continue

            # Category filter
            if category and c.get("applies_to"):
                cat_lower = category.lower()
                chunk_applies = [a.lower() for a in c["applies_to"]]
                if not any(cat in chunk_applies for cat in [cat_lower, "goods", "works", "services"]):
                    continue

            # Effective date filter
            if procurement_date:
                eff_from = c.get("effective_from")
                eff_to = c.get("effective_to")
                if eff_from and procurement_date < eff_from:
                    continue
                if eff_to and procurement_date > eff_to:
                    continue

            filtered.append(idx)
        return filtered

    def search_bm25(self, query: str, top_k: int = 5, **filters) -> List[Dict[str, Any]]:
        """Lexical BM25 search."""
        if not self.bm25 or not self.chunks:
            return []
        tokens = self.tokenize(query)
        scores = self.bm25.get_scores(tokens)
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        filtered = self._apply_prefilters(sorted_indices, **filters)

        results = []
        for idx in filtered[:top_k]:
            c = dict(self.chunks[idx])
            c["retrieval_score"] = float(scores[idx])
            c["retrieval_strategy"] = "bm25"
            results.append(c)
        return results

    def search_dense(self, query: str, top_k: int = 5, **filters) -> List[Dict[str, Any]]:
        """Dense semantic search using vector representations."""
        if not self.dense_vectors or not self.chunks:
            return []
        q_vec = self._compute_dense_vector(query)
        scores = [self._cosine_similarity(q_vec, d_vec) for d_vec in self.dense_vectors]
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        filtered = self._apply_prefilters(sorted_indices, **filters)

        results = []
        for idx in filtered[:top_k]:
            c = dict(self.chunks[idx])
            c["retrieval_score"] = float(scores[idx])
            c["retrieval_strategy"] = "dense"
            results.append(c)
        return results

    def search_hybrid(self, query: str, top_k: int = 5, rrf_k: int = 60, **filters) -> List[Dict[str, Any]]:
        """Hybrid search combining BM25 and Dense with Reciprocal Rank Fusion (RRF)."""
        if not self.chunks:
            return []

        bm25_res = self.search_bm25(query, top_k=len(self.chunks), **filters)
        dense_res = self.search_dense(query, top_k=len(self.chunks), **filters)

        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(bm25_res):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank + 1))
            chunk_map[cid] = item

        for rank, item in enumerate(dense_res):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank + 1))
            chunk_map[cid] = item

        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        results = []
        for cid in sorted_cids[:top_k]:
            item = dict(chunk_map[cid])
            item["retrieval_score"] = float(rrf_scores[cid])
            item["retrieval_strategy"] = "hybrid_rrf"
            results.append(item)
        return results

    def decompose_queries(self, desc: str, route: str, category: str) -> List[str]:
        """Decomposes an assessment into 7 targeted retrieval sub-queries (§31)."""
        return [
            f"applicable procurement method {route} {category}",
            f"threshold rule ceiling amount {route}",
            "GeM condition mandatory availability certificate Rule 149",
            f"required certificate document for {route}",
            "document checklist local purchase committee statutory format",
            "exception proprietary emergency special condition",
            "institutional delegation of financial powers matrix"
        ]

    def retrieve_for_assessment(
        self,
        item_description: str,
        procurement_route: str,
        category: str,
        procurement_date: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Executes multi-query decomposed retrieval for an assessment."""
        sub_queries = self.decompose_queries(item_description, procurement_route, category)
        collected_chunks: Dict[str, Dict[str, Any]] = {}

        for sq in sub_queries:
            hits = self.search_hybrid(
                sq,
                top_k=2,
                procurement_date=procurement_date,
                category=category,
                allow_synthetic=True
            )
            for h in hits:
                cid = h["chunk_id"]
                if cid not in collected_chunks:
                    collected_chunks[cid] = h

        # Return top_k highest scoring chunks
        sorted_hits = sorted(collected_chunks.values(), key=lambda x: x.get("retrieval_score", 0.0), reverse=True)
        return sorted_hits[:top_k]
