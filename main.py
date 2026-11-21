import src.services, src.db_service, src.generate_png


def import_csv(csv_path, tournament_id):
    csv_data = src.services.load_csv_data(csv_path=csv_path)
    built_game = src.services.build_game_from_csv(csv_data)
    if not src.db_service.is_game_saved(tournament_id=tournament_id, game_id=built_game.game_id):
        src.db_service.save_game(tournament_id=tournament_id, game=built_game)


def show_standings(tournament_id):
    tournament = src.db_service.load_leaderboard(tournament_id=tournament_id)
    return tournament.overall_standings()

def create_png(tournament_id, output_path):
    standings = show_standings(tournament_id)
    src.generate_png.create_png(standings, output_path)

if __name__ == "__main__":
    import_csv("assets/Game 1.csv", "EU_DOJO_NR_1")
    for s in show_standings("EU_DOJO_NR_1"):
        print(s.rank, s.team.team_name, s.points)

    create_png("EU_DOJO_NR_1", "output_test.png")