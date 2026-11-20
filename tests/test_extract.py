import unittest
from datetime import date
from pathlib import Path
from typing import Dict, List

from models import Game, GameEntryPerTeam, Team
from services import extract_game_id, load_csv_data

"""
Unit tests for the game extraction logic from CSV data.
CREATED WITH AI ASSISTANCE. 
"""
PROJECT_DIR = Path(__file__).resolve().parent
GAME_CSV = PROJECT_DIR / "Game 1.csv"


def parse_game_from_csv(rows: List[Dict[str, str]]) -> Game:
    """Build one Game with one entry for each team in the CSV."""
    if not rows:
        raise ValueError("The CSV does not contain any rows.")

    game_id = extract_game_id(rows)
    teams: Dict[str, Team] = {}
    entries: Dict[str, GameEntryPerTeam] = {}

    for row in rows:
        team_name = row.get("teamName")
        nickname = row.get("nickname")
        if not team_name:
            continue

        team = teams.setdefault(team_name, Team(team_name=team_name))
        if nickname and nickname not in team.account_names:
            team.account_names.append(nickname)

        if team_name not in entries:
            score_text = row.get("tournament total score", "")
            if not score_text:
                raise ValueError(f"Missing score for team {team_name!r}.")

            entries[team_name] = GameEntryPerTeam(
                team=team,
                score=float(score_text),
                total_score=float(score_text),
                game_id=game_id,
            )

        entries[team_name].characters_used += 1

    return Game(game_id=game_id, date=date.today(), entries=list(entries.values()))


class GameExtractionTests(unittest.TestCase):
    def test_game_one_contains_expected_teams_and_scores(self) -> None:
        rows = load_csv_data(str(GAME_CSV))
        game = parse_game_from_csv(rows)

        expected_scores = {
            "Cat Studying": 28.0,
            "FUNHAVERS": 23.5,
            "ByYiuYuiMyu": 11.0,
            "kikokuguys": 9.0,
            "Seekers Of Ba'ul": 5.0,
            "2andAHalfTyranticalWalrus": 8.0,
            "Mythic Dead MangoS": 3.0,
            "Big Intas": 1.5,
        }

        self.assertEqual(game.game_id, 63716452)
        self.assertEqual(
            {entry.team.team_name for entry in game.entries},
            set(expected_scores),
        )
        self.assertEqual(
            {entry.team.team_name: entry.score for entry in game.entries},
            expected_scores,
        )

    def test_team_entries_contain_all_players_from_game_one(self) -> None:
        rows = load_csv_data(str(GAME_CSV))
        game = parse_game_from_csv(rows)

        player_counts = {
            entry.team.team_name: len(entry.team.account_names)
            for entry in game.entries
        }

        self.assertEqual(
            player_counts,
            {
                "Cat Studying": 3,
                "FUNHAVERS": 3,
                "ByYiuYuiMyu": 3,
                "kikokuguys": 3,
                "Seekers Of Ba'ul": 3,
                "2andAHalfTyranticalWalrus": 3,
                "Mythic Dead MangoS": 3,
                "Big Intas": 3,
            },
        )


if __name__ == "__main__":
    unittest.main()
