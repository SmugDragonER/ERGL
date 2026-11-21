from datetime import date

from tinydb import TinyDB, Query
from src.models import Game, Leaderboard
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "tournament_db.json"




def save_game(tournament_id, game):
    with TinyDB(db_path=DB_PATH) as db:
    
        table = db.table(tournament_id)
        Game_Q = Query()
        table.upsert(game.to_dict(), Game_Q.game_id == game.game_id)
        print("game saved")


def is_game_saved(tournament_id, game_id):
    with TinyDB(db_path=DB_PATH) as db:
        table = db.table(tournament_id)
        Game_Q = Query()
        game_is_saved = table.contains(Game_Q.game_id == game_id)
    return game_is_saved

def load_leaderboard(tournament_id):
    with TinyDB(db_path=DB_PATH) as db:
        table = db.table(tournament_id)
        all_games = table.all()
    return Leaderboard(tournament_name=tournament_id, date=date.fromisoformat(date.today), games=[Game.from_dict(g) for g in all_games])