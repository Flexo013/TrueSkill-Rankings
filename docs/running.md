# Running the software

## Install

```bash
pip3 install -r requirements.txt
```

## Commands

| Command | Purpose |
|---|---|
| `python3 authenticate.py` | One-time OAuth login as the host account; creates `token.json` and verifies spreadsheet access for every registered game. |
| `python3 mail_checker.py` | The main process: watches Gmail and processes every game in `rankings/games.py`. |
| `python3 list_labels.py` | Prints all Gmail labels with their IDs, for configuring a new game. |

## Runtime behavior

- The process polls each game's Gmail label every 30 seconds during working hours: **weekdays 08:00–22:00** (configured in `rankings/watcher.py`).
- Outside working hours the process exits, so it needs to be started each working day via cron on the host system (`-u` keeps the log unbuffered):

    ```
    55 8 * * 1-5  cd /path/to/repo && /usr/bin/python3 -u mail_checker.py >> /path/to/repo/logs/mail-checker-$(date +\%m-\%d).log 2>&1
    ```

- A processing failure in one game (bad input, API errors) is logged and does not affect other games; the failed game's unprocessed rows are retried when its next email arrives.
- Sheets API rate limits are handled with exponential backoff automatically.
- Restart the process after changing `rankings/games.py`.
