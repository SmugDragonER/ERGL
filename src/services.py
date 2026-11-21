import csv
from collections import Counter
from datetime import date
from typing import List, Dict

from src.models import Team, GameEntryPerTeam, Game

'''Öffnet CSV und gibt eine Liste zurück, eine pro spieler'''
def load_csv_data(csv_path: str) -> List[Dict[str, str]]:
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        # Clean extra spaces from header keys automatically
        if reader.fieldnames:
            reader.fieldnames = [field.strip() for field in reader.fieldnames]
            
        return [{k.strip(): v.strip() for k, v in row.items() if k} for row in reader]

def extract_game_id(rows: List[Dict[str, str]]) -> int:
    """Returns the single game ID from the CSV rows as an integer."""
    for row in rows:
        val = row.get('gameId')
        if val is not None and str(val).isdigit():
            return int(val)
    raise ValueError("No valid 'gameId' found in CSV rows.")


def extract_character_usage(rows: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Returns a dictionary of characters that reached 3+ plays and their ban duration (in games).
    - 3 plays = 1 game ban
    - 4 plays = 2 games ban (+1 for each additional play)

    Not much use atm but could be expanded in the future to easily display character bans for the user.
    """
    # 1. Collect all character names used in rows
    characters = [row['character'] for row in rows if row.get('character')]
    
    # 2. Count how many times each character was played
    usage_counts = Counter(characters)
    
    banned_characters: Dict[str, int] = {}
    
    # 3. Apply ban rules
    for character, count in usage_counts.items():
        if count >= 3:
            ban_duration = count - 2
            banned_characters[character] = ban_duration
            print(f"Warning: '{character}' was played {count} times and is banned for {ban_duration} game(s)!")
            
    return banned_characters



### CODE THAT I ACTUALLY REMEMBER

def build_entry(team_name, team_rows):
    """
    Returns one TeamEntry
    """
    first = team_rows[0] # just taking the first team
    characters = []
    team_accounts = []
    for row in team_rows:
        character = row.get("character")
        characters.append(character)
        player_account = row.get("nickname")
        team_accounts.append(player_account)
    points = float(first.get("tournament total score"))
    placement = int(first.get("rank"))
    p1tk = int(first.get("down can not eliminate"))
    p2tk = int(first.get("elimination")) + int(first.get("down can eliminate"))
    team = Team(team_name=team_name,account_names=team_accounts)
    
    return GameEntryPerTeam(team=team, characters_used=characters, csv_points=points, placement=placement, p1_tk=p1tk, p2_tk=p2tk)


def build_game_from_csv(rows):
    teams = {}
    for row in rows:
        teamname = row.get("teamName")
        teams.setdefault(teamname, []).append(row)

    teamentries = []
    for team in teams:
        one_single_team_entry = build_entry(team, teams[team])
        teamentries.append(one_single_team_entry)


    currentdate = date.today()
    game_Id = extract_game_id(rows)

    return Game(game_id=game_Id, date=currentdate, entries=teamentries)
