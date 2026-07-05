"""Entry point: watch Gmail for new match submissions and process each game."""

from rankings.games import GAMES
from rankings.watcher import MailWatcher


def main():
    MailWatcher(GAMES).run()


if __name__ == "__main__":
    main()
