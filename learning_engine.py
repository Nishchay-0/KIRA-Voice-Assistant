"""
learning_engine.py - KIRA Continuous Learning Engine (4 Pillars)
-----------------------------------------------------------------
Pillar 1 - StructuredMemory:  SQLite facts, user profile, command stats, corrections
Pillar 2 - SemanticMemory:    ChromaDB + SentenceTransformers (optional)
Pillar 3 - PatternLearner:    Time-based suggestions and frequency heatmap
Pillar 4 - Feedback Loop:     Correction logging + auto-remapping after threshold

All layers degrade gracefully if optional dependencies are missing.
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, List

import sqlite3

# Optional semantic layer
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False


BRAIN_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kira_brain.db")
CHROMA_BRAIN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_brain")


# ─────────────────────────────────────────────────────────────────────────────
# PILLAR 1 — STRUCTURED MEMORY (SQLite)
# ─────────────────────────────────────────────────────────────────────────────

class StructuredMemory:
    """
    SQLite-based persistent memory for:
    - User profile (arbitrary key/value facts)
    - Command frequency (hour/day patterns)
    - Correction history (for auto-remapping)
    """

    def __init__(self, db_path: str = BRAIN_DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        # Arbitrary key/value user profile
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_profile (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Command frequency stats — unique per (command_text, intent) pair
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS command_stats (
            command_text TEXT,
            intent TEXT,
            service TEXT,
            count INTEGER DEFAULT 1,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hour_of_day INTEGER,
            day_of_week INTEGER,
            UNIQUE(command_text, intent)
        )''')

        # Correction history for the feedback loop
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_input TEXT,
            wrong_intent TEXT,
            correct_intent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        self.conn.commit()

    # ── User Profile Facts ────────────────────────────────────────────────────

    def remember_fact(self, key: str, value: str):
        """Store or update a user fact (e.g., name, music_genre)."""
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO user_profile (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (key.lower().strip(), str(value).strip())
            )
            self.conn.commit()
        except Exception as e:
            logging.warning(f"[StructuredMemory] remember_fact error: {e}")

    def recall_fact(self, key: str) -> Optional[str]:
        """Recall a stored user fact."""
        try:
            self.cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key.lower().strip(),))
            row = self.cursor.fetchone()
            return row[0] if row else None
        except Exception:
            return None

    def get_all_facts(self) -> Dict[str, str]:
        """Return full user profile as a dict."""
        try:
            self.cursor.execute("SELECT key, value FROM user_profile")
            return dict(self.cursor.fetchall())
        except Exception:
            return {}

    # ── Command Frequency Logging ─────────────────────────────────────────────

    def log_command(self, text: str, intent: str, service: str = ""):
        """Log a command for pattern analysis. Upserts on conflict."""
        try:
            now = datetime.now()
            self.cursor.execute(
                """INSERT INTO command_stats
                   (command_text, intent, service, count, last_used, hour_of_day, day_of_week)
                   VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP, ?, ?)
                   ON CONFLICT(command_text, intent) DO UPDATE SET
                   count = count + 1,
                   last_used = CURRENT_TIMESTAMP,
                   hour_of_day = excluded.hour_of_day,
                   day_of_week = excluded.day_of_week""",
                (text.strip()[:200], intent.strip(), (service or "").strip(), now.hour, now.weekday())
            )
            self.conn.commit()
        except Exception as e:
            logging.warning(f"[StructuredMemory] log_command error: {e}")

    def predict_next_command(self) -> List[Dict]:
        """Predict likely next commands based on current hour/weekday and history."""
        try:
            now = datetime.now()
            self.cursor.execute(
                """SELECT command_text, intent, count
                   FROM command_stats
                   WHERE hour_of_day BETWEEN ? AND ? OR day_of_week = ?
                   ORDER BY count DESC LIMIT 3""",
                (max(0, now.hour - 1), min(23, now.hour + 1), now.weekday())
            )
            return [{"text": r[0], "intent": r[1], "frequency": r[2]} for r in self.cursor.fetchall()]
        except Exception:
            return []

    def get_frequency_heatmap(self) -> Dict[int, Dict[str, int]]:
        """Returns {hour: {intent: count}} heatmap."""
        try:
            self.cursor.execute(
                "SELECT hour_of_day, intent, SUM(count) FROM command_stats GROUP BY hour_of_day, intent"
            )
            heatmap: Dict[int, Dict[str, int]] = {}
            for hour, intent, count in self.cursor.fetchall():
                heatmap.setdefault(hour, {})[intent] = count
            return heatmap
        except Exception:
            return {}

    # ── Correction Logging (Pillar 4) ─────────────────────────────────────────

    def log_correction(self, original: str, wrong_intent: str, correct_intent: str):
        """Record a user correction for the feedback loop."""
        try:
            self.cursor.execute(
                "INSERT INTO corrections (original_input, wrong_intent, correct_intent) VALUES (?, ?, ?)",
                (original.strip(), wrong_intent.strip(), correct_intent.strip())
            )
            self.conn.commit()
        except Exception as e:
            logging.warning(f"[StructuredMemory] log_correction error: {e}")

    def get_correction_count(self, original: str, correct_intent: str) -> int:
        """How many times has this phrase been corrected to this intent?"""
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM corrections WHERE original_input = ? AND correct_intent = ?",
                (original.strip(), correct_intent.strip())
            )
            row = self.cursor.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0

    def get_all_corrections(self) -> List[tuple]:
        """Return all (original_input, correct_intent) correction pairs."""
        try:
            self.cursor.execute("SELECT original_input, correct_intent FROM corrections")
            return self.cursor.fetchall()
        except Exception:
            return []


# ─────────────────────────────────────────────────────────────────────────────
# PILLAR 2 — SEMANTIC MEMORY (ChromaDB + SentenceTransformers, optional)
# ─────────────────────────────────────────────────────────────────────────────

class SemanticMemory:
    """
    Stores and retrieves past conversations using vector embeddings.
    Requires: pip install chromadb sentence-transformers
    Degrades gracefully if not installed.
    """

    def __init__(self, collection_name: str = "conversations"):
        self.is_ready = False
        self.collection = None
        self.model = None

        if not HAS_SEMANTIC:
            return

        try:
            os.makedirs(CHROMA_BRAIN_PATH, exist_ok=True)
            client = chromadb.PersistentClient(path=CHROMA_BRAIN_PATH)
            self.collection = client.get_or_create_collection(collection_name)
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.is_ready = True
        except Exception as e:
            logging.warning(f"[SemanticMemory] Init note: {e}")

    def remember_conversation(self, user_input: str, assistant_response: str):
        """Embed and store a conversation turn."""
        if not self.is_ready:
            return
        try:
            text = f"User: {user_input} | KIRA: {assistant_response}"
            embedding = self.model.encode([text])
            self.collection.add(
                documents=[text],
                embeddings=embedding.tolist(),
                metadatas=[{
                    "timestamp": datetime.now().isoformat(),
                    "user_input": user_input[:300],
                    "response": assistant_response[:300]
                }],
                ids=[str(uuid.uuid4())]
            )
        except Exception as e:
            logging.warning(f"[SemanticMemory] remember error: {e}")

    def recall_context(self, query: str, n: int = 3) -> List[Dict]:
        """Find past conversations semantically similar to current query."""
        if not self.is_ready or not query:
            return []
        try:
            query_embedding = self.model.encode([query])
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=min(n, max(1, self.collection.count()))
            )
            if results and results.get("documents") and results["documents"][0]:
                return [
                    {
                        "context": doc,
                        "distance": results["distances"][0][i],
                        "metadata": results["metadatas"][0][i]
                    }
                    for i, doc in enumerate(results["documents"][0])
                ]
        except Exception as e:
            logging.warning(f"[SemanticMemory] recall error: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# PILLAR 3 — PATTERN LEARNER
# ─────────────────────────────────────────────────────────────────────────────

class PatternLearner:
    """
    Analyzes usage patterns from StructuredMemory to:
    - Suggest time-appropriate commands
    - Expose a frequency heatmap
    - Feed corrections back into the intent system
    """

    def __init__(self, memory: StructuredMemory):
        self.memory = memory

    def get_time_based_suggestion(self) -> Optional[str]:
        """
        Suggest the most likely command for the current time.
        Returns a human-readable suggestion string or None.
        """
        predictions = self.memory.predict_next_command()
        if predictions:
            top = predictions[0]
            if top["frequency"] >= 3:  # Only suggest if seen at least 3 times
                return f"Based on your routine, would you like to '{top['text']}'?"
        return None

    def get_frequency_heatmap(self) -> Dict[int, Dict[str, int]]:
        return self.memory.get_frequency_heatmap()

    def evolve_intent_weights(self) -> List[tuple]:
        """Return all known corrections for downstream intent weight boosting."""
        return self.memory.get_all_corrections()
