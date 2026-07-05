# Documentation

All games are managed by a single host Google account running a single process. Setup is split into one-time account setup, per-game setup, and running the software.

## One-time

- [Account setup](account-setup.md) — Google Cloud project, OAuth credentials, authentication.

## Per game

Follow the [game setup checklist](game-setup.md), which walks through:

1. [Forms and spreadsheet](forms.md) — the game spreadsheet and its input forms.
2. [Apps Script](apps-script.md) — keeping form dropdowns in sync with the player list.
3. [Mail triggers](mail-triggers.md) — how form submissions notify the processor.
4. [Registering games](registering-games.md) — adding the `GameConfig` to the code.

## Operating

- [Running the software](running.md) — launch commands and runtime behavior.
- [Managing players](managing-players.md) — retiring, unretiring, and renaming players.
