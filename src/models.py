from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict, Tuple

"""
Data models for the tournament system.
"""


# CONSTANTS
HEADBOOM_PENALTY = 5


@dataclass
class Team:
    """Represents a single team in the tournament."""
    team_name: str
    account_names: List[str] = field(default_factory=list)

    def to_dict(self):
        team_dict = {
            "team_name": self.team_name,
            "account_names": self.account_names
        }
        return team_dict

    @classmethod
    def from_dict(cls, d):    
        return cls(team_name = d["team_name"], account_names = d.get("account_names", []))
    

@dataclass
class GameEntryPerTeam:
    """Represents a single team's performance in one game/match."""
    team: Team
    characters_used: List[str]
    csv_points: float
    placement: int
    checkpoint: bool = False
    headbooms: int = 0
    p1_tk: int = 0
    p2_tk: int = 0
    replay_code: Optional[str] = None

    @property
    def total_score(self) -> float:
        return self.csv_points - self.headbooms * HEADBOOM_PENALTY

    def to_dict(self):
        game_entry_per_team_dict = {
            "team" : self.team.to_dict(),
            "characters_used": self.characters_used,
            "csv_points": self.csv_points,
            "placement": self.placement,
            "checkpoint": self.checkpoint,
            "headbooms": self.headbooms,
            "p1_tk": self.p1_tk,
            "p2_tk": self.p2_tk,
            "replay_code": self.replay_code
        }
        return game_entry_per_team_dict

    @classmethod
    def from_dict(cls, d):
        return cls(team = Team.from_dict(d["team"]), characters_used=d.get("characters_used",[]),csv_points=d["csv_points"], placement = d["placement"], checkpoint=d.get("checkpoint", False), headbooms=d.get("headbooms",0), p1_tk=d.get("p1_tk",0), p2_tk=d.get("p2_tk",0), replay_code=d.get("replay_code",None))


@dataclass
class Game:
    """A single game containing multiple `GameEntry` rows (one per team)."""
    game_id: int
    date: date
    entries: List[GameEntryPerTeam] = field(default_factory=list)

    def sorted_entries(self) -> List[GameEntryPerTeam]:
        return sorted(self.entries, key=lambda e: e.total_score, reverse=True)

    def character_counters(self):
        all_characters=[]
        for e in self.entries:
            all_characters.extend(e.characters_used)
        return Counter(all_characters)

    def to_dict(self):
        game_dict =  {
            "game_id": self.game_id,
            "date": self.date.isoformat(),
            "entries": [entry.to_dict() for entry in self.entries]
        }
        return game_dict
    @classmethod
    def from_dict(cls, d):
        return cls(game_id=d["game_id"],date=date.isoformat(d["date"]), entries = [GameEntryPerTeam.from_dict(e) for e in d["entries"]])


@dataclass
class TeamStanding:
    team: Team
    points: float
    p1_tk: int
    p2_tk: int
    rank: int = 0



@dataclass
class Leaderboard:
    """Aggregates multiple games into a tournament leaderboard.

    Use `games` as the canonical list of per-game results; aggregate
    methods compute totals per team when needed.
    """
    tournament_name: str
    date: date
    games: List[Game] = field(default_factory=list)

    def add_game(self, game: Game) -> None:
        self.games.append(game)

    def team_entries(self, team_name: str) -> List[GameEntryPerTeam]:
        result: List[GameEntryPerTeam] = []
        for g in self.games:
            for e in g.entries:
                if e.team.team_name == team_name:
                    result.append(e)
        return result

    def team_total_score(self, team_name: str) -> float:
        return sum(e.total_score for e in self.team_entries(team_name))

    def overall_standings(self):
        all_team_data = {}
        for game in self.games:
            for entry in game.entries:
                all_team_data.setdefault(entry.team.team_name, []).append(entry)
        scorelist = []
        for team_name in all_team_data:
            entries = all_team_data[team_name]
            points = self.team_total_score(team_name)
            p1_tk = 0 
            p2_tk = 0
            team = entries[0].team
            for e in entries:
                p1_tk = p1_tk + e.p1_tk
                p2_tk = p2_tk + e.p2_tk

            standing = TeamStanding(team=team, points=points, p1_tk=p1_tk, p2_tk=p2_tk)
            scorelist.append(standing)

        scorelist.sort(key=lambda s: (-s.points, -(s.p1_tk + s.p2_tk)))
        for i, s in enumerate(scorelist, start = 1):
            s.rank = i
        return scorelist
