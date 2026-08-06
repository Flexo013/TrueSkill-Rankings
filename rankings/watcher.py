"""Polls Gmail for new match submissions and triggers processing per game."""

import datetime
import time
from typing import Iterable

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from rankings.auth import load_credentials
from rankings.config import GameConfig
from rankings.processor import GameProcessor

POLL_INTERVAL_SECONDS = 30
WORKING_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
WORKING_HOURS_START = "08:00:00"
WORKING_HOURS_END = "22:00:00"


class MailWatcher:
    """Watches one Gmail label per game and processes games with new mail.

    Every Google Form submission produces a labeled notification email, so a
    growing count of today's emails under a game's label means new input rows.
    """

    def __init__(self, games: Iterable[GameConfig], token_path: str = "token.json"):
        credentials = load_credentials(token_path)
        self._gmail = build("gmail", "v1", credentials=credentials)
        self._games = list(games)
        names = [game.name for game in self._games]
        if len(set(names)) != len(names):
            raise ValueError(f"Game names must be unique, got: {names}")
        self._processors = {
            game.name: GameProcessor(game, credentials=credentials)
            for game in self._games
        }
        self._seen_email_counts = {game.name: 0 for game in self._games}

    def run(self) -> None:
        self._process_all_games()
        while self._within_working_hours():
            for game in self._games:
                self._poll_game(game)
            time.sleep(POLL_INTERVAL_SECONDS)
        print("Outside of working hours, terminating...")

    def _process_all_games(self) -> None:
        # The email-count trigger only looks at today's mail, so a game left
        # unprocessed from a prior run (crash, missed cron, downtime) would
        # otherwise sit stale until unrelated new mail happens to trigger it.
        # Running every game once on startup catches those up immediately.
        for game in self._games:
            print(f"[{game.name}] Running startup catch-up processing!")
            try:
                self._processors[game.name].run()
            except Exception as error:
                print(f"[{game.name}] Startup processing failed: {error}")

    def _within_working_hours(self) -> bool:
        return (
            time.strftime("%A") in WORKING_DAYS
            and WORKING_HOURS_START <= time.strftime("%H:%M:%S") <= WORKING_HOURS_END
        )

    def _poll_game(self, game: GameConfig) -> None:
        try:
            email_count = self._count_todays_emails(game.gmail_label_id)
        except HttpError as error:
            print(f"[{game.name}] Gmail check failed: {error}")
            return

        current_time = time.strftime("%H:%M:%S")
        print(f"[{current_time}] [{game.name}] Found {email_count} labeled emails.")
        if email_count > self._seen_email_counts[game.name]:
            print(f"[{game.name}] Executing processing script!")
            try:
                self._processors[game.name].run()
            except Exception as error:
                # One game's bad data or API failure must not take down the
                # other games running in this process. Unprocessed rows keep
                # their state, so the next email triggers a full retry.
                print(f"[{game.name}] Processing failed: {error}")
            self._seen_email_counts[game.name] = email_count
            print(f"[{game.name}] Done processing!")

    def _count_todays_emails(self, label_id: str) -> int:
        today_start = int(
            datetime.datetime.combine(datetime.date.today(), datetime.time.min).timestamp()
        )
        results = (
            self._gmail.users()
            .messages()
            .list(userId="me", labelIds=[label_id], q=f"after:{today_start}")
            .execute()
        )
        return len(results.get("messages", []))
