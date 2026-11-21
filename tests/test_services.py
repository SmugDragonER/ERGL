"""
###########################################################################
#                                                                         #
#   AI-GENERATED TESTS                                                    #
#   These tests were written by an AI assistant (Claude).                 #
#   The production code they test was written by hand.                    #
#                                                                         #
###########################################################################

Unit tests for the CSV -> Game conversion in src/services.py.

Run from the project root:
    python -m unittest discover -s tests -v
"""
import unittest
from pathlib import Path

from src.models import Game, GameEntryPerTeam, Team
from src.services import build_entry, build_game_from_csv, extract_game_id, load_csv_data

PROJECT_DIR = Path(__file__).resolve().parent.parent
GAME_CSV = PROJECT_DIR / "assets" / "Game 1.csv"


def make_row(team, nickname, character, *, rank="1", total="10", dcne="0", elim="0", dce="0", game_id="123"):
    """One CSV row as load_csv_data returns it (all values are strings)."""
    return {
        "teamName": team,
        "nickname": nickname,
        "character": character,
        "rank": rank,
        "tournament total score": total,
        "down can not eliminate": dcne,
        "elimination": elim,
        "down can eliminate": dce,
        "gameId": game_id,
    }


class TestBuildEntry(unittest.TestCase):
    def setUp(self):
        self.rows = [
            make_row("Alpha", "P1", "Darko", rank="2", total="23.5", dcne="7", elim="12", dce="1"),
            make_row("Alpha", "P2", "Emma", rank="2", total="23.5", dcne="7", elim="12", dce="1"),
            make_row("Alpha", "P3", "Karla", rank="2", total="23.5", dcne="7", elim="12", dce="1"),
        ]
        self.entry = build_entry("Alpha", self.rows)

    def test_returns_game_entry(self):
        self.assertIsInstance(self.entry, GameEntryPerTeam)

    def test_team_is_a_team_object_with_all_players(self):
        self.assertIsInstance(self.entry.team, Team)
        self.assertEqual(self.entry.team.team_name, "Alpha")
        self.assertEqual(self.entry.team.account_names, ["P1", "P2", "P3"])

    def test_characters_from_every_row(self):
        self.assertEqual(self.entry.characters_used, ["Darko", "Emma", "Karla"])

    def test_team_values_taken_once_not_summed(self):
        # Values repeat on every row -> must NOT be multiplied by 3
        self.assertEqual(self.entry.csv_points, 23.5)
        self.assertEqual(self.entry.p1_tk, 7)

    def test_p2_tk_is_numeric_sum_not_string_concat(self):
        # "12" + "1" would be "121" if strings were concatenated
        self.assertEqual(self.entry.p2_tk, 13)

    def test_types_are_converted(self):
        self.assertIsInstance(self.entry.csv_points, float)
        self.assertIsInstance(self.entry.placement, int)
        self.assertIsInstance(self.entry.p1_tk, int)
        self.assertIsInstance(self.entry.p2_tk, int)

    def test_team_with_only_two_players(self):
        entry = build_entry("Duo", self.rows[:2])
        self.assertEqual(len(entry.team.account_names), 2)
        self.assertEqual(entry.csv_points, 23.5)


class TestBuildGameFromHandmadeRows(unittest.TestCase):
    def test_groups_by_team_even_when_rows_are_mixed(self):
        rows = [
            make_row("A", "a1", "X", total="10"),
            make_row("B", "b1", "Y", total="20"),
            make_row("A", "a2", "Z", total="10"),
            make_row("B", "b2", "W", total="20"),
        ]
        game = build_game_from_csv(rows)
        by_name = {e.team.team_name: e for e in game.entries}
        self.assertEqual(set(by_name), {"A", "B"})
        self.assertEqual(by_name["A"].team.account_names, ["a1", "a2"])
        self.assertEqual(by_name["B"].characters_used, ["Y", "W"])


class TestBuildGameFromRealCsv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_csv_data(str(GAME_CSV))
        cls.game = build_game_from_csv(cls.rows)
        cls.by_name = {e.team.team_name: e for e in cls.game.entries}

    def test_csv_file_exists(self):
        self.assertTrue(GAME_CSV.exists(), f"Missing test file: {GAME_CSV}")

    def test_returns_game(self):
        self.assertIsInstance(self.game, Game)

    def test_game_id(self):
        self.assertEqual(self.game.game_id, 63716452)
        self.assertEqual(self.game.game_id, extract_game_id(self.rows))

    def test_eight_distinct_teams(self):
        self.assertEqual(len(self.game.entries), 8)
        self.assertEqual(len(self.by_name), 8)

    def test_every_team_has_three_players(self):
        for name, entry in self.by_name.items():
            with self.subTest(team=name):
                self.assertEqual(len(entry.team.account_names), 3)
                self.assertEqual(len(entry.characters_used), 3)

    def test_cat_studying_values(self):
        e = self.by_name["Cat Studying"]
        self.assertEqual(e.csv_points, 28.0)
        self.assertEqual(e.placement, 1)
        self.assertEqual(e.p1_tk, 4)
        self.assertEqual(e.p2_tk, 16)  # 11 + 5
        self.assertEqual(e.characters_used, ["Darko", "Kenneth", "Karla"])
        self.assertEqual(e.total_score, 28.0)

    def test_funhavers_decimal_points(self):
        e = self.by_name["FUNHAVERS"]
        self.assertEqual(e.csv_points, 23.5)
        self.assertEqual(e.p1_tk, 7)
        self.assertEqual(e.p2_tk, 13)  # 12 + 1

    def test_placements_are_one_to_eight(self):
        self.assertEqual(sorted(e.placement for e in self.game.entries), list(range(1, 9)))


if __name__ == "__main__":
    unittest.main()
