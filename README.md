# TrueSkill Rankings

A Python implementation of the [TrueSkill](https://trueskill.org/) ranking system. Used for modelling the skill level of players in a mix of 1v1, 1v2, 2v1, and 2v2 matches. Data storage is handled by Google Sheets, and data collection by Google Forms. Google Apps Script is used for syncing data between the input forms.

## Foosball

The current foosball rankings and leaderboard are managed by this repository's code. The [create player](https://docs.google.com/forms/d/e/1FAIpQLSe6t1b2XdOFceT9-mOzIVnFznLl1ZtgOAoBt6j9D5ipek-fcQ/viewform) and [submit match](https://docs.google.com/forms/u/0/d/e/1FAIpQLSeflIJn3-6S0LcnKtBoi0NXz4P_MIzsPnrvgv_zNzMMDRTzEQ/viewform) forms are the main way of interacting with the system. Leaderboard is yet to be implemented.