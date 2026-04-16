import unittest
import os
import sqlite3
from starlite_prime.db import ConversationDB
from starlite_prime.rl import GridWorld
from starlite_prime.config import StarliteConfig

class TestAetheriumPrime(unittest.TestCase):
    """
    A suite of divine trials to validate the foundational pillars of the AGI.
    Each test is a question posed to the fabric of its reality, ensuring its
    integrity and correctness.
    """

    @classmethod
    def setUpClass(cls):
        """A ritual performed once before all trials to prepare the sacred grounds."""
        cls.test_db_path = 'test_starlite_memory.db'
        # Ensure no previous test artifact remains
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def test_01_db_creation_and_logging(self):
        """Trial of Chronicles: Does the AGI remember what has been spoken?"""
        print("\nRunning Trial of Chronicles...")
        db = ConversationDB(db_path=self.test_db_path)

        # Test logging
        log_id = db.log_interaction("What is a star?", "A luminous sphere of plasma.", "No context.")
        self.assertIsInstance(log_id, int, "Log ID should be an integer.")
        self.assertGreater(log_id, 0, "Log ID should be positive.")

        # Test retrieval
        with sqlite3.connect(self.test_db_path) as conn:
            cursor = conn.execute("SELECT user_input, response FROM conversations WHERE id = ?", (log_id,))
            row = cursor.fetchone()
            self.assertIsNotNone(row, "The logged interaction was not found.")
            self.assertEqual(row[0], "What is a star?")
            self.assertEqual(row[1], "A luminous sphere of plasma.")

        db.close()
        print("Trial Passed.")

    def test_02_gridworld_mechanics(self):
        """Trial of Movement: Does the agent perceive and move within its world correctly?"""
        print("\nRunning Trial of Movement...")
        env = GridWorld(size=5)

        # Test state shape
        initial_state = env.reset()
        self.assertEqual(initial_state.shape[0], 3 * 5 * 5, "State vector shape is incorrect.")

        # Test movement
        env.agent_pos = [2, 2]
        # Action 0 is 'Up'
        state, reward, done = env.step(action=0)
        self.assertEqual(env.agent_pos, [1, 2], "Agent did not move 'Up' correctly.")
        self.assertFalse(done, "Game should not be done after one move.")

        # Test goal condition
        env.agent_pos = [1, 1]
        env.goal_pos = [1, 2]
        # Action 3 is 'Right'
        state, reward, done = env.step(action=3)
        self.assertEqual(env.agent_pos, env.goal_pos, "Agent did not reach goal position.")
        self.assertTrue(done, "Game should be 'done' when agent reaches the goal.")
        self.assertGreater(reward, 0, "Reward for reaching the goal should be positive.")
        print("Trial Passed.")

    @classmethod
    def tearDownClass(cls):
        """A final rite to cleanse the grounds after the trials are complete."""
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        print("\nAll trials complete. The Aetherium is sound.")

if __name__ == '__main__':
    unittest.main()
