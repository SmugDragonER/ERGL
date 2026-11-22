from datetime import date
from tinydb import TinyDB, Query
from src.models import Game, Leaderboard
from pathlib import Path
import sys


# Needed for Pyinstaller
if getattr(sys, "frozen", False): #running as exe?
    BASE_DIR = Path(sys.executable).parent # folder where the EXE is
else:
    BASE_DIR = Path(__file__).parent.parent # normal project folder


DB_PATH = BASE_DIR / "tournament_db.json"

def save_game(tournament_id, game, db_path=DB_PATH):
    with TinyDB(db_path) as db:
    
        table = db.table(tournament_id)
        Game_Q = Query()
        table.upsert(game.to_dict(), Game_Q.game_id == game.game_id)
        print("game saved")


def is_game_saved(tournament_id, game_id,db_path=DB_PATH):
    with TinyDB(db_path) as db:
        table = db.table(tournament_id)
        Game_Q = Query()
        game_is_saved = table.contains(Game_Q.game_id == game_id)
    return game_is_saved

def load_leaderboard(tournament_id,db_path=DB_PATH):
    with TinyDB(db_path) as db:
        table = db.table(tournament_id)
        all_games = table.all()
    return Leaderboard(tournament_name=tournament_id, date=date.today(), games=[Game.from_dict(g) for g in all_games])

def set_headbooms(tournament_id, game_id, team_name, headbooms, db_path=DB_PATH):
    with TinyDB(db_path) as db:
        table = db.table(tournament_id)
        Game_Q = Query()
        game_doc = table.get(Game_Q.game_id == game_id)
        if game_doc is None:
            raise ValueError(f"Could not find {game_id}!") #to make sure it doesnt crash if it cant find the game
        
        game_obj = Game.from_dict(game_doc)

        for entry in game_obj.entries:
            if entry.team.team_name == team_name:
                entry.headbooms = headbooms

    save_game(tournament_id, game_obj, db_path)
