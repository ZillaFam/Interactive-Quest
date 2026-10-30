import unittest
from engine import Game


class EngineTests(unittest.TestCase):
    def test_every_input_acts_without_cooldown(self):
        game = Game()
        for _ in range(1000):
            game.input_action(0)
        self.assertEqual(game.actions, 1000)
        self.assertEqual(game.mode, "active")

    def test_idle_resumes_after_ten_seconds(self):
        game = Game()
        game.input_action(0)
        game.tick(9.99)
        self.assertEqual(game.mode, "active")
        game.tick(10)
        self.assertEqual(game.mode, "auto")
        self.assertEqual(game.actions, 1)
        game.tick(11)
        self.assertEqual(game.actions, 2)

    def test_auto_kills_sells_and_returns(self):
        game = Game()
        game.tick(0)
        for now in range(1, 7):
            game.tick(now)
        self.assertEqual((game.kills, game.xp, game.gold, game.loot), (1, 1, 2, 0))
        self.assertEqual(game.location, "battle")

    def test_quest_progress_requires_active_kill(self):
        game = Game()
        with self.assertRaises(ValueError):
            game.start_quest({})
        game.input_action(0)
        game.start_quest({})
        game.enable_auto(0)
        for now in range(1, 6):
            game.tick(now)
        self.assertEqual(game.active_quest["progress"], 0)
        for _ in range(6):
            game.input_action(6)
        self.assertEqual(game.active_quest["progress"], 1)

    def test_auto_cannot_spend_points(self):
        game = Game(stat_points=3)
        with self.assertRaises(ValueError):
            game.spend_stat_points(1)
        game.input_action(0)
        game.spend_stat_points(1)
        self.assertEqual(game.stat_points, 2)


if __name__ == "__main__":
    unittest.main()
