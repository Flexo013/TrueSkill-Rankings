import trueskill as tk
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import google_auth
import rating_logic

MATCH_ENTRY_CELL_COUNT = 6
NAME_ENTRY_CELL_COUNT = 1

# The ID and ranges of the spreadsheet.
MAIN_SPREADSHEET_ID = "1ij0SE4S9ZPYfDm8_JW4PFMnbDvhp6hmlIckQN1fKUQ8"
PLAYER_NAMES_RANGE = "Players!B2:B"
PLAYER_NAMES_PROC_RANGE = "Players!B2:C"
RATINGS_OVERALL_RANGE = "Ratings!A3:C"
RATINGS_OFFENSE_RANGE = "Ratings!E3:G"
RATINGS_DEFENSE_RANGE = "Ratings!I3:K"
MATCHES_PROC_RANGE = "Matches!B2:H"
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
    names = read_value("Players!B2:C")

    for i in range(len(names)):
        if len(names[i]) > NAME_ENTRY_CELL_COUNT:
            continue

        row_number = i + int(RATINGS_OVERALL_RANGE[10])
        row_label = "R" + str(row_number)
        processed_cell = "Players!" + row_label + "C3"
        processed = read_value(processed_cell)
        if not processed:
            new_rating = tk.Rating()
            rating_cells = "Ratings!" + row_label + "C2:" + row_label + "C3"
            write_value(rating_cells, [[new_rating.mu, new_rating.sigma]])
            write_value(processed_cell, [["TRUE"]])


def update_rating(row_number, mu, sigma):
    write_value(
        "Ratings!R{0}C2:R{0}C3".format(row_number),
        [[mu, sigma]]
    )


def process_match(match_data):
    rating_data = read_value(PLAYER_NAMES_PROC_RANGE)

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

    if len(set(result)) != len(result):
        # Bogus input where a player occurs multiple times
        return

    old_ratings = []
    for p in result:
        if p == "":
            old_ratings.append(None)
        else:
            old_ratings.append(tk.Rating(rating_dict[p][0], rating_dict[p][1]))

    new_ratings = rating_logic.run_dynamic_match(old_ratings)

    for i, p in enumerate(filter(lambda name: name, result)):
        update_rating(list(rating_dict.keys()).index(p) + 2,
                      new_ratings[i].mu, new_ratings[i].sigma)


def process_matches():
    matches = read_value(MATCHES_PROC_RANGE)

    for i in range(len(matches)):
        if len(matches[i]) > MATCH_ENTRY_CELL_COUNT:
            continue

        row_number = i + int(MATCHES_PROC_RANGE[10])
        row_label = "R" + str(row_number)
        processed_cell = "Matches!" + row_label + "C8"
        processed = read_value(processed_cell)
        if not processed:
            process_match(matches[i])
            write_value(processed_cell, [["TRUE"]])


def calculate_leaderboard():
    rating_data = read_value(RATINGS_OVERALL_RANGE)

    name_list = []
    rating_dict = {}
    for n, m, s in rating_data:
        rating_dict[n] = tk.Rating(float(m), float(s))
        name_list.append(n)

    leaderboard = sorted(list(rating_dict.values()), reverse=True)
    leader_ranks = []
    for s in leaderboard:
        leader_ranks.append(list(rating_dict.keys())[list(rating_dict.values()).index(s)])

    leader_ranks_values = [[i + 1, name] for i, name in enumerate(leader_ranks)]
    write_value(LEADERBOARD_OVERALL_RANGE, leader_ranks_values)


def main():
    tk.setup(1000, 333, 166, 3.3333, draw_probability=0.001)
    init_players()
    process_matches()
    calculate_leaderboard()


if __name__ == "__main__":
    main()
