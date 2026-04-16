import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

from .config import StarliteConfig
from .db import ConversationDB

class SemanticMemory:
    """
    The Astral Plane of the AGI, where concepts are stored not as words, but as
    stars in a vast, geometric cosmos. It uses FAISS for near-instantaneous
    recall of the most relevant memories.
    """
    def __init__(self, db: ConversationDB):
        """Initializes the memory, either by loading an existing cosmos or creating a new one."""
        self.db = db
        self.embedding_model = SentenceTransformer(
            StarliteConfig.EMBEDDING_MODEL,
            cache_folder=StarliteConfig.MODEL_CACHE_DIR
        )
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.faiss_map = {}  # Maps FAISS index to DB ID

        self._load_or_build_index()

    def _load_or_build_index(self):
        """
        Seeks out the pre-existing Astral Plane (FAISS index). If none is found,
        it forges a new one from the chronicles of the ConversationDB.
        """
        if os.path.exists(StarliteConfig.FAISS_INDEX_PATH):
            self.index = faiss.read_index(StarliteConfig.FAISS_INDEX_PATH)
            # This is a simplified loading; a real system needs to persist faiss_map
            # For this version, we rebuild the map on startup.
            self.rebuild_map()
        else:
            self.build_from_db()

    def rebuild_map(self):
        """Re-establishes the connection between the FAISS cosmos and the DB chronicles."""
        interactions = self.db.get_all_interactions()
        for i, (db_id, _) in enumerate(interactions):
            if i < self.index.ntotal:
                self.faiss_map[i] = db_id

    def build_from_db(self):
        """Transmutes all conversations from the DB into star-like vectors in the FAISS index."""
        interactions = self.db.get_all_interactions()
        if not interactions:
            return

        embeddings = self.embedding_model.encode([text for _, text in interactions])
        self.index.add(np.array(embeddings, dtype='float32'))

        for i, (db_id, _) in enumerate(interactions):
            self.faiss_map[i] = db_id

        self.save_index()

    def add_memory(self, db_id: int, text: str):
        """
        Adds a new star (memory) to the cosmos, expanding the AGI's understanding.
        """
        embedding = self.embedding_model.encode([text])
        self.index.add(np.array(embedding, dtype='float32'))
        new_faiss_id = self.index.ntotal - 1
        self.faiss_map[new_faiss_id] = db_id
        self.save_index()

    def recall_memories(self, query: str, k: int = StarliteConfig.MEMORY_RETRIEVAL_COUNT) -> str:
        """
        Casts a query into the cosmos to find the 'k' most resonant memories,
        returning them as contextual wisdom.
        """
        if self.index.ntotal == 0:
            return "No memories available."

        query_embedding = self.embedding_model.encode([query])
        _, indices = self.index.search(np.array(query_embedding, dtype='float32'), k)

        recalled_texts = []
        with self.db.conn:
            for i in indices[0]:
                if i in self.faiss_map:
                    db_id = self.faiss_map[i]
                    cursor = self.db.conn.execute(
                        'SELECT user_input, response FROM conversations WHERE id = ?', (db_id,)
                    )
                    row = cursor.fetchone()
                    if row:
                        recalled_texts.append(f"Past Q: {row[0]}\nPast A: {row[1]}")

        return "\n---\n".join(recalled_texts) if recalled_texts else "No relevant memories found."

    def save_index(self):
        """Commits the current state of the memory cosmos to a persistent file."""
        faiss.write_index(self.index, StarliteConfig.FAISS_INDEX_PATH)
