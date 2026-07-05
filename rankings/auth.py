"""Google OAuth credential handling shared by the Sheets and Gmail clients."""

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.readonly",
]

TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"


def load_credentials(token_path: str = TOKEN_PATH) -> Credentials:
    """Load previously stored credentials; fails if authentication never ran."""
    if not os.path.exists(token_path):
        raise FileNotFoundError(
            f"No token found at {token_path}. Run 'python3 authenticate.py' first."
        )
    return Credentials.from_authorized_user_file(token_path, SCOPES)


def create_or_refresh_credentials(
    token_path: str = TOKEN_PATH, credentials_path: str = CREDENTIALS_PATH
) -> Credentials:
    """Run the interactive OAuth flow (or refresh) and store the token."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds
