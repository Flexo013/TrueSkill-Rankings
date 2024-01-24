import trueskill as tk


def run_2v2_match(results):
    winning_team = [results[0], results[1]]
    losing_team = [results[2], results[3]]

    [(new_w1_rating, new_w2_rating), (new_l1_rating, new_l2_rating)] = tk.rate(
        [winning_team, losing_team],
        [0, 1]
    )

    return [new_w1_rating, new_w2_rating, new_l1_rating, new_l2_rating]


def run_dynamic_match(results):
    """Run 1v1, 1v2, 2v1, and 2v2 matches.
    Accepts 4 players as Rating() objects, in the order:
    [winner, winner, loser, loser]
    The 2nd and 4th parameter can be None if the team only had 1 player.
    """
    winning_team = [results[0]]
    losing_team = [results[2]]
    if results[1] is not None:
        winning_team.append(results[1])
    if results[3] is not None:
        losing_team.append(results[3])

    new_ratings = tk.rate(
        [winning_team, losing_team],
        [0, 1]
    )

    return [i for tup in new_ratings for i in tup]
