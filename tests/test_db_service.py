"""
###########################################################################
#                                                                         #
#   AI-GENERATED TESTS                                                    #
#   These tests were written by an AI assistant (Claude).                 #
#   The production code they test was written by hand.                   #
#                                                                         #
###########################################################################

Unit tests for src/db_service.py.

Every test uses its own temporary database file, so the real
tournament_db.json is never touched.

Expected function signatures:
    save_game(tournament_id, game, db_path=DB_PATH)
    is_game_saved(tournament_id, game_id, db_path=DB_PATH)
    load_leaderboard(tournament_id, db_path=DB_PATH)

Run from the project root:
    python -m unittest discover -s tests -v
"""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from src.db_service import (delete_tournament, is_game_saved, list_tournaments, load_leaderboard, save_game,
                            set_headbooms)
from src.models import HEADBOOM_PENALTY, Game, GameEntryPerTeam, Leaderboard, Team

TOURNAMENT = "TEST_TOURNAMENT"


def make_entry(name, points, p1_tk=0, p2_tk=0, headbooms=0, placement=1):
    return GameEntryPerTeam(
        team=Team(team_name=name, account_names=[f"{name}_1", f"{name}_2"]),
        characters_used=["Darko", "Emma"],
        csv_points=points,
        placement=placement,
        headbooms=headbooms,
        p1_tk=p1_tk,
        p2_tk=p2_tk,
    )


def make_game(game_id, entries=None):
    return Game(
        game_id=game_id,
        date=date(2026, 11, 21),
        entries=entries if entries is not None else [
            make_entry("Alpha", 28, p1_tk=4, p2_tk=16, placement=1),
            make_entry("Beta", 23.5, p1_tk=7, p2_tk=13, placement=2),
        ],
    )


