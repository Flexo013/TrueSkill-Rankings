# Account setup

One-time setup of the host Google account. This account owns every game's spreadsheet, forms, and Gmail labels, and is the account the software authenticates as.

## 1. Google Cloud project

1. Create a project in the [Google Cloud console](https://console.cloud.google.com/) under the host account.
    - Project name: `Games Data`
    - Project ID: `games-data-1` (or something similar)
    - No organisation
2. Select the newly created project.
3. Navigate to 'Getting started' -> 'Explore and enable APIs' -> 'Enable APIs and services'.
4. Enable the **Google Sheets API** and the **Gmail API** for the project.
5. Navigate to 'OAuth consent screen' and 'Get started'.
    1. App info
        - App name: `Games Data`
        - Support email: Select current email from dropdown.
    2. Audience: `External`
    3. Contact info: Same email as above
    4. Finish
6. Navigate to 'Data access' and add the following scopes:
    1. `auth/spreedsheets` to read and edit them.
    2. `auth/gmail.readonly` to get notified of new matches.
    3.  Save these changes.
7. Navigate to 'Branding' and set URLs and a domain.
    1. Add any image as logo.
    2. Home page: `https://github.com/Flexo013/TrueSkill-Rankings`
    3. Privacy policy and ToS: `https://github.com/Flexo013/TrueSkill-Rankings/blob/main/README.md`
    4. Authorized domain: `github.com`
    5. Save these changes.
8. Navigate to 'Audience' and publish the app.
    - Note that the verification status is not blocking for using the app.

## 2. Authenticate

```bash
python3 authenticate.py
```

This opens a browser to log in as the host account and asks consent for the two scopes the software uses (defined in `rankings/auth.py`):

- `spreadsheets`: read and write the game sheets.
- `gmail.readonly`: count notification emails to detect new submissions.

The resulting token is stored as `token.json` (also gitignored). The script then verifies spreadsheet access for every game registered in `rankings/games.py`.

## Re-authenticating

- If the scopes in `rankings/auth.py` ever change, delete `token.json` and run `authenticate.py` again.
