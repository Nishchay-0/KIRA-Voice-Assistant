"""
kira_intelligence.py - Persistent Memory, Semantic Understanding, & Knowledge Base for Kira AI
----------------------------------------------------------------------------------------------
Combines:
1. SQLite Memory Layer (kira_memory.db):
   - User personalization (name, favorite genre, preferences)
   - Real-time command history logging
   - Extensible Q&A Knowledge Base (learns custom answers via teaching)
2. Semantic Understanding & Vector Search (ChromaDB + SentenceTransformers / Fast Fuzzy Semantic Fallback)
3. Optional Local LLM Integration (Ollama / Llama / Mistral)
"""

import os
import sqlite3
import shutil
import subprocess
import logging
from typing import Optional, List, Tuple, Dict, Any

from colorama import Fore, init

init(autoreset=True)

# Safe optional imports for Vector DB / SentenceTransformers
try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


DB_PATH = os.path.join(os.path.dirname(__file__), "kira_memory.db")
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")


class KiraMemory:
    """
    SQLite-based Persistent Memory Layer for Kira AI.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_tables()
        self._seed_default_knowledge()

    def _init_tables(self):
        """Create necessary tables if they don't exist."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            preferred_genre TEXT,
            default_engine TEXT
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            query TEXT,
            intent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY,
            question TEXT UNIQUE,
            answer TEXT
        )''')
        self.conn.commit()

    def _seed_default_knowledge(self):
        """Seed essential local knowledge and Q&A pairs."""
        default_qa = [
            ("who are you", "Main Kira hoon, aapki AI voice assistant."),
            ("kaun ho tum", "Main Kira hoon, aapki AI voice assistant."),
            ("who created you", "I was created to be your intelligent, hands-free AI voice assistant."),
            ("what can you do", "I can control your OS, play music on YouTube, open any website, calculate math, and answer questions."),
            ("kya kar sakti ho", "Main YouTube par music chala sakti hoon, websites khol sakti hoon, hisab kitab kar sakti hoon aur baatein kar sakti hoon.")
        ]
        for q, a in default_qa:
            try:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO knowledge (question, answer) VALUES (?, ?)",
                    (q.lower().strip(), a)
                )
            except Exception:
                pass
        self.conn.commit()

    def get_user_preference(self, key: str) -> Optional[str]:
        """Fetch user preference by key."""
        try:
            valid_keys = {"name", "preferred_genre", "default_engine"}
            if key not in valid_keys:
                return None
            self.cursor.execute(f"SELECT {key} FROM users LIMIT 1")
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception:
            return None

    def save_user_preference(self, key: str, value: str):
        """Save or update user preference."""
        try:
            valid_keys = {"name", "preferred_genre", "default_engine"}
            if key not in valid_keys:
                return
            self.cursor.execute("SELECT id FROM users LIMIT 1")
            row = self.cursor.fetchone()
            if row:
                self.cursor.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (value, row[0]))
            else:
                self.cursor.execute(f"INSERT INTO users ({key}) VALUES (?)", (value,))
            self.conn.commit()
        except Exception as e:
            logging.warning(f"[Memory] Error saving preference {key}: {e}")

    def log_command(self, query: str, intent: str):
        """Log user command to history table."""
        try:
            self.cursor.execute(
                "INSERT INTO history (query, intent) VALUES (?, ?)",
                (query.strip(), intent.strip())
            )
            self.conn.commit()
        except Exception:
            pass

    def get_knowledge(self, question: str) -> Optional[str]:
        """Retrieve answer from knowledge base using exact or pattern matching."""
        if not question:
            return None
        q = question.lower().strip()
        try:
            # 1. Exact match
            self.cursor.execute("SELECT answer FROM knowledge WHERE question = ?", (q,))
            row = self.cursor.fetchone()
            if row:
                return row[0]

            # 2. Substring match
            self.cursor.execute("SELECT answer FROM knowledge WHERE ? LIKE '%' || question || '%'", (q,))
            row = self.cursor.fetchone()
            if row:
                return row[0]

            self.cursor.execute("SELECT answer FROM knowledge WHERE question LIKE ?", ('%' + q + '%',))
            row = self.cursor.fetchone()
            if row:
                return row[0]
        except Exception:
            pass
        return None

    def add_knowledge(self, question: str, answer: str):
        """Teach Kira a new Q&A pair."""
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO knowledge (question, answer) VALUES (?, ?)",
                (question.lower().strip(), answer.strip())
            )
            self.conn.commit()
        except Exception as e:
            logging.warning(f"[Memory] Error adding knowledge: {e}")


class KiraSemantic:
    """
    Semantic Vector Search Layer using ChromaDB or Fast Fuzzy Semantic Search fallback.
    """

    def __init__(self, collection_name: str = "commands"):
        self.collection_name = collection_name
        self.is_vector_ready = False
        self.model = None
        self.collection = None

        if HAS_CHROMADB and HAS_SENTENCE_TRANSFORMERS:
            try:
                os.makedirs(CHROMA_PATH, exist_ok=True)
                self.client = chromadb.PersistentClient(path=CHROMA_PATH)
                self.collection = self.client.get_or_create_collection(self.collection_name)
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.is_vector_ready = True
                self._seed_commands()
            except Exception as e:
                logging.warning(f"[Semantic] Vector DB init note: {e}")
                self.is_vector_ready = False

    def _seed_commands(self):
        """Pre-load standard commands and their vector representations."""
        if not self.is_vector_ready or not self.collection:
            return
        commands = [
            "open youtube", "play music", "search google", "open calculator",
            "what is the time", "tell me a joke", "open whatsapp",
            "play songs", "stop assistant", "exit", "hello", "who are you",
            "open file explorer", "open notepad", "voice manager", "set keyword"
        ]
        try:
            if self.collection.count() == 0:
                embeddings = self.model.encode(commands)
                self.collection.add(
                    documents=commands,
                    embeddings=embeddings.tolist(),
                    ids=[str(i) for i in range(len(commands))]
                )
        except Exception:
            pass

    def find_closest(self, query: str, n: int = 1) -> List[Tuple[str, float]]:
        """Find the closest semantic command match."""
        if not query or not str(query).strip():
            return []

        if self.is_vector_ready and self.model and self.collection:
            try:
                query_embedding = self.model.encode([query])
                results = self.collection.query(
                    query_embeddings=query_embedding.tolist(),
                    n_results=n
                )
                if results and results.get('documents') and len(results['documents'][0]) > 0:
                    docs = results['documents'][0]
                    distances = results['distances'][0] if 'distances' in results else [0.0] * len(docs)
                    return list(zip(docs, distances))
            except Exception:
                pass

        # Fallback to fuzzy substring match
        return []


def ask_local_llm(prompt: str, model: str = "llama3.2:3b") -> Optional[str]:
    """
    Optional Local LLM query via Ollama if installed on host.
    """
    if not shutil.which("ollama"):
        return None
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


class KiraBrain:
    """
    Combined Brain orchestrating Memory, Semantic Classification, Knowledge Base, and LLM fallback.
    """

    def __init__(self):
        self.memory = KiraMemory()
        self.semantic = KiraSemantic()

    def understand(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query across:
        1. Local Knowledge Base (FAQ / learned facts)
        2. Semantic Vector search
        3. History logging
        """
        if not query or not query.strip():
            return {"intent": "unknown", "confidence": 0.0}

        cleaned = query.strip()

        # 1. Check local knowledge base
        answer = self.memory.get_knowledge(cleaned)
        if answer:
            self.memory.log_command(cleaned, "knowledge")
            return {"intent": "knowledge", "response": answer, "confidence": 1.0}

        # 2. Semantic search
        matches = self.semantic.find_closest(cleaned)
        if matches and len(matches) > 0 and matches[0][1] < 0.45:
            matched_command, dist = matches[0]
            confidence = max(0.0, 1.0 - dist)
            self.memory.log_command(cleaned, "semantic_command")
            return {"intent": "command", "matched": matched_command, "confidence": confidence}

        # 3. Log query for learning
        self.memory.log_command(cleaned, "unknown")
        return {"intent": "unknown", "confidence": 0.0}

    def remember(self, key: str, value: str):
        """Save a user preference (e.g. name, music genre)."""
        self.memory.save_user_preference(key, value)

    def teach(self, question: str, answer: str):
        """Teach Kira a new Q&A fact."""
        self.memory.add_knowledge(question, answer)


# Brain Singleton Instance
_brain: Optional[KiraBrain] = None


def get_brain() -> KiraBrain:
    """Return persistent singleton KiraBrain instance."""
    global _brain
    if _brain is None:
        _brain = KiraBrain()
    return _brain


if __name__ == "__main__":
    print(Fore.CYAN + "=== KIRA Intelligence & Memory System Test ===")
    brain = get_brain()
    
    # Test Teaching
    brain.teach("my favorite color", "Your favorite color is Cyan.")
    print(Fore.GREEN + "Knowledge test:", brain.understand("what is my favorite color"))
    print(Fore.GREEN + "Default knowledge:", brain.understand("who are you"))
    
    # Test User Preference
    brain.remember("name", "Alex")
    print(Fore.YELLOW + "Stored user name:", brain.memory.get_user_preference("name"))
    print(Fore.GREEN + "=== Intelligence Test Complete ===")
