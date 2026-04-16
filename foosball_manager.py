import trueskill as tk
from dataclasses import dataclass
from enum import Enum
import math
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
MATCHES_PROC_RANGE = "Matches!B2:H"
BALANCING_PROC_RANGE = "Balancing!B2:G"
# Score impact factors
MIN_SCORE_FACTOR = 0.75
MAX_SCORE_FACTOR = 1.25
QUALITY_MIN_FACTOR = 0.85
QUALITY_FACTOR_SPAN = 0.3
STANDARD_MATCH_TARGET_SCORE = 10


class RatingCategory(Enum):
    OVERALL = "overall"
    OFFENSE = "offense"
    DEFENSE = "defense"
    SOLO = "solo"


@dataclass(frozen=True)
class RatingCategoryConfig:
    rating_range: str
    leaderboard_range: str
    start_col: int


RATING_CATEGORY_CONFIG = {
    RatingCategory.OVERALL: RatingCategoryConfig(
        rating_range="Ratings!A3:C",
        leaderboard_range="Leaderboard!A3:B",
        start_col=2,
    ),
    RatingCategory.OFFENSE: RatingCategoryConfig(
        rating_range="Ratings!E3:G",
        leaderboard_range="Leaderboard!D3:E",
        start_col=6,
    ),
    RatingCategory.DEFENSE: RatingCategoryConfig(
        rating_range="Ratings!I3:K",
        leaderboard_range="Leaderboard!G3:H",
        start_col=10,
    ),
    RatingCategory.SOLO: RatingCategoryConfig(
        rating_range="Ratings!M3:O",
        leaderboard_range="Leaderboard!J3:K",
        start_col=14,
    ),
}


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
    player_names = [ # Convert to strings to ensure set logic works to catch duplicates
        str(row[0]).strip()
        for row in names
        if row and str(row[0]).strip()
    ]

    if len(set(player_names)) != len(player_names):
        print("Found duplicate player, aborting this run.")
        return False

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
            for category in RatingCategory:
                start_col = RATING_CATEGORY_CONFIG[category].start_col
                rating_cells = "Ratings!{0}C{1}:{0}C{2}".format(
                    rating_row_label,
                    start_col,
                    start_col + 1,
                )
                write_value(rating_cells, [[new_rating.mu, new_rating.sigma]])
            write_value(processed_cell, [["TRUE"]])

    return True


def update_rating(category, row_number, mu, sigma):
    start_col = RATING_CATEGORY_CONFIG[category].start_col
    write_value(
        "Ratings!R{0}C{1}:R{0}C{2}".format(row_number, start_col, start_col + 1),
        [[mu, sigma]]
    )


def scale_rating_update(old_rating, new_rating, factor):
    return tk.Rating(
        mu=old_rating.mu + (new_rating.mu - old_rating.mu) * factor,
        sigma=old_rating.sigma + (new_rating.sigma - old_rating.sigma) * factor,
    )


def read_rating_dict(category):
    rating_data = read_value(RATING_CATEGORY_CONFIG[category].rating_range)
    rating_dict = {}
    for n, m, s in rating_data:
        rating_dict[n] = [float(m), float(s)]
    return rating_dict


def get_player_rating(rating_dict, player_name):
    return tk.Rating(mu=rating_dict[player_name][0], sigma=rating_dict[player_name][1])


def get_player_row_number(rating_dict, player_name):
    return list(rating_dict.keys()).index(player_name) + 3


def is_default_rating(rating):
    env = tk.global_env()
    return math.isclose(rating.mu, env.mu) and math.isclose(rating.sigma, env.sigma)


def calculate_match_length_factor(target_score):
    return 0.5 + 0.5 * (target_score / STANDARD_MATCH_TARGET_SCORE)


def calculate_score_factor(blue_team, red_team, score_blue, score_red):
    margin = abs(score_blue - score_red)
    target_score = max(score_blue, score_red)

    # Score Factor: Linear margin scaling, capped at 1.25
    scaled_margin = MIN_SCORE_FACTOR + margin / 20.0
    score_factor = min(MAX_SCORE_FACTOR, scaled_margin)

    # Quality Factor: Damp score impact for uneven matchups and boost it slightly for balanced ones.
    quality_factor = QUALITY_MIN_FACTOR + QUALITY_FACTOR_SPAN * tk.quality([blue_team, red_team])

    match_length_factor = calculate_match_length_factor(target_score)

    return score_factor * quality_factor * match_length_factor


