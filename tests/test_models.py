"""
###########################################################################
#                                                                         #
#   AI-GENERATED TESTS                                                    #
#   These tests were written by an AI assistant (Claude).                 #
#   The production code they test was written by hand.                    #
#                                                                         #
###########################################################################

Unit tests for src/models.py.

Run from the project root:
    python -m unittest discover -s tests -v
"""
import unittest
from collections import Counter
from datetime import date

from src.models import (
    HEADBOOM_PENALTY,
    Game,
    GameEntryPerTeam,
    Leaderboard,
    Team,
    TeamStanding,
)


def make_entry(name, points, p1_tk=0, p2_tk=0, headbooms=0, placement=1, characters=None):
    """Small helper so each test only has to state the values it cares about."""
    return GameEntryPerTeam(
        team=Team(team_name=name, account_names=[f"{name}_player"]),
        characters_used=characters if characters is not None else [],
        csv_points=points,
        placement=placement,
        headbooms=headbooms,
        p1_tk=p1_tk,
        p2_tk=p2_tk,
    )


class TestTeam(unittest.TestCase):
    def test_to_dict_contains_all_fields(self):
        team = Team(team_name="Alpha", account_names=["P1", "P2"])
        self.assertEqual(team.to_dict(), {"team_name": "Alpha", "account_names": ["P1", "P2"]})

    def test_from_dict_roundtrip(self):
        team = Team(team_name="Alpha", account_names=["P1", "P2"])
        self.assertEqual(Team.from_dict(team.to_dict()), team)

    def test_from_dict_without_accounts_defaults_to_empty_list(self):
        team = Team.from_dict({"team_name": "Alpha"})
        self.assertEqual(team.account_names, [])


class TestGameEntryPerTeam(unittest.TestCase):
    def test_total_score_without_headbooms_equals_csv_points(self):
        self.assertEqual(make_entry("A", 28).total_score, 28.0)

    def test_total_score_subtracts_headbooms(self):
        entry = make_entry("A", 28, headbooms=2)
        self.assertEqual(entry.total_score, 28 - 2 * HEADBOOM_PENALTY)

    def test_total_score_updates_when_headbooms_change(self):
        # total_score is a @property, so it must never be stale
        entry = make_entry("A", 28)
        entry.headbooms = 3
        self.assertEqual(entry.total_score, 28 - 3 * HEADBOOM_PENALTY)

    def test_total_score_works_with_decimal_points(self):
        self.assertEqual(make_entry("A", 23.5).total_score, 23.5)


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(
            game_id=1,
            date=date(2026, 1, 1),
            entries=[
                make_entry("Low", 5, characters=["Darko", "Emma", "Karla"]),
                make_entry("High", 28, characters=["Darko", "Kenneth", "Karla"]),
                make_entry("Mid", 11, characters=["Cathy", "Rio", "Abigail"]),
            ],
        )

    def test_sorted_entries_highest_score_first(self):
        names = [e.team.team_name for e in self.game.sorted_entries()]
        self.assertEqual(names, ["High", "Mid", "Low"])

    def test_sorted_entries_respects_headbooms(self):
        # 28 points but 25 headbooms -> drops below "Mid" (11)
        self.game.entries[1].headbooms = 25
        names = [e.team.team_name for e in self.game.sorted_entries()]
        self.assertEqual(names[0], "Mid")

    def test_sorted_entries_does_not_change_original_order(self):
        self.game.sorted_entries()
        self.assertEqual(self.game.entries[0].team.team_name, "Low")

    def test_character_counters_counts_across_all_teams(self):
        counts = self.game.character_counters()
        self.assertIsInstance(counts, Counter)
        self.assertEqual(counts["Darko"], 2)
        self.assertEqual(counts["Karla"], 2)
        self.assertEqual(counts["Kenneth"], 1)
        self.assertEqual(sum(counts.values()), 9)

    def test_character_counters_empty_game(self):
        self.assertEqual(Game(game_id=2, date=date(2026, 1, 1)).character_counters(), Counter())


