import trueskill as tk
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import google_auth
import rating_logic

MATCH_ENTRY_CELL_COUNT = 6
BALANCING_ENTRY_CELL_COUNT = 4
NAME_ENTRY_CELL_COUNT = 1

# The ID and ranges of the spreadsheet.
MAIN_SPREADSHEET_ID = "1ij0SE4S9ZPYfDm8_JW4PFMnbDvhp6hmlIckQN1fKUQ8"
PLAYER_NAMES_RANGE = "Players!B3:B"
PLAYER_NAMES_PROC_RANGE = "Players!B3:C"
RATINGS_OVERALL_RANGE = "Ratings!A3:C"
RATINGS_OFFENSE_RANGE = "Ratings!E3:G"
RATINGS_DEFENSE_RANGE = "Ratings!I3:K"
MATCHES_PROC_RANGE = "Matches!B2:H"
BALANCING_PROC_RANGE = "Balancing!B2:G"
LEADERBOARD_OVERALL_RANGE = "Leaderboard!A3:B"
LEADERBOARD_OFFENSE_RANGE = "Leaderboard!D3:E"
LEADERBOARD_DEFENSE_RANGE = "Leaderboard!G3:H"


def read_value(sheet_range):
    creds = Credentials.from_authorized_user_file("token.json", google_auth.SCOPES)

    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=MAIN_SPREADSHEET_ID, range=sheet_range)
        .execute()
    )
    values = result.get("values", [])

    return values


def write_value(sheet_range, value_array):
    creds = Credentials.from_authorized_user_file("token.json", google_auth.SCOPES)

    service = build("sheets", "v4", credentials=creds)

    body = {"values": value_array}

    # Call the Sheets API
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=MAIN_SPREADSHEET_ID,
            range=sheet_range,
            valueInputOption="RAW",
            body=body,
        )
        .execute()
    )

    print(result)


def init_players():
    names = read_value(PLAYER_NAMES_PROC_RANGE)

    for i in range(len(names)):
        if len(names[i]) > NAME_ENTRY_CELL_COUNT:
            continue

        row_number = i + int(PLAYER_NAMES_RANGE[9])
        player_row_label = "R" + str(row_number)
        rating_row_label = "R" + str(row_number)
        processed_cell = "Players!" + player_row_label + "C3"
        processed = read_value(processed_cell)
        if not processed:
            new_rating = tk.Rating()
            for j in range(2, 12, 4):
                rating_cells = "Ratings!" + rating_row_label + "C" + str(j) + ":" + rating_row_label + "C" + str(j + 1)
                write_value(rating_cells, [[new_rating.mu, new_rating.sigma]])
            write_value(processed_cell, [["TRUE"]])


def update_overall_rating(row_number, mu, sigma):
    write_value(
        "Ratings!R{0}C2:R{0}C3".format(row_number),
        [[mu, sigma]]
    )


def update_offense_rating(row_number, mu, sigma):
    write_value(
        "Ratings!R{0}C6:R{0}C7".format(row_number),
        [[mu, sigma]]
    )


def update_defense_rating(row_number, mu, sigma):
    write_value(
        "Ratings!R{0}C10:R{0}C11".format(row_number),
        [[mu, sigma]]
    )


def process_match(match_data):
    rating_data = read_value(RATINGS_OVERALL_RANGE)

    rating_dict = {}
    for n, m, s in rating_data:
        rating_dict[n] = [float(m), float(s)]

    [p1, p2, p3, p4, score_red, score_blue] = match_data
    score_red = int(score_red)
    score_blue = int(score_blue)
    if score_red > score_blue:
        result = (p1, p2, p3, p4)
    elif score_blue > score_red:
        result = (p3, p4, p1, p2)
    else:
        # We don't support draws
        return

    if len(set(result)) != len(result) and not(p2 == "" and p4 == ""):
        # Bogus input where a player occurs multiple times
        return

    if "" in result:
        run_small_match(rating_dict, result, score_blue, score_red)
    else:
        run_full_match(p1, p2, p3, p4, score_blue, score_red)


def run_small_match(rating_dict, result, score_blue, score_red):
    old_ratings = []
    for p in result:
        if p == "":
            old_ratings.append(None)
        else:
            old_ratings.append(tk.Rating(rating_dict[p][0], rating_dict[p][1]))

    new_ratings = rating_logic.run_dynamic_match(old_ratings)
    for i, p in enumerate(filter(lambda name: name, result)):
        update_overall_rating(list(rating_dict.keys()).index(p) + 3,
                              new_ratings[i].mu, new_ratings[i].sigma)