def process_match(match_data):
    rating_dict = read_rating_dict(RatingCategory.OVERALL)

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
        run_small_match(rating_dict, result)
    else:
        run_full_match(p1, p2, p3, p4, score_blue, score_red)


def run_small_match(rating_dict, result):
    old_ratings = []
    for p in result:
        if p == "":
            old_ratings.append(None)
        else:
            old_ratings.append(get_player_rating(rating_dict, p))

    new_ratings = rating_logic.run_dynamic_match(old_ratings)
    for i, p in enumerate(filter(lambda name: name, result)):
        update_rating(RatingCategory.OVERALL, get_player_row_number(rating_dict, p),
                      new_ratings[i].mu, new_ratings[i].sigma)

    solo_rating_dict = read_rating_dict(RatingCategory.SOLO)
    old_solo_ratings = []
    for p in result:
        if p == "":
            old_solo_ratings.append(None)
        else:
            old_solo_ratings.append(get_player_rating(solo_rating_dict, p))

    new_solo_ratings = rating_logic.run_dynamic_match(old_solo_ratings)
    for i, p in enumerate(filter(lambda name: name, result)):
        update_rating(RatingCategory.SOLO, get_player_row_number(solo_rating_dict, p),
                      new_solo_ratings[i].mu, new_solo_ratings[i].sigma)


