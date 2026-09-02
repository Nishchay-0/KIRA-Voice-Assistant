"""
kira_learner.py - KIRA Learning Orchestrator
---------------------------------------------
Ties together all 4 learning pillars:
  1. StructuredMemory  → SQLite facts, profile, command stats
  2. SemanticMemory    → ChromaDB conversation embeddings (optional)
  3. PatternLearner    → Time-based suggestions and heatmaps
  4. Feedback Loop     → Correction logging + auto-remapping to learned_mappings.json

Usage:
    from kira_learner import get_learner
    learner = get_learner()
    learner.process_interaction(user_input, response, intent, service)
"""

import os
import json
import random
import logging
from typing import Dict, Optional, List

from learning_engine import StructuredMemory, SemanticMemory, PatternLearner


MAPPINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "learned_mappings.json")
TRAINING_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "training_data.csv")


class KiraLearner:
    """
    Orchestrates all learning layers.
    Called after every successful interaction.
    """

    FEEDBACK_THRESHOLD = 3   # Auto-remap after N confirmed corrections
    SUGGESTION_PROBABILITY = 0.15  # 15% chance to proactively suggest

    def __init__(self):
        self.memory = StructuredMemory()
        self.semantic = SemanticMemory()
        self.patterns = PatternLearner(self.memory)
        self._learned_mappings: Dict[str, str] = self._load_mappings()

    # ── Core Interaction Loop ─────────────────────────────────────────────────

    def process_interaction(
        self,
        user_input: str,
        assistant_response: str,
        intent: str,
        service: str = ""
    ) -> Optional[str]:
        """
        Called after every successful command dispatch.
        Logs command, stores semantic memory, may return a proactive suggestion.
        """
        if not user_input or not user_input.strip():
            return None

        # Pillar 1: Log to structured memory
        self.memory.log_command(user_input.strip(), intent, service or "")

        # Pillar 2: Store semantic conversation (if available)
        self.semantic.remember_conversation(user_input.strip(), assistant_response.strip())

        # Pillar 3: Maybe offer a proactive time-based suggestion
        if random.random() < self.SUGGESTION_PROBABILITY:
            return self.patterns.get_time_based_suggestion()

        return None

    # ── Learned Mappings (Feedback Loop) ─────────────────────────────────────

    def get_learned_mappings(self) -> Dict[str, str]:
        """Return all auto-learned phrase→intent mappings."""
        return self._learned_mappings

    def check_learned_mapping(self, text: str) -> Optional[str]:
        """Check if a specific phrase has a learned intent override."""
        return self._learned_mappings.get(text.lower().strip())

    def handle_correction(self, original: str, wrong_intent: str, correct_intent: str):
        """
        Called when the user corrects KIRA's intent.
        After FEEDBACK_THRESHOLD corrections, auto-remap the phrase.
        """
        self.memory.log_correction(original.strip(), wrong_intent, correct_intent)

        count = self.memory.get_correction_count(original.strip(), correct_intent)
        if count >= self.FEEDBACK_THRESHOLD:
            key = original.strip().lower()
            self._learned_mappings[key] = correct_intent
            self._save_mappings()
            print(f"[KIRA Learned]: Auto-mapped '{key}' -> '{correct_intent}' (after {count} corrections)")

    def _load_mappings(self) -> Dict[str, str]:
        if os.path.exists(MAPPINGS_PATH):
            try:
                with open(MAPPINGS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_mappings(self):
        try:
            with open(MAPPINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self._learned_mappings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.warning(f"[KiraLearner] Could not save mappings: {e}")

    # ── Semantic Context Retrieval ────────────────────────────────────────────

    def recall_context_for(self, query: str, n: int = 2) -> Optional[str]:
        """
        Retrieve past similar conversations to enrich response context.
        Returns None if semantic layer is unavailable or no useful match.
        """
        memories = self.semantic.recall_context(query, n=n)
        if not memories:
            return None
        # Filter by distance — only use highly similar past turns
        relevant = [m for m in memories if m.get("distance", 1.0) < 0.4]
        if not relevant:
            return None
        return "\n".join(m["context"] for m in relevant)

    # ── User Profile Shortcuts ────────────────────────────────────────────────

    def remember(self, key: str, value: str):
        """Store a user preference fact."""
        self.memory.remember_fact(key, value)

    def recall(self, key: str) -> Optional[str]:
        """Recall a user preference fact."""
        return self.memory.recall_fact(key)

    def get_user_profile(self) -> Dict[str, str]:
        """Return the full user profile dict."""
        return self.memory.get_all_facts()

    # ── Training Data Export ──────────────────────────────────────────────────

    def export_training_data(self, output_path: str = TRAINING_DATA_PATH):
        """
        Export all command logs + corrections as CSV training data
        for fine-tuning a local intent classification model.
        """
        import csv
        rows = []

        # Command stats
        self.memory.cursor.execute("SELECT command_text, intent FROM command_stats")
        rows.extend(self.memory.cursor.fetchall())

        # Corrections (higher-quality signal)
        rows.extend(self.memory.get_all_corrections())

        if not rows:
            print("[KiraLearner] No training data collected yet.")
            return

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["text", "label"])
            writer.writerows(rows)

        print(f"✅ Training data exported: {output_path} ({len(rows)} examples)")
        return output_path

    # ── Analytics ────────────────────────────────────────────────────────────

    def get_usage_stats(self) -> Dict:
        """Return a summary of usage stats for display."""
        try:
            self.memory.cursor.execute(
                "SELECT intent, SUM(count) as total FROM command_stats GROUP BY intent ORDER BY total DESC"
            )
            intent_counts = dict(self.memory.cursor.fetchall())

            self.memory.cursor.execute("SELECT COUNT(*) FROM corrections")
            total_corrections = self.memory.cursor.fetchone()[0]

            self.memory.cursor.execute("SELECT COUNT(*) FROM command_stats")
            unique_commands = self.memory.cursor.fetchone()[0]

            return {
                "intent_distribution": intent_counts,
                "total_corrections": total_corrections,
                "unique_commands_seen": unique_commands,
                "learned_mappings_count": len(self._learned_mappings),
                "user_profile": self.get_user_profile()
            }
        except Exception as e:
            return {"error": str(e)}


# ── Singleton ─────────────────────────────────────────────────────────────────

_learner: Optional[KiraLearner] = None


def get_learner() -> KiraLearner:
    """Return the persistent KiraLearner singleton."""
    global _learner
    if _learner is None:
        _learner = KiraLearner()
    return _learner


# ── Self-Test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from colorama import Fore, init
    init(autoreset=True)

    learner = get_learner()
    print(Fore.CYAN + "=== KIRA Learner Self-Test ===")

    # Test profile facts
    learner.remember("name", "TestUser")
    learner.remember("music_genre", "Punjabi")
    print(Fore.GREEN + "Profile:", learner.get_user_profile())

    # Test command logging
    learner.process_interaction("play punjabi songs", "Playing Punjabi songs on YouTube.", "play_media", "youtube")
    learner.process_interaction("open youtube", "Opened YouTube.", "open_web", "youtube")
    learner.process_interaction("what is the time", "It is 9:00 PM.", "conversational", "")

    # Test corrections
    learner.handle_correction("ytube", "unknown", "open_web")
    learner.handle_correction("ytube", "unknown", "open_web")
    learner.handle_correction("ytube", "unknown", "open_web")  # 3rd → auto-maps
    print(Fore.GREEN + "Learned mappings:", learner.get_learned_mappings())

    # Test check
    print(Fore.GREEN + "Check 'ytube':", learner.check_learned_mapping("ytube"))

    # Stats
    print(Fore.YELLOW + "Usage stats:", learner.get_usage_stats())
    print(Fore.CYAN + "=== Test Complete ===")
