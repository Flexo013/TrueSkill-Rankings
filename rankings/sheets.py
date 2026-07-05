"""Thin Google Sheets client with rate-limit backoff and A1 range helpers."""

import random
import re
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from rankings.auth import load_credentials

RATE_LIMIT_MAX_RETRIES = 6
RATE_LIMIT_BASE_DELAY_SECONDS = 4

_RANGE_START_PATTERN = re.compile(r"^(?P<sheet>[^!]+)!(?P<col>[A-Z]+)(?P<row>\d+)")


def parse_range_start(a1_range: str):
    """Return (sheet_name, start_col_number, start_row_number) of an A1 range.

    Column and row numbers are 1-based, e.g. "Matches!B2:H" -> ("Matches", 2, 2).
    """
    match = _RANGE_START_PATTERN.match(a1_range)
    if not match:
        raise ValueError(f"Cannot parse A1 range: {a1_range!r}")
    col = 0
    for letter in match["col"]:
        col = col * 26 + ord(letter) - ord("A") + 1
    return match["sheet"], col, int(match["row"])


def execute_with_backoff(request):
    """Execute a googleapiclient request, retrying rate-limit errors with backoff."""
    for attempt in range(RATE_LIMIT_MAX_RETRIES):
        try:
            return request.execute()
        except HttpError as error:
            is_rate_limited = error.resp.status == 429
            is_last_attempt = attempt == RATE_LIMIT_MAX_RETRIES - 1
            if not is_rate_limited or is_last_attempt:
                raise
            delay = RATE_LIMIT_BASE_DELAY_SECONDS * (2 ** attempt) + random.uniform(0, 1)
            print(
                f"Sheets API rate limit hit, retrying in {delay:.1f}s "
                f"(attempt {attempt + 1}/{RATE_LIMIT_MAX_RETRIES})"
            )
            time.sleep(delay)


class SheetsClient:
    """Reads and writes cell values of a single spreadsheet."""

    def __init__(self, spreadsheet_id: str, credentials=None):
        self.spreadsheet_id = spreadsheet_id
        creds = credentials or load_credentials()
        self._values = build("sheets", "v4", credentials=creds).spreadsheets().values()

    def read(self, sheet_range: str) -> list:
        result = execute_with_backoff(
            self._values.get(spreadsheetId=self.spreadsheet_id, range=sheet_range)
        )
        return result.get("values", [])

    def write(self, sheet_range: str, values: list) -> None:
        execute_with_backoff(
            self._values.update(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_range,
                valueInputOption="RAW",
                body={"values": values},
            )
        )
