from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict, Tuple

"""
Data models for the tournament system.
"""

@dataclass
class Team:
    """Represents a single team in the tournament."""
    team_name: str
    account_names: List[str] = field(default_factory=list)
        

@dataclass
class GameEntryPerTeam:
    """Represents a single team's performance in one game/match."""
    team: Team
    score: float = 0.0
    characters_used: int = 0
    checkpoint: bool = False
    headbooms: int = 0
    p1_tk: int = 0
    p2_tk: int = 0
    total_score: Optional[float] = None
    replay_code: Optional[str] = None
    # optional link back to the parent game
    game_id: Optional[int] = None
    date: Optional[date] = None

    def compute_total(self) -> float:
        if self.total_score is not None:
            return self.total_score
        self.total_score = self.score + float(self.p1_tk or 0) + float(self.p2_tk or 0)
        return self.total_score


@dataclass
class Game:
    """A single game containing multiple `GameEntry` rows (one per team)."""
    game_id: int
    date: date
    entries: List[GameEntryPerTeam] = field(default_factory=list)

    def sorted_entries(self) -> List[GameEntryPerTeam]:
        for e in self.entries:
            if e.total_score is None:
                e.compute_total()
        return sorted(self.entries, key=lambda e: e.total_score or 0.0, reverse=True)


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

    def team_total_characters(self, team_name: str) -> int:
        return sum(e.characters_used for e in self.team_entries(team_name))

    def team_total_score(self, team_name: str) -> float:
        return sum((e.total_score if e.total_score is not None else e.compute_total()) for e in self.team_entries(team_name))

    def overall_standings(self) -> List[Tuple[Team, float, int]]:
        """Return a list of (Team, total_score, total_characters) sorted by score desc."""
        totals: Dict[str, Dict[str, float]] = {}
        for g in self.games:
            for e in g.entries:
                name = e.team.team_name
                if name not in totals:
                    totals[name] = {"team": e.team, "score": 0.0, "characters": 0}
                totals[name]["score"] += (e.total_score if e.total_score is not None else e.compute_total())
                totals[name]["characters"] += int(e.characters_used or 0)

        rows: List[Tuple[Team, float, int]] = []
        for v in totals.values():
            rows.append((v["team"], v["score"], v["characters"]))

        rows.sort(key=lambda r: r[1], reverse=True)
        return rows

