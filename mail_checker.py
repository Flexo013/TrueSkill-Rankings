import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import google_auth
import foosball_manager

# Path to the file where the OAuth2 token will be stored
TOKEN_PATH = "token.json"

# Label to filter emails
TARGET_LABEL_ID = 'Label_6763635978072909105'  # Foosball
FETCH_LABELS = False
FETCH_EMAILS = True


def check_email(credentials):
    # Connect to Gmail server using OAuth2 credentials
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=credentials)
        if FETCH_LABELS:
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            print("Labels:")
            for i, label in enumerate(labels):
                print("{0}, {1}".format(label["name"], label["id"]))

        if FETCH_EMAILS:
            results = service.users().messages().list(userId="me", labelIds=[TARGET_LABEL_ID]).execute()
            messages = results.get('messages', [])

            return len(messages)
            print("Messages:")
            for i, message in enumerate(messages):
                print("{0}".format(message["id"]))

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

    exit()


def get_access_token(creds):
    return creds.token


if __name__ == "__main__":
    # creds = get_gmail_credentials()
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", google_auth.SCOPES)
    else:
        print("No token found!")
        exit()

    old_email_count = 0
    while True:
        emails_found = check_email(creds)
        print("Found {0} emails labelled Foosball.".format(emails_found))
        if emails_found > old_email_count:
            print("Executing processing script!")
            foosball_manager.main()
            old_email_count = emails_found

        # Sleep for 30 seconds before checking again
        time.sleep(30)