def run_full_match(red_off, red_def, blue_off, blue_def, score_blue, score_red):
    score_delta = abs(score_blue - score_red) / 5.

    # Calculate new ratings for players (OVERALL)
    overall_data = read_value(RATINGS_OVERALL_RANGE)
    overall_dict = {}
    for n, m, s in overall_data:
        overall_dict[n] = [float(m), float(s)]

    player_red_offense_old_rating_overall = tk.Rating(mu=overall_dict[red_off][0], sigma=overall_dict[red_off][1])
    player_red_defense_old_rating_overall = tk.Rating(mu=overall_dict[red_def][0], sigma=overall_dict[red_def][1])
    player_blue_offense_old_rating_overall = tk.Rating(mu=overall_dict[blue_off][0], sigma=overall_dict[blue_off][1])
    player_blue_defense_old_rating_overall = tk.Rating(mu=overall_dict[blue_def][0], sigma=overall_dict[blue_def][1])

    blue_team = [player_blue_offense_old_rating_overall, player_blue_defense_old_rating_overall]
    red_team = [player_red_offense_old_rating_overall, player_red_defense_old_rating_overall]

    # Team points are intentionally reverted!
    (player_blue_offense_new_rating_overall, player_blue_defense_new_rating_overall), (
        player_red_offense_new_rating_overall, player_red_defense_new_rating_overall) = tk.rate([blue_team, red_team],
                                                                                                ranks=[score_red,
                                                                                                       score_blue])
    player_red_offense_new_rating_overall = tk.Rating(mu=player_red_offense_old_rating_overall.mu + (
            player_red_offense_new_rating_overall.mu - player_red_offense_old_rating_overall.mu) * score_delta,
                                                      sigma=player_red_offense_new_rating_overall.sigma)
    player_red_defense_new_rating_overall = tk.Rating(mu=player_red_defense_old_rating_overall.mu + (
            player_red_defense_new_rating_overall.mu - player_red_defense_old_rating_overall.mu) * score_delta,
                                                      sigma=player_red_defense_new_rating_overall.sigma)
    player_blue_offense_new_rating_overall = tk.Rating(mu=player_blue_offense_old_rating_overall.mu + (
            player_blue_offense_new_rating_overall.mu - player_blue_offense_old_rating_overall.mu) * score_delta,
                                                       sigma=player_blue_offense_new_rating_overall.sigma)
    player_blue_defense_new_rating_overall = tk.Rating(mu=player_blue_defense_old_rating_overall.mu + (
            player_blue_defense_new_rating_overall.mu - player_blue_defense_old_rating_overall.mu) * score_delta,
                                                       sigma=player_blue_defense_new_rating_overall.sigma)

    update_overall_rating(list(overall_dict.keys()).index(red_off) + 3,
                          player_red_offense_new_rating_overall.mu, player_red_offense_new_rating_overall.sigma)
    update_overall_rating(list(overall_dict.keys()).index(red_def) + 3,
                          player_red_defense_new_rating_overall.mu, player_red_defense_new_rating_overall.sigma)
    update_overall_rating(list(overall_dict.keys()).index(blue_off) + 3,
                          player_blue_offense_new_rating_overall.mu, player_blue_offense_new_rating_overall.sigma)
    update_overall_rating(list(overall_dict.keys()).index(blue_def) + 3,
                          player_blue_defense_new_rating_overall.mu, player_blue_defense_new_rating_overall.sigma)

    # Calculate new ratings for players (OFFENSE/DEFENSE)
    offense_data = read_value(RATINGS_OFFENSE_RANGE)
    offense_dict = {}
    for n, m, s in offense_data:
        offense_dict[n] = [float(m), float(s)]

    defense_data = read_value(RATINGS_DEFENSE_RANGE)
    defense_dict = {}
    for n, m, s in defense_data:
        defense_dict[n] = [float(m), float(s)]

    player_red_offense_old_rating_offense = tk.Rating(mu=offense_dict[red_off][0], sigma=offense_dict[red_off][1])
    player_red_defense_old_rating_defense = tk.Rating(mu=defense_dict[red_def][0], sigma=defense_dict[red_def][1])
    player_blue_offense_old_rating_offense = tk.Rating(mu=offense_dict[blue_off][0], sigma=offense_dict[blue_off][1])
    player_blue_defense_old_rating_defense = tk.Rating(mu=defense_dict[blue_def][0], sigma=defense_dict[blue_def][1])

    red_team = [player_red_offense_old_rating_offense, player_red_defense_old_rating_defense]
    blue_team = [player_blue_offense_old_rating_offense, player_blue_defense_old_rating_defense]

    # Team points are intentionally reverted!
    (player_blue_offense_new_rating_offense, player_blue_defense_new_rating_defense), (
        player_red_offense_new_rating_offense, player_red_defense_new_rating_defense) = tk.rate([blue_team, red_team],
                                                                                                ranks=[score_red,
                                                                                                       score_blue])
    player_red_offense_new_rating_offense = tk.Rating(mu=player_red_offense_old_rating_offense.mu + (
            player_red_offense_new_rating_offense.mu - player_red_offense_old_rating_offense.mu) * score_delta,
                                                      sigma=player_red_offense_new_rating_offense.sigma)
    player_red_defense_new_rating_defense = tk.Rating(mu=player_red_defense_old_rating_defense.mu + (
            player_red_defense_new_rating_defense.mu - player_red_defense_old_rating_defense.mu) * score_delta,
                                                      sigma=player_red_defense_new_rating_defense.sigma)
    player_blue_offense_new_rating_offense = tk.Rating(mu=player_blue_offense_old_rating_offense.mu + (
            player_blue_offense_new_rating_offense.mu - player_blue_offense_old_rating_offense.mu) * score_delta,
                                                       sigma=player_blue_offense_new_rating_offense.sigma)
    player_blue_defense_new_rating_defense = tk.Rating(mu=player_blue_defense_old_rating_defense.mu + (
            player_blue_defense_new_rating_defense.mu - player_blue_defense_old_rating_defense.mu) * score_delta,
                                                       sigma=player_blue_defense_new_rating_defense.sigma)

    update_offense_rating(list(offense_dict.keys()).index(red_off) + 3,
                          player_red_offense_new_rating_offense.mu, player_red_offense_new_rating_offense.sigma)
    update_defense_rating(list(defense_dict.keys()).index(red_def) + 3,
                          player_red_defense_new_rating_defense.mu, player_red_defense_new_rating_defense.sigma)
    update_offense_rating(list(offense_dict.keys()).index(blue_off) + 3,
                          player_blue_offense_new_rating_offense.mu, player_blue_offense_new_rating_offense.sigma)
    update_defense_rating(list(defense_dict.keys()).index(blue_def) + 3,
                          player_blue_defense_new_rating_defense.mu, player_blue_defense_new_rating_defense.sigma)