def run_full_match(red_off, red_def, blue_off, blue_def, score_blue, score_red):
    """Process a 2v2 foosball match.

    red_off, red_def, blue_off, and blue_def are player name strings.
    score_blue and score_red are the final team scores.
    """
    # Calculate new ratings for players (OVERALL)
    overall_dict = read_rating_dict(RatingCategory.OVERALL)

    player_red_offense_old_rating_overall = get_player_rating(overall_dict, red_off)
    player_red_defense_old_rating_overall = get_player_rating(overall_dict, red_def)
    player_blue_offense_old_rating_overall = get_player_rating(overall_dict, blue_off)
    player_blue_defense_old_rating_overall = get_player_rating(overall_dict, blue_def)

    blue_team = [player_blue_offense_old_rating_overall, player_blue_defense_old_rating_overall]
    red_team = [player_red_offense_old_rating_overall, player_red_defense_old_rating_overall]
    score_delta = calculate_score_factor(blue_team, red_team, score_blue, score_red)

    # Raw scores do not affect the TrueSkill update directly; only winner/loser order does.
    team_ranks = [0, 1] if score_blue > score_red else [1, 0]

    (
        blue_team_new_ratings_overall,
        red_team_new_ratings_overall,
    ) = tk.rate(
        [blue_team, red_team],
        ranks=team_ranks
    )
    (
        player_blue_offense_new_rating_overall,
        player_blue_defense_new_rating_overall,
    ) = blue_team_new_ratings_overall
    (
        player_red_offense_new_rating_overall,
        player_red_defense_new_rating_overall,
    ) = red_team_new_ratings_overall

    player_red_offense_new_rating_overall = scale_rating_update(
        player_red_offense_old_rating_overall, player_red_offense_new_rating_overall, score_delta
    )
    player_red_defense_new_rating_overall = scale_rating_update(
        player_red_defense_old_rating_overall, player_red_defense_new_rating_overall, score_delta
    )
    player_blue_offense_new_rating_overall = scale_rating_update(
        player_blue_offense_old_rating_overall, player_blue_offense_new_rating_overall, score_delta
    )
    player_blue_defense_new_rating_overall = scale_rating_update(
        player_blue_defense_old_rating_overall, player_blue_defense_new_rating_overall, score_delta
    )

    update_rating(RatingCategory.OVERALL, get_player_row_number(overall_dict, red_off),
                  player_red_offense_new_rating_overall.mu, player_red_offense_new_rating_overall.sigma)
    update_rating(RatingCategory.OVERALL, get_player_row_number(overall_dict, red_def),
                  player_red_defense_new_rating_overall.mu, player_red_defense_new_rating_overall.sigma)
    update_rating(RatingCategory.OVERALL, get_player_row_number(overall_dict, blue_off),
                  player_blue_offense_new_rating_overall.mu, player_blue_offense_new_rating_overall.sigma)
    update_rating(RatingCategory.OVERALL, get_player_row_number(overall_dict, blue_def),
                  player_blue_defense_new_rating_overall.mu, player_blue_defense_new_rating_overall.sigma)

    # Calculate new ratings for players (OFFENSE/DEFENSE)
    offense_dict = read_rating_dict(RatingCategory.OFFENSE)
    defense_dict = read_rating_dict(RatingCategory.DEFENSE)

    player_red_offense_old_rating_offense = get_player_rating(offense_dict, red_off)
    player_red_defense_old_rating_defense = get_player_rating(defense_dict, red_def)
    player_blue_offense_old_rating_offense = get_player_rating(offense_dict, blue_off)
    player_blue_defense_old_rating_defense = get_player_rating(defense_dict, blue_def)

    red_team = [player_red_offense_old_rating_offense, player_red_defense_old_rating_defense]
    blue_team = [player_blue_offense_old_rating_offense, player_blue_defense_old_rating_defense]
    score_delta = calculate_score_factor(blue_team, red_team, score_blue, score_red)

    # Raw scores do not affect the TrueSkill update directly; only winner/loser order does.
    team_ranks = [0, 1] if score_blue > score_red else [1, 0]

    (
        blue_team_new_ratings_offense_defense,
        red_team_new_ratings_offense_defense,
    ) = tk.rate(
        [blue_team, red_team],
        ranks=team_ranks
    )
    (
        player_blue_offense_new_rating_offense,
        player_blue_defense_new_rating_defense,
    ) = blue_team_new_ratings_offense_defense
    (
        player_red_offense_new_rating_offense,
        player_red_defense_new_rating_defense,
    ) = red_team_new_ratings_offense_defense
    player_red_offense_new_rating_offense = scale_rating_update(
        player_red_offense_old_rating_offense, player_red_offense_new_rating_offense, score_delta
    )
    player_red_defense_new_rating_defense = scale_rating_update(
        player_red_defense_old_rating_defense, player_red_defense_new_rating_defense, score_delta
    )
    player_blue_offense_new_rating_offense = scale_rating_update(
        player_blue_offense_old_rating_offense, player_blue_offense_new_rating_offense, score_delta
    )
    player_blue_defense_new_rating_defense = scale_rating_update(
        player_blue_defense_old_rating_defense, player_blue_defense_new_rating_defense, score_delta
    )

    update_rating(RatingCategory.OFFENSE, get_player_row_number(offense_dict, red_off),
                  player_red_offense_new_rating_offense.mu, player_red_offense_new_rating_offense.sigma)
    update_rating(RatingCategory.DEFENSE, get_player_row_number(defense_dict, red_def),
                  player_red_defense_new_rating_defense.mu, player_red_defense_new_rating_defense.sigma)
    update_rating(RatingCategory.OFFENSE, get_player_row_number(offense_dict, blue_off),
                  player_blue_offense_new_rating_offense.mu, player_blue_offense_new_rating_offense.sigma)
    update_rating(RatingCategory.DEFENSE, get_player_row_number(defense_dict, blue_def),
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
    for category in RatingCategory:
        raw_rating_dict = read_rating_dict(category)
        rating_dict = {
            name: tk.Rating(mu=float(mu), sigma=float(sigma))
            for name, (mu, sigma) in raw_rating_dict.items()
        }
        rating_dict = {
            name: rating
            for name, rating in rating_dict.items()
            if not is_default_rating(rating)
        }

        leaderboard = sorted(
            ((rating, name) for name, rating in rating_dict.items()),
            key=lambda x: tk.expose(x[0]),
            reverse=True)

        leader_ranks_values = [[i + 1, name] for i, (r, name) in enumerate(leaderboard)]
        write_value(RATING_CATEGORY_CONFIG[category].leaderboard_range, leader_ranks_values)


def get_quality_teams(balancing_data):
    [[p1, p2, p3, p4]] = balancing_data

    overall_data = read_value(RATING_CATEGORY_CONFIG[RatingCategory.OVERALL].rating_range)
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
        write_value(team_2_cell, [[team_2]])


def main():
    tk.setup(1000, 333, 166, 3.3333, draw_probability=0.001)
    if not init_players():
        return
    match_quality_checker()
    process_matches()
    calculate_leaderboard()


if __name__ == "__main__":
    main()
