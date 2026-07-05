# Account setup

One-time setup of the host Google account. This account owns every game's spreadsheet, forms, and Gmail labels, and is the account the software authenticates as.

## 1. Google Cloud project

1. Create a project in the [Google Cloud console](https://console.cloud.google.com/) under the host account.
2. Enable the **Google Sheets API** and the **Gmail API** for the project.
3. Configure the OAuth consent screen. Since only the host account uses the app, testing mode with the host account added as a test user is sufficient.
4. Create an OAuth client ID of type **Desktop app** and download the client secret JSON as `credentials.json` in the repository root.

`credentials.json` is gitignored and must never be committed.

## 2. Authenticate

```bash
python3 authenticate.py
```

This opens a browser to log in as the host account and asks consent for the two scopes the software uses (defined in `rankings/auth.py`):

- `spreadsheets` — read and write the game sheets.
- `gmail.readonly` — count notification emails to detect new submissions.

The resulting token is stored as `token.json` (also gitignored). The script then verifies spreadsheet access for every game registered in `rankings/games.py`.

## Re-authenticating

- Tokens refresh automatically; re-running `authenticate.py` is only needed when the token is revoked or invalid.
- If the scopes in `rankings/auth.py` ever change, delete `token.json` and run `authenticate.py` again.
