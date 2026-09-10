# Game setup checklist

Everything on this page happens under the host account (see [Account setup](account-setup.md)). Follow these steps for each new game. A second league of an existing game for a different group of colleagues is set up exactly the same way, with its own spreadsheet, forms, and label.

1. **[Forms and spreadsheet](forms.md)**: copy the spreadsheet template and create the game's input forms.
2. **[Apps Script](apps-script.md)**: install the dropdown-sync script on the new spreadsheet and point it at the new forms.
3. **[Mail triggers](mail-triggers.md)**: enable form email notifications and label them in Gmail.
4. **[Registering games](registering-games.md)**: add the game's `GameConfig` to `rankings/games.py`.

After registering, restart the running process (see [Running the software](running.md)) to pick up the new game. `authenticate.py` can be re-run at any time to verify the process can reach the new spreadsheet.
