# Domain model structure

The domain model is defined in [`models.py`](./models.py). It represents a tournament
as a leaderboard containing games, with one result entry per team in each game.

```mermaid
classDiagram
    class Team {
        +str team_name
        +List~str~ account_names
    }

    class GameEntryPerTeam {
        +Team team
        +float score
        +int characters_used
        +bool checkpoint
        +int headbooms
        +int p1_tk
        +int p2_tk
        +Optional~float~ total_score
        +Optional~str~ replay_code
        +Optional~int~ game_id
        +Optional~date~ date
        +compute_total() float
    }

    class Game {
        +int game_id
        +date date
        +List~GameEntryPerTeam~ entries
        +sorted_entries() List~GameEntryPerTeam~
    }

    class Leaderboard {
        +str tournament_name
        +date date
        +List~Game~ games
        +add_game(Game) None
        +team_entries(str) List~GameEntryPerTeam~
        +team_total_characters(str) int
        +team_total_score(str) float
        +overall_standings() List
    }

    GameEntryPerTeam --> Team : records performance for
    Game "1" *-- "0..*" GameEntryPerTeam : contains
    Leaderboard "1" *-- "0..*" Game : aggregates
```

## Relationships

- **`Team`** is the registered team and its player/account names.
- **`GameEntryPerTeam`** is the team's result for one game. It owns the
  per-game scoring and usage fields and references the team it belongs to.
- **`Game`** groups all team entries for one game identified by `game_id`.
- **`Leaderboard`** groups games for a tournament and calculates totals and
  standings across those games.

## Data flow around the model

```mermaid
flowchart LR
    CSV["Game CSV"] --> Services["services.py"]
    JSON["teams.json"] --> DB["db_service.py"]
    Services --> Models["models.py"]
    Models --> DB
    DB --> Stored[(tournament_db.json)]
    Models --> PNG["generate_png.py"]
    PNG --> Image["standings PNG"]
```

`services.py` extracts raw CSV values, `db_service.py` persists and reconstructs
the dataclasses, and `generate_png.py` consumes `Leaderboard.overall_standings()`
to render the final standings image.