class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        self.game1 = Game(1, date(2026, 1, 1), [
            make_entry("Alpha", 20, p1_tk=2, p2_tk=3),
            make_entry("Beta", 10, p1_tk=1, p2_tk=1),
            make_entry("Gamma", 5, p1_tk=0, p2_tk=0),
        ])
        self.game2 = Game(2, date(2026, 1, 2), [
            make_entry("Alpha", 5, p1_tk=1, p2_tk=0),
            make_entry("Beta", 30, p1_tk=4, p2_tk=6),
            make_entry("Gamma", 5, p1_tk=0, p2_tk=1),
        ])
        self.lb = Leaderboard(tournament_name="Test", date=date(2026, 1, 1))
        self.lb.add_game(self.game1)
        self.lb.add_game(self.game2)

    def standing_by_name(self, name):
        for s in self.lb.overall_standings():
            if s.team.team_name == name:
                return s
        self.fail(f"{name!r} missing from standings")

    # --- helpers -----------------------------------------------------------

    def test_add_game(self):
        self.assertEqual(len(self.lb.games), 2)

    def test_team_entries_returns_one_entry_per_game(self):
        self.assertEqual(len(self.lb.team_entries("Alpha")), 2)

    def test_team_entries_unknown_team_is_empty(self):
        self.assertEqual(self.lb.team_entries("Nobody"), [])

    def test_team_total_score_sums_all_games(self):
        self.assertEqual(self.lb.team_total_score("Alpha"), 25.0)
        self.assertEqual(self.lb.team_total_score("Beta"), 40.0)

    # --- overall_standings ------------------------------------------------

    def test_standings_returns_team_standing_objects(self):
        standings = self.lb.overall_standings()
        self.assertEqual(len(standings), 3)
        for s in standings:
            self.assertIsInstance(s, TeamStanding)
            self.assertIsInstance(s.team, Team)  # must be the object, not just the name

    def test_standings_sums_points_and_tks_across_games(self):
        beta = self.standing_by_name("Beta")
        self.assertEqual(beta.points, 40.0)
        self.assertEqual(beta.p1_tk, 5)
        self.assertEqual(beta.p2_tk, 7)

    def test_standings_sorted_by_points_desc(self):
        names = [s.team.team_name for s in self.lb.overall_standings()]
        self.assertEqual(names, ["Beta", "Alpha", "Gamma"])

    def test_standings_ranks_start_at_one(self):
        ranks = [s.rank for s in self.lb.overall_standings()]
        self.assertEqual(ranks, [1, 2, 3])

    def test_standings_include_headbooms(self):
        self.game2.entries[1].headbooms = 20  # Beta: 40 -> 20, falls behind Alpha (25)
        names = [s.team.team_name for s in self.lb.overall_standings()]
        self.assertEqual(names[0], "Alpha")

    def test_tiebreaker_more_total_tk_wins(self):
        lb = Leaderboard("Tie", date(2026, 1, 1), [Game(1, date(2026, 1, 1), [
            make_entry("FewKills", 10, p1_tk=1, p2_tk=1),
            make_entry("ManyKills", 10, p1_tk=3, p2_tk=4),
        ])])
        names = [s.team.team_name for s in lb.overall_standings()]
        self.assertEqual(names, ["ManyKills", "FewKills"])

    def test_tiebreaker_uses_p1_plus_p2(self):
        # Same total TK (5) split differently -> neither should crash, both present
        lb = Leaderboard("Tie", date(2026, 1, 1), [Game(1, date(2026, 1, 1), [
            make_entry("A", 10, p1_tk=5, p2_tk=0),
            make_entry("B", 10, p1_tk=0, p2_tk=5),
        ])])
        self.assertEqual(len(lb.overall_standings()), 2)

    def test_team_missing_from_a_game_still_counted(self):
        self.lb.add_game(Game(3, date(2026, 1, 3), [make_entry("Delta", 50)]))
        delta = self.standing_by_name("Delta")
        self.assertEqual(delta.points, 50.0)
        self.assertEqual(delta.rank, 1)

    def test_empty_leaderboard(self):
        self.assertEqual(Leaderboard("Empty", date(2026, 1, 1)).overall_standings(), [])

    def test_calling_standings_twice_gives_same_result(self):
        first = [(s.team.team_name, s.points, s.rank) for s in self.lb.overall_standings()]
        second = [(s.team.team_name, s.points, s.rank) for s in self.lb.overall_standings()]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