class DbTestCase(unittest.TestCase):
    """Creates a fresh, empty database file for every single test."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self._tmp.name) / "test_db.json"

    def tearDown(self):
        self._tmp.cleanup()

    def read_raw_file(self):
        """Look at the JSON file directly, exactly as TinyDB wrote it."""
        with open(self.db_path, encoding="utf-8") as f:
            return json.load(f)


class TestSaveGame(DbTestCase):
    def test_creates_database_file(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        self.assertTrue(self.db_path.exists())

    def test_game_is_stored_in_tournament_table(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        raw = self.read_raw_file()
        self.assertIn(TOURNAMENT, raw)
        self.assertEqual(len(raw[TOURNAMENT]), 1)

    def test_stored_document_is_plain_json(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        doc = next(iter(self.read_raw_file()[TOURNAMENT].values()))
        self.assertEqual(doc["game_id"], 1)
        self.assertEqual(doc["date"], "2026-11-21")          # date stored as text
        self.assertEqual(doc["entries"][0]["team"]["team_name"], "Alpha")  # team stored as dict

    def test_total_score_is_not_stored(self):
        # total_score is calculated, it must not end up in the file
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        doc = next(iter(self.read_raw_file()[TOURNAMENT].values()))
        self.assertNotIn("total_score", doc["entries"][0])

    def test_two_different_games_create_two_documents(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        save_game(TOURNAMENT, make_game(2), db_path=self.db_path)
        self.assertEqual(len(self.read_raw_file()[TOURNAMENT]), 2)

    def test_saving_same_game_twice_does_not_duplicate(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        self.assertEqual(len(self.read_raw_file()[TOURNAMENT]), 1)

    def test_saving_same_game_again_overwrites_values(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        changed = make_game(1)
        changed.entries[0].headbooms = 3
        save_game(TOURNAMENT, changed, db_path=self.db_path)

        loaded = load_leaderboard(TOURNAMENT, db_path=self.db_path)
        self.assertEqual(loaded.games[0].entries[0].headbooms, 3)

    def test_tournaments_are_separated(self):
        save_game("SEASON_1", make_game(1), db_path=self.db_path)
        save_game("SEASON_2", make_game(2), db_path=self.db_path)
        raw = self.read_raw_file()
        self.assertEqual(len(raw["SEASON_1"]), 1)
        self.assertEqual(len(raw["SEASON_2"]), 1)


class TestIsGameSaved(DbTestCase):
    def test_false_on_empty_database(self):
        self.assertFalse(is_game_saved(TOURNAMENT, 1, db_path=self.db_path))

    def test_true_after_saving(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        self.assertTrue(is_game_saved(TOURNAMENT, 1, db_path=self.db_path))

    def test_false_for_other_game_id(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        self.assertFalse(is_game_saved(TOURNAMENT, 999, db_path=self.db_path))

    def test_false_in_other_tournament(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        self.assertFalse(is_game_saved("OTHER_TOURNAMENT", 1, db_path=self.db_path))


class TestLoadLeaderboard(DbTestCase):
    def test_returns_leaderboard(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        lb = load_leaderboard(TOURNAMENT, db_path=self.db_path)
        self.assertIsInstance(lb, Leaderboard)
        self.assertEqual(lb.tournament_name, TOURNAMENT)

    def test_empty_tournament_gives_empty_leaderboard(self):
        lb = load_leaderboard(TOURNAMENT, db_path=self.db_path)
        self.assertEqual(lb.games, [])
        self.assertEqual(lb.overall_standings(), [])

    def test_loaded_objects_have_correct_types(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        game = load_leaderboard(TOURNAMENT, db_path=self.db_path).games[0]
        self.assertIsInstance(game, Game)
        self.assertIsInstance(game.date, date)
        self.assertIsInstance(game.entries[0], GameEntryPerTeam)
        self.assertIsInstance(game.entries[0].team, Team)

    def test_save_then_load_gives_identical_game(self):
        # The most important test: nothing may get lost on the way
        original = make_game(1, [
            make_entry("Alpha", 28, p1_tk=4, p2_tk=16, headbooms=2, placement=1),
            make_entry("Beta", 23.5, p1_tk=7, p2_tk=13, placement=2),
        ])
        save_game(TOURNAMENT, original, db_path=self.db_path)
        loaded = load_leaderboard(TOURNAMENT, db_path=self.db_path).games[0]
        self.assertEqual(loaded, original)

    def test_loads_all_games(self):
        for game_id in (1, 2, 3):
            save_game(TOURNAMENT, make_game(game_id), db_path=self.db_path)
        lb = load_leaderboard(TOURNAMENT, db_path=self.db_path)
        self.assertEqual(sorted(g.game_id for g in lb.games), [1, 2, 3])

    def test_standings_work_after_loading(self):
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)
        save_game(TOURNAMENT, make_game(2), db_path=self.db_path)
        standings = load_leaderboard(TOURNAMENT, db_path=self.db_path).overall_standings()
        self.assertEqual(standings[0].team.team_name, "Alpha")
        self.assertEqual(standings[0].points, 56.0)
        self.assertEqual(standings[0].p2_tk, 32)
        self.assertEqual(standings[0].rank, 1)

    def test_only_loads_requested_tournament(self):
        save_game("SEASON_1", make_game(1), db_path=self.db_path)
        save_game("SEASON_2", make_game(2), db_path=self.db_path)
        lb = load_leaderboard("SEASON_1", db_path=self.db_path)
        self.assertEqual([g.game_id for g in lb.games], [1])


class TestSetHeadbooms(DbTestCase):
    def setUp(self):
        super().setUp()
        save_game(TOURNAMENT, make_game(1), db_path=self.db_path)

    def entry(self, team_name, game_id=1):
        game = next(g for g in load_leaderboard(TOURNAMENT, db_path=self.db_path).games
                    if g.game_id == game_id)
        return next(e for e in game.entries if e.team.team_name == team_name)

    def test_sets_headbooms_for_the_team(self):
        set_headbooms(TOURNAMENT, 1, "Alpha", 2, db_path=self.db_path)
        self.assertEqual(self.entry("Alpha").headbooms, 2)

    def test_other_teams_stay_unchanged(self):
        set_headbooms(TOURNAMENT, 1, "Alpha", 2, db_path=self.db_path)
        self.assertEqual(self.entry("Beta").headbooms, 0)

    def test_can_be_changed_again(self):
        set_headbooms(TOURNAMENT, 1, "Alpha", 2, db_path=self.db_path)
        set_headbooms(TOURNAMENT, 1, "Alpha", 0, db_path=self.db_path)
        self.assertEqual(self.entry("Alpha").headbooms, 0)

    def test_only_changes_the_given_game(self):
        save_game(TOURNAMENT, make_game(2), db_path=self.db_path)
        set_headbooms(TOURNAMENT, 2, "Alpha", 1, db_path=self.db_path)
        self.assertEqual(self.entry("Alpha", game_id=1).headbooms, 0)
        self.assertEqual(self.entry("Alpha", game_id=2).headbooms, 1)

    def test_does_not_create_a_duplicate_game(self):
        set_headbooms(TOURNAMENT, 1, "Alpha", 2, db_path=self.db_path)
        self.assertEqual(len(self.read_raw_file()[TOURNAMENT]), 1)

    def test_points_are_deducted_in_standings(self):
        set_headbooms(TOURNAMENT, 1, "Alpha", 2, db_path=self.db_path)
        alpha = next(s for s in load_leaderboard(TOURNAMENT, db_path=self.db_path).overall_standings()
                     if s.team.team_name == "Alpha")
        self.assertEqual(alpha.points, 28 - 2 * HEADBOOM_PENALTY)

    def test_unknown_game_raises_value_error(self):
        with self.assertRaises(ValueError):
            set_headbooms(TOURNAMENT, 999, "Alpha", 1, db_path=self.db_path)

    def test_unknown_team_raises_and_changes_nothing(self):
        with self.assertRaises(ValueError):
            set_headbooms(TOURNAMENT, 1, "Nobody", 3, db_path=self.db_path)
        self.assertEqual(self.entry("Alpha").headbooms, 0)
        self.assertEqual(self.entry("Beta").headbooms, 0)


# AI-GENERATED (Claude): tests for list_tournaments and delete_tournament
class TestListTournaments(DbTestCase):
    def test_empty_database_returns_empty_list(self):
        self.assertEqual(list_tournaments(db_path=self.db_path), [])

    def test_returns_all_tournaments_sorted(self):
        save_game("ZULU_CUP", make_game(1), db_path=self.db_path)
        save_game("ALPHA_CUP", make_game(1), db_path=self.db_path)
        self.assertEqual(list_tournaments(db_path=self.db_path), ["ALPHA_CUP", "ZULU_CUP"])

    def test_hides_internal_tables_starting_with_underscore(self):
        save_game("ALPHA_CUP", make_game(1), db_path=self.db_path)
        save_game("_settings", make_game(1), db_path=self.db_path)
        save_game("_default", make_game(1), db_path=self.db_path)
        self.assertEqual(list_tournaments(db_path=self.db_path), ["ALPHA_CUP"])

    def test_returns_a_list(self):
        save_game("ALPHA_CUP", make_game(1), db_path=self.db_path)
        self.assertIsInstance(list_tournaments(db_path=self.db_path), list)


class TestDeleteTournament(DbTestCase):
    def test_deleted_tournament_is_gone(self):
        save_game("ALPHA_CUP", make_game(1), db_path=self.db_path)
        delete_tournament("ALPHA_CUP", db_path=self.db_path)
        self.assertNotIn("ALPHA_CUP", list_tournaments(db_path=self.db_path))

    def test_deleted_tournament_has_no_games_left(self):
        save_game("ALPHA_CUP", make_game(1), db_path=self.db_path)
        save_game("ALPHA_CUP", make_game(2), db_path=self.db_path)
        delete_tournament("ALPHA_CUP", db_path=self.db_path)
        self.assertEqual(load_leaderboard("ALPHA_CUP", db_path=self.db_path).games, [])

    def test_other_tournaments_are_kept_with_their_games(self):
        save_game("ALPHA_CUP", make_game(1), db_path=self.db_path)
        save_game("BETA_CUP", make_game(1), db_path=self.db_path)
        save_game("BETA_CUP", make_game(2), db_path=self.db_path)
        delete_tournament("ALPHA_CUP", db_path=self.db_path)
        self.assertEqual(list_tournaments(db_path=self.db_path), ["BETA_CUP"])
        self.assertEqual(len(load_leaderboard("BETA_CUP", db_path=self.db_path).games), 2)

    def test_unknown_tournament_raises_value_error(self):
        save_game("ALPHA_CUP", make_game(1), db_path=self.db_path)
        with self.assertRaises(ValueError):
            delete_tournament("DOES_NOT_EXIST", db_path=self.db_path)
        self.assertEqual(list_tournaments(db_path=self.db_path), ["ALPHA_CUP"])



if __name__ == "__main__":
    unittest.main()
