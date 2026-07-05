# Mail triggers

The processor does not poll the spreadsheets directly. Instead, every form submission produces a notification email, and the watcher (`rankings/watcher.py`) counts today's emails under each game's Gmail label. When the count grows, that game — and only that game — is processed.

## Setup per game

1. On each of the game's forms, open the **Responses** tab and enable **Get email notifications for new responses** (while logged in as the host account, which owns the forms).
2. In the host account's Gmail, create a label for the game (e.g. `Games/Airhockey`).
3. Create a filter that applies this label to the game's notification emails. Filtering on subject works well, since notification subjects contain the form title — make sure each game's form titles are distinguishable.
4. Find the label's ID:

   ```bash
   python3 list_labels.py
   ```

5. Use that label ID as the `gmail_label_id` of the game's `GameConfig` — see [Registering games](registering-games.md).

## How detection behaves

- The watcher polls every 30 seconds during working hours (weekdays 08:00–22:00, see `rankings/watcher.py`).
- Only emails from the current day are counted, so old mail does not need to be cleaned up.
- On startup the count for each game starts at zero, so any of today's existing emails trigger one initial processing run per game.
- Each label must be specific to one game: a shared label would trigger processing of the wrong game (harmless, as processing is idempotent, but noisy).
