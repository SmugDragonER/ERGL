from dataclasses import asdict
from datetime import date
import json
from typing import List
from tinydb import TinyDB, Query

from models import Game, GameEntryPerTeam, Team, Leaderboard


# AI USED FOR THIS

DB_PATH = "tournament_db.json"

def get_db() -> TinyDB:
    return TinyDB(DB_PATH)

def register_teams_from_json(tournament_id: str, json_path: str) -> None:
    """Pre-populates registered teams in TinyDB so all teams exist on the leaderboard."""
    db = TinyDB("tournament_db.json")
    teams_table = db.table(f"{tournament_id}_teams")
    
    with open(json_path, "r", encoding="utf-8") as f:
        registered_teams = json.load(f)

    for team_data in registered_teams:
        TeamQuery = Query()
        teams_table.upsert(
            {
                "team_name": team_data["team_name"],
                "account_names": team_data.get("account_names", [])
            },
            TeamQuery.team_name == team_data["team_name"]
        )

def is_game_processed(game_id: int) -> bool:
    """Checks if a game with the given ID already exists in TinyDB."""
    db = get_db()
    games_table = db.table('games')
    GameQuery = Query()
    return games_table.contains(GameQuery.game_id == game_id)

def save_game(game: Game) -> None:
    """Saves or updates a Game instance in TinyDB."""
    db = get_db()
    games_table = db.table('games')
    
    # Serialize dataclass to dict
    data = asdict(game)
    data['date'] = str(data['date'])
    for entry in data['entries']:
        if entry.get('date'):
            entry['date'] = str(entry['date'])

    # Upsert by game_id so duplicate runs don't create duplicate entries
    GameQuery = Query()
    games_table.upsert(data, GameQuery.game_id == game.game_id)

def load_leaderboard(tournament_id: str) -> Leaderboard:
    """Fetches all stored games for a specific tournament from TinyDB."""
    db = get_db()
    games_table = db.table(tournament_id)  # Query the correct tournament table
    
    leaderboard = Leaderboard(tournament_name=tournament_id, date=date.today())

    for record in games_table.all():
        entries = []
        for e in record.get('entries', []):
            team = Team(
                team_name=e['team']['team_name'],
                account_names=e['team']['account_names']
            )
            entry = GameEntryPerTeam(
                team=team,
                score=e['score'],
                total_score=e.get('total_score', e['score']),
                characters_used=e['characters_used'],
                game_id=e.get('game_id')
            )
            entries.append(entry)

        game = Game(
            game_id=record['game_id'],
            date=date.fromisoformat(record['date']) if isinstance(record['date'], str) else date.today(),
            entries=entries
        )
        leaderboard.add_game(game)

    return leaderboard