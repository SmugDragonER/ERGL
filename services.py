import csv
from collections import Counter, defaultdict
from typing import List, Dict, Set

from models import Team

def load_csv_data(csv_path: str) -> List[Dict[str, str]]:
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        # Clean extra spaces from header keys automatically
        if reader.fieldnames:
            reader.fieldnames = [field.strip() for field in reader.fieldnames]
            
        return [{k.strip(): v.strip() for k, v in row.items() if k} for row in reader]

def extract_team_objects(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    team_player = defaultdict(set)

    for row in rows:
        t_name = row.get('teamName')
        player = row.get('nickname')
        if t_name and player:
            team_player[t_name].add(player)

    return [Team(team_name=t_name, account_names=list(players)) for name, players in team_player.items()]

def extract_teams(rows: List[Dict[str, str]]) -> Set[str]:
    """Returns a set of unique team names."""
    return {row['teamName'] for row in rows if row.get('teamName')}

def extract_teams_scores(rows: List[Dict[str, str]]) -> Dict[str, float]:
    """Returns a dictionary mapping team names to their total scores."""
    return {row['tournament total score'] for row in rows if row.get('teamName') and row.get('tournament total score')}

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