def process_matches():
    matches = read_value(MATCHES_PROC_RANGE)

    for i in range(len(matches)):
        if len(matches[i]) > MATCH_ENTRY_CELL_COUNT:
            continue

        row_number = i + int(MATCHES_PROC_RANGE[9])
        row_label = "R" + str(row_number)
        processed_cell = "Matches!" + row_label + "C8"
        processed = read_value(processed_cell)
        if not processed:
            process_match(matches[i])
            write_value(processed_cell, [["TRUE"]])


def calculate_leaderboard():
    boards = [
        [RATINGS_OVERALL_RANGE, LEADERBOARD_OVERALL_RANGE],
        [RATINGS_OFFENSE_RANGE, LEADERBOARD_OFFENSE_RANGE],
        [RATINGS_DEFENSE_RANGE, LEADERBOARD_DEFENSE_RANGE],
    ]
    for rating_range, leaderboard_range in boards:
        rating_data = read_value(rating_range)

        name_list = []
        rating_dict = {}
        for n, m, s in rating_data:
            rating_dict[n] = tk.Rating(float(m), float(s))
            name_list.append(n)

        leaderboard = sorted(
            ((rating, name) for name, rating in rating_dict.items()),
            key=lambda x: tk.expose(x[0]),
            reverse=True)

        leader_ranks_values = [[i + 1, name] for i, (r, name) in enumerate(leaderboard)]
        write_value(leaderboard_range, leader_ranks_values)


def get_quality_teams(balancing_data):
    [[p1, p2, p3, p4]] = balancing_data

    overall_data = read_value(RATINGS_OVERALL_RANGE)
    overall_dict = {}
    for n, m, s in overall_data:
        overall_dict[n] = [float(m), float(s)]

    p1_rating = tk.Rating(overall_dict[p1][0], overall_dict[p1][1])
    p2_rating = tk.Rating(overall_dict[p2][0], overall_dict[p2][1])
    p3_rating = tk.Rating(overall_dict[p3][0], overall_dict[p3][1])
    p4_rating = tk.Rating(overall_dict[p4][0], overall_dict[p4][1])

    quality_list = [
        (tk.quality([[p1_rating, p2_rating], [p3_rating, p4_rating]]), [p1 + " " + p2, p3 + " " + p4]),
        (tk.quality([[p1_rating, p3_rating], [p2_rating, p4_rating]]), [p1 + " " + p3, p2 + " " + p4]),
        (tk.quality([[p1_rating, p4_rating], [p2_rating, p3_rating]]), [p1 + " " + p4, p2 + " " + p3]),
    ]

    min_draw_chance = 100
    best_combo = ""
    for i, (q, l) in enumerate(quality_list):
        draw_chance = abs(q - 0.5)
        if draw_chance < min_draw_chance:
            min_draw_chance = draw_chance
            best_combo = l

    return best_combo


def match_quality_checker():
    balancing_data = read_value(BALANCING_PROC_RANGE)

    for i in range(len(balancing_data)):
        if len(balancing_data[i]) > BALANCING_ENTRY_CELL_COUNT:
            continue

        row_number = i + int(BALANCING_PROC_RANGE[11])
        team_1_cell = "Balancing!{0}C6".format("R" + str(row_number))
        team_2_cell = "Balancing!{0}C7".format("R" + str(row_number))
        team_1, team_2 = get_quality_teams(balancing_data)
        write_value(team_1_cell, [[team_1]])
        write_value(team_2_cell, [[team_1]])


def main():
    tk.setup(1000, 333, 166, 3.3333, draw_probability=0.001)
    init_players()
    match_quality_checker()
    process_matches()
    calculate_leaderboard()


if __name__ == "__main__":
    main()
