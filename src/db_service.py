from datetime import date
from tinydb import TinyDB, Query
from src.models import Game, Leaderboard
from src.paths import DB_PATH

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

        found = False
        for entry in game_obj.entries:
            if entry.team.team_name == team_name:
                entry.headbooms = headbooms
                found = True

        if not found:
            raise ValueError(f"Could not find team {team_name} in game {game_id}!")  # AI-ADDED: typo in a team name no longer gets lost silently

    save_game(tournament_id, game_obj, db_path)

def list_tournaments(db_path=DB_PATH):
    with TinyDB(db_path) as db:
        sorted_all_tables = sorted(t for t in db.tables() if not t.startswith('_'))
    return sorted_all_tables

def delete_tournament(tournament_id, db_path=DB_PATH):
    with TinyDB(db_path) as db:
        names = db.tables()
        if tournament_id not in names:
            raise ValueError(f"Could not find {tournament_id}!")
        db.drop_table(tournament_id)

def delete_game(tournament_id, game_id, db_path=DB_PATH):
    with TinyDB(db_path) as db:
        table = db.table(tournament_id)
        Game_Q = Query()
        game_to_be_deleted = table.get(Game_Q.game_id == game_id)
        if game_to_be_deleted is None:
            raise ValueError(f"Could not find {game_id} in {tournament_id}!")
        table.remove(Game_Q.game_id == game_id)